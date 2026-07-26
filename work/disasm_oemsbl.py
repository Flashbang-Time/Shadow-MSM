#!/usr/bin/env python3
"""Disassemble a selected OEMSBL address range with PC-literal annotations."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_MODE_ARM,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_OP_MEM, ARM_REG_PC


LINK_BASE = 0x00020000


def read_u32(image: bytes, address: int) -> int | None:
    offset = address - LINK_BASE
    if offset < 0 or offset + 4 > len(image):
        return None
    return struct.unpack_from("<I", image, offset)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=Path("firmware/oemsbl.mbn"),
    )
    parser.add_argument("address", type=lambda value: int(value, 0))
    parser.add_argument("size", type=lambda value: int(value, 0))
    parser.add_argument("--arm", action="store_true", help="decode ARM, not Thumb")
    args = parser.parse_args()

    image = args.image.read_bytes()
    offset = args.address - LINK_BASE
    if offset < 0 or offset >= len(image):
        raise SystemExit(f"address 0x{args.address:08X} is outside the image")

    mode = CS_MODE_LITTLE_ENDIAN | (CS_MODE_ARM if args.arm else CS_MODE_THUMB)
    disassembler = Cs(CS_ARCH_ARM, mode)
    disassembler.detail = True

    code = image[offset : offset + args.size]
    for instruction in disassembler.disasm(code, args.address):
        raw = instruction.bytes.hex(" ")
        annotation = ""
        for operand in instruction.operands:
            if operand.type != ARM_OP_MEM or operand.mem.base != ARM_REG_PC:
                continue
            if args.arm:
                pc = instruction.address + 8
            else:
                pc = (instruction.address + 4) & ~3
            literal_address = (pc + operand.mem.disp) & 0xFFFFFFFF
            value = read_u32(image, literal_address)
            if value is not None:
                annotation = (
                    f" ; [0x{literal_address:08X}] = 0x{value:08X}"
                )
            else:
                annotation = f" ; literal address 0x{literal_address:08X}"
        print(
            f"{instruction.address:08X}: {raw:<20} "
            f"{instruction.mnemonic:<8} {instruction.op_str}{annotation}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
