# SPDX-License-Identifier: GPL-3.0-only

"""Build the RAM-only K3765-Z BL1 0.3 Linux handoff stage."""

from pathlib import Path
import binascii
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BL1_BASE = 0x01000000
BL1_STACK_TOP = 0x01FFF000
ZIMAGE_ADDR = 0x01200000
ZIMAGE_MAX = 0x00D00000
DTB_ADDR = 0x01F80000
DTB_MAX = 0x00010000
PRINT_STRING = 0x00816CF4
PMIC_LED_SET = 0x00042B78
LINUX_MARKER = 0x4C4E5831  # "LNX1"

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1700
HEX_BUFFER_OFFSET = 0x1720

OUT = Path("outputs")
OUTPUT = OUT / "k3765_bl1_linux_boot.bin"
DISASSEMBLY = OUT / "k3765_bl1_linux_boot.disasm.txt"
MAP = OUT / "k3765_bl1_linux_boot.map.txt"


strings = {
    "banner": "K3765-Z BL1 0.3 Linux boot\r\n",
    "mode": "Mode  : validated non-returning zImage handoff\r\n",
    "persist": "Flash : untouched; RAM execution only\r\n",
    "sizes": "Input images\r\n",
    "zimage_size": "zImage size    : ",
    "dtb_size": "DTB size       : ",
    "marker": "Host marker     : ",
    "headers": "Header validation\r\n",
    "zimage_magic": "zImage magic   : ",
    "zimage_start": "zImage hdr start: ",
    "zimage_end": "zImage hdr end : ",
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
    "jump": "JUMPING TO LINUX; BL1 WILL NOT RETURN\r\n",
    "bad_size": "Validation FAIL: image size/range\r\n",
    "bad_zimage": "Validation FAIL: ARM zImage magic\r\n",
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


asm_source = f"""
entry:
    mov r11, sp
    mov r10, lr
    ldr sp, =0x{BL1_STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11}}
    mov r4, r0
    mov r5, r1
    mov r6, r2
    ldr r7, =0x{ZIMAGE_ADDR:08X}
    ldr r8, =0x{DTB_ADDR:08X}

    {print_literal("banner")}
    {print_literal("mode")}
    {print_literal("persist")}
    {print_literal("sizes")}
    mov r1, r4
    ldr r0, =0x{addresses["zimage_size"]:08X}
    bl print_value
    mov r1, r5
    ldr r0, =0x{addresses["dtb_size"]:08X}
    bl print_value
    mov r1, r6
    ldr r0, =0x{addresses["marker"]:08X}
    bl print_value

    ldr r0, =0x{LINUX_MARKER:08X}
    cmp r6, r0
    bne fail_marker
    cmp r4, #0x30
    blo fail_size
    ldr r0, =0x{ZIMAGE_MAX:08X}
    cmp r4, r0
    bhi fail_size
    cmp r5, #0x28
    blo fail_size
    ldr r0, =0x{DTB_MAX:08X}
    cmp r5, r0
    bhi fail_size

    {print_literal("headers")}
    ldr r9, [r7, #0x24]
    mov r1, r9
    ldr r0, =0x{addresses["zimage_magic"]:08X}
    bl print_value
    ldr r0, =0x016F2818
    cmp r9, r0
    bne fail_zimage
    ldr r1, [r7, #0x28]
    ldr r0, =0x{addresses["zimage_start"]:08X}
    bl print_value
    ldr r1, [r7, #0x2C]
    ldr r0, =0x{addresses["zimage_end"]:08X}
    bl print_value

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

    {print_constant("pc", ZIMAGE_ADDR)}
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
    ldr r0, =0xBAD30003
    b finish
fail_zimage:
    {print_literal("bad_zimage")}
    ldr r0, =0xBAD30001
    b finish
fail_dtb:
    {print_literal("bad_dtb")}
    ldr r0, =0xBAD30002
    b finish
fail_marker:
    {print_literal("bad_marker")}
    ldr r0, =0xBAD30004
    b finish
fail_state:
    {print_literal("bad_state")}
    ldr r0, =0xBAD30005

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

image_size = HEX_BUFFER_OFFSET + len(b"0x00000000\r\n\x00")
image = bytearray(image_size)
image[: len(code)] = code
image[STRINGS_OFFSET : STRINGS_OFFSET + len(string_blob)] = string_blob
image[HEX_TABLE_OFFSET : HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
image[HEX_BUFFER_OFFSET:image_size] = b"0x00000000\r\n\x00"

OUT.mkdir(exist_ok=True)
OUTPUT.write_bytes(image)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(code, BL1_BASE)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

map_lines = [
    f"bl1_base=0x{BL1_BASE:08X}",
    f"bl1_entry=0x{BL1_BASE:08X}",
    f"bl1_stack_top=0x{BL1_STACK_TOP:08X}",
    f"code_size={len(code)}",
    f"image_size={len(image)}",
    f"zimage_addr=0x{ZIMAGE_ADDR:08X}",
    f"zimage_max=0x{ZIMAGE_MAX:08X}",
    f"dtb_addr=0x{DTB_ADDR:08X}",
    f"dtb_max=0x{DTB_MAX:08X}",
    f"linux_marker=0x{LINUX_MARKER:08X}",
    f"print_string=0x{PRINT_STRING:08X}",
    f"pmic_led_set=0x{PMIC_LED_SET:08X}",
    f"hex_table=0x{hex_table_addr:08X}",
    f"hex_buffer=0x{hex_buffer_addr:08X}",
]
map_lines.extend(f"{name}=0x{address:08X}" for name, address in addresses.items())
MAP.write_text("\n".join(map_lines) + "\n", encoding="ascii")

print(f"BL1 0.3 size   : {len(image):,}")
print(f"BL1 0.3 SHA256 : {hashlib.sha256(image).hexdigest()}")
print(f"BL1 0.3 CRC32  : {binascii.crc32(image) & 0xFFFFFFFF:08X}")
print("Handoff marker : 0x4C4E5831 (LNX1)")
