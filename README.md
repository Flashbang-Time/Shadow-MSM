
# Shadow-MSM

Experimental Linux and custom bootloader bring-up for the **Qualcomm MSM6290**, initially targeting the **ZTE Vodafone K3765-Z** USB modem.

Shadow-MSM aims to turn an undocumented late-2000s Qualcomm modem platform into a usable ARM development target by reverse engineering its boot chain, hardware interfaces, firmware formats, and recovery protocols.

> **Current state:** arbitrary ARM code can be uploaded and executed entirely from RAM through the factory Qualcomm downloader. NAND flashing is not required for development.

---

## Project goals

- Build a custom RAM-resident monitor and bootloader for MSM6290
- Reverse engineer the MSM6290 memory map and peripherals
- Boot a minimal ARM Linux kernel with a built-in initramfs
- Add UART or USB-based console support
- Support the onboard RGB status LED
- Support the watchdog, timer, and interrupt controller
- Access the onboard microSD slot
- Eventually boot Linux automatically from microSD or NAND
- Preserve a reliable stock recovery path

The initial Linux target is intentionally minimal:

```text
Linux zImage
+ Device Tree
+ built-in BusyBox initramfs
+ shell
````

Networking, NAND, USB gadget support, audio, display output, and the original cellular functionality are later goals.

---

## Target hardware

### ZTE Vodafone K3765-Z

| Component         | Details                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| SoC               | Qualcomm MSM6290                                                        |
| CPU               | ARM926EJ-S / ARMv5TEJ                                                   |
| Original system   | Qualcomm AMSS on OKL4                                                   |
| NAND              | 128 MiB Hynix NAND                                                      |
| NAND geometry     | 2048-byte pages, 64-byte OOB, 64 pages per block                        |
| RAM               | Likely approximately 32 MiB, still to be fully verified                 |
| Storage expansion | microSD                                                                 |
| Connectivity      | USB, diagnostic interfaces, modem interfaces                            |
| Indicators        | Multicolor RGB status LED                                               |
| Cellular          | GSM, EDGE, UMTS, HSUPA                                                  |
| Audio             | Raw G.711 A-law or μ-law audio through a dedicated USB serial interface |

The flash and RAM appear to be combined in a Hynix MCP package:

```text
Hynix H8ACS0PL0MCR-56M
```

---

## Original boot chain

The stock device appears to boot through:

```text
Qualcomm Boot ROM / PBL
        ↓
QCSBL
        ↓
OEMSBL
        ↓
OKL4 microkernel
        ↓
Qualcomm Quartz / REX environment
        ↓
AMSS modem firmware
```

Shadow-MSM initially reuses the factory PBL download mode:

```text
PBL download mode
        ↓
Upload custom payload to RAM
        ↓
Execute at 0x00800000
        ↓
Custom monitor or bootloader
        ↓
Linux kernel
```

This allows development without modifying NAND.

A future standalone boot path may be:

```text
Boot ROM
        ↓
QCSBL
        ↓
OEMSBL
        ↓
Shadow-MSM bootloader in the AMSS partition
        ↓
Linux kernel and DTB from microSD
        ↓
Linux root filesystem
```

---

## Current progress

### Firmware recovery

The exact Vodafone K3765-Z firmware updater was recovered and statically extracted.

Recovered components include:

```text
amss.mbn
amsshd.mbn
armprg.bin
efs.mbn
oemsbl.mbn
oemsblhd.mbn
qcsbl.mbn
qcsblhd_cfgdata.mbn
partition.mbn
nandprgcombined.mbn
nandprghd.mbn
```

The Qualcomm EFS image was also parsed and reconstructed into a normal directory tree.

### NAND identification

The OEM programmer identifies the NAND geometry as:

```text
1024 blocks
64 pages per block
2048 data bytes per page
64 OOB bytes per page
```

Usable NAND size:

```text
1024 × 64 × 2048 = 134,217,728 bytes
                   = 128 MiB
```

Raw size including OOB:

```text
138,412,032 bytes
```

### Legacy downloader access

The modem exposes an old pre-Sahara Qualcomm downloader rather than modern Firehose.

Confirmed protocol properties:

```text
Transport:       USB serial / COM port
Baud rate:       115200
Format:          8N1
Framing:         Qualcomm HDLC
RAM write cmd:   0x0F
Execute cmd:     0x05
Load address:    0x00800000
Positive ACK:    0x02
```

A 16-byte RAM-write probe was acknowledged successfully.

### OEM programmer execution

The exact factory `armprg.bin` can be:

1. uploaded completely into RAM;
2. executed at `0x00800000`;
3. observed reinitializing the USB interface.

No NAND erase or program operation is required.

### Arbitrary code execution

Custom raw ARM payloads have been uploaded and executed.

A one-instruction payload:

```asm
1:
    b 1b
```

runs for several seconds before the hardware watchdog resets the SoC.

This strongly confirms:

```text
Arbitrary RAM write     ✅
Arbitrary ARM execution ✅
Automatic recovery      ✅
NAND untouched          ✅
```

### Watchdog work

The next major bring-up task is locating the exact MSM6290 watchdog service or disable sequence.

Current evidence suggests custom payloads execute successfully but reset after a consistent watchdog timeout.

### RGB LED

The board includes a multicolor status LED.

Known stock behavior includes:

* green when registered to a cellular network;
* other colors during startup, searching, and activity.

RGB control is being reverse engineered for use as an early boot debugging mechanism.

Proposed boot indicators:

```text
Red      bootloader entered
Yellow   RAM and hardware setup complete
Blue     kernel loaded
Green    jumping to Linux
Blink N  error code N
```

---

## Linux bring-up strategy

The first Linux boot will happen entirely from RAM.

Development sequence:

```text
Host PC
  → uploads Shadow-MSM stage-1 loader
  → uploads zImage
  → uploads DTB
  → loader configures CPU state
  → loader jumps into Linux
```

The first kernel will include:

* ARM926EJ-S support
* one CPU
* no modules
* built-in BusyBox initramfs
* Device Tree
* early debug output
* minimal timer support
* minimal interrupt-controller support
* watchdog handling
* no NAND dependency
* no microSD dependency
* no networking
* no framebuffer
* no sound

Initial success target:

```text
Booting Linux on physical CPU 0x0
CPU: ARM926EJ-S
Linux version ...
Run /init as init process
/ #
```

---

## Required MSM6290 platform support

Linux already supports the ARM926 CPU architecture, but MSM6290-specific peripherals are undocumented.

Expected new components include:

```text
arch/arm/mach-msm6290/
drivers/irqchip/irq-msm6290.c
drivers/clocksource/timer-msm6290.c
drivers/watchdog/msm6290_wdt.c
drivers/tty/serial/msm6290_uart.c
arch/arm/boot/dts/qcom/msm6290.dtsi
arch/arm/boot/dts/qcom/msm6290-zte-k3765-z.dts
```

Later drivers may include:

```text
drivers/mmc/host/
drivers/mtd/nand/raw/
drivers/usb/gadget/
drivers/leds/
drivers/gpio/
```

---

## Building a minimal userspace

Buildroot is recommended for the initial root filesystem.

Suggested target:

```text
Architecture:          ARM little-endian
CPU variant:           ARM926T / ARM926EJ-S
ABI:                   EABI
Floating point:        soft-float
C library:             musl
Init:                  BusyBox
Filesystem image:      cpio
```

Example dependencies on Ubuntu or WSL:

```bash
sudo apt update

sudo apt install -y \
    git build-essential \
    gcc-arm-linux-gnueabi \
    binutils-arm-linux-gnueabi \
    bc bison flex \
    libssl-dev libelf-dev \
    libncurses-dev \
    device-tree-compiler \
    cpio rsync python3
```

Clone Buildroot:

```bash
git clone --depth=1 https://gitlab.com/buildroot.org/buildroot.git
cd buildroot
make menuconfig
make -j"$(nproc)"
```

Expected root filesystem:

```text
output/images/rootfs.cpio
```

---

## Building the kernel

A stable Linux branch such as Linux 6.6 is a reasonable starting point.

```bash
git clone --depth=1 \
    --branch linux-6.6.y \
    https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git \
    linux-msm6290

cd linux-msm6290

make ARCH=arm \
    CROSS_COMPILE=arm-linux-gnueabi- \
    multi_v5_defconfig
```

The generic ARMv5 configuration is only a starting point. MSM6290 platform code must be added before the kernel can boot normally.

Build command:

```bash
make -j"$(nproc)" \
    ARCH=arm \
    CROSS_COMPILE=arm-linux-gnueabi- \
    zImage dtbs
```

Expected outputs:

```text
arch/arm/boot/zImage
arch/arm/boot/dts/qcom/msm6290-zte-k3765-z.dtb
```

---

## Suggested repository layout

```text
Shadow-MSM/
├── README.md
├── LICENSE
├── docs/
│   ├── hardware.md
│   ├── boot-chain.md
│   ├── downloader-protocol.md
│   ├── memory-map.md
│   ├── nand-layout.md
│   └── linux-bringup.md
├── host/
│   ├── pbl-uploader/
│   ├── monitor-client/
│   └── image-tools/
├── loader/
│   ├── stage0/
│   ├── stage1/
│   ├── linker/
│   └── include/
├── payloads/
│   ├── hold/
│   ├── watchdog/
│   ├── led-test/
│   └── ram-test/
├── linux/
│   ├── patches/
│   ├── configs/
│   └── dts/
├── buildroot/
│   ├── configs/
│   └── overlays/
├── tools/
│   ├── mbn/
│   ├── efs/
│   └── firmware/
└── captures/
    └── README.md
```

Proprietary firmware should not be committed to the public repository.

Use hashes and extraction instructions instead.

---

## Recovery and safety

This project involves undocumented bootloaders, raw flash access, and custom code execution.

### Current safest development method

Use only the factory RAM downloader:

```text
Enter download mode
→ upload payload to RAM
→ execute payload
→ power-cycle to recover
```

This does not require modifying NAND.

### Do not write NAND casually

Do not run any NAND erase or program operation unless all of the following are available:

* complete NAND backup;
* partition-level backups;
* stock firmware package;
* working OEM programmer;
* verified recovery procedure;
* confirmed partition boundaries;
* stable power;
* known-good image format.

Avoid commands or tools that perform:

```text
erase
program
write
flash
restore
download firmware
```

The Qualcomm boot partitions are especially sensitive:

```text
MIBIB
QCSBL
OEMSBL
```

Corrupting these may prevent normal USB recovery.

Experimental writes should initially be restricted to a recoverable application partition such as AMSS, and only after the raw NAND layout has been verified.

---

## Firmware policy

Shadow-MSM does not distribute proprietary Qualcomm, ZTE, Vodafone, or carrier firmware.

The repository may contain:

* original reverse-engineered code;
* protocol documentation;
* extraction scripts;
* patch files;
* hashes;
* open-source bootloader and kernel code;
* user-created Device Trees;
* hardware notes.

Users must obtain legally permitted firmware for their own hardware.

---

## Legal and ethical use

Shadow-MSM is intended for:

* research;
* preservation;
* interoperability;
* owner-controlled hardware modification;
* embedded Linux education;
* reverse engineering of personally owned devices.

Do not use this project to:

* bypass carrier billing;
* clone device identities;
* alter IMEI values;
* interfere with cellular networks;
* access devices without authorization;
* distribute proprietary firmware illegally.

Cellular transmission must continue to comply with local radio and telecommunications laws.

---

## Contributing

Contributions are welcome, especially in these areas:

* MSM6290 register identification
* watchdog reverse engineering
* timer and interrupt-controller analysis
* UART and USB research
* PMIC and LED control
* microSD interface tracing
* NAND partition analysis
* ARM926 Linux bring-up
* Device Tree development
* bootloader development
* documentation of related MSM6246, MSM6275, MSM6280, and MSM6290 devices

Useful contribution material includes:

* annotated disassembly;
* hardware photographs;
* verified register traces;
* USB captures;
* non-destructive diagnostic results;
* logic-analyzer captures;
* reproducible build instructions.

Clearly mark all guessed or unverified information.

---

## Project status

Shadow-MSM is highly experimental.

| Area                            | Status      |
| ------------------------------- | ----------- |
| Exact firmware recovered        | Working     |
| Firmware resource extraction    | Working     |
| Qualcomm EFS extraction         | Working     |
| NAND geometry identified        | Working     |
| Download mode access            | Working     |
| Legacy HDLC framing             | Working     |
| RAM upload                      | Working     |
| OEM ARMPRG execution            | Working     |
| Arbitrary ARM payload execution | Working     |
| Watchdog control                | In progress |
| RGB LED control                 | In progress |
| Custom monitor protocol         | In progress |
| Stage-1 bootloader              | In progress |
| RAM detection                   | Planned     |
| UART console                    | Planned     |
| Linux decompressor entry        | Planned     |
| Linux timer and IRQ support     | Planned     |
| BusyBox shell                   | Planned     |
| microSD support                 | Planned     |
| NAND Linux support              | Planned     |
| Automatic standalone boot       | Planned     |

---

## Why “Shadow-MSM”?

The Qualcomm MSM6290 platform is mostly undocumented, hidden beneath proprietary bootloaders and modem firmware.

Shadow-MSM is an attempt to reconstruct enough of that hidden platform to run open software on it.

The hardware was always a computer.

We are simply giving it a bootloader.

```
