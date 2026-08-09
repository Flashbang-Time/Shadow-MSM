# Shadow-MSM K3765-Z Linux shell kit

This directory boots the verified Shadow-MSM Linux v6.1 probe and a static
BusyBox 1.36.1 `ash` shell on a ZTE/Vodafone K3765-Z. The prompt remains
`shadow-msm#`. Everything executes from volatile SDRAM. Power-cycling returns
the modem to its stock firmware.

The launcher contains no NAND, CEFS, partition-table, erase, or flash-program
operation. Putting this directory into the modem's virtual-CD ISO does not
make the Linux boot persistent; it only makes the host-side boot kit available
from the modem itself.

## Requirements

- Windows with Python 3.9 or newer and the `py` launcher.
- The normal K3765-Z ZTE drivers.
- A USB connection to the K3765-Z.

`pyserial` 3.5 is included under `vendor/`, so the kit does not need internet
access or a separate package installation.

The exact signed ZTE Diagnostics Interface driver dated 09/18/2009 is included
under `driver/zteusbdiag-2009`. On a new PC, right-click
`INSTALL_ZTE_DRIVER.cmd`, choose **Run as administrator**, and accept the UAC
prompt before booting Linux. Its INF explicitly covers the modem's normal
`19D2:2002` diagnostics interface and raw `19D2:0016` downloader interface.
The vendor driver files remain ZTE software and are not GPLv3-covered project
code.

## Boot Linux

1. Power-cycle the modem and wait for its normal interfaces.
2. Double-click `BOOT_LINUX.cmd`, or open a terminal in this directory and run:

   ```powershell
   py -3.9 .\SHADOW_MSM_BOOT.py
   ```

3. The launcher verifies every binary before opening a serial port.
4. It copies the verified kit into a unique session directory below
   `%LOCALAPPDATA%\Shadow-MSM\runtime`, then opens a separate local console.
   The virtual-CD launcher exits before the modem changes USB personalities.
5. The local console sends only Qualcomm diagnostic command `DIAG_DLOAD_F`
   (`0x3a`) to enter
   the legacy downloader.
6. After the switch, the copied session directory opens in Explorer so the
   exact files still in use remain visible even though the virtual CD has
   disconnected.
7. If Windows shows a driverless `ZTE WCDMA Technologies MSM`, install the
   bundled package by right-clicking `INSTALL_ZTE_DRIVER.cmd` and choosing
   **Run as administrator**. Manual selection remains available at:

   ```text
   Ports (COM & LPT)
   -> ZTE Corporation
   -> ZTE Diagnostics Interface, 09/18/2009
   ```

   The launcher keeps waiting and continues automatically when the COM port
   appears.
8. The launcher uploads the monitor, Linux Image, BL1, and DTB to their fixed
   SDRAM addresses, verifies BL1 and DTB with target-side CRC32, prints every
   boot milestone, and presents:

   ```text
   shadow-msm#
   ```

Standard BusyBox commands such as `uname`, `id`, `ps`, `mount`, `ls`, `cat`,
`mkdir`, `cp`, `mv`, `rm`, `grep`, and `vi` are available. Press `Ctrl+C` to
detach without deliberately resetting the target. When the local launcher
exits, it deletes only its own staged session directory. Logs remain under
`%LOCALAPPDATA%\Shadow-MSM\logs`.

## Reattach

If Linux remains running in RAM, double-click `ATTACH_SHELL.cmd`, or run:

```powershell
py -3.9 .\SHADOW_MSM_BOOT.py --attach
```

If automatic COM detection is ambiguous, add:

```powershell
--downloader-port COMxx
```

## Verification-only mode

This checks every payload and opens no serial port:

```powershell
py -3.9 .\SHADOW_MSM_BOOT.py --dry-run
```

You can also double-click `VERIFY_KIT.cmd`. It forces Python to use only the
standard library plus the vendored serial package, providing an offline-kit
check as well as a payload check.

All host-side loading, target inspection, CRC verification, Linux handoff, and
interactive-console logic is integrated into `SHADOW_MSM_BOOT.py`. The CMD
files are only double-clickable wrappers around that one Python program.

## Logs

Every session keeps all output visible in the terminal and also writes
timestamped transcripts to the PC's writable application-data directory:

```text
%LOCALAPPDATA%\Shadow-MSM\logs
```

This location is used because the kit may be running directly from the
read-only virtual CD. Logs include the mode switch, RAM bundle metadata,
stage-0 CPU information, target-side preflight CRCs, and complete Linux/shell
output. Use `--log-dir C:\some\folder` to choose another location.

## Included payload map

| File | SDRAM address | Purpose |
|---|---:|---|
| `armprg_stage0_monitor.bin` | `0x00800000` | Resident USB monitor |
| `Image-k3765-probe` | `0x00208000` | Linux v6.1 ARM Image |
| `k3765_bl1_linux_image.bin` | `0x01000000` | Validating BL1 handoff |
| `k3765-z-probe.dtb` | `0x01f80000` | Device tree |

The Linux file ends at `0x0069b9b0`; its complete static runtime, including
BSS, ends at `0x006ba858`. This leaves 1,333,160 bytes before the resident
monitor at `0x00800000`. `SHA256SUMS` covers every distributable file in this
directory. The generated kit corresponds to the build-verified BusyBox
payload set from GitHub Actions run `31323294185`. That exact payload set has
booted on the physical K3765-Z: BusyBox ran as PID 1 and UID 0, ordinary
commands completed, and a later host process reattached to the same live
shell. The test did not access NAND or replace the modem's existing virtual-CD
image.
