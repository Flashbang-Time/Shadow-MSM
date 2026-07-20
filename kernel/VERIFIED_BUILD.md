# Verified K3765-Z Linux probe build

The current fixed-stack ARM926 Linux probe completed successfully in GitHub
Actions run
[`29761806131`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29761806131)
from commit `a63dbb1`.

## Verified artifacts

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `zImage-k3765-probe` | 1,721,544 | `165A367A` | `0f17aaa6a6c8b4652e01e9db85f489e1df766eefb0173254288b3e45e3b298a4` |
| `Image-k3765-probe` | 3,569,520 | `4E1D617D` | `ef9d742b1d3784682f9196bd3d3eff30876ec70a039f6a8260096e893bd1ded2` |
| `k3765-z-probe.dtb` | 549 | `5D395650` | `53e5df6453001df89ff73985901bc613bff87ecbd8b8479108de09299a8e42bb` |
| `kernel.config` | 51,552 | — | `e5861316037a1978101242b5cd9379d50df30e68499021e28b4232ce696a7acf` |
| `vmlinux-k3765-probe` | 4,640,156 | — | `72e34de4545d0e5b3ff6f45fe7a106fa6f5a3ac74582639d1e85b0a9aa7591c7` |

The independent local verifier reproduced the CI report:

- Linux physical base: `0x00200000`
- decompressed entry: `0x00208000`
- decompressed Image end: `0x0056F770`
- stage-0 begins: `0x00800000`
- DTB staging address: `0x01F80000`
- both required FDT reservations are present
- `CONFIG_CPU_ARM926T=y`
- `CONFIG_ARCH_MULTIPLATFORM=y`
- `CONFIG_AUTO_ZRELADDR=y`
- `CONFIG_ARM_PATCH_PHYS_VIRT=y`
- `CONFIG_SHADOW_MSM_EARLY_TRACE=y`

The corresponding BL1 0.4 target run validated all 17 sparse Image
fingerprints, completed the ARM926 cache and TLB setup routines, returned the
processor control word, and reached the call boundary immediately before
Linux enables the MMU. The complete transcript is preserved in
`outputs/bl1_0.4_fixedtrace_boot_20260720.log`.

This is a RAM-only probe artifact. It contains no NAND driver or
persistent-storage operation.
