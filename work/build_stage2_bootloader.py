# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BASE = 0x01000000
STACK_TOP = 0x01FFF000
PRINT_STRING = 0x00816CF4

STRINGS_OFFSET = 0x800
HEX_TABLE_OFFSET = 0xB00
HEX_BUFFER_OFFSET = 0xB20

OUTPUT = Path("outputs/k3765_stage2_bootloader.bin")
DISASSEMBLY = Path("outputs/k3765_stage2_bootloader.disasm.txt")
MAP = Path("outputs/k3765_stage2_bootloader.map.txt")

strings = {
    "banner": "K3765-Z BL1 0.1\r\n",
    "mode": "Mode  : RAM-only diagnostic bootloader\r\n",
    "console": "Log   : ARMPRG USB diagnostic transport\r\n",
    "board": "Board : ZTE/Vodafone K3765-Z\r\n",
    "soc": "SoC   : Qualcomm MSM6290\r\n",
    "cpu": "CPU   : ARM926EJ-S / ARMv5TEJ\r\n",
    "pmic": "PMIC  : PM6658-family (R=MPP1 G=LED0 B=LED1)\r\n",
    "nand": "NAND  : HYNIX_HSACS0PL0MCR, 128 MiB + OOB\r\n",
    "persist": "Flash : untouched; no NAND routine is linked\r\n",
    "midr": "MIDR  : ",
    "ctr": "CTR   : ",
    "cpsr": "CPSR  : ",
    "sctlr": "SCTLR : ",
    "ttbr": "TTBR  : ",
    "dacr": "DACR  : ",
    "sp": "SP    : ",
    "arg0": "ARG0  : ",
    "arg1": "ARG1  : ",
    "arg2": "ARG2  : ",
    "ready": "BL1 READY; returning BOOT magic to stage-0\r\n",
}

string_blob = bytearray()
addresses = {}
for name, text in strings.items():
    addresses[name] = BASE + STRINGS_OFFSET + len(string_blob)
    string_blob.extend(text.encode("ascii") + b"\x00")

if len(string_blob) > HEX_TABLE_OFFSET - STRINGS_OFFSET:
    raise SystemExit("bootloader strings overlap the hex table")

hex_table_addr = BASE + HEX_TABLE_OFFSET
hex_buffer_addr = BASE + HEX_BUFFER_OFFSET

asm_source = f"""
entry:
    mov r11, sp
    mov r10, lr
    ldr sp, =0x{STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11}}
    mov r4, r0
    mov r5, r1
    mov r6, r2

    ldr r0, =0x{addresses["banner"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["mode"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["console"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["board"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["soc"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["cpu"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["pmic"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["nand"]:08X}
    bl 0x{PRINT_STRING:08X}
    ldr r0, =0x{addresses["persist"]:08X}
    bl 0x{PRINT_STRING:08X}

    mrc p15, 0, r1, c0, c0, 0
    ldr r0, =0x{addresses["midr"]:08X}
    bl print_value
    mrc p15, 0, r1, c0, c0, 1
    ldr r0, =0x{addresses["ctr"]:08X}
    bl print_value
    mrs r1, cpsr
    ldr r0, =0x{addresses["cpsr"]:08X}
    bl print_value
    mrc p15, 0, r1, c1, c0, 0
    ldr r0, =0x{addresses["sctlr"]:08X}
    bl print_value
    mrc p15, 0, r1, c2, c0, 0
    ldr r0, =0x{addresses["ttbr"]:08X}
    bl print_value
    mrc p15, 0, r1, c3, c0, 0
    ldr r0, =0x{addresses["dacr"]:08X}
    bl print_value
    mov r1, sp
    ldr r0, =0x{addresses["sp"]:08X}
    bl print_value

    mov r1, r4
    ldr r0, =0x{addresses["arg0"]:08X}
    bl print_value
    mov r1, r5
    ldr r0, =0x{addresses["arg1"]:08X}
    bl print_value
    mov r1, r6
    ldr r0, =0x{addresses["arg2"]:08X}
    bl print_value

    ldr r0, =0x{addresses["ready"]:08X}
    bl 0x{PRINT_STRING:08X}

    pop {{r4, r5, r6, r7, r8, r9, r10, r11}}
    mov sp, r11
    ldr r0, =0x424F4F54
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
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(asm_source, addr=BASE)
code = bytes(encoding)
if len(code) > STRINGS_OFFSET:
    raise SystemExit("bootloader code overlaps its string table")

image_size = HEX_BUFFER_OFFSET + len(b"0x00000000\r\n\x00")
image = bytearray(image_size)
image[: len(code)] = code
image[STRINGS_OFFSET : STRINGS_OFFSET + len(string_blob)] = string_blob
image[HEX_TABLE_OFFSET : HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
image[HEX_BUFFER_OFFSET:image_size] = b"0x00000000\r\n\x00"

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_bytes(image)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(code, BASE)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

map_lines = [
    f"base=0x{BASE:08X}",
    f"entry=0x{BASE:08X}",
    f"stack_top=0x{STACK_TOP:08X}",
    f"code_size={len(code)}",
    f"image_size={len(image)}",
    f"hex_table=0x{hex_table_addr:08X}",
    f"hex_buffer=0x{hex_buffer_addr:08X}",
]
map_lines.extend(f"{name}=0x{address:08X}" for name, address in addresses.items())
MAP.write_text("\n".join(map_lines) + "\n", encoding="ascii")

print(f"entry=0x{BASE:08X}")
print(f"code_size={len(code)}")
print(f"image_size={len(image)}")
print(f"sha256={hashlib.sha256(image).hexdigest()}")
