# SPDX-License-Identifier: GPL-3.0-only

"""Locate display/graphics evidence and candidate MMIO literals in AMSS.

The vendor image is supplied by the user at runtime and is never copied into
the repository.  The report is deliberately static: this utility does not
communicate with a target and cannot write flash or MMIO.
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
import re
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM, ARM_REG_PC


TERMS = re.compile(
    r"(?:^|[^a-z])(?:"
    r"adreno|egl|framebuffer|gfx|gmem|gpu|graphics|imageon|kgsl|lcdc|"
    r"mddi|mdp|open(?:gl|vg)|q3d|stargate|yamato"
    r")(?:[^a-z]|$)",
    re.IGNORECASE,
)


def elf_loads(data):
    if data[:6] != b"\x7fELF\x01\x01":
        raise ValueError("expected an ELF32 little-endian image")
    phoff = struct.unpack_from("<I", data, 0x1C)[0]
    phentsize, phnum = struct.unpack_from("<HH", data, 0x2A)
    result = []
    for index in range(phnum):
        fields = struct.unpack_from(
            "<IIIIIIII", data, phoff + index * phentsize
        )
        p_type, offset, vaddr, paddr, filesz, memsz, flags, align = fields
        if p_type == 1 and filesz:
            result.append(
                {
                    "index": index,
                    "offset": offset,
                    "vaddr": vaddr,
                    "paddr": paddr,
                    "filesz": filesz,
                    "memsz": memsz,
                    "flags": flags,
                    "align": align,
                }
            )
    return result


def file_offset_to_address(loads, offset):
    for load in loads:
        start = load["offset"]
        if start <= offset < start + load["filesz"]:
            return load["vaddr"] + offset - start
    return None


def read_address_word(data, loads, address):
    for load in loads:
        start = load["vaddr"]
        if start <= address and address + 4 <= start + load["filesz"]:
            offset = load["offset"] + address - start
            return struct.unpack_from("<I", data, offset)[0]
    return None


def interesting_strings(data, loads):
    result = []
    for match in re.finditer(rb"[\x20-\x7e]{4,}", data):
        text = match.group().decode("ascii", "replace").rstrip()
        if TERMS.search(text):
            result.append(
                (match.start(), file_offset_to_address(loads, match.start()), text)
            )
    return result


def mmio_literals(data, loads):
    """Return PC-relative ARM literal loads whose values resemble MMIO."""
    result = defaultdict(list)
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    md.skipdata = True
    for load in loads:
        if not (load["flags"] & 1):
            continue
        blob = data[load["offset"] : load["offset"] + load["filesz"]]
        for insn in md.disasm(blob, load["vaddr"]):
            if insn.mnemonic != "ldr" or len(insn.operands) < 2:
                continue
            source = insn.operands[1]
            if source.type != ARM_OP_MEM or source.mem.base != ARM_REG_PC:
                continue
            literal = (insn.address + 8 + source.mem.disp) & 0xFFFFFFFF
            value = read_address_word(data, loads, literal)
            if value is None or not (0x80000000 <= value < 0xFFF00000):
                continue
            if value & 3:
                continue
            result[value].append((insn.address, literal))
    return result


def mapping_runs(data, minimum_entries=8):
    """Find tables of consecutive 1-MiB virtual-to-physical pairs."""
    runs = []
    offset = 0
    while offset <= len(data) - 8:
        virtual, physical = struct.unpack_from("<II", data, offset)
        if not (
            0xF0000000 <= virtual < 0xFFF00000
            and not (virtual & 0xFFFFF)
            and not (physical & 0xFFFFF)
        ):
            offset += 4
            continue
        entries = []
        cursor = offset
        expected = virtual
        while cursor <= len(data) - 8:
            current_virtual, current_physical = struct.unpack_from(
                "<II", data, cursor
            )
            if current_virtual != expected or current_physical & 0xFFFFF:
                break
            entries.append((current_virtual, current_physical))
            expected += 0x00100000
            cursor += 8
        if len(entries) >= minimum_entries:
            runs.append((offset, entries))
            offset = cursor
        else:
            offset += 4
    return runs


def format_report(image, data, loads, strings, mappings, literals=None):
    lines = [
        "MSM6290 static graphics reconnaissance",
        # Reports are intended to be publishable.  Never leak the analyst's
        # local directory layout into a generated artifact.
        f"image={image.name}",
        f"size={len(data)}",
        "execution=none (static analysis only)",
        "",
        "[graphics/display strings]",
    ]
    for offset, address, text in strings:
        mapped = f"0x{address:08X}" if address is not None else "unmapped"
        lines.append(f"file=0x{offset:08X} addr={mapped} {text}")

    for offset, entries in mappings:
        lines.extend(
            (
                "",
                f"[1-MiB mapping table at file offset 0x{offset:08X}]",
            )
        )
        for virtual, physical in entries:
            lines.append(
                f"virtual=0x{virtual:08X} physical=0x{physical:08X}"
            )

    if literals is not None:
        pages = Counter()
        for value, xrefs in literals.items():
            pages[value & 0xFFFF0000] += len(xrefs)
        lines.extend(
            ("", "[candidate high-address literals from ARM disassembly]")
        )
        for page, count in pages.most_common():
            lines.append(f"0x{page:08X} xrefs={count}")
        lines.append(
            "note=executable segments contain mixed code/data; treat these as leads"
        )
    return "\n".join(lines) + "\n"


def main():
    parser = ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--include-high-literals",
        action="store_true",
        help="include noisy high-address ARM literal statistics",
    )
    args = parser.parse_args()

    data = args.image.read_bytes()
    loads = elf_loads(data)
    strings = interesting_strings(data, loads)
    mappings = mapping_runs(data)
    literals = mmio_literals(data, loads) if args.include_high_literals else None
    report = format_report(args.image, data, loads, strings, mappings, literals)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
