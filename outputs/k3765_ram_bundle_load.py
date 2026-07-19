#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Load a bounded K3765-Z RAM-only image bundle through the legacy PBL."""

import argparse
import binascii
from datetime import datetime
import hashlib
from pathlib import Path
import sys
import time

import serial


FLAG = 0x7E
ESC = 0x7D
MONITOR_BASE = 0x00800000
SAFE_EXTRA_START = 0x01000000
SAFE_RAM_END = 0x02000000
MAX_CHUNK = 0x3F9


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


def read_frame(port, timeout=5.0):
    deadline = time.monotonic() + timeout
    started = False
    encoded = bytearray()
    while time.monotonic() < deadline:
        item = port.read(1)
        if not item:
            continue
        byte = item[0]
        if byte == FLAG:
            if not started:
                started = True
                continue
            if not encoded:
                continue
            raw = bytearray()
            escaped = False
            for value in encoded:
                if escaped:
                    raw.append(value ^ 0x20)
                    escaped = False
                elif value == ESC:
                    escaped = True
                else:
                    raw.append(value)
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


def normalise_port(name):
    name = name.upper()
    if sys.platform.startswith("win") and name.startswith("COM"):
        if name[3:].isdigit() and int(name[3:]) >= 10:
            return r"\\.\\" + name
    return name


def write_ram(port, address, data):
    payload = (
        b"\x0F"
        + address.to_bytes(4, "big")
        + len(data).to_bytes(2, "big")
        + data
    )
    for attempt in range(1, 4):
        port.reset_input_buffer()
        port.write(frame(payload))
        port.flush()
        response = read_frame(port)
        if response == b"\x02" or (response and response[0] == 0x0F):
            return
        if response:
            raise RuntimeError(
                f"RAM write at 0x{address:08X}: response {response.hex()}"
            )
        print(f"  timeout retry {attempt}/3 at 0x{address:08X}")
    raise TimeoutError(f"RAM write timeout at 0x{address:08X}")


def upload(port, address, data, label):
    written = 0
    while written < len(data):
        chunk = data[written : written + MAX_CHUNK]
        write_ram(port, address + written, chunk)
        written += len(chunk)
        print(
            f"\r{label}: {written:,}/{len(data):,} "
            f"({written * 100 / len(data):6.2f}%)",
            end="",
            flush=True,
        )
    print()


def execute(port, address):
    port.reset_input_buffer()
    port.write(frame(b"\x05" + address.to_bytes(4, "big")))
    port.flush()
    try:
        return read_frame(port, timeout=2.0)
    except (OSError, serial.SerialException):
        return None


def image_description(address, path, data):
    return (
        f"0x{address:08X}  {path}\n"
        f"  size   : {len(data):,}\n"
        f"  SHA-256: {hashlib.sha256(data).hexdigest()}\n"
        f"  CRC32  : {binascii.crc32(data) & 0xFFFFFFFF:08X}"
    )


def parse_image(value):
    try:
        address_text, path_text = value.split(":", 1)
        return int(address_text, 0), Path(path_text)
    except (ValueError, TypeError) as error:
        raise argparse.ArgumentTypeError(
            "image must be ADDRESS:PATH"
        ) from error


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Bounded RAM-only bundle loader. It has no NAND command "
            "implementation."
        )
    )
    parser.add_argument("port", help="fresh PBL downloader port")
    parser.add_argument("monitor", type=Path)
    parser.add_argument(
        "--image",
        action="append",
        type=parse_image,
        required=True,
        help="repeatable ADDRESS:PATH RAM image",
    )
    parser.add_argument("--log", type=Path, default=Path("ram_bundle_load.log"))
    args = parser.parse_args()

    monitor = args.monitor.read_bytes()
    if len(monitor) != 105_928:
        raise SystemExit(
            f"monitor must remain stock-sized (105,928); got {len(monitor):,}"
        )

    bundle = [(MONITOR_BASE, args.monitor, monitor)]
    for address, path in args.image:
        data = path.read_bytes()
        if address < SAFE_EXTRA_START or address + len(data) > SAFE_RAM_END:
            raise SystemExit(
                f"{path} exceeds 0x{SAFE_EXTRA_START:08X}.."
                f"0x{SAFE_RAM_END - 1:08X}"
            )
        bundle.append((address, path, data))

    occupied = sorted(
        (address, address + len(data), path)
        for address, path, data in bundle[1:]
    )
    for (_, previous_end, previous_path), (
        current_start,
        _,
        current_path,
    ) in zip(occupied, occupied[1:]):
        if current_start < previous_end:
            raise SystemExit(
                f"RAM images overlap: {previous_path} and {current_path}"
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
    args.log.write_text("\n".join(transcript), encoding="utf-8")
    print("\n".join(transcript))

    with serial.Serial(
        normalise_port(args.port),
        115200,
        timeout=0.05,
        write_timeout=5,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    ) as port:
        port.dtr = True
        port.rts = True
        port.reset_input_buffer()
        port.reset_output_buffer()
        time.sleep(0.2)
        for address, path, data in bundle:
            upload(port, address, data, path.name)
        print(f"Executing stage-0 at 0x{MONITOR_BASE:08X}...")
        response = execute(port, MONITOR_BASE)
        print(
            f"GO response: {response.hex(' ')}"
            if response
            else "USB reset/no GO response"
        )

    with args.log.open("a", encoding="utf-8") as log:
        log.write("PBL acknowledged every bounded RAM chunk.\n")
        log.write("Stage-0 execute command sent.\n")
        log.write("No persistent-storage command was sent.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
