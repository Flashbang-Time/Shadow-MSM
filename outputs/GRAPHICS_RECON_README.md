# MSM6290 graphics reconnaissance

This directory contains an offline static-analysis report and a conservative
RAM-only probe for the ZTE K3765-Z MSM6290 target.  The vendor firmware is not
included and must be supplied locally.

## What is confirmed

The examined K3765-Z AMSS image contains a substantial Qualcomm display stack:

- MDP device and driver code (`/dev/mdp`, overlays, display update and capture)
- MDDI host/panel support
- display MISR/CRC diagnostics
- Toshiba, Sharp and Corona panel-related code

The same image did not expose recognizable Adreno, EGL, OpenGL ES, OpenVG,
KGSL, Q3D, Yamato or Stargate runtime strings.  This does not prove that the
MSM6290 silicon lacks 3D hardware.  It means the modem firmware examined here
does not contain an identifiable 3D software stack.

Static analysis also recovered a table of consecutive 1-MiB virtual-to-
physical mappings.  Several high physical apertures are retained as neutral
`lead_*` entries.  They are investigation leads, not identified GPU registers.
The `xref_8000` entry is a control case with two direct PC-relative references
from executable ARM code.  The `lead_a000`, `lead_a800*` and `lead_b800`
aliases had no such direct references in this scan, which weakens—but does not
eliminate—the hypothesis that this particular AMSS actively uses them.

## Reproduce the static report

Install the Python dependencies used elsewhere by Shadow-MSM, then run:

```powershell
py -3.9 .\work\analyze_msm6290_graphics.py `
  C:\path\to\amss.mbn `
  --report .\outputs\msm6290_graphics_static_report.txt
```

The report records only the firmware basename, never the local source path.

Rebuild the probe with:

```powershell
py -3.9 .\work\build_msm6290_graphics_map_probe.py
```

## Probe safety boundary

`k3765_graphics_map_probe.bin`:

- executes only from SDRAM at `0x01000000`;
- reads CP15 TTBR and five inherited L1 page-table words in RAM;
- does not dereference any candidate peripheral address;
- does not enable clocks or write MMIO;
- contains no NAND erase/program/write implementation;
- returns `0x474D5031` (`GMP1`) to the resident stage-0 monitor.

The probe prints the raw TTBR, aligned L1 base and each descriptor.  For an ARM
short-descriptor section mapping, bits `[1:0]` equal `2` and the physical base
is `descriptor & 0xFFF00000`.  A zero/fault descriptor means that alias is not
present in the inherited downloader map.

## Future hardware test

From a fresh legacy downloader session, with the user-supplied resident
stage-0 monitor available:

```powershell
py -3.9 .\outputs\k3765_stage0_load.py COMxx `
  .\outputs\armprg_stage0_monitor.bin `
  .\outputs\k3765_graphics_map_probe.bin `
  --log .\graphics_map_load.log

py -3.9 .\outputs\k3765_stage0_console.py COMxx `
  crc 0x01000000 5933

py -3.9 .\outputs\k3765_stage0_console.py COMxx `
  boot 0x01000000 0 0 0 `
  --log .\graphics_map_probe.log
```

Use the size and CRC printed by the current builder/map file if they differ
from the example.  Hardware behavior remains unverified until a replacement
target is available.
