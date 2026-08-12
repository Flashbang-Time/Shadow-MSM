# Final K3765-Z hardware verification

This report records the last completed physical tests before development on
the original board was halted by accidental PMIC damage. All tests below ran
on a ZTE/Vodafone K3765-Z with Qualcomm MSM6290 entirely from volatile SDRAM.
No NAND, CEFS, partition-table, or virtual-CD write operation was issued.

## Linux and console

- Linux: `6.1.0-shadow-msm-probe+`
- CPU: ARM926EJ-S revision 5 (`ARMv5TEJ`, MIDR `0x41069265`)
- Machine: `ZTE Vodafone K3765-Z (MSM6290)`
- Console: bidirectional `ttySHM0` through the bounded resident USB bridge
- Reported RAM: 30 MiB physical window, approximately 25 MiB available
- Interactive shell: static BusyBox 1.36.1 `ash`, with detach and reattach
- Device nodes: devtmpfs automatically exposes `/dev/mmcblk0` and partition
  nodes

## microSD

The polling PL180-compatible SDCC0 driver completed physical identification,
block reads, filesystem mounting, a reversible write test, and deletion on a
SanDisk Ultra Plus 64 GB SDXC card:

```text
mmc0: new SDXC card at address aaaa
mmcblk0: mmc0:aaaa SK64G 59.5 GiB
mmcblk0: p1
```

The controller initializes at 400 kHz, then transfers at 4 MHz in one-bit
mode. Partition 1 mounted as exFAT. The target read existing Nikon files and
completed this authorized reversible test:

1. create `SHADOWMS.TXT`;
2. write `SHADOW_MSM_SD_RW_TEST_2026_08_10`;
3. read it back and verify checksum `2119301490`;
4. delete the file;
5. synchronize and remount read-only.

Every data-sector `CMD24` completed successfully during that run. This does
not claim production-grade hotplug, error recovery, multi-block I/O, or higher
clock-rate support.

## Genuine Bash and upstream Neofetch

The final XZ-compressed initramfs embeds Debian's static ARMEL Bash and the
LF-preserved upstream `dylanaraps/neofetch` script without modification:

```text
GNU bash, version 5.2.37(1)-release (arm-unknown-linux-gnueabi)
Neofetch 7.1.0
```

Neofetch provenance:

- repository: `https://github.com/dylanaraps/neofetch`
- commit: `ccd5d9f52609bbdcd5d8fa78c4fdb0f12954125f`
- Git blob: `48b96d215e38fb8e3750b68833229057153ca7a6`
- SHA-256: `2a272bbaa1275f21835fd3258fb8032ccdc98348e6ccb9cf58acacd366340170`
- license: MIT, vendored as `kernel/userspace/NEOFETCH_LICENSE.md`

The complete upstream ASCII and system-information display rendered over
`ttySHM0`. An initial Windows checkout exposed a CRLF shebang failure; the
final physical pass used the exact LF-only Git blob above.

## Final verified RAM layout

| Item | Value |
|---|---:|
| Linux entry | `0x00208000` |
| Raw Image end / BSS start | `0x0074FAAC` |
| Linux static runtime end | `0x0076DFE8` |
| Resident monitor base | `0x00800000` |
| Runtime-to-monitor separation | 598,040 bytes |
| BL1 address | `0x01000000` |
| DTB address | `0x01F80000` |

Verified final artifacts:

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `Image-k3765-probe` | 5,536,428 | `AF5F11A0` | `c4fe5d5073e565e1083adc21074719d5a1db02ce04fb979e5c46610ced3915e0` |
| `k3765_bl1_linux_image.bin` | 5,933 | `E535AB77` | `bfd98420d2ed21609e6c3502bf4f6fe584cbb0d33e75467796b117986cf9a6de` |
| `k3765-z-probe.dtb` | 883 | `C511699F` | `1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e` |
| `bash-static-armel` | 2,054,784 | — | `7aeb4245cbdb4b64a229a4290df267afd3df2c4ed375c260f18c2959ca45b306` |

The build verifier rejects an Image whose complete static runtime crosses the
guarded boundary. The final loader implements bounded SDRAM uploads and
target-side CRC checks; it contains no NAND operation.
