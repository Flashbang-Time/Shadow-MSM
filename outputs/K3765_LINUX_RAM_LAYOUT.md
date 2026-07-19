# K3765-Z Linux RAM layout (dry run)

| Address range | Purpose |
|---|---|
| `0x00100000..0x007FFFFF` | Future decompressed Linux region |
| `0x00800000..0x00819DC7` | RAM-only stage-0/USB monitor |
| `0x01000000..0x0100162C` | BL1 0.2 dry-run image |
| `0x01200000..0x01EFFFFF` | zImage staging window (13 MiB max) |
| `0x01F80000..0x01F8FFFF` | DTB reserved window |
| `0x01FFF000` | BL1 private stack top |
| `0x02000000` | End of 32 MiB RAM |

The test zImage is header-only and cannot be executed. BL1 0.2 validates the
zImage and DTB headers, prints the intended Linux entry registers, and returns
`0x44525931` (`DRY1`) to stage-0 without jumping.
