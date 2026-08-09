#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Verify, RAM-load, boot, and attach to Shadow-MSM on a K3765-Z."""

import argparse
import binascii
from collections import deque
from contextlib import contextmanager
import ctypes
from datetime import datetime
import hashlib
import os
from pathlib import Path
import queue
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
import traceback


sys.dont_write_bytecode = True


KIT_ROOT = Path(__file__).resolve().parent
VENDOR_ROOT = KIT_ROOT / "vendor"
if VENDOR_ROOT.is_dir():
    sys.path.insert(0, str(VENDOR_ROOT))

try:
    import serial
    from serial.tools import list_ports
except ImportError as error:
    raise SystemExit(
        "pyserial is unavailable. Use the complete ISO kit, which includes "
        "vendor/serial, or install pyserial 3.5."
    ) from error


TARGET_VID = 0x19D2
NORMAL_PID = 0x2002
DOWNLOAD_PID = 0x0016
FLAG = 0x7E
ESC = 0x7D
MONITOR_BASE = 0x00800000
DIRECT_IMAGE_START = 0x00208000
DIRECT_IMAGE_END = 0x00700000
IMAGE_RUNTIME_END = 0x00680D58
SAFE_RAM_START = 0x01000000
SAFE_RAM_END = 0x02000000
MAX_CHUNK = 0x3F9
INPUT_SUBCOMMAND = 0x0E
INPUT_PACKET_LIMIT = 64
DETACH_INPUT = object()
BL1_ADDRESS = 0x01000000
DTB_ADDRESS = 0x01F80000
LINUX_MARKER = 0x494D4731
DRIVER_ROOT = KIT_ROOT / "driver" / "zteusbdiag-2009"
DRIVER_INF = DRIVER_ROOT / "zteusbdiag.inf"

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

PAYLOADS = {
    "monitor": {
        "name": "armprg_stage0_monitor.bin",
        "size": 105_928,
        "sha256": "588e897f46a3d7dfe4f5f989bcc85ab3b4604b4f7ccacd5d802b53be226f4f52",
    },
    "image": {
        "name": "Image-k3765-probe",
        "size": 4_564_500,
        "sha256": "60a99e09134738428dd0f3693c5bd2fd72bd8926403d9afc6b0851dab38a974f",
    },
    "bl1": {
        "name": "k3765_bl1_linux_image.bin",
        "size": 5_933,
        "sha256": "53bba2751e32ee044ced5522eb9676abdd38f76c2637841fd12274c2da2f64cc",
        "crc32": 0xD26A57AB,
    },
    "dtb": {
        "name": "k3765-z-probe.dtb",
        "size": 883,
        "sha256": "1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e",
        "crc32": 0xC511699F,
    },
}


def crc16_x25(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x8408 if crc & 1 else 0)
    return crc ^ 0xFFFF


def hdlc_frame(payload):
    flag = 0x7E
    escape = 0x7D
    body = payload + crc16_x25(payload).to_bytes(2, "little")
    encoded = bytearray()
    for byte in body:
        if byte in (flag, escape):
            encoded.extend((escape, byte ^ 0x20))
        else:
            encoded.append(byte)
    return bytes((flag,)) + encoded + bytes((flag,))


def normalise_port(name):
    name = name.upper()
    if os.name == "nt" and name.startswith("COM"):
        suffix = name[3:]
        if suffix.isdigit() and int(suffix) >= 10:
            return "\\\\.\\" + name
    return name


def port_matches(port, pid):
    if port.vid == TARGET_VID and port.pid == pid:
        return True
    text = f"{port.hwid} {port.description}".upper()
    return "VID_19D2" in text and f"PID_{pid:04X}" in text


def normal_ports():
    return [
        port for port in list_ports.comports()
        if port_matches(port, NORMAL_PID)
    ]


def downloader_ports():
    return [
        port for port in list_ports.comports()
        if port_matches(port, DOWNLOAD_PID)
    ]


def describe_ports(ports):
    if not ports:
        return "  (none)"
    return "\n".join(
        f"  {port.device}: {port.description} [{port.hwid}]" for port in ports
    )


def select_normal_diag(override=None):
    if override:
        return override.upper()
    ports = normal_ports()
    candidates = []
    for port in ports:
        description = port.description.lower()
        location = str(getattr(port, "location", "") or "").lower()
        if (
            ("diagnostics" in description or "diag" in description)
            and "hs-usb" not in description
        ) or location.endswith(".0"):
            candidates.append(port)
    if len(candidates) == 1:
        return candidates[0].device
    raise RuntimeError(
        "Could not uniquely identify the normal ZTE diagnostic port.\n"
        f"Visible normal-mode VID_19D2&PID_2002 ports:\n"
        f"{describe_ports(ports)}\n"
        "Pass --diag-port COMxx if necessary."
    )


def select_downloader(override=None):
    if override:
        return override.upper()
    ports = downloader_ports()
    if len(ports) == 1:
        return ports[0].device
    hs_ports = [
        port for port in ports if "hs-usb" in port.description.lower()
    ]
    if len(hs_ports) == 1:
        return hs_ports[0].device
    return None


def select_obvious_downloader(override=None):
    """Return a port only when it is explicitly selected or clearly raw."""
    if override:
        return override.upper()
    ports = downloader_ports()
    hs_ports = [
        port for port in ports if "hs-usb" in port.description.lower()
    ]
    if len(hs_ports) == 1:
        return hs_ports[0].device
    return None


def default_log_dir():
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "Shadow-MSM" / "logs"
    return Path.home() / ".shadow-msm" / "logs"


def runtime_root():
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "Shadow-MSM" / "runtime"
    return Path.home() / ".shadow-msm" / "runtime"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(root):
    manifest = root / "SHA256SUMS"
    if not manifest.is_file():
        raise RuntimeError(f"missing distribution manifest: {manifest}")
    entries = []
    for line_number, raw_line in enumerate(
        manifest.read_text(encoding="ascii").splitlines(), 1
    ):
        if not raw_line:
            continue
        parts = raw_line.split("  ", 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise RuntimeError(
                f"malformed SHA256SUMS line {line_number}: {raw_line!r}"
            )
        relative = Path(parts[1])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(
                f"unsafe SHA256SUMS path on line {line_number}: {relative}"
            )
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"missing distribution file: {relative}")
        actual = sha256_file(path)
        if actual != parts[0]:
            raise RuntimeError(
                f"distribution checksum mismatch: {relative}\n"
                f"  expected {parts[0]}\n"
                f"  actual   {actual}"
            )
        entries.append(relative)
    if not entries:
        raise RuntimeError("SHA256SUMS contains no files")
    digest = sha256_file(manifest)
    print(
        f"Distribution manifest: PASS ({len(entries)} files, "
        f"SHA-256 {digest})"
    )
    return manifest, entries, digest


def stage_and_relaunch(manifest, entries, digest):
    session_name = (
        f"{digest[:16]}-{datetime.now().strftime('%Y%m%d_%H%M%S')}-"
        f"{os.getpid()}"
    )
    destination = runtime_root() / session_name
    destination.mkdir(parents=True, exist_ok=True)
    print(
        "Staging the verified kit locally before the modem's virtual CD "
        "disconnects"
    )
    print(f"  Runtime directory: {destination}")
    for relative in entries:
        source = KIT_ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    shutil.copyfile(manifest, destination / manifest.name)
    verify_manifest(destination)

    command = [
        sys.executable,
        str(destination / "SHADOW_MSM_BOOT.py"),
        *sys.argv[1:],
        "--staged",
        "--cleanup-runtime",
    ]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    print()
    print(f"> {command_text(command)}")
    if os.name == "nt":
        process = subprocess.Popen(
            command,
            cwd=destination,
            env=environment,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print(f"Local Shadow-MSM console started (PID {process.pid}).")
        print("This virtual-CD launcher can now close safely.")
        return 0
    return subprocess.call(command, cwd=destination, env=environment)


def open_runtime_directory():
    if os.name != "nt":
        return
    try:
        os.startfile(str(KIT_ROOT))
        print(f"Opened staged runtime directory: {KIT_ROOT}")
    except OSError as error:
        print(f"Warning: could not open staged runtime directory: {error}")


def cleanup_runtime_directory():
    root = runtime_root().resolve()
    target = KIT_ROOT.resolve()
    if target.parent != root:
        print(f"Refusing to clean non-session directory: {target}")
        return
    try:
        os.chdir(root.parent)
        shutil.rmtree(target)
        print(f"Removed staged session directory: {target}")
    except OSError as error:
        print(f"Warning: could not completely remove {target}: {error}")


def verify_payloads():
    print("Verifying the exact RAM-only payload set before device access")
    paths = {}
    for label, expected in PAYLOADS.items():
        path = KIT_ROOT / expected["name"]
        if not path.is_file():
            raise RuntimeError(f"missing payload: {path}")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != expected["size"]:
            raise RuntimeError(
                f"{path.name}: size {len(data):,} != {expected['size']:,}"
            )
        if digest != expected["sha256"]:
            raise RuntimeError(
                f"{path.name}: SHA-256 {digest} != {expected['sha256']}"
            )
        crc = binascii.crc32(data) & 0xFFFFFFFF
        print(
            f"  PASS {path.name}: {len(data):,} bytes, "
            f"SHA-256 {digest}, CRC32 0x{crc:08X}"
        )
        paths[label] = path
    image_file_end = DIRECT_IMAGE_START + PAYLOADS["image"]["size"]
    if not image_file_end <= IMAGE_RUNTIME_END <= DIRECT_IMAGE_END:
        raise RuntimeError(
            "verified Linux Image/runtime metadata exceeds the bounded "
            "direct-image window"
        )
    print(
        f"  PASS Linux runtime end 0x{IMAGE_RUNTIME_END:08X}; "
        f"{MONITOR_BASE - IMAGE_RUNTIME_END:,} bytes below monitor"
    )
    return paths


def command_text(command):
    return subprocess.list2cmdline([str(part) for part in command])


def switch_to_downloader(diag_port, log_path):
    packet = hdlc_frame(b"\x3A")
    lines = [
        "Shadow-MSM diagnostic download-mode switch",
        f"Host time: {datetime.now().isoformat(timespec='seconds')}",
        f"Port: {diag_port}",
        "Command: DIAG_DLOAD_F (0x3A)",
        f"TX: {packet.hex(' ')}",
        "Persistence: no NAND command",
    ]
    print("\n".join(lines))
    outcome = "No reply before timeout; checking USB re-enumeration."
    port = None
    try:
        port = serial.Serial(
            normalise_port(diag_port),
            115200,
            timeout=2.0,
            write_timeout=5.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        port.dtr = True
        port.rts = True
        port.reset_input_buffer()
        port.reset_output_buffer()
        port.write(packet)
        port.flush()
        reply = port.read(512)
        if reply:
            outcome = f"RX before re-enumeration: {reply.hex(' ')}"
    except (OSError, serial.SerialException) as error:
        outcome = (
            "Diagnostic handle disconnected during re-enumeration "
            f"(expected): {error}"
        )
    finally:
        if port is not None:
            try:
                port.close()
            except (OSError, serial.SerialException):
                pass
    print(outcome)
    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines + [outcome, ""]))


def wait_for_downloader(override, timeout):
    if override:
        return override.upper()
    deadline = time.monotonic() + timeout
    last_notice = 0.0
    while time.monotonic() < deadline:
        port = select_downloader()
        if port:
            print(f"Downloader detected: {port}")
            return port
        now = time.monotonic()
        if now >= last_notice:
            print(
                "Waiting for the raw downloader COM port. If Device Manager "
                "shows a driverless ZTE WCDMA Technologies MSM device, run "
                "INSTALL_ZTE_DRIVER.cmd as Administrator, or choose manually:\n"
                "  Ports (COM & LPT) -> ZTE Corporation -> "
                "ZTE Diagnostics Interface, 09/18/2009"
            )
            last_notice = now + 15.0
        time.sleep(1.0)
    raise TimeoutError(
        f"downloader COM port did not appear within {timeout:g} seconds"
    )


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


def open_stage0_port(name):
    port = serial.Serial(
        normalise_port(name),
        115200,
        timeout=0.05,
        write_timeout=5,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    )
    port.dtr = True
    port.rts = True
    port.reset_input_buffer()
    return port


def pbl_write_ram(port, address, data):
    payload = (
        b"\x0F"
        + address.to_bytes(4, "big")
        + len(data).to_bytes(2, "big")
        + data
    )
    for attempt in range(1, 4):
        port.reset_input_buffer()
        port.write(hdlc_frame(payload))
        port.flush()
        response = read_frame(port, timeout=5.0)
        if response == b"\x02" or (response and response[0] == 0x0F):
            return
        if response:
            raise RuntimeError(
                f"RAM write at 0x{address:08X}: response {response.hex()}"
            )
        print(f"  timeout retry {attempt}/3 at 0x{address:08X}")
    raise TimeoutError(f"RAM write timeout at 0x{address:08X}")


def pbl_upload(port, address, data, label):
    written = 0
    while written < len(data):
        chunk = data[written:written + MAX_CHUNK]
        pbl_write_ram(port, address + written, chunk)
        written += len(chunk)
        print(
            f"\r{label}: {written:,}/{len(data):,} "
            f"({written * 100 / len(data):6.2f}%)",
            end="",
            flush=True,
        )
    print()


def pbl_execute(port, address):
    port.reset_input_buffer()
    port.write(hdlc_frame(b"\x05" + address.to_bytes(4, "big")))
    port.flush()
    try:
        return read_frame(port, timeout=2.0)
    except (OSError, serial.SerialException):
        return None


def range_is_allowed(address, length):
    end = address + length
    return (
        DIRECT_IMAGE_START <= address and end <= DIRECT_IMAGE_END
    ) or (
        SAFE_RAM_START <= address and end <= SAFE_RAM_END
    )


def image_description(address, path, data):
    return (
        f"0x{address:08X}  {path}\n"
        f"  size   : {len(data):,}\n"
        f"  SHA-256: {hashlib.sha256(data).hexdigest()}\n"
        f"  CRC32  : {binascii.crc32(data) & 0xFFFFFFFF:08X}"
    )


def load_ram_bundle(port_name, payloads, log_path):
    bundle = [
        (MONITOR_BASE, payloads["monitor"], payloads["monitor"].read_bytes()),
        (0x00208000, payloads["image"], payloads["image"].read_bytes()),
        (BL1_ADDRESS, payloads["bl1"], payloads["bl1"].read_bytes()),
        (DTB_ADDRESS, payloads["dtb"], payloads["dtb"].read_bytes()),
    ]
    if len(bundle[0][2]) != PAYLOADS["monitor"]["size"]:
        raise RuntimeError("monitor no longer has the verified stock size")
    for address, path, data in bundle[1:]:
        if not range_is_allowed(address, len(data)):
            raise RuntimeError(
                f"{path.name} is outside the bounded SDRAM windows"
            )
    occupied = sorted(
        (address, address + len(data), path.name)
        for address, path, data in bundle
    )
    for (_, previous_end, previous_name), (
        current_start,
        _,
        current_name,
    ) in zip(occupied, occupied[1:]):
        if current_start < previous_end:
            raise RuntimeError(
                f"RAM images overlap: {previous_name} and {current_name}"
            )

    transcript = [
        "K3765-Z bounded RAM bundle load",
        f"Host time: {datetime.now().isoformat(timespec='seconds')}",
        "No NAND erase/program/write operation is implemented.",
        "",
    ]
    transcript.extend(
        image_description(address, path, data) + "\n"
        for address, path, data in bundle
    )
    text = "\n".join(transcript)
    print(text)
    log_path.write_text(text, encoding="utf-8")

    with open_stage0_port(port_name) as port:
        port.reset_output_buffer()
        time.sleep(0.2)
        for address, path, data in bundle:
            pbl_upload(port, address, data, path.name)
        print(f"Executing stage-0 at 0x{MONITOR_BASE:08X}...")
        response = pbl_execute(port, MONITOR_BASE)
        print(
            f"GO response: {response.hex(' ')}"
            if response else "USB reset/no GO response"
        )

    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("PBL acknowledged every bounded RAM chunk.\n")
        handle.write("Stage-0 execute command sent.\n")
        handle.write("No persistent-storage command was sent.\n")


def extract_text(payload, preserve_line_endings=False):
    if payload is None:
        raise RuntimeError("target response timeout")
    if payload and payload[0] == 0x0E:
        payload = payload[1:]
    if preserve_line_endings:
        # ARMPRG's print wrapper appends one transport LF to every frame.
        # Remove exactly that byte while preserving a real preceding CR/LF.
        if payload.endswith(b"\n"):
            payload = payload[:-1]
        payload = payload.rstrip(b"\x00")
    else:
        payload = payload.rstrip(b"\x00\r\n")
    return payload.decode("ascii", "replace")


def stage0_command(port, subcommand, args=b"", expected=None, on_message=None):
    if expected is None:
        expected = "banner" if subcommand == 0 else "hex"
    port.reset_input_buffer()
    port.write(hdlc_frame(bytes((0x1C, subcommand)) + args))
    port.flush()
    deadline = time.monotonic() + 3.0
    ignored = []
    while time.monotonic() < deadline:
        response = read_frame(
            port,
            timeout=min(0.5, deadline - time.monotonic()),
        )
        if response is None:
            continue
        text = extract_text(response)
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
        0x10: "USR", 0x11: "FIQ", 0x12: "IRQ", 0x13: "SVC",
        0x17: "ABT", 0x1B: "UND", 0x1F: "SYS",
    }
    mode = modes.get(value & 0x1F, f"0x{value & 0x1F:02X}")
    return (
        f"mode={mode}, ARM-state={'Thumb' if value & 0x20 else 'ARM'}, "
        f"IRQ={'masked' if value & 0x80 else 'enabled'}, "
        f"FIQ={'masked' if value & 0x40 else 'enabled'}"
    )


def decode_sctlr(value):
    flags = []
    for bit, name in (
        (0, "MMU"), (1, "alignment"), (2, "D-cache"),
        (3, "write-buffer"), (12, "I-cache"), (13, "high-vectors"),
    ):
        flags.append(f"{name}={'on' if value & (1 << bit) else 'off'}")
    return ", ".join(flags)


def write_boot_log(port_name, log_path):
    with open_stage0_port(port_name) as port, log_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as log:
        def emit(line=""):
            print(line)
            log.write(line + "\n")
            log.flush()

        emit("K3765-Z RAM stage-0 boot log")
        emit(f"Host time: {datetime.now().isoformat(timespec='seconds')}")
        emit("Transport: legacy Qualcomm HDLC over USB serial")
        emit("Persistence: RAM only; no NAND operation")
        emit()
        emit(f"Monitor: {stage0_command(port, 0x00)}")
        values = {}
        for label, subcommand in QUERIES:
            value = int(stage0_command(port, subcommand), 16)
            values[label] = value
            emit(f"{label:5}: 0x{value:08X}")
        emit()
        emit(f"CPU   : {decode_midr(values['MIDR'])}")
        emit(f"CPSR  : {decode_cpsr(values['CPSR'])}")
        emit(f"SCTLR : {decode_sctlr(values['SCTLR'])}")
        emit("Board : ZTE/Vodafone K3765-Z")
        emit("SoC   : Qualcomm MSM6290 (MSM6246-family downloader)")
        emit("PMIC  : Qualcomm PM6658-family; RGB map R=MPP1 G=LED0 B=LED1")
        emit("NAND  : HYNIX_HSACS0PL0MCR OEM profile, 128 MiB + OOB")
        emit(
            "RAM   : firmware physical span reaches 0x01FAC000; "
            "stage-0 safe window is 0x01000000..0x01FFFFFF"
        )
        emit("OEMSBL: 00.02.00.04 / KPVDFP673A1M256")


def target_crc_query(port, address, length):
    if not SAFE_RAM_START <= address < SAFE_RAM_END:
        raise ValueError("CRC start is outside the stage-0 safe RAM window")
    if length < 0 or address + length > SAFE_RAM_END:
        raise ValueError("CRC range exceeds the stage-0 safe RAM window")
    return int(
        stage0_command(port, 0x0C, struct.pack("<II", address, length)),
        16,
    )


def crc_check(port_name, address, payload, log_path):
    expected = PAYLOADS[payload]["crc32"]
    length = PAYLOADS[payload]["size"]
    with open_stage0_port(port_name) as port:
        actual = target_crc_query(port, address, length)
    line = f"CRC32 {payload} at 0x{address:08X}: 0x{actual:08X}"
    print(line)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
    if actual != expected:
        raise RuntimeError(
            f"{payload} RAM CRC 0x{actual:08X} != 0x{expected:08X}"
        )
    print(f"PASS: {payload} target RAM CRC is 0x{actual:08X}")


def stage2_request(address, r0, r1, r2):
    if address & 3 or not SAFE_RAM_START <= address < SAFE_RAM_END:
        raise ValueError("stage-2 PC must be aligned inside the safe RAM window")
    args = struct.pack("<IIII", address, r0, r1, r2)
    return hdlc_frame(bytes((0x1C, 0x0D)) + args)


def send_linux_input(port, data):
    if isinstance(data, str):
        data = data.encode("ascii", "replace")
    for offset in range(0, len(data), INPUT_PACKET_LIMIT):
        chunk = data[offset:offset + INPUT_PACKET_LIMIT]
        port.write(hdlc_frame(bytes((0x1C, INPUT_SUBCOMMAND)) + chunk))
        port.flush()


@contextmanager
def raw_console_input():
    """Put an interactive host terminal into per-key mode, then restore it."""
    if not sys.stdin.isatty():
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
        processed_input = 0x0001
        line_input = 0x0002
        echo_input = 0x0004
        raw_mode = input_mode.value & ~(
            processed_input | line_input | echo_input
        )
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
                "H": b"\x1b[A",
                "P": b"\x1b[B",
                "M": b"\x1b[C",
                "K": b"\x1b[D",
                "G": b"\x1b[H",
                "O": b"\x1b[F",
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
    max_runtime,
    initial_commands=(),
    issue_boot_request=True,
):
    port.reset_input_buffer()
    if issue_boot_request:
        port.write(stage2_request(address, r0, r1, r2))
        port.flush()
    pending_lines = deque(
        command.rstrip("\r\n") + "\n" for command in initial_commands
    )
    live_chunks = queue.Queue()
    with raw_console_input() as raw_keys:
        threading.Thread(
            target=stdin_reader,
            args=(live_chunks, raw_keys),
            daemon=True,
        ).start()
        start = time.monotonic()
        absolute_deadline = (
            start + max_runtime if max_runtime > 0 else float("inf")
        )
        terminal_ready = not issue_boot_request
        scripted_ready = not issue_boot_request
        while True:
            if terminal_ready:
                outgoing = None
                scripted = False
                if pending_lines and scripted_ready:
                    outgoing = pending_lines.popleft().encode(
                        "ascii", "replace"
                    )
                    scripted = True
                elif not pending_lines:
                    try:
                        outgoing = live_chunks.get_nowait()
                    except queue.Empty:
                        pass
                if outgoing is DETACH_INPUT:
                    on_message(
                        "\r\nHost detached with Ctrl+]; Linux remains in RAM.\r\n"
                    )
                    return
                if outgoing:
                    send_linux_input(port, outgoing)
                    if scripted or not raw_keys:
                        scripted_ready = False
            now = time.monotonic()
            if now >= absolute_deadline:
                on_message(
                    f"\r\nMaximum runtime of {max_runtime:g} seconds "
                    "reached; target left running.\r\n"
                )
                return
            try:
                payload = read_frame(
                    port,
                    timeout=min(0.1, absolute_deadline - now),
                )
            except (OSError, serial.SerialException) as error:
                on_message(
                    f"\r\nTransport disconnected after handoff: {error}\r\n"
                )
                return
            if payload is None:
                continue
            text = extract_text(payload, preserve_line_endings=True)
            on_message(text)
            if "shadow-msm# " in text:
                terminal_ready = True
                scripted_ready = True


def run_linux_console(
    port_name,
    log_path,
    max_runtime,
    initial_commands=(),
    attach=False,
):
    with open_stage0_port(port_name) as port, log_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as log:
        def emit(text):
            sys.stdout.write(text)
            sys.stdout.flush()
            log.write(text)
            log.flush()

        follow_linux(
            port,
            0 if attach else BL1_ADDRESS,
            0 if attach else PAYLOADS["image"]["size"],
            0 if attach else PAYLOADS["dtb"]["size"],
            0 if attach else LINUX_MARKER,
            on_message=emit,
            max_runtime=max_runtime,
            initial_commands=initial_commands,
            issue_boot_request=not attach,
        )


def install_driver():
    if os.name != "nt":
        raise RuntimeError("the bundled ZTE driver is for Windows only")
    if not DRIVER_INF.is_file():
        raise RuntimeError(f"missing bundled driver INF: {DRIVER_INF}")
    if not ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError(
            "driver installation requires Administrator rights; right-click "
            "INSTALL_ZTE_DRIVER.cmd and choose Run as administrator"
        )
    print("Installing the signed ZTE Diagnostics Interface driver package")
    result = subprocess.run(
        ["pnputil.exe", "/add-driver", str(DRIVER_INF), "/install"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout or "", end="")
    if result.returncode:
        raise RuntimeError(f"PnPUtil exited with status {result.returncode}")
    print("Driver package installation completed.")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Boot the verified Shadow-MSM Linux shell entirely from RAM. "
            "No NAND command is implemented."
        )
    )
    parser.add_argument("--diag-port", help="normal-mode diagnostic COM port")
    parser.add_argument(
        "--downloader-port", help="raw downloader/stage-0 COM port"
    )
    parser.add_argument(
        "--no-switch",
        action="store_true",
        help="device is already in the raw PBL downloader",
    )
    parser.add_argument(
        "--attach",
        action="store_true",
        help="attach to an already-running Shadow-MSM Linux shell",
    )
    parser.add_argument(
        "--driver-wait",
        type=float,
        default=300.0,
        help="seconds to wait for the legacy downloader driver (default: 300)",
    )
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=0.0,
        help="maximum shell runtime; zero runs until Ctrl+C",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="send a command after the prompt (repeatable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify the kit and print the plan without device access",
    )
    parser.add_argument(
        "--install-driver",
        action="store_true",
        help="install the bundled signed 2009 ZTE diagnostic driver",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=default_log_dir(),
        help=(
            "writable session-log directory (default: "
            "LOCALAPPDATA/Shadow-MSM/logs)"
        ),
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--cleanup-runtime",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest, manifest_entries, manifest_digest = verify_manifest(KIT_ROOT)
    payloads = verify_payloads()

    print()
    print("Shadow-MSM safety boundary")
    print("  Target writes: volatile SDRAM only")
    print("  NAND/CEFS/partition operations: not implemented")
    print("  Recovery: power-cycle to return to stock firmware")
    if args.install_driver:
        install_driver()
        return 0
    if args.dry_run:
        print("Dry run complete. No serial port was opened.")
        return 0
    if not args.staged:
        return stage_and_relaunch(
            manifest,
            manifest_entries,
            manifest_digest,
        )

    logs = args.log_dir.expanduser().resolve()
    logs.mkdir(parents=True, exist_ok=True)
    print(f"Session logs: {logs}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.attach:
        port = select_downloader(args.downloader_port)
        if not port:
            raise RuntimeError(
                "No unique Shadow-MSM COM port found; pass "
                "--downloader-port COMxx."
            )
        run_linux_console(
            port,
            logs / f"linux_attach_{stamp}.log",
            args.max_runtime,
            initial_commands=args.command,
            attach=True,
        )
        return 0

    if args.no_switch:
        port = wait_for_downloader(args.downloader_port, args.driver_wait)
    else:
        already_raw = select_obvious_downloader(args.downloader_port)
        if already_raw:
            port = already_raw
            print(f"Using already-present raw downloader: {port}")
        else:
            diag_port = select_normal_diag(args.diag_port)
            switch_to_downloader(
                diag_port,
                logs / f"diag_dload_switch_{stamp}.log",
            )
            open_runtime_directory()
            time.sleep(2.0)
            port = wait_for_downloader(args.downloader_port, args.driver_wait)

    bundle_log = logs / f"ram_bundle_load_{stamp}.log"
    load_ram_bundle(port, payloads, bundle_log)

    time.sleep(1.0)
    write_boot_log(port, logs / f"stage0_info_{stamp}.log")

    crc_log = logs / f"preflight_crc_{stamp}.log"
    with crc_log.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "Shadow-MSM target-side RAM CRC preflight\n"
            f"Host time: {datetime.now().isoformat(timespec='seconds')}\n"
            "No NAND operation\n\n"
        )
    crc_check(
        port,
        BL1_ADDRESS,
        "bl1",
        crc_log,
    )
    crc_check(
        port,
        DTB_ADDRESS,
        "dtb",
        crc_log,
    )

    print()
    print("Preflight complete. Booting Linux and opening shadow-msm#")
    print("Type normally. Ctrl+C signals Linux; Ctrl+] detaches the host.")
    try:
        run_linux_console(
            port,
            logs / f"linux_shell_{stamp}.log",
            args.max_runtime,
            initial_commands=args.command,
        )
    except KeyboardInterrupt:
        print("\nDetached. The RAM-only target may still be running.")
        print("Run ATTACH_SHELL.cmd to reconnect.")
    return 0


def entrypoint():
    status = 1
    try:
        status = main()
    except Exception:
        traceback.print_exc()
        if os.name == "nt" and "--staged" in sys.argv:
            try:
                input("\nShadow-MSM stopped. Press Enter to close and clean up...")
            except (EOFError, KeyboardInterrupt):
                pass
    finally:
        if "--cleanup-runtime" in sys.argv:
            cleanup_runtime_directory()
    return status


if __name__ == "__main__":
    raise SystemExit(entrypoint())
