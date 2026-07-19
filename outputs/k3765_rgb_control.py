#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Control the K3765-Z RAM-only RGB test runtime."""

import argparse
import sys
import time

import serial


FLAG = 0x7E
ESC = 0x7D

GREEN = 0x01
BLUE = 0x02
MPP1 = 0x04
MPP3 = 0x08

MODES = {
    "off": 0,
    "green": GREEN,
    "blue": BLUE,
    "cyan": GREEN | BLUE,
    "mpp1": MPP1,
    "mpp3": MPP3,
    "mpp1-green": MPP1 | GREEN,
    "mpp1-blue": MPP1 | BLUE,
    "mpp1-white": MPP1 | GREEN | BLUE,
    "mpp3-green": MPP3 | GREEN,
    "mpp3-blue": MPP3 | BLUE,
    "mpp3-white": MPP3 | GREEN | BLUE,
}


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
        chunk = port.read(1)
        if not chunk:
            continue
        byte = chunk[0]
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
                raise RuntimeError(f"CRC mismatch: {got:04x} != {want:04x}")
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


def set_mask(port, mask, label, quiet=False):
    packet = frame(bytes((0x1C, mask & 0x0F)))
    port.write(packet)
    port.flush()
    response = read_frame(port)
    if response is None:
        raise RuntimeError(f"{label}: response timeout")
    if b"RGB_OK" not in response:
        text = "".join(chr(x) if 32 <= x < 127 else "." for x in response)
        raise RuntimeError(f"{label}: unexpected response {text!r}")
    if not quiet:
        print(f"{label:8} mask=0x{mask:02X}  OK")


def cycle(port, red_bit, period):
    sequence = (
        ("red", red_bit),
        ("yellow", red_bit | GREEN),
        ("green", GREEN),
        ("cyan", GREEN | BLUE),
        ("blue", BLUE),
        ("magenta", red_bit | BLUE),
    )
    print("Cycling continuously. Press Ctrl+C to stop and switch everything off.")
    while True:
        for label, mask in sequence:
            set_mask(port, mask, label)
            time.sleep(period)


def parse_args():
    parser = argparse.ArgumentParser(
        description="RAM-only K3765-Z LED control; no NAND operations exist here."
    )
    parser.add_argument("port", help="programmer COM port, for example COM40")
    parser.add_argument(
        "mode",
        choices=sorted(MODES) + ["cycle1", "cycle3"],
        help="single color/output state or a continuous RGB cycle",
    )
    parser.add_argument(
        "--period",
        type=float,
        default=0.65,
        help="seconds per color in cycle mode (default: 0.65)",
    )
    parser.add_argument(
        "--log-file",
        help="append status and command acknowledgements to this file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.period < 0.1:
        raise SystemExit("--period must be at least 0.1 seconds")

    log_handle = None
    if args.log_file:
        log_handle = open(args.log_file, "a", buffering=1, encoding="utf-8")
        sys.stdout = log_handle
        sys.stderr = log_handle
        print(f"\ncycle process started at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open_port(args.port) as port:
        try:
            if args.mode == "cycle1":
                cycle(port, MPP1, args.period)
            elif args.mode == "cycle3":
                cycle(port, MPP3, args.period)
            else:
                set_mask(port, MODES[args.mode], args.mode)
        except KeyboardInterrupt:
            print("\nStopping cycle...")
            set_mask(port, 0, "off")
            print("All four tested LED outputs are off.")
    if log_handle:
        log_handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
