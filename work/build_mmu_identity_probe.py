# SPDX-License-Identifier: GPL-3.0-only

"""Build a returning, RAM-only ARM926 identity-MMU diagnostic payload."""

from pathlib import Path
import binascii
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BASE = 0x01000000
STACK_TOP = 0x01FFE000
L1_TABLE = 0x01100000
PRINT_STRING = 0x00816CF4
PMIC_LED_SET = 0x00042B78
RETURN_MAGIC = 0x4D4D5531  # "MMU1"

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1700
HEX_BUFFER_OFFSET = 0x1720

OUT = Path("outputs")
OUTPUT = OUT / "k3765_mmu_identity_probe.bin"
DISASSEMBLY = OUT / "k3765_mmu_identity_probe.disasm.txt"
MAP = OUT / "k3765_mmu_identity_probe.map.txt"


strings = {
    "banner": "K3765-Z ARM926 identity-MMU probe\r\n",
    "mode": "Mode  : temporary 4 GiB non-cacheable 1:1 section map\r\n",
    "persist": "Flash : untouched; RAM execution only\r\n",
    "table": "L1 table: 0x01100000..0x01103FFF\r\n",
    "original": "Original CPU state\r\n",
    "sctlr": "SCTLR: ",
    "ttbr": "TTBR : ",
    "dacr": "DACR : ",
    "table_ready": "Identity table built; installing TTBR and DACR\r\n",
    "enable": "Enabling MMU now\r\n",
    "enabled": "MMU ENABLED: translated diagnostic call succeeded\r\n",
    "enabled_state": "Translated CPU state\r\n",
    "restoring": "Restoring original MMU control state\r\n",
    "returned": "MMU disabled and original TTBR/DACR restored; returning MMU1\r\n",
}

string_blob = bytearray()
addresses = {}
for name, text in strings.items():
    addresses[name] = BASE + STRINGS_OFFSET + len(string_blob)
    string_blob.extend(text.encode("ascii") + b"\x00")

if len(string_blob) > HEX_TABLE_OFFSET - STRINGS_OFFSET:
    raise SystemExit("probe strings overlap the hexadecimal table")

hex_table_addr = BASE + HEX_TABLE_OFFSET
hex_buffer_addr = BASE + HEX_BUFFER_OFFSET


def print_literal(name):
    return (
        f"ldr r0, =0x{addresses[name]:08X}\n"
        f"    bl 0x{PRINT_STRING:08X}\n"
    )


asm_source = f"""
entry:
    mov r12, sp
    ldr sp, =0x{STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    push {{r12}}

    mrs r4, cpsr
    mrc p15, 0, r5, c1, c0, 0
    mrc p15, 0, r6, c2, c0, 0
    mrc p15, 0, r7, c3, c0, 0

    {print_literal("banner")}
    {print_literal("mode")}
    {print_literal("persist")}
    {print_literal("table")}
    {print_literal("original")}
    mov r1, r5
    ldr r0, =0x{addresses["sctlr"]:08X}
    bl print_value
    mov r1, r6
    ldr r0, =0x{addresses["ttbr"]:08X}
    bl print_value
    mov r1, r7
    ldr r0, =0x{addresses["dacr"]:08X}
    bl print_value

    ldr r8, =0x{L1_TABLE:08X}
    mov r9, #0
    /*
     * Match cpu_arm926_proc_info.io_mmu_flags from the verified vmlinux.
     * Bit 4 is required by this ARMv5 section-descriptor format.
     */
    ldr r10, =0x00000C12
    mov r11, #0x1000
build_l1:
    orr r0, r9, r10
    str r0, [r8], #4
    add r9, r9, #0x00100000
    subs r11, r11, #1
    bne build_l1

    {print_literal("table_ready")}
    mov r0, #0
    mcr p15, 0, r0, c7, c10, 4
    mcr p15, 0, r0, c8, c7, 0
    mov r0, #3
    mcr p15, 0, r0, c3, c0, 0
    ldr r0, =0x{L1_TABLE:08X}
    mcr p15, 0, r0, c2, c0, 0

    {print_literal("enable")}
    orr r8, r5, #1
    bic r8, r8, #6
    mcr p15, 0, r8, c1, c0, 0
    mrc p15, 0, r0, c0, c0, 0
    mov r0, r0

    {print_literal("enabled")}
    mov r0, #0
    mov r1, #15
    bl 0x{PMIC_LED_SET:08X}
    {print_literal("enabled_state")}
    mrc p15, 0, r1, c1, c0, 0
    ldr r0, =0x{addresses["sctlr"]:08X}
    bl print_value
    mrc p15, 0, r1, c2, c0, 0
    ldr r0, =0x{addresses["ttbr"]:08X}
    bl print_value
    mrc p15, 0, r1, c3, c0, 0
    ldr r0, =0x{addresses["dacr"]:08X}
    bl print_value

    {print_literal("restoring")}
    mcr p15, 0, r5, c1, c0, 0
    mrc p15, 0, r0, c0, c0, 0
    mov r0, r0
    mcr p15, 0, r6, c2, c0, 0
    mcr p15, 0, r7, c3, c0, 0
    mov r0, #0
    mcr p15, 0, r0, c8, c7, 0

    {print_literal("returned")}
    ldr r3, =0x{RETURN_MAGIC:08X}
    pop {{r12}}
    pop {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    mov sp, r12
    mov r0, r3
    bx lr

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
format_hex_loop:
    mov r0, r4, lsr #28
    ldrb r0, [r6, r0]
    strb r0, [r5], #1
    mov r4, r4, lsl #4
    subs r7, r7, #1
    bne format_hex_loop
    pop {{r4, r5, r6, r7, pc}}
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(asm_source, addr=BASE)
code = bytes(encoding)
if len(code) > STRINGS_OFFSET:
    raise SystemExit("probe code overlaps its strings")

image_size = HEX_BUFFER_OFFSET + len(b"0x00000000\r\n\x00")
image = bytearray(image_size)
image[:len(code)] = code
image[STRINGS_OFFSET:STRINGS_OFFSET + len(string_blob)] = string_blob
image[HEX_TABLE_OFFSET:HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
image[HEX_BUFFER_OFFSET:image_size] = b"0x00000000\r\n\x00"

OUT.mkdir(exist_ok=True)
OUTPUT.write_bytes(image)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} "
    f"{ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(code, BASE)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

map_lines = [
    f"base=0x{BASE:08X}",
    f"entry=0x{BASE:08X}",
    f"stack_top=0x{STACK_TOP:08X}",
    f"l1_table=0x{L1_TABLE:08X}",
    f"l1_table_end=0x{L1_TABLE + 0x4000:08X}",
    "section_descriptor_flags=0x00000C12",
    f"print_string=0x{PRINT_STRING:08X}",
    f"pmic_led_set=0x{PMIC_LED_SET:08X}",
    f"return_magic=0x{RETURN_MAGIC:08X}",
    f"code_size={len(code)}",
    f"image_size={len(image)}",
    f"sha256={hashlib.sha256(image).hexdigest()}",
    f"crc32={binascii.crc32(image) & 0xFFFFFFFF:08X}",
]
MAP.write_text("\n".join(map_lines) + "\n", encoding="ascii")

print(f"entry=0x{BASE:08X}")
print(f"code_size={len(code)}")
print(f"image_size={len(image)}")
print(f"sha256={hashlib.sha256(image).hexdigest()}")
print(f"crc32={binascii.crc32(image) & 0xFFFFFFFF:08X}")
