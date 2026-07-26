# SPDX-License-Identifier: GPL-3.0-only

"""Build the MSM6290 RAM-only watchdog keepalive hold test."""

from pathlib import Path
import argparse
import binascii
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


LOAD_ADDRESS = 0x00800000
WATCHDOG_RESET = 0x8000540C
DELAY_ITERATIONS = 0x10000


ASM_SOURCE = f"""
    ldr r4, =0x{WATCHDOG_RESET:08X}
    mov r5, #1
    mov r6, #0x{DELAY_ITERATIONS:X}

kick:
    str r5, [r4]
    mov r0, r6

delay:
    subs r0, r0, #1
    bne delay
    b kick
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a RAM-only MSM6290 hold loop using the watchdog reset "
            "write recovered from the stock ARMPRG runtime."
        )
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs"),
    )
    args = parser.parse_args()

    assembler = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
    encoding, _ = assembler.asm(ASM_SOURCE, addr=LOAD_ADDRESS)
    payload = bytes(encoding)

    disassembler = Cs(
        CS_ARCH_ARM,
        CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN,
    )
    instructions = list(disassembler.disasm(payload, LOAD_ADDRESS))
    stores = [
        instruction
        for instruction in instructions
        if instruction.mnemonic.startswith("str")
    ]
    if len(stores) != 1 or stores[0].op_str != "r5, [r4]":
        raise SystemExit("unexpected store in watchdog hold payload")
    if WATCHDOG_RESET.to_bytes(4, "little") not in payload:
        raise SystemExit("watchdog reset literal is missing")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    binary_path = args.out_dir / "k3765_watchdog_hold.bin"
    disassembly_path = (
        args.out_dir / "k3765_watchdog_hold.disasm.txt"
    )
    map_path = args.out_dir / "k3765_watchdog_hold.map.txt"

    binary_path.write_bytes(payload)
    disassembly_path.write_text(
        "\n".join(
            f"0x{instruction.address:08X}: "
            f"{instruction.bytes.hex():8} "
            f"{instruction.mnemonic:8} {instruction.op_str}"
            for instruction in instructions
        )
        + "\n",
        encoding="ascii",
    )
    map_path.write_text(
        "\n".join(
            (
                f"load_address=0x{LOAD_ADDRESS:08X}",
                f"watchdog_reset=0x{WATCHDOG_RESET:08X}",
                f"delay_iterations=0x{DELAY_ITERATIONS:X}",
                f"size={len(payload)}",
                f"crc32=0x{binascii.crc32(payload) & 0xFFFFFFFF:08X}",
                f"sha256={hashlib.sha256(payload).hexdigest()}",
                "nand_operations=none",
            )
        )
        + "\n",
        encoding="ascii",
    )

    print(f"binary={binary_path}")
    print(f"size={len(payload)}")
    print(f"crc32=0x{binascii.crc32(payload) & 0xFFFFFFFF:08X}")
    print(f"sha256={hashlib.sha256(payload).hexdigest()}")
    print(f"watchdog_reset=0x{WATCHDOG_RESET:08X}")
    print("nand_operations=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
