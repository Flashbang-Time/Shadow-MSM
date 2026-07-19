#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Control the RAM-only PMIC LED test callback."""

import sys
import time

import serial


FLAG = 0x7E
ESC = 0x7D
MODES = {"off": 0, "ch0": 1, "ch1": 2, "both": 3}


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


def main():
    if len(sys.argv) != 3 or sys.argv[2].lower() not in MODES:
        raise SystemExit(
            "Usage: py -3.9 k3765_led_control.py COMxx off|ch0|ch1|both"
        )
    name = sys.argv[1].upper()
    if name.startswith("COM") and int(name[3:]) >= 10:
        name = r"\\.\\" + name
    mode_name = sys.argv[2].lower()
    payload = bytes((0x1C, MODES[mode_name]))

    with serial.Serial(name, 115200, timeout=0.05, write_timeout=5) as port:
        port.dtr = True
        port.rts = True
        port.reset_input_buffer()
        packet = frame(payload)
        print("MODE:", mode_name)
        print("TX:", packet.hex(" "))
        port.write(packet)
        port.flush()
        response = read_frame(port)
        if response is None:
            print("RX: timeout")
            return 1
        print("RX:", response.hex(" "))
        print("TEXT:", "".join(chr(x) if 32 <= x < 127 else "." for x in response))
        return 0 if b"LED_OK" in response else 2


if __name__ == "__main__":
    raise SystemExit(main())
