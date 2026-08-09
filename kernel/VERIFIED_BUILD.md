# Verified K3765-Z ttySHM0 Linux build

The current ARM926 Linux, static BusyBox, and `ttySHM0` bundle completed
successfully in
GitHub Actions run
[`31330993698`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/31330993698)
from commit `411b48d`.

The downloaded artifact ZIP matched GitHub's published SHA-256 digest
`55d257e6462a8290199f5ff5c8f52f8ed81846c1420e104f16f359d54dfe8dcb`.
Every entry in the bundle's internal `SHA256SUMS` file also matched.

## Verified artifacts

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `zImage-k3765-probe` | 2,806,696 | `2DF1EA4A` | `920d8e8ef36ad25482ea4b916a8255c2209340da773d6e9bb9522aa6a448c92f` |
| `Image-k3765-probe` | 4,564,500 | `3ECE065C` | `60a99e09134738428dd0f3693c5bd2fd72bd8926403d9afc6b0851dab38a974f` |
| `k3765-z-probe.dtb` | 883 | `C511699F` | `1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e` |
| `busybox-armv5-static` | 2,119,272 | — | `3490829ccfade04de5fca428504073935458bb17553b8f9e2d25113e1a8d3d3e` |
| `kernel.config` | 48,080 | — | `4732ab4a762220858dda0346a7f7fe1e7d36206a6fd000ccfe130ef79b06c333` |
| `vmlinux-k3765-probe` | 5,582,028 | — | `0ce19b355760af6a4e1055680b007ce6ad02a6e17691a69f1b5bc3f7058444b0` |

## Verified memory bounds

- Linux physical base: `0x00200000`
- direct `Image` entry: `0x00208000`
- raw `Image` end / BSS start: `0x00662614`
- static runtime end: `0x00680D58`
- enforced direct-image limit: `0x00700000`
- remaining space to that limit: 520,872 bytes
- guard below the resident monitor: 1 MiB
- resident monitor begins: `0x00800000`
- DTB staging address: `0x01F80000`

The verifier derives `_end` from `System.map`, checks the raw `Image` boundary,
and rejects a build if the complete kernel, BSS, and built-in initramfs runtime
cross `0x00700000`.

## Physical target status

The exact `ttySHM0` artifact above is build-verified but has not yet been
booted on physical hardware. Its expected target-side preflight CRC32 values
are BL1 `D26A57AB` and DTB `C511699F`.

The preceding BusyBox baseline from commit `4c5eff8` and run `31323294185`
was loaded into SDRAM through the bounded Shadow-MSM transport. Linux booted
and reported:

```text
Linux (none) 6.1.0-shadow-msm-probe+ #1 Sun Aug 9 16:19:35 UTC 2026 armv5tejl GNU/Linux
BusyBox v1.36.1 (2026-08-09 16:16:08 UTC) multi-call binary.
uid=0 gid=0
```

BusyBox ran as PID 1, mounted `proc`, `sysfs`, and RAM-backed `tmpfs`, exposed
25,728 KiB of RAM, and executed the scripted command suite through
`/dev/shadowtrace`. A separate host process reattached more than four minutes
later; `/proc/1/exe` still resolved to `/bin/busybox`.

The target was left running from volatile SDRAM. No NAND erase, program,
partition-table, CEFS, or other persistent-storage operation was sent.
