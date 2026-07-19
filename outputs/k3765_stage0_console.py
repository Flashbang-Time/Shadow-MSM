#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Host console for the RAM-only K3765-Z stage-0 monitor."""

import argparse
import binascii
from datetime import datetime
from pathlib import Path
import re
import struct
import time

import serial


FLAG = 0x7E
ESC = 0x7D
SAFE_RAM_START = 0x01000000
SAFE_RAM_END = 0x02000000

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


def extract_text(payload):
    if payload is None:
        raise RuntimeError("target response timeout")
    # ARMPRG's print routine emits a 0x0E log frame followed by ASCII.
    if payload and payload[0] == 0x0E:
        payload = payload[1:]
    return payload.rstrip(b"\x00\r\n").decode("ascii", "replace")


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


def follow_linux(port, address, r0, r1, r2, on_message, idle_timeout):
    request = stage2_request(port, address, r0, r1, r2)
    port.reset_input_buffer()
    port.write(request)
    port.flush()
    idle_deadline = time.monotonic() + idle_timeout
    while time.monotonic() < idle_deadline:
        try:
            payload = read_frame(
                port,
                timeout=min(1.0, idle_deadline - time.monotonic()),
            )
        except (OSError, serial.SerialException) as error:
            on_message(f"Transport disconnected after handoff: {error}")
            return None
        if payload is None:
            continue
        text = extract_text(payload)
        on_message(text)
        idle_deadline = time.monotonic() + idle_timeout
        if re.fullmatch(r"[0-9A-Fa-f]{8}", text):
            return int(text, 16)
    on_message(f"No new target frame for {idle_timeout:g} seconds.")
    return None


def parse_int(text):
    return int(text, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="ARMPRG monitor port, for example COM41")
    parser.add_argument(
        "action",
        choices=("info", "crc", "call", "boot", "linux"),
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
        if len(args.values) not in (1, 4):
            raise SystemExit(f"{args.action} requires PC [R0 R1 R2]")
        values = list(map(parse_int, args.values))
        while len(values) < 4:
            values.append(0)
        if args.action in ("boot", "linux"):
            with Path(args.log).open("w", encoding="utf-8", newline="\n") as log:
                def emit_stage2(text):
                    print(text, end="" if text.endswith("\n") else "\n")
                    log.write(text)
                    if not text.endswith("\n"):
                        log.write("\n")
                    log.flush()

                if args.action == "linux":
                    result = follow_linux(
                        port,
                        *values,
                        on_message=emit_stage2,
                        idle_timeout=args.idle_timeout,
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
