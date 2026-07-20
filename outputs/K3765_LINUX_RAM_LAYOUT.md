# K3765-Z Linux RAM layout

| Address range | Purpose |
|---|---|
| `0x00100000..0x001FFFFF` | Conservatively unused low SDRAM |
| `0x00200000..0x007FFFFF` | Linux RAM; `Image` starts at `0x00208000` |
| `0x00800000..0x00819DC7` | RAM-only stage-0/USB monitor |
| `0x01000000..0x0100162C` | BL1 0.2 dry-run image |
| `0x01200000..0x01EFFFFF` | zImage staging window (13 MiB max) |
| `0x01F80000..0x01F8FFFF` | DTB reserved window |
| `0x01FFF000` | BL1 private stack top |
| `0x02000000` | End of 32 MiB RAM |

Linux v6.1's ARM DT-assisted `AUTO_ZRELADDR` path requires a 2 MiB-aligned
physical base. The probe DT therefore exposes `0x00200000..0x01FFFFFF` and
leaves the observed first MiB of SDRAM unused. BL1 still enters the compressed
zImage at `0x01200000`; the decompressor places `Image` at `0x00208000`.

The BL1 0.2 dry-run fixture remains a historical header-parser test and is not
an executable kernel.
