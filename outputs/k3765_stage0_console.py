#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Host console for the RAM-only K3765-Z stage-0 monitor."""

import argparse
import binascii
from collections import deque
from contextlib import contextmanager
import ctypes
from datetime import datetime
from pathlib import Path
import os
import queue
import re
import struct
import sys
import threading
import time

import serial


FLAG = 0x7E
ESC = 0x7D
SAFE_RAM_START = 0x01000000
SAFE_RAM_END = 0x02000000
INPUT_SUBCOMMAND = 0x0E
INPUT_PACKET_LIMIT = 64
DETACH_INPUT = object()

QUERIES = (
    ("MIDR", 0x01),
    ("CTR", 0x02),
    ("TCMTR", 0x03),
    ("CPSR", 0x04),
    ("SCTLR", 0x05),
    ("TTBR", 0x06),
    ("DACR", 0x07),
    ("DFSR", 0x08),
    ("IFSR", 0x09),
    ("FAR", 0x0A),
    ("SP", 0x0B),
)


def crc16_x25(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x8408 if crc & 1 else 0)
    return crc ^ 0xFFFF


def frame(payload):
    body = payload + crc16_x25(payload).to_bytes(2, "little")
    encoded = bytearray()
    for byte in body:
        if byte in (FLAG, ESC):
            encoded.extend((ESC, byte ^ 0x20))
        else:
            encoded.append(byte)
    return bytes((FLAG,)) + encoded + bytes((FLAG,))


def read_frame(port, timeout=3.0):
    deadline = time.monotonic() + timeout
    started = False
    encoded = bytearray()
    while time.monotonic() < deadline:
        value = port.read(1)
        if not value:
            continue
        byte = value[0]
        if byte == FLAG:
            if not started:
                started = True
                continue
            if not encoded:
                continue
            raw = bytearray()
            escaped = False
            for item in encoded:
                if escaped:
                    raw.append(item ^ 0x20)
                    escaped = False
                elif item == ESC:
                    escaped = True
                else:
                    raw.append(item)
            if len(raw) < 3:
                return bytes(raw)
            payload = bytes(raw[:-2])
            got = int.from_bytes(raw[-2:], "little")
            want = crc16_x25(payload)
            if got != want:
                raise RuntimeError(f"CRC mismatch: {got:04X} != {want:04X}")
            return payload
        if started:
            encoded.append(byte)
    return None


def open_port(name):
    name = name.upper()
    if name.startswith("COM") and int(name[3:]) >= 10:
        name = r"\\.\\" + name
    port = serial.Serial(name, 115200, timeout=0.05, write_timeout=5)
    port.dtr = True
    port.rts = True
    port.reset_input_buffer()
    return port


def extract_text(payload, preserve_line_endings=False):
    if payload is None:
        raise RuntimeError("target response timeout")
    # ARMPRG's print routine emits a 0x0E log frame followed by ASCII.
    if payload and payload[0] == 0x0E:
        payload = payload[1:]
    trailer = b"\x00" if preserve_line_endings else b"\x00\r\n"
    return payload.rstrip(trailer).decode("ascii", "replace")


def command(port, subcommand, args=b"", expected=None, on_message=None):
    if expected is None:
        expected = "banner" if subcommand == 0 else "hex"

    # A diagnostic print can arrive just after the preceding command has
    # returned. Clear anything already queued, then ignore any delayed frame
    # that does not match the response type requested by this command.
    port.reset_input_buffer()
    port.write(frame(bytes((0x1C, subcommand)) + args))
    port.flush()
    deadline = time.monotonic() + 3.0
    ignored = []
    while time.monotonic() < deadline:
        payload = read_frame(port, timeout=min(0.5, deadline - time.monotonic()))
        if payload is None:
            continue
        text = extract_text(payload)
        if expected == "banner" and text.startswith("K3765-S0-"):
            return text
        if expected == "hex" and re.fullmatch(r"[0-9A-Fa-f]{8}", text):
            return text
        ignored.append(text)
        if on_message is not None:
            on_message(text)
    detail = f"; ignored delayed replies: {ignored!r}" if ignored else ""
    raise RuntimeError(f"target response timeout{detail}")


def decode_midr(value):
    implementer = (value >> 24) & 0xFF
    variant = (value >> 20) & 0xF
    architecture = (value >> 16) & 0xF
    part = (value >> 4) & 0xFFF
    revision = value & 0xF
    vendor = "ARM" if implementer == 0x41 else f"implementer 0x{implementer:02X}"
    core = "ARM926EJ-S" if part == 0x926 else f"part 0x{part:03X}"
    return (
        f"{vendor} {core}, architecture field {architecture}, "
        f"variant {variant}, revision {revision}"
    )


def decode_cpsr(value):
    modes = {
        0x10: "USR",
        0x11: "FIQ",
        0x12: "IRQ",
        0x13: "SVC",
        0x17: "ABT",
        0x1B: "UND",
        0x1F: "SYS",
    }
    mode = modes.get(value & 0x1F, f"0x{value & 0x1F:02X}")
    return (
        f"mode={mode}, ARM-state={'Thumb' if value & 0x20 else 'ARM'}, "
        f"IRQ={'masked' if value & 0x80 else 'enabled'}, "
        f"FIQ={'masked' if value & 0x40 else 'enabled'}"
    )


def decode_sctlr(value):
    flags = []
    for bit, name in ((0, "MMU"), (1, "alignment"), (2, "D-cache"),
                      (3, "write-buffer"), (12, "I-cache"),
                      (13, "high-vectors")):
        flags.append(f"{name}={'on' if value & (1 << bit) else 'off'}")
    return ", ".join(flags)


def boot_log(port, log, include_banner=True):
    def emit(line=""):
        print(line)
        log.write(line + "\n")
        log.flush()

    emit("K3765-Z RAM stage-0 boot log")
    emit(f"Host time: {datetime.now().isoformat(timespec='seconds')}")
    emit("Transport: legacy Qualcomm HDLC over USB serial")
    emit("Persistence: RAM only; no NAND operation")
    emit()

    if include_banner:
        banner = command(port, 0x00)
        emit(f"Monitor: {banner}")
    else:
        emit("Monitor: K3765-S0-V1 (banner verified earlier in this RAM session)")

    values = {}
    for label, subcommand in QUERIES:
        text = command(port, subcommand)
        value = int(text, 16)
        values[label] = value
        emit(f"{label:5}: 0x{value:08X}")

    emit()
    emit(f"CPU   : {decode_midr(values['MIDR'])}")
    emit(f"CPSR  : {decode_cpsr(values['CPSR'])}")
    emit(f"SCTLR : {decode_sctlr(values['SCTLR'])}")
    emit(f"Board : ZTE/Vodafone K3765-Z")
    emit(f"SoC   : Qualcomm MSM6290 (MSM6246-family downloader)")
    emit(f"PMIC  : Qualcomm PM6658-family; RGB map R=MPP1 G=LED0 B=LED1")
    emit(f"NAND  : HYNIX_HSACS0PL0MCR OEM profile, 128 MiB + OOB")
    emit(
        "RAM   : firmware physical span reaches 0x01FAC000; "
        "stage-0 safe window is 0x01000000..0x01FFFFFF"
    )
    emit("OEMSBL: 00.02.00.04 / KPVDFP673A1M256")
    return values


def crc_query(port, address, length):
    if not SAFE_RAM_START <= address < SAFE_RAM_END:
        raise ValueError("CRC start is outside the stage-0 safe RAM window")
    if length < 0 or address + length > SAFE_RAM_END:
        raise ValueError("CRC range exceeds the stage-0 safe RAM window")
    args = struct.pack("<II", address, length)
    return int(command(port, 0x0C, args), 16)


def verify_file(port, address, path, chunk_size):
    data = path.read_bytes()
    if not data:
        raise ValueError("verification file is empty")
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    if address + len(data) > SAFE_RAM_END:
        raise ValueError("verification file exceeds the stage-0 safe RAM window")

    print(
        f"Verifying {path.name}: {len(data):,} bytes at "
        f"0x{address:08X} in {chunk_size:,}-byte watchdog-safe chunks"
    )
    for offset in range(0, len(data), chunk_size):
        chunk = data[offset:offset + chunk_size]
        local_crc = binascii.crc32(chunk) & 0xFFFFFFFF
        target_crc = crc_query(port, address + offset, len(chunk))
        status = "OK" if target_crc == local_crc else "MISMATCH"
        print(
            f"  0x{address + offset:08X}  {len(chunk):6,} bytes  "
            f"target={target_crc:08X} local={local_crc:08X}  {status}"
        )
        if target_crc != local_crc:
            raise RuntimeError(
                f"verification failed at SDRAM address "
                f"0x{address + offset:08X}"
            )

    full_crc = binascii.crc32(data) & 0xFFFFFFFF
    print(
        f"PASS: every chunk matched; local full-image CRC32 "
        f"is 0x{full_crc:08X}"
    )


def stage2_request(port, address, r0, r1, r2):
    if address & 3 or not SAFE_RAM_START <= address < SAFE_RAM_END:
        raise ValueError("stage-2 PC must be aligned inside the safe RAM window")
    args = struct.pack("<IIII", address, r0, r1, r2)
    return frame(bytes((0x1C, 0x0D)) + args)


def call_stage2(port, address, r0, r1, r2, on_message=None):
    if address & 3 or not SAFE_RAM_START <= address < SAFE_RAM_END:
        raise ValueError("stage-2 PC must be aligned inside the safe RAM window")
    args = struct.pack("<IIII", address, r0, r1, r2)
    return int(command(port, 0x0D, args, on_message=on_message), 16)


def send_linux_input(port, data):
    if isinstance(data, str):
        data = data.encode("ascii", "replace")
    for offset in range(0, len(data), INPUT_PACKET_LIMIT):
        chunk = data[offset:offset + INPUT_PACKET_LIMIT]
        port.write(frame(bytes((0x1C, INPUT_SUBCOMMAND)) + chunk))
        port.flush()


@contextmanager
def raw_console_input(enabled):
    """Put an interactive host terminal into per-key mode, then restore it."""
    if not enabled or not sys.stdin.isatty():
        yield False
        return

    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        input_handle = kernel32.GetStdHandle(ctypes.c_ulong(-10 & 0xFFFFFFFF))
        output_handle = kernel32.GetStdHandle(ctypes.c_ulong(-11 & 0xFFFFFFFF))
        input_mode = ctypes.c_ulong()
        output_mode = ctypes.c_ulong()
        if input_handle in (0, -1) or not kernel32.GetConsoleMode(
            input_handle, ctypes.byref(input_mode)
        ):
            yield False
            return
        raw_mode = input_mode.value & ~(0x0001 | 0x0002 | 0x0004)
        if not kernel32.SetConsoleMode(input_handle, raw_mode):
            yield False
            return
        output_changed = (
            output_handle not in (0, -1)
            and kernel32.GetConsoleMode(
                output_handle, ctypes.byref(output_mode)
            )
            and kernel32.SetConsoleMode(
                output_handle, output_mode.value | 0x0004
            )
        )
        try:
            yield True
        finally:
            kernel32.SetConsoleMode(input_handle, input_mode.value)
            if output_changed:
                kernel32.SetConsoleMode(output_handle, output_mode.value)
        return

    import termios
    import tty

    descriptor = sys.stdin.fileno()
    original = termios.tcgetattr(descriptor)
    tty.setraw(descriptor)
    try:
        yield True
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, original)


def stdin_reader(chunks, raw_keys):
    try:
        if raw_keys and os.name == "nt":
            import msvcrt

            extended_keys = {
                "H": b"\x1b[A", "P": b"\x1b[B",
                "M": b"\x1b[C", "K": b"\x1b[D",
                "G": b"\x1b[H", "O": b"\x1b[F",
                "S": b"\x1b[3~",
            }
            while True:
                character = msvcrt.getwch()
                if character in ("\x00", "\xe0"):
                    mapped = extended_keys.get(msvcrt.getwch())
                    if mapped:
                        chunks.put(mapped)
                    continue
                if character == "\x1d":
                    chunks.put(DETACH_INPUT)
                    return
                if character == "\r":
                    chunks.put(b"\n")
                elif character == "\x08":
                    chunks.put(b"\x7f")
                else:
                    chunks.put(character.encode("ascii", "replace"))
            return

        if raw_keys:
            while True:
                character = os.read(sys.stdin.fileno(), 1)
                if not character:
                    return
                if character == b"\x1d":
                    chunks.put(DETACH_INPUT)
                    return
                chunks.put(character)
            return

        for line in sys.stdin:
            chunks.put(line.encode("ascii", "replace"))
    except (EOFError, OSError):
        return


def follow_linux(
    port,
    address,
    r0,
    r1,
    r2,
    on_message,
    idle_timeout,
    max_runtime,
    interactive=False,
    initial_commands=(),
    issue_boot_request=True,
):
    port.reset_input_buffer()
    if issue_boot_request:
        request = stage2_request(port, address, r0, r1, r2)
        port.write(request)
        port.flush()

    pending_lines = deque(
        command.rstrip("\r\n") + "\n" for command in initial_commands
    )
    live_chunks = queue.Queue()
    with raw_console_input(interactive) as raw_keys:
        if interactive:
            threading.Thread(
                target=stdin_reader,
                args=(live_chunks, raw_keys),
                daemon=True,
            ).start()

        start = time.monotonic()
        idle_deadline = (
            float("inf") if interactive or idle_timeout <= 0
            else start + idle_timeout
        )
        absolute_deadline = (
            start + max_runtime if max_runtime > 0 else float("inf")
        )
        terminal_ready = not issue_boot_request
        scripted_ready = not issue_boot_request
        while True:
            now = time.monotonic()

            if terminal_ready:
                outgoing = None
                scripted = False
                if pending_lines and scripted_ready:
                    outgoing = pending_lines.popleft().encode(
                        "ascii", "replace"
                    )
                    scripted = True
                elif interactive and not pending_lines:
                    try:
                        outgoing = live_chunks.get_nowait()
                    except queue.Empty:
                        pass
                if outgoing is DETACH_INPUT:
                    on_message(
                        "\r\nHost detached with Ctrl+]; Linux remains in RAM.\r\n"
                    )
                    return None
                if outgoing:
                    send_linux_input(port, outgoing)
                    if scripted or not raw_keys:
                        scripted_ready = False

            if now >= absolute_deadline:
                on_message(
                    f"\r\nMaximum capture runtime of {max_runtime:g} seconds "
                    "reached; target left running.\r\n"
                )
                return None
            if now >= idle_deadline:
                on_message(
                    f"\r\nNo new target frame for {idle_timeout:g} seconds.\r\n"
                )
                return None
            try:
                payload = read_frame(
                    port,
                    timeout=min(
                        0.1 if interactive else 1.0,
                        idle_deadline - now,
                        absolute_deadline - now,
                    ),
                )
            except (OSError, serial.SerialException) as error:
                on_message(
                    f"\r\nTransport disconnected after handoff: {error}\r\n"
                )
                return None
            if payload is None:
                continue
            text = extract_text(payload, preserve_line_endings=True)
            on_message(text)
            if "shadow-msm# " in text:
                terminal_ready = True
                scripted_ready = True
            if not interactive and idle_timeout > 0:
                idle_deadline = time.monotonic() + idle_timeout
            if re.fullmatch(r"[0-9A-Fa-f]{8}", text):
                return int(text, 16)


def parse_int(text):
    return int(text, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="ARMPRG monitor port, for example COM41")
    parser.add_argument(
        "action",
        choices=("info", "crc", "verify", "call", "boot", "linux", "attach"),
        nargs="?",
        default="info",
    )
    parser.add_argument("values", nargs="*")
    parser.add_argument(
        "--log",
        default="stage0_boot.log",
        help="boot-log output path (default: stage0_boot.log)",
    )
    parser.add_argument(
        "--skip-banner",
        action="store_true",
        help="skip the mutable banner buffer after it was verified once",
    )
    parser.add_argument(
        "--idle-timeout",
        type=float,
        default=20.0,
        help="seconds without a target frame before linux mode stops",
    )
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=0.0,
        help=(
            "maximum linux log-capture time in seconds; "
            "zero keeps capturing until idle"
        ),
    )
    parser.add_argument(
        "--chunk-size",
        type=parse_int,
        default=0x8000,
        help="target CRC chunk size for verify (default: 0x8000)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="forward raw terminal input to the RAM-only Linux TTY",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="send one command after the Linux prompt (repeatable)",
    )
    args = parser.parse_args()

    with open_port(args.port) as port:
        if args.action == "info":
            with Path(args.log).open("w", encoding="utf-8", newline="\n") as log:
                boot_log(port, log, include_banner=not args.skip_banner)
            return 0
        if args.action == "crc":
            if len(args.values) != 2:
                raise SystemExit("crc requires ADDRESS LENGTH")
            value = crc_query(port, *map(parse_int, args.values))
            print(f"CRC32: 0x{value:08X}")
            return 0
        if args.action == "verify":
            if len(args.values) != 2:
                raise SystemExit("verify requires ADDRESS FILE")
            verify_file(
                port,
                parse_int(args.values[0]),
                Path(args.values[1]),
                args.chunk_size,
            )
            return 0
        if args.action == "attach":
            if args.values:
                raise SystemExit("attach does not take PC/register values")
            with Path(args.log).open("w", encoding="utf-8", newline="\n") as log:
                def emit_attached(text):
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    log.write(text)
                    log.flush()

                follow_linux(
                    port,
                    0,
                    0,
                    0,
                    0,
                    on_message=emit_attached,
                    idle_timeout=args.idle_timeout,
                    max_runtime=args.max_runtime,
                    interactive=True,
                    initial_commands=args.command,
                    issue_boot_request=False,
                )
            return 0
        if len(args.values) not in (1, 4):
            raise SystemExit(f"{args.action} requires PC [R0 R1 R2]")
        values = list(map(parse_int, args.values))
        while len(values) < 4:
            values.append(0)
        if args.action in ("boot", "linux"):
            with Path(args.log).open("w", encoding="utf-8", newline="\n") as log:
                def emit_stage2(text):
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    log.write(text)
                    log.flush()

                if args.action == "linux":
                    result = follow_linux(
                        port,
                        *values,
                        on_message=emit_stage2,
                        idle_timeout=args.idle_timeout,
                        max_runtime=args.max_runtime,
                        interactive=args.interactive,
                        initial_commands=args.command,
                    )
                    if result is not None:
                        emit_stage2(f"UNEXPECTED RETURN R0: 0x{result:08X}")
                else:
                    result = call_stage2(
                        port,
                        *values,
                        on_message=emit_stage2,
                    )
                    emit_stage2(f"RETURN R0: 0x{result:08X}")
            return 0
        result = call_stage2(port, *values)
        print(f"RETURN R0: 0x{result:08X}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
