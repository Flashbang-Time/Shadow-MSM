# K3765-Z Linux RAM layout

| Address range | Purpose |
|---|---|
| `0x00100000..0x001FFFFF` | Conservatively unused low SDRAM |
| `0x00200000..0x0076DFE7` | Final verified Linux image, BSS, and built-in userspace runtime |
| `0x0076DFE8..0x0077FFFF` | Verified space below the direct-image limit |
| `0x00780000..0x007FFFFF` | 512 KiB guard below the resident monitor |
| `0x00800000..0x00819DC7` | RAM-only stage-0/USB monitor |
| `0x008FF800..0x008FF90B` | RAM-only host-input ring inside the reserved monitor window |
| `0x01000000..0x0100162C` | BL1 0.2 dry-run image |
| `0x01200000..0x01EFFFFF` | zImage staging window (13 MiB max) |
| `0x01F80000..0x01F8FFFF` | DTB reserved window |
| `0x01FFF000` | BL1 private stack top |
| `0x02000000` | End of 32 MiB RAM |

Linux v6.1's ARM DT-assisted `AUTO_ZRELADDR` path requires a 2 MiB-aligned
physical base. The probe DT therefore exposes `0x00200000..0x01FFFFFF` and
leaves the observed first MiB of SDRAM unused. BL1 still enters the compressed
zImage at `0x01200000`; the decompressor places `Image` at `0x00208000`.

The direct-image builder and artifact verifier require the complete static
kernel runtime, including BSS through `_end`, to finish before `0x00780000`.
The final verified `_end` is `0x0076DFE8`, leaving 598,040 bytes before
stage-0 and preserving a minimum 512 KiB guard. The BL1 0.2 dry-run fixture
remains a historical header-parser test and is not an executable kernel.
