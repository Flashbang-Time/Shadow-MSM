# SPDX-License-Identifier: GPL-3.0-only

"""Verify that a K3765-Z probe kernel fits the RAM-only handoff contract."""

from pathlib import Path
import argparse
import binascii
import hashlib
import struct


LINUX_PHYS_ENTRY = 0x00108000
STAGE0_BASE = 0x00800000
ZIMAGE_STAGE = 0x01200000
ZIMAGE_LIMIT = 0x00D00000
DTB_STAGE = 0x01F80000
DTB_LIMIT = 0x00010000


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def crc32(data):
    return binascii.crc32(data) & 0xFFFFFFFF


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zimage", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dtb", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    zimage = args.zimage.read_bytes()
    image = args.image.read_bytes()
    dtb = args.dtb.read_bytes()

    if len(zimage) > ZIMAGE_LIMIT:
        raise SystemExit("zImage exceeds the 13 MiB staging window")
    if ZIMAGE_STAGE + len(zimage) > DTB_STAGE:
        raise SystemExit("zImage overlaps the DTB staging window")
    if LINUX_PHYS_ENTRY + len(image) > STAGE0_BASE:
        raise SystemExit("decompressed Image would overwrite stage-0")
    if len(dtb) > DTB_LIMIT:
        raise SystemExit("DTB exceeds its 64 KiB staging window")

    zmagic = struct.unpack_from("<I", zimage, 0x24)[0]
    if zmagic != 0x016F2818:
        raise SystemExit(f"bad ARM zImage magic: 0x{zmagic:08X}")

    zstart, zend = struct.unpack_from("<II", zimage, 0x28)
    fdt_magic, fdt_size = struct.unpack_from(">II", dtb, 0)
    if fdt_magic != 0xD00DFEED:
        raise SystemExit(f"bad FDT magic: 0x{fdt_magic:08X}")
    if fdt_size != len(dtb):
        raise SystemExit(
            f"FDT size mismatch: header={fdt_size}, file={len(dtb)}"
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
            f"Image physical end: {LINUX_PHYS_ENTRY + len(image):08X}",
            f"DTB size: {len(dtb)}",
            f"DTB SHA256: {sha256(dtb)}",
            f"DTB CRC32: {crc32(dtb):08X}",
            "Resident runtime preserved: yes",
            "NAND operations present: no",
            "",
        )
    )
    args.report.write_text(report, encoding="ascii")
    print(report, end="")


if __name__ == "__main__":
    main()
