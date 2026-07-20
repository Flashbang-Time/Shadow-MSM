# SPDX-License-Identifier: GPL-3.0-only

"""Build the RAM-only K3765-Z BL1 0.4 direct Linux Image handoff."""

import argparse
import binascii
import hashlib
from pathlib import Path
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BL1_BASE = 0x01000000
BL1_STACK_TOP = 0x01FFF000
IMAGE_ADDR = 0x00208000
IMAGE_LIMIT = 0x00600000
DTB_ADDR = 0x01F80000
DTB_MAX = 0x00010000
PRINT_STRING = 0x00816CF4
PMIC_LED_SET = 0x00042B78
IMAGE_MARKER = 0x494D4731  # "IMG1"

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1700
HEX_BUFFER_OFFSET = 0x1720

OUT = Path("outputs")
OUTPUT = OUT / "k3765_bl1_linux_image.bin"
DISASSEMBLY = OUT / "k3765_bl1_linux_image.disasm.txt"
MAP = OUT / "k3765_bl1_linux_image.map.txt"


def image_probe_offsets(size):
    offsets = {
        0,
        4,
        8,
        12,
        0x00040000,
        0x00080000,
        0x000C0000,
        0x00100000,
        0x00140000,
        0x00180000,
        0x001C0000,
        0x00200000,
        0x00240000,
        0x00280000,
        0x002C0000,
        0x00300000,
        (size - 4) & ~3,
    }
    return sorted(offset for offset in offsets if offset + 4 <= size)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image",
        type=Path,
        help="verified uncompressed ARM Image used to derive sparse fingerprints",
    )
    args = parser.parse_args()

    linux_image = args.image.read_bytes()
    image_size = len(linux_image)
    if image_size < 0x1000:
        raise SystemExit("Linux Image is implausibly small")
    if IMAGE_ADDR + image_size > IMAGE_LIMIT:
        raise SystemExit(
            f"Linux Image ends at 0x{IMAGE_ADDR + image_size:08X}, "
            f"beyond 0x{IMAGE_LIMIT:08X}"
        )

    probe_offsets = image_probe_offsets(image_size)
    probes = [
        (offset, struct.unpack_from("<I", linux_image, offset)[0])
        for offset in probe_offsets
    ]

    strings = {
        "banner": "K3765-Z BL1 0.4 direct Linux Image boot\r\n",
        "mode": "Mode  : validated non-returning Image handoff\r\n",
        "persist": "Flash : untouched; RAM execution only\r\n",
        "sizes": "Input images\r\n",
        "image_size": "Image size     : ",
        "dtb_size": "DTB size       : ",
        "marker": "Host marker     : ",
        "headers": "Image fingerprints and DTB validation\r\n",
        "fingerprints": "Image sparse fingerprints: PASS\r\n",
        "dtb_magic": "DTB magic      : ",
        "dtb_total": "DTB total size : ",
        "cpu": "Linux entry state\r\n",
        "cpsr": "CPSR            : ",
        "sctlr": "SCTLR           : ",
        "pc": "PC              : ",
        "r0": "r0              : ",
        "r1": "r1              : ",
        "r2": "r2              : ",
        "pass": "Validation PASS\r\n",
        "blue": "LED checkpoint  : blue\r\n",
        "jump": "JUMPING DIRECTLY TO DECOMPRESSED LINUX IMAGE\r\n",
        "bad_size": "Validation FAIL: image size/range\r\n",
        "bad_image": "Validation FAIL: Image fingerprint mismatch\r\n",
        "bad_dtb": "Validation FAIL: flattened device tree header\r\n",
        "bad_marker": "Validation FAIL: host arming marker\r\n",
        "bad_state": "Validation FAIL: MMU or D-cache is enabled\r\n",
    }

    string_blob = bytearray()
    addresses = {}
    for name, text in strings.items():
        addresses[name] = BL1_BASE + STRINGS_OFFSET + len(string_blob)
        string_blob.extend(text.encode("ascii") + b"\x00")
    if len(string_blob) > HEX_TABLE_OFFSET - STRINGS_OFFSET:
        raise SystemExit("strings overlap the hexadecimal table")

    hex_table_addr = BL1_BASE + HEX_TABLE_OFFSET
    hex_buffer_addr = BL1_BASE + HEX_BUFFER_OFFSET

    def print_literal(name):
        return (
            f"ldr r0, =0x{addresses[name]:08X}\n"
            f"    bl 0x{PRINT_STRING:08X}\n"
        )

    def print_constant(name, value):
        return (
            f"ldr r0, =0x{addresses[name]:08X}\n"
            f"    ldr r1, =0x{value:08X}\n"
            "    bl print_value\n"
        )

    probe_asm = []
    for offset, expected in probes:
        probe_asm.extend(
            (
                f"ldr r0, =0x{IMAGE_ADDR + offset:08X}",
                "ldr r0, [r0]",
                f"ldr r1, =0x{expected:08X}",
                "cmp r0, r1",
                "bne fail_image",
            )
        )
    probe_asm_text = "\n    ".join(probe_asm)

    asm_source = f"""
entry:
    mov r11, sp
    mov r10, lr
    ldr sp, =0x{BL1_STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11}}
    mov r4, r0
    mov r5, r1
    mov r6, r2
    ldr r7, =0x{IMAGE_ADDR:08X}
    ldr r8, =0x{DTB_ADDR:08X}

    {print_literal("banner")}
    {print_literal("mode")}
    {print_literal("persist")}
    {print_literal("sizes")}
    mov r1, r4
    ldr r0, =0x{addresses["image_size"]:08X}
    bl print_value
    mov r1, r5
    ldr r0, =0x{addresses["dtb_size"]:08X}
    bl print_value
    mov r1, r6
    ldr r0, =0x{addresses["marker"]:08X}
    bl print_value

    ldr r0, =0x{IMAGE_MARKER:08X}
    cmp r6, r0
    bne fail_marker
    ldr r0, =0x{image_size:08X}
    cmp r4, r0
    bne fail_size
    cmp r5, #0x28
    blo fail_size
    ldr r0, =0x{DTB_MAX:08X}
    cmp r5, r0
    bhi fail_size

    {print_literal("headers")}
    {probe_asm_text}
    {print_literal("fingerprints")}

    ldr r9, [r8]
    mov r1, r9
    ldr r0, =0x{addresses["dtb_magic"]:08X}
    bl print_value
    ldr r0, =0xEDFE0DD0
    cmp r9, r0
    bne fail_dtb
    ldr r0, [r8, #4]
    bl bswap32
    mov r9, r0
    mov r1, r9
    ldr r0, =0x{addresses["dtb_total"]:08X}
    bl print_value
    cmp r9, r5
    bne fail_dtb

    {print_literal("cpu")}
    mrs r9, cpsr
    mov r1, r9
    ldr r0, =0x{addresses["cpsr"]:08X}
    bl print_value
    mrc p15, 0, r9, c1, c0, 0
    mov r1, r9
    ldr r0, =0x{addresses["sctlr"]:08X}
    bl print_value
    tst r9, #0x05
    bne fail_state

    {print_constant("pc", IMAGE_ADDR)}
    {print_constant("r0", 0x00000000)}
    {print_constant("r1", 0xFFFFFFFF)}
    {print_constant("r2", DTB_ADDR)}
    {print_literal("pass")}

    mov r0, #0
    mov r1, #0
    bl 0x{PMIC_LED_SET:08X}
    mov r0, #1
    mov r1, #15
    bl 0x{PMIC_LED_SET:08X}
    {print_literal("blue")}
    {print_literal("jump")}

    mrs r3, cpsr
    orr r3, r3, #0xC0
    msr cpsr_c, r3
    mov r3, #0
    mcr p15, 0, r3, c7, c10, 4
    mcr p15, 0, r3, c7, c5, 0
    mcr p15, 0, r3, c8, c7, 0
    mov r0, #0
    mvn r1, #0
    mov r2, r8
    bx r7

fail_size:
    {print_literal("bad_size")}
    ldr r0, =0xBAD40003
    b finish
fail_image:
    {print_literal("bad_image")}
    ldr r0, =0xBAD40001
    b finish
fail_dtb:
    {print_literal("bad_dtb")}
    ldr r0, =0xBAD40002
    b finish
fail_marker:
    {print_literal("bad_marker")}
    ldr r0, =0xBAD40004
    b finish
fail_state:
    {print_literal("bad_state")}
    ldr r0, =0xBAD40005

finish:
    mov r3, r0
    pop {{r4, r5, r6, r7, r8, r9, r10, r11}}
    mov sp, r11
    mov r0, r3
    bx r10

print_value:
    push {{r4, lr}}
    mov r4, r1
    bl 0x{PRINT_STRING:08X}
    mov r0, r4
    bl format_hex
    ldr r0, =0x{hex_buffer_addr:08X}
    bl 0x{PRINT_STRING:08X}
    pop {{r4, pc}}

format_hex:
    push {{r4, r5, r6, r7, lr}}
    mov r4, r0
    ldr r5, =0x{hex_buffer_addr + 2:08X}
    ldr r6, =0x{hex_table_addr:08X}
    mov r7, #8
hex_loop:
    mov r0, r4, lsr #28
    ldrb r0, [r6, r0]
    strb r0, [r5], #1
    mov r4, r4, lsl #4
    subs r7, r7, #1
    bne hex_loop
    pop {{r4, r5, r6, r7, pc}}

bswap32:
    and r1, r0, #0xFF
    mov r1, r1, lsl #24
    and r2, r0, #0xFF00
    mov r2, r2, lsl #8
    orr r1, r1, r2
    mov r2, r0, lsr #8
    and r2, r2, #0xFF00
    orr r1, r1, r2
    mov r2, r0, lsr #24
    orr r0, r1, r2
    bx lr
"""

    ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
    encoding, _ = ks.asm(asm_source, addr=BL1_BASE)
    code = bytes(encoding)
    if len(code) > STRINGS_OFFSET:
        raise SystemExit("BL1 code overlaps its strings")

    bl1_size = HEX_BUFFER_OFFSET + len(b"0x00000000\r\n\x00")
    bl1 = bytearray(bl1_size)
    bl1[:len(code)] = code
    bl1[STRINGS_OFFSET:STRINGS_OFFSET + len(string_blob)] = string_blob
    bl1[HEX_TABLE_OFFSET:HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
    bl1[HEX_BUFFER_OFFSET:bl1_size] = b"0x00000000\r\n\x00"

    OUT.mkdir(exist_ok=True)
    OUTPUT.write_bytes(bl1)

    md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
    listing = [
        f"0x{ins.address:08X}: {ins.bytes.hex():8} "
        f"{ins.mnemonic:8} {ins.op_str}"
        for ins in md.disasm(code, BL1_BASE)
    ]
    DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

    map_lines = [
        f"bl1_base=0x{BL1_BASE:08X}",
        f"bl1_entry=0x{BL1_BASE:08X}",
        f"bl1_stack_top=0x{BL1_STACK_TOP:08X}",
        f"code_size={len(code)}",
        f"bl1_size={len(bl1)}",
        f"image_addr=0x{IMAGE_ADDR:08X}",
        f"image_size={image_size}",
        f"image_end=0x{IMAGE_ADDR + image_size:08X}",
        f"image_sha256={hashlib.sha256(linux_image).hexdigest()}",
        f"image_crc32={binascii.crc32(linux_image) & 0xFFFFFFFF:08X}",
        f"dtb_addr=0x{DTB_ADDR:08X}",
        f"image_marker=0x{IMAGE_MARKER:08X}",
        f"print_string=0x{PRINT_STRING:08X}",
        f"pmic_led_set=0x{PMIC_LED_SET:08X}",
    ]
    map_lines.extend(
        f"probe_{offset:08X}=0x{expected:08X}"
        for offset, expected in probes
    )
    MAP.write_text("\n".join(map_lines) + "\n", encoding="ascii")

    print(f"BL1 0.4 size   : {len(bl1):,}")
    print(f"BL1 0.4 SHA256 : {hashlib.sha256(bl1).hexdigest()}")
    print(f"BL1 0.4 CRC32  : {binascii.crc32(bl1) & 0xFFFFFFFF:08X}")
    print(f"Image size     : {image_size:,}")
    print(f"Image end      : 0x{IMAGE_ADDR + image_size:08X}")
    print(f"Image probes   : {len(probes)}")
    print("Handoff marker : 0x494D4731 (IMG1)")


if __name__ == "__main__":
    main()
