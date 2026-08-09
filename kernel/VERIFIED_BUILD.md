# Verified K3765-Z BusyBox Linux build

The current ARM926 Linux and static BusyBox bundle completed successfully in
GitHub Actions run
[`31323294185`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/31323294185)
from commit `4c5eff8`.

The downloaded artifact ZIP matched GitHub's published SHA-256 digest
`4cb5d68fc566847d84cdbac615c0f2831067c053bdb93142784b8bd2f772eaf6`.
Every entry in the bundle's internal `SHA256SUMS` file also matched.

## Verified artifacts

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `zImage-k3765-probe` | 2,919,376 | `32A9419F` | `71e59e182ec68fc33d77940eeab0b9f383e7582725aec9a70c28a6e2b91a2559` |
| `Image-k3765-probe` | 4,798,896 | `4EEE7CDF` | `a2cb483e5b7b9c22675d594ab054e2457e7a156162839b25cd34df7a1e2579c6` |
| `k3765-z-probe.dtb` | 891 | `483C3017` | `58607b3d3b36cd2f89b9ffbad53a7758173811086249eb99954884db7ba78a35` |
| `busybox-armv5-static` | 2,119,272 | — | `bce9e2d7d9ad6fbdbb0835e06fbd348053d9ff3850d610b4f17d614bd414325c` |
| `kernel.config` | 52,422 | — | `c8928d66dfdf4dbab99e7aa5b71f1171da8e32edcc36d37271d5911192764716` |
| `vmlinux-k3765-probe` | 5,880,128 | — | `89431d5d92c8c1fb6d060e0da538d2f273ff79df6e6608d82806677804634606` |

## Verified memory bounds

- Linux physical base: `0x00200000`
- direct `Image` entry: `0x00208000`
- raw `Image` end / BSS start: `0x0069B9B0`
- static runtime end: `0x006BA858`
- enforced direct-image limit: `0x00700000`
- remaining space to that limit: 284,584 bytes
- guard below the resident monitor: 1 MiB
- resident monitor begins: `0x00800000`
- DTB staging address: `0x01F80000`

The verifier derives `_end` from `System.map`, checks the raw `Image` boundary,
and rejects a build if the complete kernel, BSS, and built-in initramfs runtime
cross `0x00700000`.

## Physical target result

The bundle was loaded into SDRAM through the bounded Shadow-MSM transport.
Every downloader packet was acknowledged, and target-side preflight CRC32
matched for BL1 (`AF2CF379`) and the DTB (`483C3017`). Linux then booted and
reported:

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
