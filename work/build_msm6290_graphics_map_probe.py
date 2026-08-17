# SPDX-License-Identifier: GPL-3.0-only

"""Build a returning RAM-only probe for the inherited ARM926 L1 map.

The payload reads CP15 and page-table RAM only.  It deliberately does not
dereference any candidate peripheral address, change clocks, or access NAND.
"""

from argparse import ArgumentParser
from pathlib import Path
import binascii
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BASE = 0x01000000
STACK_TOP = 0x01FFF000
PRINT_STRING = 0x00816CF4
RETURN_MAGIC = 0x474D5031  # "GMP1"

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1700
HEX_BUFFER_OFFSET = 0x1720

# These aliases are present in the stock AMSS static 1-MiB mapping table.
# Only their L1 descriptors are read; the mapped devices are never touched.
CANDIDATES = (
    ("xref_8000", 0xFAD00000, 0x80000000),
    ("lead_a000", 0xFB400000, 0xA0000000),
    ("lead_a800a", 0xFB500000, 0xA8000000),
    ("lead_a800b", 0xFB600000, 0xA8000000),
    ("lead_b800", 0xFB700000, 0xB8000000),
)


def main():
    parser = ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    strings = {
        "banner": "K3765-Z MSM6290 graphics-map probe\r\n",
        "scope": "Scope : CP15 and L1 page-table RAM reads only\r\n",
        "safety": "MMIO/NAND/clocks: untouched\r\n",
        "ttbr": "TTBR raw                : ",
        "l1base": "L1 table physical base   : ",
        "done": "Descriptor snapshot complete; returning GMP1\r\n",
    }
    for name, virtual, static_physical in CANDIDATES:
        strings[name] = (
            f"  {name:<12} VA 0x{virtual:08X} stock-table PA "
            f"0x{static_physical:08X} descriptor: "
        )

    string_blob = bytearray()
    addresses = {}
    for name, value in strings.items():
        addresses[name] = BASE + STRINGS_OFFSET + len(string_blob)
        string_blob.extend(value.encode("ascii") + b"\x00")
    if len(string_blob) > HEX_TABLE_OFFSET - STRINGS_OFFSET:
        raise SystemExit("probe strings overlap the hexadecimal table")

    hex_table_addr = BASE + HEX_TABLE_OFFSET
    hex_buffer_addr = BASE + HEX_BUFFER_OFFSET

    def print_literal(name):
        return (
            f"ldr r0, =0x{addresses[name]:08X}\n"
            f"    bl 0x{PRINT_STRING:08X}\n"
        )

    reads = []
    for name, virtual, _static_physical in CANDIDATES:
        descriptor_offset = (virtual >> 20) * 4
        reads.append(
            f"ldr r0, =0x{addresses[name]:08X}\n"
            f"    bl 0x{PRINT_STRING:08X}\n"
            f"    ldr r1, =0x{descriptor_offset:08X}\n"
            "    ldr r0, [r5, r1]\n"
            "    bl print_hex_value\n"
        )

    asm_source = f"""
entry:
    mov r12, sp
    ldr sp, =0x{STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    push {{r12}}

    {print_literal("banner")}
    {print_literal("scope")}
    {print_literal("safety")}

    mrc p15, 0, r4, c2, c0, 0
    ldr r6, =0xFFFFC000
    and r5, r4, r6

    ldr r0, =0x{addresses["ttbr"]:08X}
    bl 0x{PRINT_STRING:08X}
    mov r0, r4
    bl print_hex_value

    ldr r0, =0x{addresses["l1base"]:08X}
    bl 0x{PRINT_STRING:08X}
    mov r0, r5
    bl print_hex_value

    {''.join(reads)}
    {print_literal("done")}

    ldr r3, =0x{RETURN_MAGIC:08X}
    pop {{r12}}
    pop {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    mov sp, r12
    mov r0, r3
    bx lr

print_hex_value:
    push {{r4, r5, r6, r7, lr}}
    mov r4, r0
    ldr r5, =0x{hex_buffer_addr + 2:08X}
    ldr r6, =0x{hex_table_addr:08X}
    mov r7, #8
format_hex_loop:
    mov r0, r4, lsr #28
    ldrb r0, [r6, r0]
    strb r0, [r5], #1
    mov r4, r4, lsl #4
    subs r7, r7, #1
    bne format_hex_loop
    ldr r0, =0x{hex_buffer_addr:08X}
    bl 0x{PRINT_STRING:08X}
    pop {{r4, r5, r6, r7, pc}}
"""

    ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
    encoding, _ = ks.asm(asm_source, addr=BASE)
    code = bytes(encoding)
    if len(code) > STRINGS_OFFSET:
        raise SystemExit("probe code overlaps its strings")

    image_size = HEX_BUFFER_OFFSET + len(b"0x00000000\r\n\x00")
    image = bytearray(image_size)
    image[: len(code)] = code
    image[STRINGS_OFFSET : STRINGS_OFFSET + len(string_blob)] = string_blob
    image[HEX_TABLE_OFFSET : HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
    image[HEX_BUFFER_OFFSET:image_size] = b"0x00000000\r\n\x00"

    args.out_dir.mkdir(parents=True, exist_ok=True)
    binary = args.out_dir / "k3765_graphics_map_probe.bin"
    disassembly = args.out_dir / "k3765_graphics_map_probe.disasm.txt"
    memory_map = args.out_dir / "k3765_graphics_map_probe.map.txt"
    binary.write_bytes(image)

    md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
    listing = [
        f"0x{ins.address:08X}: {ins.bytes.hex():8} "
        f"{ins.mnemonic:8} {ins.op_str}"
        for ins in md.disasm(code, BASE)
    ]
    disassembly.write_text("\n".join(listing) + "\n", encoding="ascii")

    sha256 = hashlib.sha256(image).hexdigest()
    crc32 = binascii.crc32(image) & 0xFFFFFFFF
    map_lines = [
        f"base=0x{BASE:08X}",
        f"entry=0x{BASE:08X}",
        f"stack_top=0x{STACK_TOP:08X}",
        f"print_string=0x{PRINT_STRING:08X}",
        f"return_magic=0x{RETURN_MAGIC:08X}",
        "access=cp15-and-page-table-ram-read-only",
        "mmio_access=none",
        "nand_access=none",
        f"code_size={len(code)}",
        f"image_size={len(image)}",
        f"sha256={sha256}",
        f"crc32={crc32:08X}",
    ]
    for name, virtual, static_physical in CANDIDATES:
        map_lines.append(
            f"candidate={name},virtual=0x{virtual:08X},"
            f"stock_table_physical=0x{static_physical:08X}"
        )
    memory_map.write_text("\n".join(map_lines) + "\n", encoding="ascii")

    print(f"entry=0x{BASE:08X}")
    print(f"code_size={len(code)}")
    print(f"image_size={len(image)}")
    print(f"sha256={sha256}")
    print(f"crc32={crc32:08X}")


if __name__ == "__main__":
    main()
