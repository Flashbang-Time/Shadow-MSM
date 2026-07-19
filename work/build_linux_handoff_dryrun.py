# SPDX-License-Identifier: GPL-3.0-only

"""Build the RAM-only K3765-Z Linux handoff dry run and test fixtures."""

from pathlib import Path
import binascii
import hashlib
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


BL1_BASE = 0x01000000
BL1_STACK_TOP = 0x01FFF000
ZIMAGE_ADDR = 0x01200000
ZIMAGE_MAX = 0x00D00000
DTB_ADDR = 0x01F80000
DTB_MAX = 0x00010000
LINUX_ENTRY = 0x00108000
PRINT_STRING = 0x00816CF4

STRINGS_OFFSET = 0x1000
HEX_TABLE_OFFSET = 0x1600
HEX_BUFFER_OFFSET = 0x1620

OUT = Path("outputs")
BL1_OUTPUT = OUT / "k3765_bl1_linux_dryrun.bin"
DISASSEMBLY = OUT / "k3765_bl1_linux_dryrun.disasm.txt"
MAP = OUT / "k3765_bl1_linux_dryrun.map.txt"
ZIMAGE_FIXTURE = OUT / "k3765_zimage_header_fixture.bin"
DTB_OUTPUT = OUT / "k3765_minimal.dtb"
LAYOUT_OUTPUT = OUT / "K3765_LINUX_RAM_LAYOUT.md"


def align(value, boundary):
    return (value + boundary - 1) & ~(boundary - 1)


def be32(value):
    return struct.pack(">I", value)


def fdt_prop(name_offset, value):
    body = be32(3) + be32(len(value)) + be32(name_offset) + value
    return body.ljust(align(len(body), 4), b"\x00")


def fdt_node(name, body):
    encoded_name = name.encode("ascii") + b"\x00"
    begin = (be32(1) + encoded_name).ljust(
        align(4 + len(encoded_name), 4), b"\x00"
    )
    return begin + body + be32(2)


def build_dtb():
    names = (
        "compatible",
        "model",
        "#address-cells",
        "#size-cells",
        "device_type",
        "reg",
        "bootargs",
    )
    strings = bytearray()
    name_offsets = {}
    for name in names:
        name_offsets[name] = len(strings)
        strings.extend(name.encode("ascii") + b"\x00")

    memory = fdt_node(
        "memory@100000",
        fdt_prop(name_offsets["device_type"], b"memory\x00")
        + fdt_prop(
            name_offsets["reg"],
            be32(0x00100000) + be32(0x01F00000),
        ),
    )
    chosen = fdt_node(
        "chosen",
        fdt_prop(
            name_offsets["bootargs"],
            (
                b"earlycon loglevel=8 ignore_loglevel initcall_debug "
                b"rdinit=/init\x00"
            ),
        ),
    )
    root = fdt_node(
        "",
        fdt_prop(
            name_offsets["compatible"],
            b"zte,k3765-z\x00qcom,msm6290\x00",
        )
        + fdt_prop(
            name_offsets["model"],
            b"ZTE Vodafone K3765-Z (MSM6290)\x00",
        )
        + fdt_prop(name_offsets["#address-cells"], be32(1))
        + fdt_prop(name_offsets["#size-cells"], be32(1))
        + memory
        + chosen,
    )
    structure = root + be32(9)

    header_size = 40
    reserve_map = (
        struct.pack(">QQ", DTB_ADDR, DTB_MAX)
        + struct.pack(">QQ", 0, 0)
    )
    off_mem_rsvmap = header_size
    off_dt_struct = align(off_mem_rsvmap + len(reserve_map), 4)
    off_dt_strings = align(off_dt_struct + len(structure), 4)
    total_size = off_dt_strings + len(strings)
    header = struct.pack(
        ">10I",
        0xD00DFEED,
        total_size,
        off_dt_struct,
        off_dt_strings,
        off_mem_rsvmap,
        17,
        16,
        0,
        len(strings),
        len(structure),
    )
    image = bytearray(total_size)
    image[: len(header)] = header
    image[off_mem_rsvmap : off_mem_rsvmap + len(reserve_map)] = reserve_map
    image[off_dt_struct : off_dt_struct + len(structure)] = structure
    image[off_dt_strings : off_dt_strings + len(strings)] = strings
    return bytes(image)


def build_zimage_fixture():
    image = bytearray(64)
    # Header-only parser fixture. It is deliberately not executable.
    struct.pack_into("<I", image, 0x24, 0x016F2818)
    struct.pack_into("<I", image, 0x28, LINUX_ENTRY)
    struct.pack_into("<I", image, 0x2C, LINUX_ENTRY + len(image))
    image[0x30:0x40] = b"HEADER-ONLY-TEST"
    return bytes(image)


strings = {
    "banner": "K3765-Z BL1 0.2 Linux handoff dry run\r\n",
    "mode": "Mode  : validate only; kernel jump is disabled\r\n",
    "persist": "Flash : untouched; no NAND routine is linked\r\n",
    "layout": "RAM layout\r\n",
    "ram_base": "RAM base       : ",
    "ram_size": "RAM size       : ",
    "linux_entry": "Linux target   : ",
    "monitor": "Stage-0 monitor : ",
    "bl1": "BL1 address     : ",
    "zimage": "zImage staging  : ",
    "zimage_max": "zImage max size : ",
    "dtb": "DTB address     : ",
    "stack": "BL1 stack top   : ",
    "inputs": "Input validation\r\n",
    "zimage_size": "zImage size    : ",
    "zimage_magic": "zImage magic   : ",
    "zimage_start": "zImage hdr start: ",
    "zimage_end": "zImage hdr end : ",
    "dtb_size": "DTB size       : ",
    "dtb_magic": "DTB magic      : ",
    "dtb_total": "DTB total size : ",
    "registers": "Future Linux entry registers\r\n",
    "pc": "PC              : ",
    "r0": "r0              : ",
    "r1": "r1              : ",
    "r2": "r2              : ",
    "cpsr": "Current CPSR    : ",
    "sctlr": "Current SCTLR   : ",
    "pass": "Validation PASS\r\n",
    "no_jump": "DRY RUN COMPLETE; no branch to Linux was performed\r\n",
    "bad_size": "Validation FAIL: image size/range\r\n",
    "bad_zimage": "Validation FAIL: ARM zImage magic\r\n",
    "bad_dtb": "Validation FAIL: flattened device tree header\r\n",
}

string_blob = bytearray()
addresses = {}
for name, text in strings.items():
    addresses[name] = BL1_BASE + STRINGS_OFFSET + len(string_blob)
    string_blob.extend(text.encode("ascii") + b"\x00")

if len(string_blob) > HEX_TABLE_OFFSET - STRINGS_OFFSET:
    raise SystemExit("strings overlap the hex table")

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
    {print_literal("layout")}
    {print_constant("ram_base", 0x00100000)}
    {print_constant("ram_size", 0x01F00000)}
    {print_constant("linux_entry", LINUX_ENTRY)}
    {print_constant("monitor", 0x00800000)}
    {print_constant("bl1", BL1_BASE)}
    {print_constant("zimage", ZIMAGE_ADDR)}
    {print_constant("zimage_max", ZIMAGE_MAX)}
    {print_constant("dtb", DTB_ADDR)}
    {print_constant("stack", BL1_STACK_TOP)}

    {print_literal("inputs")}
    mov r1, r4
    ldr r0, =0x{addresses["zimage_size"]:08X}
    bl print_value
    mov r1, r5
    ldr r0, =0x{addresses["dtb_size"]:08X}
    bl print_value

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

    {print_literal("registers")}
    {print_constant("pc", ZIMAGE_ADDR)}
    {print_constant("r0", 0x00000000)}
    {print_constant("r1", 0xFFFFFFFF)}
    {print_constant("r2", DTB_ADDR)}
    mrs r1, cpsr
    ldr r0, =0x{addresses["cpsr"]:08X}
    bl print_value
    mrc p15, 0, r1, c1, c0, 0
    ldr r0, =0x{addresses["sctlr"]:08X}
    bl print_value
    {print_literal("pass")}
    {print_literal("no_jump")}
    ldr r0, =0x44525931
    b finish

fail_size:
    {print_literal("bad_size")}
    ldr r0, =0xBAD10003
    b finish
fail_zimage:
    {print_literal("bad_zimage")}
    ldr r0, =0xBAD10001
    b finish
fail_dtb:
    {print_literal("bad_dtb")}
    ldr r0, =0xBAD10002

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

zimage = build_zimage_fixture()
dtb = build_dtb()

if struct.unpack_from("<I", zimage, 0x24)[0] != 0x016F2818:
    raise SystemExit("zImage fixture magic is invalid")
dtb_header = struct.unpack_from(">10I", dtb, 0)
if dtb_header[0] != 0xD00DFEED or dtb_header[1] != len(dtb):
    raise SystemExit("DTB header self-check failed")
if len(dtb) > DTB_MAX:
    raise SystemExit("DTB exceeds its reserved window")

OUT.mkdir(exist_ok=True)
BL1_OUTPUT.write_bytes(image)
ZIMAGE_FIXTURE.write_bytes(zimage)
DTB_OUTPUT.write_bytes(dtb)

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
    f"linux_entry=0x{LINUX_ENTRY:08X}",
    f"hex_table=0x{hex_table_addr:08X}",
    f"hex_buffer=0x{hex_buffer_addr:08X}",
]
map_lines.extend(f"{name}=0x{address:08X}" for name, address in addresses.items())
MAP.write_text("\n".join(map_lines) + "\n", encoding="ascii")

layout = f"""# K3765-Z Linux RAM layout (dry run)

| Address range | Purpose |
|---|---|
| `0x00100000..0x007FFFFF` | Future decompressed Linux region |
| `0x00800000..0x00819DC7` | RAM-only stage-0/USB monitor |
| `0x01000000..0x010{len(image) - 1:05X}` | BL1 0.2 dry-run image |
| `0x01200000..0x01EFFFFF` | zImage staging window ({ZIMAGE_MAX // 1048576} MiB max) |
| `0x01F80000..0x01F8FFFF` | DTB reserved window |
| `0x01FFF000` | BL1 private stack top |
| `0x02000000` | End of 32 MiB RAM |

The test zImage is header-only and cannot be executed. BL1 0.2 validates the
zImage and DTB headers, prints the intended Linux entry registers, and returns
`0x44525931` (`DRY1`) to stage-0 without jumping.
"""
LAYOUT_OUTPUT.write_text(layout, encoding="utf-8")

print(f"BL1 size   : {len(image):,}")
print(f"BL1 SHA256 : {hashlib.sha256(image).hexdigest()}")
print(f"BL1 CRC32  : {binascii.crc32(image) & 0xFFFFFFFF:08X}")
print(f"zImage size: {len(zimage):,}")
print(f"zImage CRC : {binascii.crc32(zimage) & 0xFFFFFFFF:08X}")
print(f"DTB size   : {len(dtb):,}")
print(f"DTB CRC    : {binascii.crc32(dtb) & 0xFFFFFFFF:08X}")
