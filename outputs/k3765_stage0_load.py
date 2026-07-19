#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Load the RAM-only K3765-Z stage-0 monitor and one second-stage image."""

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
LOAD_BASE = 0x00800000
STAGE2_BASE = 0x01000000
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


def describe(path, data):
    return (
        f"{path}\n"
        f"  size   : {len(data):,}\n"
        f"  SHA-256: {hashlib.sha256(data).hexdigest()}\n"
        f"  CRC32  : {binascii.crc32(data) & 0xFFFFFFFF:08X}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="RAM-only monitor/second-stage loader; no NAND commands."
    )
    parser.add_argument("port", help="fresh PBL downloader port")
    parser.add_argument("monitor", type=Path)
    parser.add_argument("stage2", type=Path)
    parser.add_argument(
        "--log", type=Path, default=Path("stage0_load.log")
    )
    args = parser.parse_args()

    monitor = args.monitor.read_bytes()
    stage2 = args.stage2.read_bytes()
    if len(monitor) != 105_928:
        raise SystemExit(
            f"monitor must remain stock-sized (105,928); got {len(monitor):,}"
        )
    if STAGE2_BASE + len(stage2) > SAFE_RAM_END:
        raise SystemExit("second stage exceeds the bounded SDRAM window")

    transcript = [
        "K3765-Z RAM stage-0 load transcript",
        f"Host time: {datetime.now().isoformat(timespec='seconds')}",
        "No NAND erase/program/write operation is implemented.",
        "",
        describe(args.monitor, monitor),
        f"  address: 0x{LOAD_BASE:08X}",
        "",
        describe(args.stage2, stage2),
        f"  address: 0x{STAGE2_BASE:08X}",
        "",
    ]
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
        upload(port, LOAD_BASE, monitor, "stage-0")
        upload(port, STAGE2_BASE, stage2, "stage-2")
        print(f"Executing stage-0 at 0x{LOAD_BASE:08X}...")
        response = execute(port, LOAD_BASE)
        print(
            f"GO response: {response.hex(' ')}"
            if response
            else "USB reset/no GO response"
        )

    with args.log.open("a", encoding="utf-8") as log:
        log.write("PBL acknowledged every RAM chunk.\n")
        log.write("Stage-0 execute command sent.\n")
        log.write("No persistent-storage command was sent.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
