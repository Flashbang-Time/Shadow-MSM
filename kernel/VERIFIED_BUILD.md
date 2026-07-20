# Verified K3765-Z Linux probe build

The first ARM926 Linux probe completed successfully in GitHub Actions run
[`29728599678`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29728599678)
from commit `2d4aebc183c2d593a5e1f704a30f27961e40a772`.

## Verified artifacts

| Artifact | Size | CRC32 | SHA-256 |
|---|---:|---:|---|
| `zImage-k3765-probe` | 1,721,376 | `84FA997D` | `42812837dde444f9af32612d5341e9c39bad53e2ec8c4de232f6754d456761ee` |
| `Image-k3765-probe` | 3,569,520 | — | `6a67cad42756124f7aa084e1d625c779bb39e1408e3f69648784010b35b10f51` |
| `k3765-z-probe.dtb` | 549 | `5D395650` | `53e5df6453001df89ff73985901bc613bff87ecbd8b8479108de09299a8e42bb` |
| `kernel.config` | 51,552 | — | `e5861316037a1978101242b5cd9379d50df30e68499021e28b4232ce696a7acf` |

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

This is a RAM-only probe artifact. It contains no NAND driver or
persistent-storage operation.
