# SPDX-License-Identifier: GPL-3.0-only

"""Build a returning, RAM-only MSM6290 timer register read probe."""

from argparse import ArgumentParser
from pathlib import Path
import binascii
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BASE = 0x01000000
STACK_TOP = 0x01FFF000
PRINT_STRING = 0x00816CF4
RETURN_MAGIC = 0x544D5232  # "TMR2"
# OEMSBL's services/time/timer.c routine at 0x00036F4C loads this physical
# base and obtains a stable time tick by reading offset 0x08 twice.
TIMER_BASE = 0x80005400

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1700
HEX_BUFFER_OFFSET = 0x1720

REGISTERS = (
    # Primary timer registers recovered from OEMSBL timer.c.
    ("timer_count", TIMER_BASE + 0x08),
    ("timer_status", TIMER_BASE + 0xC0),
    ("timer_match", TIMER_BASE + 0xC4),
    # Primary IRQ-controller bank 1, where logical IRQ 0x22 maps to bit 2.
    ("irq_active_index", 0x8000049C),
    ("irq_bank1_raw", 0x80000478),
    ("irq_bank1_mask", 0x80000434),
    ("irq_bank1_config", 0x8000045C),
    ("irq_bank1_type", 0x8000042C),
)


def main():
    parser = ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    strings = {
        "banner": "K3765-Z MSM timer/IRQ read probe\r\n",
        "scope": "Mode  : volatile RAM execution; MMIO reads only\r\n",
        "persist": "Flash : untouched; no NAND operation is implemented\r\n",
        "base": "OEMSBL timer base: 0x80005400\r\n",
        "snapshot_a": "Snapshot A\r\n",
        "snapshot_b": "Snapshot B after bounded busy delay\r\n",
        "done": "Timer/IRQ reads completed; returning TMR2\r\n",
    }
    for name, address in REGISTERS:
        strings[name] = f"  {name:<20} 0x{address:08X}: "

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

    def read_register(name, address):
        return (
            f"ldr r0, =0x{addresses[name]:08X}\n"
            f"    bl 0x{PRINT_STRING:08X}\n"
            f"    ldr r0, =0x{address:08X}\n"
            "    ldr r0, [r0]\n"
            "    bl print_hex_value\n"
        )

    reads = "".join(read_register(name, address) for name, address in REGISTERS)

    asm_source = f"""
entry:
    mov r12, sp
    ldr sp, =0x{STACK_TOP:08X}
    push {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    push {{r12}}

    {print_literal("banner")}
    {print_literal("scope")}
    {print_literal("persist")}
    {print_literal("base")}
    {print_literal("snapshot_a")}
    {reads}

    ldr r4, =1000000
delay_loop:
    subs r4, r4, #1
    bne delay_loop

    {print_literal("snapshot_b")}
    {reads}
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
    image[:len(code)] = code
    image[STRINGS_OFFSET:STRINGS_OFFSET + len(string_blob)] = string_blob
    image[HEX_TABLE_OFFSET:HEX_TABLE_OFFSET + 16] = b"0123456789ABCDEF"
    image[HEX_BUFFER_OFFSET:image_size] = b"0x00000000\r\n\x00"

    args.out_dir.mkdir(parents=True, exist_ok=True)
    binary = args.out_dir / "k3765_msm_timer_read_probe.bin"
    disassembly = args.out_dir / "k3765_msm_timer_read_probe.disasm.txt"
    memory_map = args.out_dir / "k3765_msm_timer_read_probe.map.txt"
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
        f"timer_base=0x{TIMER_BASE:08X}",
        f"return_magic=0x{RETURN_MAGIC:08X}",
        "access=read-only",
        f"code_size={len(code)}",
        f"image_size={len(image)}",
        f"sha256={sha256}",
        f"crc32={crc32:08X}",
    ]
    memory_map.write_text("\n".join(map_lines) + "\n", encoding="ascii")

    print(f"entry=0x{BASE:08X}")
    print(f"code_size={len(code)}")
    print(f"image_size={len(image)}")
    print(f"sha256={sha256}")
    print(f"crc32={crc32:08X}")


if __name__ == "__main__":
    main()
