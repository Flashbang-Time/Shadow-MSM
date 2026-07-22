# K3765-Z RAM-only test log

All tests in this log use the legacy PBL RAM-write command (`0x0F`) and execute
command (`0x05`). No NAND erase, program, or write command was issued.

## 2026-07-19 — watchdog candidate `0x80004038`

- Downloader interface: `COM35`
- Payload: `k3765_watchdog_pet.bin`
- Payload size: 32 bytes
- SHA-256: `ce9faf98d10605d9fe6ab6c9a3f950ca2fb1f4e11443aa2fe860c3b900624261`
- Load/entry address: `0x00800000`
- Intended operation: repeatedly write `1` to `0x80004038`

Uploader result:

```text
Opening \\.\COM35 at 115200 8N1
Uploaded 32/32 bytes (100.00%)
Executing at 0x00800000...
Execute ACK received. USB disconnect is expected now.
```

Observed result:

```text
The device had already re-enumerated in normal mode as COM26/COM30/COM27
by the first poll. It remained in normal mode for the full 30-second poll.
```

Conclusion: **failed**. `0x80004038` is not a working watchdog-reset address
in the PBL execution context. Do not reuse this payload.

## 2026-07-19 - watchdog candidate `0xC0100038`

- Downloader interface: `COM36`
- Payload: `k3765_watchdog_pet_phys.bin`
- Payload size: 32 bytes
- SHA-256: `49124951ae049ce5aa4872966f2266e5a1f9481ed8045892d255ed4da01ff000`
- Load/entry address: `0x00800000`
- Intended operation: repeatedly write `1` to `0xC0100038`

Uploader result:

```text
Uploaded 32/32 bytes (100.00%)
Executing at 0x00800000...
Execute ACK received.
```

Observed result:

```text
The device re-enumerated in normal mode as COM26/COM30/COM27.
```

Conclusion: **failed**. Do not reuse this payload.

## 2026-07-19 - stock-runtime diagnostic probe v1

- Downloader interface: `COM37`
- Image: `armprg_stage0_probe.bin`
- Image size: 105,968 bytes
- SHA-256: `91b8b5b8d23293def30f20fe030d2c23d83c942402ca7b1b6cadf71f4467cc34`
- Modification: appended a 40-byte diagnostic callback and redirected command
  table slot `0x1C`

Uploader result:

```text
Uploaded 105,968/105,968 bytes (100.00%)
Executing OEM ARMPRG from 0x00800000...
GO response: 02
```

Probe result:

```text
TX: 7e 1c 95 2a 7e
RX: 0e 49 6e 76 61 6c 69 64 20 43 6f 6d 6d 61 6e 64 0a
TEXT: .Invalid Command.
```

Conclusion: the stock runtime stayed responsive, but its pre-initialization gate
allows only command `0x01`, so slot `0x1C` was never dispatched.

## Prepared - stock-runtime diagnostic probe v2

- Image: `armprg_stage0_probe_v2.bin`
- Image size: 105,968 bytes
- SHA-256: `b95e8e09f021737049b3e3aa09030d581be6bf65b6a2d7f68f1f2a8a14b7e8e2`
- Modification: redirect the permitted pre-initialization command `0x01` to
  the appended `STAGE0_OK` callback
- Status: statically verified; waiting for a fresh PBL session

## 2026-07-19 - same-size diagnostic probe v3

- Downloader interface: `COM39`
- Image: `armprg_stage0_probe_v3.bin`
- Image size: 105,928 bytes
- SHA-256: `5fd52898e29f554f521362eaa69cceb3d61424818cf7c08a6aeb15e06a45db13`

Uploader result:

```text
Uploaded 105,928/105,928 bytes (100.00%)
Executing OEM ARMPRG from 0x00800000...
GO response: 02
```

Immediate probe:

```text
TX: 7e 1c 95 2a 7e
RX: 0e 53 54 41 47 45 30 5f 4f 4b 0a
TEXT: .STAGE0_OK.
```

Ten-second repeat probe:

```text
TX: 7e 1c 95 2a 7e
RX: 0e 53 54 41 47 45 30 5f 4f 4b 0a
TEXT: .STAGE0_OK.
```

Conclusion: **success**. The modified same-size RAM image remains responsive,
and the stock ARMPRG runtime provides a stable watchdog-safe execution shell.

## 2026-07-19 - stock-runtime diagnostic probe v2

- Downloader interface: `COM38`
- Image: `armprg_stage0_probe_v2.bin`
- Image size: 105,968 bytes
- SHA-256: `b95e8e09f021737049b3e3aa09030d581be6bf65b6a2d7f68f1f2a8a14b7e8e2`

Uploader result:

```text
Uploaded 105,968/105,968 bytes (100.00%)
Executing OEM ARMPRG from 0x00800000...
GO response: 02
```

Probe result:

```text
TX: 7e 01 f1 e1 7e
RX: timeout
```

Conclusion: **failed**. The appended callback begins at the stock image's
original end/BSS boundary and is cleared during ARMPRG startup. The command
reaches that cleared area and stalls. Do not reuse v2.

## Prepared - same-size diagnostic probe v3

- Image: `armprg_stage0_probe_v3.bin`
- Image size: 105,928 bytes, identical to stock
- SHA-256: `5fd52898e29f554f521362eaa69cceb3d61424818cf7c08a6aeb15e06a45db13`
- Modification: replaces only the existing in-image `Invalid Command` text
  with `STAGE0_OK`; no code is appended
- Status: statically verified; waiting for a fresh PBL session

## Prepared - same-size PMIC LED control runtime

- Image: `armprg_pmic_led_control.bin`
- Image size: 105,928 bytes, identical to stock
- SHA-256: `4aa7def32d962d83f41832ae258fca8cb6c5ad51296fe742331437b11ead0ff1`
- Modification: replaces the stock invalid-command handler in place
- Candidate LED API: OEMSBL `0x00042B78`, which accepts channel `0/1` and
  intensity `0..15`, then performs masked writes to PMIC register `0x48`
- Host modes: `off`, `ch0`, `ch1`, `both`
- Status: executed successfully

## 2026-07-19 - PMIC LED control test

- Downloader interface: `COM40`
- Image: `armprg_pmic_led_control.bin`
- Image size: 105,928 bytes
- SHA-256: `4aa7def32d962d83f41832ae258fca8cb6c5ad51296fe742331437b11ead0ff1`

Uploader result:

```text
Uploaded 105,928/105,928 bytes (100.00%)
Executing OEM ARMPRG from 0x00800000...
GO response: 02
```

Every control command returned:

```text
RX: 0e 4c 45 44 5f 4f 4b 0a
TEXT: .LED_OK.
```

Observed channel map:

```text
off   -> LED off
ch0   -> green
ch1   -> blue
both  -> cyan
```

The final command set both channels off and returned `LED_OK`.

Conclusion: **success**. OEMSBL `0x00042B78` is the working two-channel LED
intensity routine on this K3765-Z. Channel 0 is green, channel 1 is blue, and
intensity `15` is maximum. ARMPRG remains responsive around each call.

## Prepared - RGB/MPP LED control runtime

- Image: `armprg_rgb_control.bin`
- Image size: 105,928 bytes, identical to stock
- SHA-256: `b77fd6010fc250bec210cd15e7c77d8c19beb1f391540ab5287f317d81b77c8c`
- Replacement handler: 124 bytes at `0x00810DBC..0x00810E37`
- Verification: 122 bytes differ from stock, all confined to the replacement
  handler and diagnostic response string
- Output mask:
  - bit 0: PMIC LED channel 0 (observed green)
  - bit 1: PMIC LED channel 1 (observed blue)
  - bit 2: PMIC MPP current sink 1 (red candidate)
  - bit 3: PMIC MPP current sink 3 (red candidate)
- MPP API: OEMSBL `0x0003ED0C`, current-level enum `2`, output switch `0/1`
- Host controller: `k3765_rgb_control.py`
- Continuous modes: `cycle1` and `cycle3`; Ctrl+C sends output mask zero
- Status: statically verified; waiting for a fresh PBL download-mode session

The callback references only the two established PMIC LED functions and the
stock diagnostic reply function. No NAND operation is issued by the host
controller or replacement handler.

## 2026-07-19 - red-channel identification and continuous RGB cycle

- Downloader interface: `COM41`
- PBL RAM-write probe response: `02`
- Runtime upload: 105,928/105,928 bytes
- Execute response: `02`
- Runtime interface after USB reset: `COM41`
- New handler response: `RGB_OK`

Observed MPP map:

```text
MPP current sink 1 -> red
```

Continuous host-paced sequence:

```text
red     mask 0x04
yellow  mask 0x05
green   mask 0x01
cyan    mask 0x03
blue    mask 0x02
magenta mask 0x06
```

- Period: 0.55 seconds per color
- Host process: `python.exe`, PID `20952`
- Status at launch verification: running; repeated `RGB_OK` acknowledgement for
  every color step
- Stop behavior: Ctrl+C in the visible cycle console sends mask `0x00`

Conclusion: **success**. The complete RGB LED mapping is red = MPP current sink
1, green = PMIC LED channel 0, and blue = PMIC LED channel 1. The cycle is
running through the initialized ARMPRG runtime and remains RAM-only.

## Prepared - stage-0 monitor with boot logs and system information

- Monitor image: `armprg_stage0_monitor.bin`
- Image size: 105,928 bytes, identical to stock
- SHA-256: `2b1fbf1c8e13ae3b8038ba87ba797c27099118509aae78544c46625737f53f9f`
- Stage-0 handler: 500 bytes at `0x00811374..0x00811567`
- Command `0x1C` table entry redirected to the stage-0 handler
- Host console: `k3765_stage0_console.py`
- RAM loader: `k3765_stage0_load.py`

Runtime system-information records:

```text
MIDR  ARM main ID
CTR   cache type
TCMTR tightly coupled memory status
CPSR  processor mode / interrupt state
SCTLR MMU, cache, alignment, vector state
TTBR  translation-table base
DACR  domain access control
DFSR  data fault status
IFSR  instruction fault status
FAR   fault address
SP    live ARMPRG handler stack
```

Additional primitives:

```text
CRC32  read-only verification inside 0x01000000..0x01FFFFFF
CALL   aligned ARM call inside 0x01000000..0x01FFFFFF with r0/r1/r2
```

- Second-stage proof: `k3765_stage2_proof.bin`
- Load address: `0x01000000`
- Size: 12 bytes
- SHA-256: `d0dd40b887c5e5d612484d178967eb34afad303d9bbe0d1af5eb3dc362c11a70`
- Behavior: returns `(r0 XOR r1) + r2` through `r0`; no peripheral access
- Status: statically verified; waiting for a fresh PBL session

The ARM926EJ-S CP15 selectors were checked against the ARM DDI 0198E
technical reference. The monitor and host loader implement no NAND operation.
## 2026-07-20 01:14 +03:00 — BL1 minimal bootloader milestone

- Normal-mode diagnostic port: `COM26`
- Direct diagnostic mode switch produced downloader port: `COM44`
- PBL RAM-write probe: ACK `0x02`
- Stage-0 monitor loaded at `0x00800000`
- BL1 loaded at `0x01000000`
- BL1 artifact:
  - file: `outputs/k3765_stage2_bootloader.bin`
  - size: `2,861` bytes
  - SHA-256: `135a4af42cefc7a86237e9c7d2fa8f15ff3b0df1fabbf00e362439a52098e135`
  - host CRC32: `0xEFF2DC54`
  - target CRC32: `0xEFF2DC54` (exact match)
- BL1 established and used its own stack at `0x01FFF000`.
- BL1 emitted boot logs through the resident ARMPRG USB diagnostic transport.
- Runtime values printed by BL1:
  - MIDR: `0x41069265`
  - CTR: `0x1D192192`
  - CPSR: `0x200000D3`
  - SCTLR: `0x00051078`
  - TTBR: `0x0006C000`
  - DACR: `0xFFFFFFF5`
  - active BL1 SP: `0x01FFEFE0`
- Entry-argument proof:
  - `r0=0xA0A0A0A0`
  - `r1=0xB1B1B1B1`
  - `r2=0xC2C2C2C2`
  - all three values were printed exactly.
- BL1 returned `r0=0x424F4F54` (`BOOT`) to stage-0.
- A complete stage-0 system query after BL1 returned successfully, proving
  stack restoration, link-register restoration, USB-console survival, and a
  clean second-stage return.
- Logs:
  - `outputs/diag_dload_switch_bl1.log`
  - `outputs/bl1_load.log`
  - `outputs/bl1_boot.log`
  - `outputs/bl1_post_return_stage0.log`
- No NAND erase, program, partition-table, or persistent-storage command was sent.

## 2026-07-19 23:01 +03:00 — corrected stage-0 monitor and stage-2 execution proof

- Downloader port: `COM43`
- PBL 16-byte RAM-write probe: ACK `0x02`
- Corrected RAM-only monitor:
  - load address: `0x00800000`
  - size: `105,928` bytes
  - SHA-256: `d62987d1bf6039c05b0cbf7e80ee86d47d8d00b5f154a22594c8ab30f9978dd5`
  - CRC32: `0xE47D7226`
- Stage-2 proof:
  - load address: `0x01000000`
  - size: `12` bytes
  - SHA-256: `d0dd40b887c5e5d612484d178967eb34afad303d9bbe0d1af5eb3dc362c11a70`
  - expected/target CRC32: `0x2A152283`
- PBL acknowledged every RAM chunk and the execute command with `0x02`.
- Live monitor banner: `K3765-S0-V1`
- Runtime CPU state:
  - MIDR: `0x41069265` — ARM926EJ-S r0p5
  - CTR: `0x1D192192`
  - TCMTR: `0x00000000`
  - CPSR: `0x600000D3` — SVC, ARM state, IRQ/FIQ masked
  - SCTLR: `0x00051078` — MMU off, D-cache off, I-cache on
  - TTBR: `0x0006C000`
  - DACR: `0xFFFFFFF5`
  - DFSR: `0x0000000C`
  - IFSR: `0x000000D7`
  - FAR: `0x20000054`
  - SP: `0x0081DD74`
- Target-side CRC over `0x01000000..0x0100000B`: `0x2A152283` (exact match)
- Target-side call at `0x01000000` with
  `r0=0x11111111`, `r1=0x22222222`, `r2=0x33333333`
  returned `r0=0x66666666` exactly.
- A complete system-info query after the call returned the same values, proving
  that the monitor stayed alive and the USB console remained usable.
- Logs:
  - `outputs/stage0_load_corrected.log`
  - `outputs/stage0_boot_corrected.log`
  - `outputs/stage0_boot_post_call.log`
- No NAND erase, program, partition-table, or persistent-storage command was sent.

## 2026-07-19 22:55 +03:00 — direct diagnostic download-mode switch

- Normal-mode diagnostic port: `COM26`
- Normal USB identity: `VID_19D2&PID_0016`, composite device
- Sent one Qualcomm diagnostic command: `DIAG_DLOAD_F` (`0x3A`)
- Source used to verify the command: local `edlclient/Tools/qc_diag.py`
- The serial handle disconnected while awaiting the reply, as expected during
  USB re-enumeration.
- Resulting device: `ZTE WCDMA Technologies MSM`
- Resulting USB identity: `USB\VID_19D2&PID_0016` without composite interfaces
- Windows state: unknown device, problem code 28 (driver not bound)
- No programmer, partition table, erase, program, or NAND-write command was sent.
- Transcript: `outputs/diag_dload_switch.log`

## 2026-07-20 — BL1 0.1 post-run CRC explanation

- Host/original BL1 0.1 CRC32: `0xEFF2DC54`
- Target CRC32 after the verified BL1 run: `0x83FFF9DF`
- BL1's only writable byte range inside its image is the 13-byte hexadecimal
  formatting buffer at `0x01000B20`.
- The last value printed was argument 2, `0xC2C2C2C2`.
- Independently replacing only that buffer with `0xC2C2C2C2\r\n\0` produces
  CRC32 `0x83FFF9DF`, exactly matching the target.
- Conclusion: the executable code remained intact; the CRC change is the
  expected formatter-buffer mutation.

## 2026-07-20 — BL1 0.2 Linux handoff dry-run build

- Status: host-built and statically audited; target test awaits a fresh PBL
  RAM-only session.
- BL1 0.2:
  - address: `0x01000000`
  - size: `5,677`
  - SHA-256:
    `d6906af398b680b309b7f40403f853e4d43bd830c6159e4490b824e9794fc90c`
  - CRC32 before execution: `0x83FD9148`
  - predicted CRC32 after a successful dry run: `0x1AFE6067`
- Header-only zImage parser fixture:
  - address: `0x01200000`
  - size: `64`
  - CRC32: `0x099A07E1`
- Minimal valid flattened device tree:
  - address: `0x01F80000`
  - size: `429`
  - CRC32: `0xB82041C8`
  - FDT magic: `0xD00DFEED`
  - DTB reserve map protects `0x01F80000..0x01F8FFFF`
- Static ARM instruction audit found no MMIO writes. The only non-stack store
  is the known hexadecimal formatting-buffer byte store.
- BL1 validates both headers, prints the future Linux `PC/r0/r1/r2`, and
  returns `0x44525931` (`DRY1`) without branching to the fixture.
- No persistent-storage operation is implemented by the bundle loader.

## 2026-07-20 — BL1 0.2 target verification

- Normal stock runtime reached network registration before the test.
- Normal diagnostic port: `COM26`
- Sent only `DIAG_DLOAD_F` (`0x3A`) to enter the legacy downloader.
- Downloader/stage-0 port: `COM45`
- RAM bundle:
  - stage-0 monitor at `0x00800000`
  - BL1 0.2 at `0x01000000`
  - 64-byte header-only zImage fixture at `0x01200000`
  - 429-byte minimal DTB at `0x01F80000`
- Target-side CRC32 results before the call:
  - BL1 0.2: `0x83FD9148`
  - zImage fixture: `0x099A07E1`
  - DTB: `0xB82041C8`
- BL1 header validation:
  - zImage magic: `0x016F2818`
  - zImage header start: `0x00108000`
  - zImage header end: `0x00108040`
  - DTB in-memory magic: `0xEDFE0DD0`
  - DTB total size: `0x000001AD`
- Planned Linux entry:
  - PC: `0x01200000`
  - r0: `0x00000000`
  - r1: `0xFFFFFFFF`
  - r2: `0x01F80000`
- BL1 printed `Validation PASS` and returned `0x44525931` (`DRY1`) without
  branching to the fixture.
- Post-run BL1 CRC32: `0x1AFE6067`, exactly matching the predicted formatting
  buffer mutation.
- A complete stage-0 system query succeeded after BL1 returned.
- Logs:
  - `outputs/diag_dload_switch_bl1_0.2.log`
  - `outputs/bl1_0.2_bundle_load.log`
  - `outputs/bl1_0.2_dryrun.log`
  - `outputs/bl1_0.2_post_return_stage0.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 — post-MMU identity-execution checkpoint

- GitHub Actions run
  [`29766396164`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29766396164)
  built commit `c3b8cea` successfully.
- Verified Linux Image:
  - load/entry: `0x00208000`
  - size: `3,569,520`
  - SHA-256:
    `22fe17ee6dc3e717c628a06a88ae4116b1294f9cd596b11d1f52856aa4fd8034`
  - host and target-side BL1 fingerprint CRC32: `0x3A650669`
- BL1 0.4:
  - load address: `0x01000000`
  - size: `5,933`
  - SHA-256:
    `1090dcf5925eca2005e974e7fa57ed7af8ff2fb30bf92ccb70bf03b9a10b0097`
  - target CRC32: `0x7ED5F178`
- DTB:
  - load address: `0x01F80000`
  - size: `549`
  - target CRC32: `0x5D395650`
- Target output advanced beyond the previous MMU boundary and reached:

  ```text
  Shadow-MSM: MMU enabled; identity execution continues
  ```

- The raw transport then disconnected and the stock composite ports (`COM26`,
  `COM27`, and `COM30`) returned. This proves translated execution continued
  after writing SCTLR; the next diagnostic build brackets the high virtual
  `__mmap_switched` path, BSS clearing, and the `start_kernel` branch.
- Preserved transcript: `outputs/bl1_0.4_postmmu_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-20 — Returning ARM926 identity-MMU probe

- Raw downloader/stage-0 port: `COM50`
- RAM bundle:
  - stage-0 monitor at `0x00800000`
  - identity-MMU probe at `0x01000000`
- Identity-MMU probe:
  - size: `5,933`
  - SHA-256:
    `907079d9190a3fb0d38f84ac0d8bb6994a8c14319ae903bd470939387d86d620`
  - host and target CRC32: `0x378F1FEA`
  - temporary L1 table: `0x01100000..0x01103FFF`
  - section flags: `0x00000C12`, matching the verified ARM926 procinfo
    non-cacheable mapping flags
- Every PBL RAM-write chunk and the stage-0 execute request returned ACK
  `0x02`.
- Original CPU control state:

  ```text
  SCTLR: 0x00051078
  TTBR : 0x0006C000
  DACR : 0xFFFFFFF5
  ```

- The target built a complete non-cacheable 1:1 section map, installed it,
  enabled the ARM926 MMU, and successfully called the resident diagnostic
  runtime while translation was active:

  ```text
  MMU ENABLED: translated diagnostic call succeeded
  SCTLR: 0x00051079
  TTBR : 0x01100000
  DACR : 0x00000003
  ```

- The payload disabled translation, restored the original TTBR and DACR,
  invalidated the TLB, and returned `0x4D4D5531` (`MMU1`) to stage-0.
- A complete post-return stage-0 hardware query succeeded and confirmed that
  `SCTLR`, `TTBR`, and `DACR` exactly matched their pre-test values.
- Preserved logs:
  - `outputs/mmu_identity_bundle_load_20260720.log`
  - `outputs/stage0_info_mmu_probe_20260720.log`
  - `outputs/mmu_identity_probe_20260720.log`
  - `outputs/stage0_info_after_mmu_probe_20260720.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-20 — BL1 0.3 zImage target entry

- GitHub Actions run `29728599678` produced the verified Linux v6.1 probe:
  - zImage: `1,721,376` bytes, SHA-256
    `42812837dde444f9af32612d5341e9c39bad53e2ec8c4de232f6754d456761ee`,
    CRC32 `0x84FA997D`
  - Image: `3,569,520` bytes, SHA-256
    `6a67cad42756124f7aa084e1d625c779bb39e1408e3f69648784010b35b10f51`
  - DTB: `549` bytes, SHA-256
    `53e5df6453001df89ff73985901bc613bff87ecbd8b8479108de09299a8e42bb`,
    CRC32 `0x5D395650`
- A full-image target CRC request exceeded the watchdog interval. The host
  verifier was changed to request independent `0x8000`-byte CRC windows.
- All 53 zImage windows matched the host file exactly. The final local
  full-image CRC remained `0x84FA997D`.
- BL1 0.3, DTB, and monitor checks passed before handoff.
- BL1 entered the zImage and the target printed `Uncompressing Linux...`.
- The zImage decompressor did not complete within the hardware watchdog
  interval, so the next attempt bypassed it using the uncompressed Image.
- Preserved transcript: `outputs/bl1_0.3_linux_boot_20260720.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-20 — BL1 0.4 direct uncompressed Image handoff

- BL1 0.4:
  - load address: `0x01000000`
  - size: `5,933`
  - SHA-256:
    `bc9dbf8ef9463cda0679cbe15dbcea01c73af6c75a6f2ddc92183060542a8d83`
  - CRC32: `0xF0E0ADF7`
- Verified Linux Image:
  - load/entry address: `0x00208000`
  - end address: `0x0056F770`
  - size: `3,569,520`
  - CRC32: `0x4ECBFE56`
- The bounded host loader accepted the direct-Image range only inside
  `0x00208000..0x005FFFFF`; its original stage-2 window remains
  `0x01000000..0x01FFFFFF`.
- Every PBL RAM-write chunk and the monitor execute request returned ACK
  `0x02`.
- BL1 checked the exact Image size, 17 sparse Image fingerprints, the DTB
  magic/size, the explicit `IMG1` arming marker, and the MMU/D-cache entry
  state.
- Target output reached:

  ```text
  JUMPING DIRECTLY TO DECOMPRESSED LINUX IMAGE
  Shadow-MSM: entered decompressed Linux head.S
  Shadow-MSM: ARM926 processor lookup passed
  Shadow-MSM: initial page tables created
  ```

- The raw diagnostic USB port remained enumerated after the 30-second log
  timeout. The target did not fall back into stock composite mode during the
  observation window.
- Subsequent source review found that the missing fourth trace used `push`
  after Linux had repurposed `sp` (`r13`) as the future virtual
  `__mmap_switched` address. The trace hook itself was therefore unsafe at
  that location; the three observed milestones remain valid.
- Preserved transcript: `outputs/bl1_0.4_direct_image_boot_20260720.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-20 — BL1 0.4 fixed-stack ARM926/MMU-boundary trace

- GitHub Actions run
  [`29761806131`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29761806131)
  produced the fixed-stack probe from commit `a63dbb1`.
- Linux `Image`:
  - load/entry: `0x00208000`
  - size: `3,569,520`
  - SHA-256:
    `ef9d742b1d3784682f9196bd3d3eff30876ec70a039f6a8260096e893bd1ded2`
  - CRC32: `0x4E1D617D`
- BL1 0.4:
  - load address: `0x01000000`
  - size: `5,933`
  - SHA-256:
    `ac610441c17e96c63c4f3ab0a2014d0119126d365af62c3b086fd6a1f9f22e8d`
  - target CRC32: `0x507AFC91`
- DTB:
  - load address: `0x01F80000`
  - size: `549`
  - target CRC32: `0x5D395650`
- Stage-0 identified the target as ARM926EJ-S variant 0 revision 5 with
  `SCTLR=0x00051078`, MMU off, D-cache off, I-cache on, and IRQ/FIQ masked.
- BL1 validated the exact Image size, all 17 sparse Image fingerprints, DTB
  magic and size, and the explicit `IMG1` marker.
- Target output reached:

  ```text
  Shadow-MSM: entered decompressed Linux head.S
  Shadow-MSM: ARM926 processor lookup passed
  Shadow-MSM: initial page tables created
  Shadow-MSM: calling ARM926 processor setup
  Shadow-MSM: entered ARM926 setup
  Shadow-MSM: ARM926 cache invalidate returned
  Shadow-MSM: ARM926 TLB invalidate returned
  Shadow-MSM: ARM926 control word ready
  Shadow-MSM: ARM926 setup returned; enabling MMU next
  ```

- The raw COM transport disconnected at the MMU handoff. The normal composite
  ports (`COM26`, `COM27`, and `COM30`) subsequently returned, indicating a
  target reset after the MMU boundary.
- A host attempt to CRC the lower Image window was rejected by stage-0 with
  `BAD00001`; no read or write occurred. BL1's embedded fingerprints remain
  the target-side Image validation mechanism for this memory layout.
- Preserved logs:
  - `outputs/direct_image_bundle_load_fixedtrace_20260720.log`
  - `outputs/stage0_info_fixedtrace_20260720.log`
  - `outputs/bl1_0.4_fixedtrace_boot_20260720.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 — high-virtual Linux startup proof

- GitHub Actions run
  [`29871565525`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29871565525)
  built commit `d14ecab` successfully.
- Verified Linux Image:
  - load/entry: `0x00208000`
  - size: `3,569,520`
  - SHA-256:
    `efcd07573a3b6fab9b7d84e8098693f16891d58f4e0a091e8993f1a881a94765`
  - host CRC32: `0x0AB1B805`
- Target-side BL1 CRC32 was `0x7ED5F178`; target-side DTB CRC32 was
  `0x5D395650`. BL1 also passed all 17 embedded Image fingerprints.
- Target output reached all three new checkpoints:

  ```text
  Shadow-MSM: entered __mmap_switched at the kernel virtual address
  Shadow-MSM: __mmap_switched cleared BSS
  Shadow-MSM: branching to start_kernel
  ```

- This proves the high virtual kernel mapping, BSS clearing, early global
  stores, and branch into Linux C startup all work on the MSM6290. The next
  diagnostic build instruments `start_kernel`, ARM machine selection,
  memblock discovery, and the `paging_init` boundary.
- Preserved transcript: `outputs/bl1_0.4_highvirt_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 — early C, DT, memblock, and paging boundary

- GitHub Actions run
  [`29872580738`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29872580738)
  built commit `1a7b5d6` successfully.
- Verified Linux Image SHA-256:
  `02f807e7e5b7e6141f232b8262cad575f03bc1dfa9d482703b9aaa8675214af8`;
  host CRC32: `0x5A29B4E3`.
- Target-side BL1 CRC32 was `0xB92429C2`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux reached every new checkpoint through:

  ```text
  Shadow-MSM: entered start_kernel C code
  Shadow-MSM: initial task stack is ready
  Shadow-MSM: processor ID setup completed
  Shadow-MSM: earliest generic initialization completed
  Shadow-MSM: entering ARM setup_arch
  Shadow-MSM: entered setup_arch
  Shadow-MSM: setup_processor completed
  Shadow-MSM: device-tree machine selected
  Shadow-MSM: early_mm_init completed
  Shadow-MSM: ARM memblock initialization completed
  Shadow-MSM: entering paging_init
  ```

- This proves Linux C startup, DT machine selection, early MM setup, and ARM
  memblock discovery work. Inspection of Linux v6.1 `prepare_page_table()`
  identified the precise disconnect cause: it clears the temporary low
  identity entry containing the resident diagnostic runtime.
- Preserved transcript: `outputs/bl1_0.4_earlyc_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - permanent low and kernel mappings

- GitHub Actions run
  [`29905123406`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29905123406)
  built commit `d0236f6` successfully after validating the patch against the
  exact Linux v6.1 source.
- Verified Linux Image SHA-256:
  `1ac16f457bbeb25c55c89b5dec9180a4cabdc7d7e75bb7d26fd5e14064c83359`;
  host CRC32: `0xB2553ED4`.
- Target-side BL1 CRC32 was `0xBB3CD120`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux retained the resident monitor's single 2 MiB identity entry and
  reached these new checkpoints:

  ```text
  Shadow-MSM: permanent table kept monitor identity map
  Shadow-MSM: map_lowmem completed
  Shadow-MSM: permanent kernel mappings completed
  ```

- This proves `prepare_page_table()`, `map_lowmem()`, and `map_kernel()` all
  return on the MSM6290. The next trace separates `dma_contiguous_remap()`,
  `early_fixmap_shutdown()`, and the internal stages of `devicemaps_init()`.
- Preserved transcript: `outputs/bl1_0.4_pagingfix_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - device-map TLB boundary

- GitHub Actions run
  [`29906374787`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29906374787)
  built commit `e0352ee` successfully.
- Verified Linux Image SHA-256:
  `b9cde15e1668fa7d04cf4382620282c5a544834e1a0ef6556d23d5e6de8deb5f`;
  host CRC32: `0xEC53646C`.
- Target-side BL1 CRC32 was `0x29AAD42C`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux reached each internal device-map checkpoint through:

  ```text
  Shadow-MSM: DMA contiguous remap completed
  Shadow-MSM: early fixmap shutdown completed
  Shadow-MSM: vector pages allocated
  Shadow-MSM: early trap vectors initialized
  Shadow-MSM: static device mappings completed
  Shadow-MSM: PCI I/O reservation completed
  ```

- The transport disconnects exactly at `local_flush_tlb_all()`. This proves
  Linux completed device-map construction; the borrowed ARMPRG USB routine
  was relying on stale identity-mapped device translations cleared earlier in
  `devicemaps_init()`.
- Preserved transcript: `outputs/bl1_0.4_devmaps_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - identity mappings survive the TLB flush

- GitHub Actions run
  [`29909930945`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29909930945)
  built commit `e331393` successfully.
- Verified Linux Image SHA-256:
  `6ab35cbd8270c4621188c9ea40f3338cffa3d652895aeba4248fbf2ccf18f608`;
  host CRC32: `0x328D1AFD`.
- Target-side BL1 CRC32 was `0xEF38AFFB`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Retaining the low bootstrap identity mappings kept the resident diagnostic
  runtime reachable across both the TLB and cache flushes. Linux completed
  `devicemaps_init()` and reached `kmap_init()`.
- Retaining the temporary upper vmalloc section was then proven incorrect:
  it left a section descriptor where `kmap_init()` requires a page table.
- Preserved transcript: `outputs/bl1_0.4_identitymap_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - paging and setup_arch complete

- GitHub Actions run
  [`29910877227`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29910877227)
  built commit `2c1944c` successfully.
- Verified Linux Image SHA-256:
  `69868605d1d06a6584dd745d6cef758a1fdcd1aac9f511d7fd67180c2e0f8248`;
  host CRC32: `0x1C4557F8`.
- Target-side BL1 CRC32 was `0x7EF359B2`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Restoring normal upper-vmalloc clearing while preserving only the required
  low identity mappings allowed Linux to complete permanent kmap setup, TCM
  setup, zero-page allocation, `bootmem_init()`, `paging_init()`, and finally
  return from `setup_arch()`.
- Preserved transcript: `outputs/bl1_0.4_fixmap_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - generic memory management and scheduler complete

- GitHub Actions run
  [`29912975370`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29912975370)
  built commit `e171e99` successfully.
- Verified Linux Image SHA-256:
  `c923ff8c57b16efaf295f366c454184ea635c4f1b81044738fa63d97a5de1f57`;
  host CRC32: `0xA2852740`.
- Target-side BL1 CRC32 was `0x42713796`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux completed command-line parsing, the early RNG, log and VFS caches,
  exception sorting, trap setup, generic memory management, tracing setup,
  and `sched_init()`.
- Preserved transcript: `outputs/bl1_0.4_mm_sched_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - IRQ core, timer core, and platform time complete

- GitHub Actions run
  [`29913982901`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29913982901)
  built commit `28f2700` successfully.
- Verified Linux Image SHA-256:
  `4decdf754adbc317b1e579df09333aa251724a6a48cd07df76a3e9277f3c8e3b`;
  host CRC32: `0x0966D539`.
- Target-side BL1 CRC32 was `0x2711BFD0`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux completed radix/maple trees, housekeeping, early workqueues, RCU,
  trace events, context tracking, early and platform IRQ initialization, the
  tick and timer cores, softirqs, timekeeping, platform time initialization,
  and `random_init()`.
- Preserved transcript: `outputs/bl1_0.4_irq_timer_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.

## 2026-07-22 - CPU interrupts and console initialization complete

- GitHub Actions run
  [`29914962438`](https://github.com/Flashbang-Time/Shadow-MSM/actions/runs/29914962438)
  built commit `28943c4` successfully.
- Verified Linux Image SHA-256:
  `b596aa519b02dfca95a872aaa5e8a363f197fafdfa4587599127f80c6ec701aa`;
  host CRC32: `0xDAFF4B81`.
- Target-side BL1 CRC32 was `0x949C7DD5`; target-side DTB CRC32 was
  `0x5D395650`; all 17 embedded Image fingerprints passed.
- Linux completed KFENCE, the boot stack canary, performance/profile setup,
  cross-CPU call setup, survived the first `local_irq_enable()`, completed
  late slab setup, and returned successfully from `console_init()`.
- Preserved transcript: `outputs/bl1_0.4_irq_enable_boot_20260722.log`
- No NAND erase, program, partition-table, or persistent-storage command was
  sent.
