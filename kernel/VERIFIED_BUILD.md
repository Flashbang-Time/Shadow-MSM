# Final verified K3765-Z Linux build

This records the last complete build and physical test performed on the
original ZTE/Vodafone K3765-Z target on 2026-08-10. Development later halted
after accidental PMIC damage to that board.

## Verified artifacts

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `Image-k3765-probe` | 5,536,428 | `AF5F11A0` | `c4fe5d5073e565e1083adc21074719d5a1db02ce04fb979e5c46610ced3915e0` |
| `k3765-z-probe.dtb` | 883 | `C511699F` | `1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e` |
| `k3765_bl1_linux_image.bin` | 5,933 | `E535AB77` | `bfd98420d2ed21609e6c3502bf4f6fe584cbb0d33e75467796b117986cf9a6de` |
| `bash-armel-static` | 2,054,784 | — | `7aeb4245cbdb4b64a229a4290df267afd3df2c4ed375c260f18c2959ca45b306` |
| `neofetch` | 376,936 | — | `2a272bbaa1275f21835fd3258fb8032ccdc98348e6ccb9cf58acacd366340170` |

The Bash executable comes from the pinned Debian ARMEL package
`bash-static_5.2.37-2+b9_armel.deb`, whose SHA-256 is
`68cd0cf4a64349f5b3965141e0f7864cee4eed642e93052d7153d92a94178b0c`.
The Neofetch file is the exact upstream Git blob
`48b96d215e38fb8e3750b68833229057153ca7a6` from commit
`ccd5d9f52609bbdcd5d8fa78c4fdb0f12954125f`.

## Verified memory bounds

- Linux physical base: `0x00200000`
- direct `Image` entry: `0x00208000`
- static runtime end (`_end`): `0x0076DFE8`
- enforced direct-image limit: `0x00780000`
- space remaining to that limit: 73,752 bytes
- minimum guard below the resident monitor: 512 KiB
- resident monitor begins: `0x00800000`
- gap from static runtime end to stage-0: 598,040 bytes
- DTB staging address: `0x01F80000`

The verifier derives `_end` from `System.map`, checks the raw `Image`
boundary, and rejects a build if the complete kernel, BSS, and built-in
userspace cross `0x00780000`.

## Physical target status

The exact image above booted Linux 6.1 on the ARM926EJ-S, registered the
MSM6290 timer and interrupt controller, and exposed an interactive BusyBox
shell through the physically verified `ttySHM0` bridge. The host detached and
reattached without restarting the target.

The polling SDCC0 driver then:

- initialized a SanDisk Ultra Plus 64 GB SDXC card as `SK64G`;
- switched from 400 kHz identification to 4 MHz, 1-bit operation;
- exposed the 59.5 GiB disk and partition `p1`;
- mounted and read its existing exFAT filesystem; and
- created, synced, remounted, checksummed, deleted, and verified removal of
  `SHADOWMS.TXT`.

The test file contained `SHADOW_MSM_SD_RW_TEST_2026_08_10` and produced
checksum `2119301490`. The filesystem was returned to a read-only mounted
state after the test.

GNU Bash 5.2.37 and the exact upstream Neofetch 7.1.0 script both ran on the
target. The fuller evidence record is in
`../outputs/FINAL_HARDWARE_VERIFICATION_20260810.md`.

No NAND erase, program, partition-table, CEFS, or virtual-CD operation was
performed by this build or test.
