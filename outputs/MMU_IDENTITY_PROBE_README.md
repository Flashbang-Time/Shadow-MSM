# K3765-Z ARM926 identity-MMU probe

This returning RAM-only payload isolates the ARM926 MMU from the Linux boot
path. It builds a temporary non-cacheable 1:1 section map at `0x01100000`,
installs it in TTBR, enables address translation, and makes a diagnostic call
while the MMU is active. It then restores the original `SCTLR`, `TTBR`, and
`DACR` values before returning `MMU1` (`0x4D4D5531`) to stage-0.

Every section uses descriptor flags `0x00000C12`, matching
`cpu_arm926_proc_info.io_mmu_flags` in the verified probe kernel.

The identity map deliberately covers the full 32-bit address space so the
already-initialized ARMPRG runtime and its device registers retain the same
addresses during the short diagnostic call. The D-cache remains disabled.

The payload and host workflow contain no NAND erase, program, partition, or
flash-write operation.

## RAM layout

| Region | Address |
|---|---:|
| Probe entry | `0x01000000` |
| Temporary L1 table | `0x01100000..0x01103FFF` |
| Probe stack | below `0x01FFE000` |
| Resident stage-0/diagnostic runtime | `0x00800000..0x008FFFFF` |

## Build

```powershell
py -3.9 .\work\build_mmu_identity_probe.py
```

## Target call

Load the probe alongside stage-0, verify its target CRC32, then call it:

```powershell
py -3.9 .\outputs\k3765_stage0_console.py COMxx `
  boot 0x01000000 0 0 0 `
  --log .\mmu_identity_probe.log
```

Success is both an in-MMU log line and the returned value:

```text
MMU ENABLED: translated diagnostic call succeeded
MMU disabled and original TTBR/DACR restored; returning MMU1
RETURN R0: 0x4D4D5531
```
