#!/usr/bin/env python3
"""Map SDCC strings and ARM literal references in a 32-bit AMSS ELF.

This is a static, read-only analysis helper.  It does not contain serial,
download-mode, NAND, or target-write functionality.
"""

from __future__ import annotations

import argparse
import re
import struct
from dataclasses import dataclass
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_MODE_ARM,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_OP_MEM, ARM_REG_PC


PT_LOAD = 1
PF_X = 1


@dataclass(frozen=True)
class Segment:
    offset: int
    vaddr: int
    paddr: int
    filesz: int
    memsz: int
    flags: int

    def file_to_virtual(self, file_offset: int) -> int | None:
        if self.offset <= file_offset < self.offset + self.filesz:
            return self.vaddr + file_offset - self.offset
        return None

    def virtual_to_file(self, address: int) -> int | None:
        if self.vaddr <= address < self.vaddr + self.filesz:
            return self.offset + address - self.vaddr
        return None


def parse_segments(data: bytes) -> list[Segment]:
    if data[:4] != b"\x7fELF" or data[4:6] != b"\x01\x01":
        raise ValueError("expected a 32-bit little-endian ELF")
    phoff = struct.unpack_from("<I", data, 0x1C)[0]
    phentsize, phnum = struct.unpack_from("<HH", data, 0x2A)
    if phentsize != 32:
        raise ValueError(f"unexpected program-header size {phentsize}")
    segments = []
    for index in range(phnum):
        values = struct.unpack_from("<8I", data, phoff + index * phentsize)
        kind, offset, vaddr, paddr, filesz, memsz, flags, _align = values
        if kind == PT_LOAD and filesz:
            segments.append(Segment(offset, vaddr, paddr, filesz, memsz, flags))
    return segments


def file_to_virtual(segments: list[Segment], offset: int) -> int | None:
    for segment in segments:
        address = segment.file_to_virtual(offset)
        if address is not None:
            return address
    return None


def virtual_to_file(segments: list[Segment], address: int) -> int | None:
    for segment in segments:
        offset = segment.virtual_to_file(address)
        if offset is not None:
            return offset
    return None


def interesting_strings(data: bytes, segments: list[Segment]):
    pattern = re.compile(rb"[\x20-\x7e]{4,}")
    keywords = (
        "sdcc_",
        "sdcc ",
        "sdcc0",
        "sdcc1",
        "sdcc2",
        "mmchc",
        "mmcplus",
        "card type:",
        "card size:",
        "/mmc1",
    )
    for match in pattern.finditer(data):
        text = match.group().decode("ascii", "replace")
        if any(keyword in text.lower() for keyword in keywords):
            address = file_to_virtual(segments, match.start())
            if address is not None:
                yield match.start(), address, text


def literal_loads(
    data: bytes,
    segments: list[Segment],
    pool_targets: set[int],
):
    by_pool_address: dict[int, list[tuple[int, str]]] = {}
    for segment in segments:
        if not segment.flags & PF_X:
            continue
        start = segment.offset
        end = start + segment.filesz

        # ARM LDR Rt,[pc,+/-imm12].  U is deliberately excluded from the
        # mask so both positive and negative literal offsets are accepted.
        for offset in range(start, end - 3, 4):
            word = struct.unpack_from("<I", data, offset)[0]
            if word & 0x0F7F0000 != 0x051F0000:
                continue
            address = segment.vaddr + offset - start
            displacement = word & 0xFFF
            if not word & 0x00800000:
                displacement = -displacement
            pool_address = (address + 8 + displacement) & 0xFFFFFFFF
            if pool_address in pool_targets:
                by_pool_address.setdefault(pool_address, []).append(
                    (address, "arm")
                )

        # Thumb-1 LDR Rt,[pc,#imm8*4].
        for offset in range(start, end - 1, 2):
            halfword = struct.unpack_from("<H", data, offset)[0]
            if halfword & 0xF800 != 0x4800:
                continue
            address = segment.vaddr + offset - start
            pool_address = (
                ((address + 4) & ~3) + ((halfword & 0xFF) << 2)
            ) & 0xFFFFFFFF
            if pool_address in pool_targets:
                by_pool_address.setdefault(pool_address, []).append(
                    (address, "thumb")
                )
    return by_pool_address


def pointer_values(
    data: bytes,
    segments: list[Segment],
    targets: set[int],
):
    values: dict[int, list[int]] = {}
    for segment in segments:
        start = segment.offset
        end = start + segment.filesz - 3
        for offset in range(start, end, 2):
            address = segment.vaddr + offset - start
            value = struct.unpack_from("<I", data, offset)[0]
            if value in targets:
                values.setdefault(value, []).append(address)
    return values


def disassembly_window(
    data: bytes,
    segments: list[Segment],
    address: int,
    before: int = 48,
    after: int = 80,
    mode_name: str = "arm",
) -> list[str]:
    segment = next(
        (
            item
            for item in segments
            if item.flags & PF_X
            and item.vaddr <= address < item.vaddr + item.filesz
        ),
        None,
    )
    if segment is None:
        return []
    alignment_mask = ~3 if mode_name == "arm" else ~1
    start = max(segment.vaddr, (address - before) & alignment_mask)
    end = min(segment.vaddr + segment.filesz, address + after)
    offset = segment.offset + start - segment.vaddr
    mode = CS_MODE_ARM if mode_name == "arm" else CS_MODE_THUMB
    decoder = Cs(CS_ARCH_ARM, mode | CS_MODE_LITTLE_ENDIAN)
    lines = []
    for instruction in decoder.disasm(data[offset : offset + end - start], start):
        marker = ">" if instruction.address == address else " "
        lines.append(
            f"{marker} 0x{instruction.address:08X}: "
            f"{instruction.mnemonic:<8} {instruction.op_str}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("amss", type=Path)
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument(
        "--constant",
        action="append",
        type=lambda value: int(value, 0),
        default=[],
        help="also locate a 32-bit constant and its PC-relative loads",
    )
    args = parser.parse_args()

    data = args.amss.read_bytes()
    segments = parse_segments(data)
    strings = list(interesting_strings(data, segments))
    string_targets = {
        address + delta
        for _offset, address, _text in strings
        for delta in range(-16, 5)
    }
    values = pointer_values(data, segments, string_targets)
    pool_targets = {
        pool_address
        for pool_addresses in values.values()
        for pool_address in pool_addresses
    }
    constant_pools: dict[int, list[int]] = {}
    for constant in args.constant:
        needle = struct.pack("<I", constant)
        position = 0
        while True:
            position = data.find(needle, position)
            if position < 0:
                break
            address = file_to_virtual(segments, position)
            if address is not None:
                constant_pools.setdefault(constant, []).append(address)
                pool_targets.add(address)
            position += 1
    loads = literal_loads(data, segments, pool_targets)

    print(f"File: {args.amss}")
    print(f"Size: {len(data):,} bytes")
    print("Load segments:")
    for segment in segments:
        print(
            f"  file 0x{segment.offset:08X}  "
            f"VA 0x{segment.vaddr:08X}  PA 0x{segment.paddr:08X}  "
            f"file/mem 0x{segment.filesz:X}/0x{segment.memsz:X}  "
            f"flags 0x{segment.flags:X}"
        )

    print(f"\nInteresting strings: {len(strings)}")
    linked = 0
    for file_offset, string_address, text in strings[: args.limit]:
        target_addresses = set(range(string_address - 16, string_address + 5))
        pool_addresses = [
            address
            for target in target_addresses
            for address in values.get(target, ())
        ]
        references = []
        for pool_address in pool_addresses:
            for instruction_address, mode_name in loads.get(pool_address, ()):
                references.append((instruction_address, pool_address, mode_name))
        print(
            f"\nSTRING file=0x{file_offset:08X} VA=0x{string_address:08X} "
            f"{text!r}"
        )
        if not references:
            print("  direct ARM literal xref: none")
            continue
        linked += 1
        for instruction_address, pool_address, mode_name in references[:8]:
            print(
                f"  xref instruction=0x{instruction_address:08X} "
                f"literal=0x{pool_address:08X} mode={mode_name}"
            )
            for line in disassembly_window(
                data, segments, instruction_address, mode_name=mode_name
            ):
                print("   " + line)

    print(f"\nStrings with direct ARM literal xrefs: {linked}/{min(len(strings), args.limit)}")

    if constant_pools:
        print("\nRequested constants:")
    for constant in args.constant:
        locations = constant_pools.get(constant, [])
        print(f"\nCONSTANT 0x{constant:08X}: {len(locations)} mapped occurrences")
        for pool_address in locations[:32]:
            references = loads.get(pool_address, ())
            print(
                f"  literal=0x{pool_address:08X}; "
                f"PC-relative loads={len(references)}"
            )
            for instruction_address, mode_name in references[:8]:
                print(
                    f"    xref instruction=0x{instruction_address:08X} "
                    f"mode={mode_name}"
                )
                for line in disassembly_window(
                    data,
                    segments,
                    instruction_address,
                    before=32,
                    after=64,
                    mode_name=mode_name,
                ):
                    print("     " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
