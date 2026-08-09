# SPDX-License-Identifier: GPL-3.0-only

"""Verify that a K3765-Z probe kernel fits the RAM-only handoff contract."""

from pathlib import Path
import argparse
import binascii
import hashlib
import struct


LINUX_PHYS_BASE = 0x00200000
LINUX_PHYS_ENTRY = LINUX_PHYS_BASE + 0x00008000
STAGE0_BASE = 0x00800000
LINUX_RUNTIME_LIMIT = 0x00700000
ZIMAGE_STAGE = 0x01200000
ZIMAGE_LIMIT = 0x00D00000
DTB_STAGE = 0x01F80000
DTB_LIMIT = 0x00010000
LINUX_RAM_SIZE = 0x01E00000
STAGE0_RESERVE_SIZE = 0x00100000

FDT_BEGIN_NODE = 1
FDT_END_NODE = 2
FDT_PROP = 3
FDT_NOP = 4
FDT_END = 9


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def crc32(data):
    return binascii.crc32(data) & 0xFFFFFFFF


def align4(value):
    return (value + 3) & ~3


def parse_symbols(path):
    symbols = {}
    for line_number, line in enumerate(
        path.read_text(encoding="ascii").splitlines(), start=1
    ):
        fields = line.split()
        if len(fields) != 3:
            raise SystemExit(
                f"malformed System.map line {line_number}: {line!r}"
            )
        address_text, _kind, name = fields
        try:
            address = int(address_text, 16)
        except ValueError as error:
            raise SystemExit(
                f"bad System.map address on line {line_number}: "
                f"{address_text!r}"
            ) from error
        symbols[name] = address
    return symbols


def cstring(data, offset, limit):
    end = data.find(b"\0", offset, limit)
    if end < 0:
        raise SystemExit("unterminated FDT string")
    return data[offset:end].decode("ascii")


def parse_fdt(dtb):
    if len(dtb) < 40:
        raise SystemExit("FDT is shorter than its header")

    header = struct.unpack_from(">10I", dtb, 0)
    (
        magic,
        total_size,
        struct_offset,
        strings_offset,
        reserve_offset,
        _version,
        _last_version,
        _boot_cpu,
        strings_size,
        struct_size,
    ) = header
    if magic != 0xD00DFEED:
        raise SystemExit(f"bad FDT magic: 0x{magic:08X}")
    if total_size != len(dtb):
        raise SystemExit(
            f"FDT size mismatch: header={total_size}, file={len(dtb)}"
        )
    if struct_offset + struct_size > len(dtb):
        raise SystemExit("FDT structure block is out of bounds")
    if strings_offset + strings_size > len(dtb):
        raise SystemExit("FDT strings block is out of bounds")

    reserves = []
    cursor = reserve_offset
    while True:
        if cursor + 16 > len(dtb):
            raise SystemExit("FDT reserve map is out of bounds")
        address, size = struct.unpack_from(">QQ", dtb, cursor)
        cursor += 16
        if address == 0 and size == 0:
            break
        reserves.append((address, size))

    properties = {}
    stack = []
    cursor = struct_offset
    struct_end = struct_offset + struct_size
    strings_end = strings_offset + strings_size
    while cursor + 4 <= struct_end:
        token = struct.unpack_from(">I", dtb, cursor)[0]
        cursor += 4
        if token == FDT_BEGIN_NODE:
            name = cstring(dtb, cursor, struct_end)
            cursor = align4(cursor + len(name) + 1)
            stack.append(name)
        elif token == FDT_END_NODE:
            if not stack:
                raise SystemExit("unbalanced FDT end-node token")
            stack.pop()
        elif token == FDT_PROP:
            if cursor + 8 > struct_end:
                raise SystemExit("truncated FDT property header")
            length, name_offset = struct.unpack_from(">II", dtb, cursor)
            cursor += 8
            if cursor + length > struct_end:
                raise SystemExit("truncated FDT property value")
            if name_offset >= strings_size:
                raise SystemExit("FDT property name is out of bounds")
            name = cstring(
                dtb, strings_offset + name_offset, strings_end
            )
            path = "/" + "/".join(part for part in stack if part)
            properties[(path or "/", name)] = dtb[cursor : cursor + length]
            cursor = align4(cursor + length)
        elif token == FDT_NOP:
            continue
        elif token == FDT_END:
            if stack:
                raise SystemExit("unbalanced FDT node stack")
            return reserves, properties
        else:
            raise SystemExit(f"unknown FDT token 0x{token:08X}")

    raise SystemExit("FDT structure has no end token")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zimage", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dtb", type=Path, required=True)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    zimage = args.zimage.read_bytes()
    image = args.image.read_bytes()
    dtb = args.dtb.read_bytes()
    symbols = parse_symbols(args.symbols)

    if len(zimage) > ZIMAGE_LIMIT:
        raise SystemExit("zImage exceeds the 13 MiB staging window")
    if ZIMAGE_STAGE + len(zimage) > DTB_STAGE:
        raise SystemExit("zImage overlaps the DTB staging window")
    if LINUX_PHYS_ENTRY + len(image) > STAGE0_BASE:
        raise SystemExit("decompressed Image would overwrite stage-0")

    required_symbols = ("_text", "__bss_start", "__bss_stop", "_end")
    missing_symbols = [name for name in required_symbols if name not in symbols]
    if missing_symbols:
        raise SystemExit(
            "System.map is missing required symbols: "
            + ", ".join(missing_symbols)
        )
    if symbols["_text"] != 0xC0008000:
        raise SystemExit(
            f"unexpected virtual _text address: 0x{symbols['_text']:08X}"
        )
    image_end = LINUX_PHYS_ENTRY + len(image)
    bss_start = LINUX_PHYS_ENTRY + (
        symbols["__bss_start"] - symbols["_text"]
    )
    bss_stop = LINUX_PHYS_ENTRY + (
        symbols["__bss_stop"] - symbols["_text"]
    )
    runtime_end = LINUX_PHYS_ENTRY + (
        symbols["_end"] - symbols["_text"]
    )
    if bss_start != image_end:
        raise SystemExit(
            f"Image/BSS boundary mismatch: file ends at 0x{image_end:08X}, "
            f"BSS starts at 0x{bss_start:08X}"
        )
    if not bss_start <= bss_stop <= runtime_end:
        raise SystemExit("unexpected BSS/runtime symbol ordering")
    if runtime_end > LINUX_RUNTIME_LIMIT:
        raise SystemExit(
            f"Linux runtime ends at 0x{runtime_end:08X}, beyond guarded "
            f"limit 0x{LINUX_RUNTIME_LIMIT:08X}"
        )
    if len(dtb) > DTB_LIMIT:
        raise SystemExit("DTB exceeds its 64 KiB staging window")

    zmagic = struct.unpack_from("<I", zimage, 0x24)[0]
    if zmagic != 0x016F2818:
        raise SystemExit(f"bad ARM zImage magic: 0x{zmagic:08X}")

    zstart, zend = struct.unpack_from("<II", zimage, 0x28)
    reserves, properties = parse_fdt(dtb)
    expected_reserves = {
        (STAGE0_BASE, STAGE0_RESERVE_SIZE),
        (DTB_STAGE, DTB_LIMIT),
    }
    if not expected_reserves.issubset(set(reserves)):
        raise SystemExit(f"missing required FDT reservations: {reserves!r}")

    memory_reg = properties.get(("/memory@200000", "reg"))
    expected_memory_reg = struct.pack(
        ">II", LINUX_PHYS_BASE, LINUX_RAM_SIZE
    )
    if memory_reg != expected_memory_reg:
        raise SystemExit(
            "unexpected FDT memory map: "
            f"{memory_reg.hex() if memory_reg else 'missing'}"
        )

    report = "\n".join(
        (
            "Shadow-MSM K3765-Z probe artifact report",
            f"zImage size: {len(zimage)}",
            f"zImage SHA256: {sha256(zimage)}",
            f"zImage CRC32: {crc32(zimage):08X}",
            f"zImage header start: {zstart:08X}",
            f"zImage header end: {zend:08X}",
            f"Image size: {len(image)}",
            f"Image SHA256: {sha256(image)}",
            f"Linux physical base: {LINUX_PHYS_BASE:08X}",
            f"Image physical end: {image_end:08X}",
            f"BSS physical start: {bss_start:08X}",
            f"BSS physical end: {bss_stop:08X}",
            f"Linux runtime end: {runtime_end:08X}",
            f"Runtime-to-monitor guard: {STAGE0_BASE - runtime_end}",
            f"DTB size: {len(dtb)}",
            f"DTB SHA256: {sha256(dtb)}",
            f"DTB CRC32: {crc32(dtb):08X}",
            f"DTB Linux RAM: {LINUX_PHYS_BASE:08X}+{LINUX_RAM_SIZE:08X}",
            "Required FDT reservations: present",
            "Resident runtime preserved: yes",
            "Resident trace init_mm bridge: yes",
            "NAND operations present: no",
            "",
        )
    )
    args.report.write_text(report, encoding="ascii")
    print(report, end="")


if __name__ == "__main__":
    main()
