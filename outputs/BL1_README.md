# K3765-Z BL1 0.1

Verified RAM-only minimal bootloader for the ZTE/Vodafone K3765-Z
(Qualcomm MSM6290).

## Verified execution

- Stage-0 monitor address: `0x00800000`
- BL1 address/entry: `0x01000000`
- BL1 stack top: `0x01FFF000`
- BL1 size: `2,861` bytes
- BL1 SHA-256:
  `135a4af42cefc7a86237e9c7d2fa8f15ff3b0df1fabbf00e362439a52098e135`
- BL1 CRC32: `0xEFF2DC54`
- Verified return value: `0x424F4F54` (`BOOT`)

BL1 emits a boot log over the resident ARMPRG USB diagnostic transport,
identifies the board and major hardware, reads the ARM926EJ-S control
registers at runtime, prints its entry arguments, uses a private stack, and
returns cleanly to stage-0.

## Host sequence

From a fresh legacy downloader session:

```powershell
py -3.9 .\k3765_stage0_load.py COMxx `
  .\armprg_stage0_monitor.bin `
  .\k3765_stage2_bootloader.bin `
  --log .\bl1_load.log

py -3.9 .\k3765_stage0_console.py COMxx `
  crc 0x01000000 2861

py -3.9 .\k3765_stage0_console.py COMxx `
  boot 0x01000000 0xA0A0A0A0 0xB1B1B1B1 0xC2C2C2C2 `
  --log .\bl1_boot.log
```

Expected CRC:

```text
0xEFF2DC54
```

Expected return:

```text
0x424F4F54
```

These tools contain no NAND erase/program/write implementation. BL1 does not
link or call any NAND routine.
