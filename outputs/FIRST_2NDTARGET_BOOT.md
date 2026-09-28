Distribution manifest: PASS (50 files, SHA-256 0f968014f3d431babe7fe54e4b1833405384a768cd51401bc25bddc0e29d7055)
Verifying the exact RAM-only payload set before device access
  PASS armprg_stage0_monitor.bin: 105,928 bytes, SHA-256 588e897f46a3d7dfe4f5f989bcc85ab3b4604b4f7ccacd5d802b53be226f4f52, CRC32 0x75F82125
  PASS Image-k3765-probe: 5,536,428 bytes, SHA-256 c4fe5d5073e565e1083adc21074719d5a1db02ce04fb979e5c46610ced3915e0, CRC32 0xAF5F11A0
  PASS k3765_bl1_linux_image.bin: 5,933 bytes, SHA-256 bfd98420d2ed21609e6c3502bf4f6fe584cbb0d33e75467796b117986cf9a6de, CRC32 0xE535AB77
  PASS k3765-z-probe.dtb: 883 bytes, SHA-256 1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e, CRC32 0xC511699F
  PASS Linux runtime end 0x0076DFE8; 598,040 bytes below monitor

Shadow-MSM safety boundary
  Target writes: volatile SDRAM only
  NAND/CEFS/partition operations: not implemented
  Recovery: power-cycle to return to stock firmware
Session logs: C:\Users\hy\AppData\Local\Shadow-MSM\logs
Shadow-MSM diagnostic download-mode switch
Host time: 2026-09-28T16:48:51
Port: COM25
Command: DIAG_DLOAD_F (0x3A)
TX: 7e 3a a1 6e 7e
Persistence: no NAND command
RX before re-enumeration: 3a a1 6e 7e
Opened staged runtime directory: C:\Users\hy\AppData\Local\Shadow-MSM\runtime\0f968014f3d431ba-20260928_164850-29236
Downloader detected: COM25
K3765-Z bounded RAM bundle load
Host time: 2026-09-28T16:48:55
No NAND erase/program/write operation is implemented.

0x00800000  C:\Users\hy\AppData\Local\Shadow-MSM\runtime\0f968014f3d431ba-20260928_164850-29236\armprg_stage0_monitor.bin
  size   : 105,928
  SHA-256: 588e897f46a3d7dfe4f5f989bcc85ab3b4604b4f7ccacd5d802b53be226f4f52
  CRC32  : 75F82125

0x00208000  C:\Users\hy\AppData\Local\Shadow-MSM\runtime\0f968014f3d431ba-20260928_164850-29236\Image-k3765-probe
  size   : 5,536,428
  SHA-256: c4fe5d5073e565e1083adc21074719d5a1db02ce04fb979e5c46610ced3915e0
  CRC32  : AF5F11A0

0x01000000  C:\Users\hy\AppData\Local\Shadow-MSM\runtime\0f968014f3d431ba-20260928_164850-29236\k3765_bl1_linux_image.bin
  size   : 5,933
  SHA-256: bfd98420d2ed21609e6c3502bf4f6fe584cbb0d33e75467796b117986cf9a6de
  CRC32  : E535AB77

0x01F80000  C:\Users\hy\AppData\Local\Shadow-MSM\runtime\0f968014f3d431ba-20260928_164850-29236\k3765-z-probe.dtb
  size   : 883
  SHA-256: 1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e
  CRC32  : C511699F

armprg_stage0_monitor.bin: 105,928/105,928 (100.00%)
Image-k3765-probe: 5,536,428/5,536,428 (100.00%)
k3765_bl1_linux_image.bin: 5,933/5,933 (100.00%)
k3765-z-probe.dtb: 883/883 (100.00%)
Executing stage-0 at 0x00800000...
GO response: 02
K3765-Z RAM stage-0 boot log
Host time: 2026-09-28T16:49:24
Transport: legacy Qualcomm HDLC over USB serial
Persistence: RAM only; no NAND operation

Monitor: K3765-S0-V1
MIDR : 0x41069265
CTR  : 0x1D192192
TCMTR: 0x00000000
CPSR : 0x600000D3
SCTLR: 0x00051078
TTBR : 0x0006C000
DACR : 0xFFFFFFF5
DFSR : 0x0000000C
IFSR : 0x000000D7
FAR  : 0xFFFF1060
SP   : 0x0081DD74

CPU   : ARM ARM926EJ-S, architecture field 6, variant 0, revision 5
CPSR  : mode=SVC, ARM-state=ARM, IRQ=masked, FIQ=masked
SCTLR : MMU=off, alignment=off, D-cache=off, write-buffer=on, I-cache=on, high-vectors=off
Board : ZTE/Vodafone K3765-Z
SoC   : Qualcomm MSM6290 (MSM6246-family downloader)
PMIC  : Qualcomm PM6658-family; RGB map R=MPP1 G=LED0 B=LED1
NAND  : HYNIX_HSACS0PL0MCR OEM profile, 128 MiB + OOB
RAM   : firmware physical span reaches 0x01FAC000; stage-0 safe window is 0x01000000..0x01FFFFFF
OEMSBL: 00.02.00.04 / KPVDFP673A1M256
CRC32 bl1 at 0x01000000: 0xE535AB77
PASS: bl1 target RAM CRC is 0xE535AB77
CRC32 dtb at 0x01F80000: 0xC511699F
PASS: dtb target RAM CRC is 0xC511699F

Preflight complete. Booting Linux and opening shadow-msm#
Type normally. Ctrl+C signals Linux; Ctrl+] detaches the host.
K3765-Z BL1 0.4 direct Linux Image boot
Mode  : validated non-returning Image handoff
Flash : untouched; RAM execution only
Input images
Image size     : 0x00547AAC
DTB size       : 0x00000373
Host marker     : 0x494D4731
Image fingerprints and DTB validation
Image sparse fingerprints: PASS
DTB magic      : 0xEDFE0DD0
DTB total size : 0x00000373
Linux entry state
CPSR            : 0x200000D3
SCTLR           : 0x00051078
PC              : 0x00208000
r0              : 0x00000000
r1              : 0xFFFFFFFF
r2              : 0x01F80000
Validation PASS
LED checkpoint  : blue
JUMPING DIRECTLY TO DECOMPRESSED LINUX IMAGE
Shadow-MSM: entered decompressed Linux head.S
Shadow-MSM: ARM926 processor lookup passed
Shadow-MSM: initial page tables created
Shadow-MSM: calling ARM926 processor setup
Shadow-MSM: entered ARM926 setup
Shadow-MSM: ARM926 cache invalidate returned
Shadow-MSM: ARM926 TLB invalidate returned
Shadow-MSM: ARM926 control word ready
Shadow-MSM: ARM926 setup returned; enabling MMU next
Shadow-MSM: MMU enabled; identity execution continues
Shadow-MSM: entered __mmap_switched at the kernel virtual address
Shadow-MSM: __mmap_switched cleared BSS
Shadow-MSM: branching to start_kernel
Shadow-MSM: entered setup_arch
Shadow-MSM: setup_processor completed
Shadow-MSM: device-tree machine selected
Shadow-MSM: early_mm_init completed
Shadow-MSM: ARM memblock initialization completed
Shadow-MSM: entering paging_init
Shadow-MSM: low bootstrap identity mappings retained
Shadow-MSM: map_lowmem completed
Shadow-MSM: permanent kernel mappings completed
Shadow-MSM: DMA contiguous remap completed
Shadow-MSM: early fixmap shutdown completed
Shadow-MSM: vector pages allocated
Shadow-MSM: early trap vectors initialized
Shadow-MSM: temporary vmalloc mappings cleared
Shadow-MSM: static device mappings completed
Shadow-MSM: PCI I/O reservation completed
Shadow-MSM: device-map TLB flush completed
Shadow-MSM: device-map cache flush completed
Shadow-MSM: asynchronous aborts enabled
Shadow-MSM: ARM device mappings completed
Shadow-MSM: permanent kmap tables completed
Shadow-MSM: TCM initialization completed
Shadow-MSM: zero page allocated
Shadow-MSM: bootmem_init completed
Shadow-MSM: leaving paging_init
Shadow-MSM: paging_init completed
Shadow-MSM: MSM6290 timer IRQ route registered
Shadow-MSM: MSM6290 32.768-kHz clockevent registered
[    0.000000] Booting Linux on physical CPU 0x0
[    0.000000] Linux version 6.1.0-shadow-msm-probe+ (root@DESKTOP-9QJL6BL) (arm-linux-gnueabi-gcc (Debian 14.2.0-19) 14.2.0, GNU ld (GNU Binutils for Debian) 2.44) #3 Mon Aug 10 03:42:09 EEST 2026
[    0.000000] CPU: ARM926EJ-S [41069265] revision 5 (ARMv5TEJ), cr=0005317f
[    0.000000] CPU: VIVT data cache, VIVT instruction cache
[    0.000000] OF: fdt: Machine model: ZTE Vodafone K3765-Z (MSM6290)
[    0.000000] Memory policy: Data cache writethrough
[    0.000000] Zone ranges:
[    0.000000]   Normal   [mem 0x0000000000200000-0x0000000001ffffff]
[    0.000000] Movable zone start for each node
[    0.000000] Early memory node ranges
[    0.000000]   node   0: [mem 0x0000000000200000-0x0000000001ffffff]
[    0.000000] Initmem setup node 0 [mem 0x0000000000200000-0x0000000001ffffff]
[    0.000000] On node 0, zone Normal: 512 pages in unavailable ranges
[    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 7620
[    0.000000] Kernel command line: console=ttySHM0,115200 loglevel=7 lpj=1000000
[    0.000000] Dentry cache hash table entries: 4096 (order: 2, 16384 bytes, linear)
[    0.000000] Inode-cache hash table entries: 2048 (order: 1, 8192 bytes, linear)
[    0.000000] mem auto-init: stack:all(zero), heap alloc:off, heap free:off
[    0.000000] Memory: 23748K/30720K available (2631K kernel code, 190K rwdata, 604K rodata, 1872K init, 121K bss, 6972K reserved, 0K cma-reserved)
[    0.000000] SLUB: HWalign=32, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
[    0.000000] NR_IRQS: 16, nr_irqs: 16, preallocated irqs: 16
[    0.000000] clocksource: shadow-msm6290-counter: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 58327039986419 ns
[    0.000000] sched_clock: 32 bits at 33kHz, resolution 30517ns, wraps every 65535999984741ns
[    0.002197] Calibrating delay loop (skipped) preset value.. 200.00 BogoMIPS (lpj=1000000)
[    0.002441] pid_max: default: 32768 minimum: 301
[    0.004516] Mount-cache hash table entries: 1024 (order: 0, 4096 bytes, linear)
[    0.004760] Mountpoint-cache hash table entries: 1024 (order: 0, 4096 bytes, linear)
[    0.011749] CPU: Testing write buffer coherency: ok
[    0.022216] Setting up static identity map for 0x208400 - 0x2084a0
[    0.027770] devtmpfs: initialized
[    0.037353] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 19112604462750000 ns
[    0.037658] futex hash table entries: 256 (order: -1, 3072 bytes, linear)
[    0.038543] pinctrl core: initialized pinctrl subsystem
[    0.049530] DMA: preallocated 256 KiB pool for atomic coherent allocations
[    0.058837] thermal_sys: Registered thermal governor 'step_wise'
[    0.059204] cpuidle: using governor ladder
[    0.095428] pps_core: LinuxPPS API ver. 1 registered
[    0.095550] pps_core: Software ver. 5.3.6 - Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it>
[    0.100891] clocksource: Switched to clocksource shadow-msm6290-counter
[    0.128417] Initialise system trusted keyrings
[    0.142669] workingset: timestamp_bits=30 max_order=13 bucket_order=0
[    0.226470] Key type asymmetric registered
[    0.226623] Asymmetric key parser 'x509' registered
[    0.340545] Serial: 8250/16550 driver, 6 ports, IRQ sharing disabled
[    0.494842] printk: console [ttySHM0] enabled
Shadow-MSM: ttySHM0 Linux TTY console registered
Shadow-MSM: /dev/shadowtrace process bridge registered
Shadow-MSM: RAM-only host input bridge registered
Shadow-MSM: hardware ZTE K3765-Z / Qualcomm MSM6290
Shadow-MSM: CPU MIDR 0x41069265
Shadow-MSM: physical RAM window 0x00000000-0x01FFFFFF
[    0.504608] shadow-sdcc: registering polling PL180 host
[    0.509399] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[    0.550445] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    0.579498] shadow-sdcc: mmc host mmc0 ready at 0x50000000, polling mode
[    0.583404] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.585937] shadow-sdcc: CMD52 arg=00000c00 failed -110 status=00400004
[    0.587249] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.589874] shadow-sdcc: CMD52 arg=80000c08 failed -110 status=00400004
[    0.591217] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    0.595092] Loading compiled-in X.509 certificates
[    0.600433] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.602935] shadow-sdcc: CMD0 arg=00000000 ok status=00400080 resp=00000000
[    0.619232] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    0.638183] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.640747] shadow-sdcc: CMD8 arg=000001aa failed -110 status=00400004
[    0.642211] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.644653] shadow-sdcc: CMD5 arg=00000000 failed -110 status=00400004
[    0.645935] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.648345] shadow-sdcc: CMD5 arg=00000000 failed -110 status=00400004
[    0.649627] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.652038] shadow-sdcc: CMD5 arg=00000000 failed -110 status=00400004
[    0.653411] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.655822] shadow-sdcc: CMD5 arg=00000000 failed -110 status=00400004
[    0.657135] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.659515] shadow-sdcc: CMD55 arg=00000000 failed -110 status=00400004
[    0.660827] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.663330] shadow-sdcc: CMD55 arg=00000000 failed -110 status=00400004
[    0.664672] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.667083] shadow-sdcc: CMD55 arg=00000000 failed -110 status=00400004
[    0.668365] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    0.670745] shadow-sdcc: CMD55 arg=00000000 failed -110 status=00400004
[    0.672058] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[    0.674285] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    0.676666] shadow-sdcc: CMD1 arg=00000000 failed -110 status=00400004
[    0.677947] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
00002
[    1.820190] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    1.843780] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.846313] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[    1.847686] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.850280] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[    1.851684] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    1.877410] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.879882] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[    1.894134] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    1.908508] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.911010] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[    1.912506] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.914947] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[    1.916290]  shadow-msm-sdcc0: no support for card's volts
[    1.917419] mmc0: error -22 whilst initialising SDIO card
[    1.918579] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.920989] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    1.922332] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.924865] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    1.926208] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.928588] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    1.929931] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    1.932312] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    1.933776] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[    1.935913] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    1.938293] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[    1.977416] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    1.979919] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.006164] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.008666] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.035308] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.037811] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.077453] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.079956] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.155151] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.157684] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.232025] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.234527] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.313690] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.316192] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.391723] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.394195] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.478332] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.480865] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.558105] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.560607] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.635864] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.638519] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.717956] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.720611] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.798645] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.801300] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.876434] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.878906] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.963378] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    2.965881] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    2.967224] mmc0: Card stuck being busy! __mmc_poll_for_busy
[    2.968383] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[    4.041015] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[    4.078002] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    4.105468] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.108123] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[    4.109527] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.111968] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[    4.113311] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    4.140075] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.142547] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[    4.155273] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    4.169555] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.172058] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[    4.173400] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.175842] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[    4.177154]  shadow-msm-sdcc0: no support for card's volts
[    4.178283] mmc0: error -22 whilst initialising SDIO card
[    4.179595] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.182006] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    4.183349] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.185760] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    4.187072] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.189605] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    4.190948] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    4.193359] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    4.194702] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[    4.196807] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.199188] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[    4.236907] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.239410] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.254150] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.256652] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.281829] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.284332] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.325347] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.327880] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.407897] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.410400] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.486175] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.488708] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.566650] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.569152] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.643829] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.646362] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.714141] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.716644] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.785339] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.787841] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.865386] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.867858] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    4.937286] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    4.939788] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    5.024749] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    5.027252] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    5.097625] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    5.100128] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    5.177551] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    5.180053] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    5.250396] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    5.252899] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    5.254272] mmc0: Card stuck being busy! __mmc_poll_for_busy
[    5.255401] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[    6.298522] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[    6.333221] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    6.356292] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.358795] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[    6.360168] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.362731] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[    6.364105] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    6.390655] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.393280] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[    6.406402] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    6.421386] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.424041] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[    6.425415] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.427856] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[    6.429199]  shadow-msm-sdcc0: no support for card's volts
[    6.430328] mmc0: error -22 whilst initialising SDIO card
[    6.431457] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.433990] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    6.435363] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.437744] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    6.439117] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.441497] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    6.442840] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    6.445343] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    6.446746] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[    6.448883] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.451232] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[    6.506256] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.508758] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.530914] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.533416] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.565155] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.567779] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.609497] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.612030] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.692016] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.694549] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.782135] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.784606] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.862792] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.865264] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    6.941589] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    6.944091] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.011566] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.014068] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.084533] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.087036] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.161376] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.163848] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.237701] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.240203] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.317413] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.319946] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.403747] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.406249] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.479736] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    7.482238] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    7.483734] mmc0: Card stuck being busy! __mmc_poll_for_busy
[    7.484924] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[    8.549072] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[    8.585540] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    8.599273] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.601806] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[    8.603149] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.605560] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[    8.606903] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    8.621490] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.623992] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[    8.637207] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[    8.651519] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.654022] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[    8.655395] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.657806] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[    8.659118]  shadow-msm-sdcc0: no support for card's volts
[    8.660430] mmc0: error -22 whilst initialising SDIO card
[    8.661590] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.664001] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    8.665313] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.667724] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    8.669067] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.671569] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    8.672943] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[    8.675354] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[    8.676696] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[    8.678802] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.681182] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[    8.719085] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.721588] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    8.734466] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.736968] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    8.771942] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.774597] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    8.821807] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.824310] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    8.905517] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.908172] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    8.984619] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    8.987152] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.069519] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.072021] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.147430] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.150085] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.230621] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.233154] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.302276] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.304779] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.378112] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.380615] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.460937] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.463592] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.540618] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.543121] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.626281] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.628784] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.696594] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.699066] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.772521] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[    9.775024] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[    9.776519] mmc0: Card stuck being busy! __mmc_poll_for_busy
[    9.777709] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   10.812469] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   10.846466] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   10.861175] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.863677] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   10.865051] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.867462] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   10.868804] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   10.888854] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.891571] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   10.905212] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   10.920196] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.922882] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   10.924285] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.926696] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   10.928009]  shadow-msm-sdcc0: no support for card's volts
[   10.929168] mmc0: error -22 whilst initialising SDIO card
[   10.930328] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.932861] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   10.934204] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.936614] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   10.937957] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.940368] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   10.941680] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   10.944183] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   10.945556] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   10.947692] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   10.950103] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   10.994995] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   10.997497] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.023437] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.026092] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.053649] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.056304] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.105468] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.108123] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.180206] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.182708] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.248901] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.251434] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.329895] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.332397] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.407073] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.409820] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.483337] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.485839] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.563537] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.566040] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.648742] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.651397] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.722229] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.724761] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.797851] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.800384] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.876007] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.878540] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   11.954711] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   11.957244] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   12.029785] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   12.032318] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   12.033843] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   12.035034] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   13.074951] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   13.112152] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   13.128723] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.131225] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   13.132598] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.135040] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   13.136413] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   13.152252] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.154724] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   13.169952] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   13.179565] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.182098] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   13.183441] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.185882] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   13.187225]  shadow-msm-sdcc0: no support for card's volts
[   13.188385] mmc0: error -22 whilst initialising SDIO card
[   13.189666] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.192108] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   13.193481] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.195892] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   13.197235] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.199737] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   13.201110] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   13.203521] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   13.204895] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   13.207000] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.209411] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   13.244293] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.246795] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.268096] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.270599] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.294006] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.296508] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.337646] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.340148] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.413452] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.415985] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.484283] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.486816] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
Shadow-MSM: ttySHM0 activated
[   13.552795] Freeing unused kernel image (initmem) memory: 1872K
[   13.554260] Kernel memory protection not selected by kernel config.
Shadow-MSM: executing built-in /init
[   13.556274] Run /init as init process
Shadow-MSM: kernel_execve entered
[   13.559143] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.561584] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
Shadow-MSM: kernel_execve arguments staged
Shadow-MSM: bprm_execve entered
Shadow-MSM: bprm_execve searching binary handler
Shadow-MSM: load_elf_binary entered
Shadow-MSM: ELF program headers loaded
Shadow-MSM: ELF calling begin_new_exec
Shadow-MSM: begin_new_exec entered
Shadow-MSM: begin_new_exec switching mm
Shadow-MSM: exec_mmap entered
Shadow-MSM: exec_mmap activating PID 1 mm
Shadow-MSM: exec_mmap activated PID 1 mm
Shadow-MSM: begin_new_exec mm switched
Shadow-MSM: ELF begin_new_exec returned
Shadow-MSM: ELF setup_new_exec completed
Shadow-MSM: ELF argument pages installed
Shadow-MSM: ELF load segments mapped
Shadow-MSM: ELF userspace tables created
Shadow-MSM: ELF starting PID 1 thread
Shadow-MSM: returning to PID 1 userspace
Shadow-MSM: PID 1 entered its first syscall
Shadow-MSM: entered freestanding PID 1 userspace
Shadow-MSM: controlling ttySHM0 acquired
Shadow-MSM: hardware timer IRQ observed
Shadow-MSM: sysname  Linux
Shadow-MSM: release  6.1.0-shadow-msm-probe+
Shadow-MSM: machine  armv5tejl
Shadow-MSM: attaching BusyBox to /dev/ttySHM0
Shadow-MSM: starting static BusyBox ARMv5 shell
Shadow-MSM: bprm_execve entered
Shadow-MSM: bprm_execve searching binary handler
Shadow-MSM: load_elf_binary entered
Shadow-MSM: ELF program headers loaded
Shadow-MSM: ELF calling begin_new_exec
Shadow-MSM: begin_new_exec entered
Shadow-MSM: begin_new_exec switching mm
Shadow-MSM: exec_mmap entered
Shadow-MSM: exec_mmap activating PID 1 mm
Shadow-MSM: exec_mmap activated PID 1 mm
Shadow-MSM: begin_new_exec mm switched
Shadow-MSM: ELF begin_new_exec returned
Shadow-MSM: ELF setup_new_exec completed
Shadow-MSM: ELF argument pages installed
Shadow-MSM: ELF load segments mapped
Shadow-MSM: ELF userspace tables created
Shadow-MSM: ELF starting PID 1 thread
[   13.636291] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.638885] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
shadow-msm# [   13.706512] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.709106] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.777099] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.779724] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.847320] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.849914] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.917907] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.920532] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   13.988128] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   13.990722] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   14.058715] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   14.061309] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   14.128936] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   14.131530] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   14.199523] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   14.202117] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   14.269714] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   14.272338] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   14.273834] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   14.275146] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
00002

shadow-msm# [   15.355957] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   15.376098] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.378723] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   15.380218] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.383209] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   15.384735] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003

shadow-msm# [   15.401519] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.404113] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   15.407348] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   15.417724] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.420318] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   15.421874] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.424438] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   15.425933]  shadow-msm-sdcc0: no support for card's volts
[   15.427429] mmc0: error -22 whilst initialising SDIO card
[   15.428741] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.431335] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   15.432891] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.435455] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   15.436981] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.439819] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   15.441314] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   15.443908] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   15.445434] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   15.447967] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.450531] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   15.458068] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.460662] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.478240] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.480865] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.508575] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.511169] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.548797] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.551391] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.619018] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.621582] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.689605] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.692230] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.759826] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.762420] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.830413] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.833007] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.900604] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.903228] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   15.971221] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   15.973815] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000

shadow-msm# [   16.041442] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.044006] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   16.112030] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.114654] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000

shadow-msm# [   16.182250] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.184814] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   16.252838] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.255462] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000

shadow-msm# [   16.323059] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.325653] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   16.393646] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.396240] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000

shadow-msm# [   16.463867] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.466461] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   16.534454] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   16.537048] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   16.538543] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   16.539855] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000

shadow-msm#
shadow-msm#
shadow-msm# ^C

shadow-msm# 00002
[   17.610412] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   17.630554] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.633178] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   17.634704] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.637329] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   17.638854] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   17.651641] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.654205] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   17.661437] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   17.671813] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.674438] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   17.675964] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.678558] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   17.680053]  shadow-msm-sdcc0: no support for card's volts
[   17.681549] mmc0: error -22 whilst initialising SDIO card
[   17.682861] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.685455] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   17.686950] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.689575] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   17.691070] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.693939] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   17.695465] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   17.698028] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   17.699554] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   17.702026] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.704620] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   17.712097] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.714691] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   17.732269] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.734863] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   17.762664] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.765258] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   17.802886] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.805450] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   17.873046] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.875671] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   17.943664] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   17.946289] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.013854] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.016448] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.084472] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.087066] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.154693] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.157287] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
^C

shadow-msm# [   18.225280] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.227905] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.295501] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.298065] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.366088] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.368713] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
^C

shadow-msm# [   18.436309] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.438903] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.506896] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.509521] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
^C

shadow-msm# [   18.577117] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.579711] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.647705] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.650299] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.717926] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.720489] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
c[   18.788513] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   18.791137] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   18.792633] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   18.793945] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
che[   19.834106] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
l[   19.864471] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   19.884582] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.887207] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   19.888732] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.891326] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   19.892852] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   19.905639] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.908233] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   19.915466] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   19.925842] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.928436] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   19.929962] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.932556] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   19.934051]  shadow-msm-sdcc0: no support for card's volts
[   19.935516] mmc0: error -22 whilst initialising SDIO card
[   19.936828] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.939422] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   19.940948] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.943511] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   19.945037] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.947875] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   19.949432] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   19.951995] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   19.953521] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   19.956024] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   19.958618] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   19.966125] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   19.968719] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   19.986267] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   19.988861] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.016632] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.019256] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
p[   20.056884] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.059478] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.127075] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.129638] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.197692] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.200286] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000

sh: cchelp: not found
shadow-msm# [   20.267883] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.270477] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.338470] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.341094] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.408691] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.411254] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.479278] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.481872] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.549499] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.552093] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.620086] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.622680] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.690307] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.692901] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.760894] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.763519] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.831115] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.833679] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.901702] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.904296] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   20.971923] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   20.974517] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   21.042633] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   21.045227] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   21.046752] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   21.048065] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   22.088104] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   22.118469] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   22.138610] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.141235] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   22.142761] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.145385] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   22.146881] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   22.159667] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.162261] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   22.169494] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   22.179870] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.182464] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   22.183990] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.186584] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   22.188079]  shadow-msm-sdcc0: no support for card's volts
[   22.189575] mmc0: error -22 whilst initialising SDIO card
[   22.190887] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.193481] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   22.194976] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.197570] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   22.199096] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.201934] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   22.203460] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   22.206054] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   22.207580] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   22.210144] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.212707] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   22.220153] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.222717] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.240264] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.242889] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.270660] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.273284] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.310913] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.313476] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.381103] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.383697] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.451690] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.454284] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.521911] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.524505] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.592498] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.595092] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.662750] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.665344] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.733306] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.735900] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.803527] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.806091] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.874114] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.876739] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   22.944305] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   22.946899] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.014953] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   23.017547] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.085144] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   23.087738] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.155731] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   23.158325] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.225952] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   23.228546] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.296539] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   23.299133] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   23.300659] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   23.301971] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   24.342132] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   24.372497] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   24.392639] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.395263] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   24.396789] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.399414] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   24.400909] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   24.413696] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.416290] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   24.423522] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   24.433898] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.436523] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   24.438049] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.440612] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   24.442108]  shadow-msm-sdcc0: no support for card's volts
[   24.443603] mmc0: error -22 whilst initialising SDIO card
[   24.444885] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.447479] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   24.449005] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.451599] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   24.453155] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.456024] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   24.457550] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   24.460113] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   24.461639] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   24.464111] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.466705] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   24.474212] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.476806] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.494354] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.496917] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.524749] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.527343] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.564971] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.567535] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.635162] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.637756] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.705749] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.708343] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.776123] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.778686] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.846557] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.849182] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.916778] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.919403] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   24.987365] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   24.989959] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.057586] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.060180] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.128173] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.130767] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.198394] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.200988] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.268981] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.271606] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.339202] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.341796] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.409820] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.412384] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.479980] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.482604] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.550598] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   25.553222] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   25.554718] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   25.556030] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   26.596191] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   26.626556] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   26.646697] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.649322] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   26.650848] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.653442] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   26.654998] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   26.667755] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.670349] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   26.677581] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   26.687957] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.690582] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   26.692108] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.694702] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   26.696197]  shadow-msm-sdcc0: no support for card's volts
[   26.697662] mmc0: error -22 whilst initialising SDIO card
[   26.698974] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.701568] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   26.703094] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.705688] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   26.707214] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.710083] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   26.711608] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   26.714202] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   26.715728] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   26.718231] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.720794] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   26.728302] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.730895] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   26.748443] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.751037] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   26.778808] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.781402] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   26.819030] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.821624] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   26.889251] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.891815] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   26.959838] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   26.962432] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.030029] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.032623] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.100646] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.103240] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.170867] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.173461] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.241455] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.244079] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.311676] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.314270] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.382293] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.384887] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.452484] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.455078] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.523071] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.525695] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.593292] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.595886] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.663879] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.666473] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.734100] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.736694] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.804687] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   27.807281] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   27.808776] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   27.810119] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   28.850280] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   28.880767] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   28.900756] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.903411] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   28.904937] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.907562] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   28.909057] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   28.921844] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.924438] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   28.931671] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   28.942047] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.944641] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   28.946166] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.948760] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   28.950225]  shadow-msm-sdcc0: no support for card's volts
[   28.951721] mmc0: error -22 whilst initialising SDIO card
[   28.953002] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.955596] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   28.957122] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.959716] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   28.961242] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.964080] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   28.965606] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   28.968200] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   28.969726] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   28.972229] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   28.974792] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   28.982299] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   28.984893] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.002441] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.005035] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.032806] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.035400] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.073028] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.075622] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.143249] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.145843] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.213836] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.216430] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.284057] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.286651] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.354644] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.357238] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.424865] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.427459] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.495452] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.498046] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.565673] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.568237] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.636260] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.638885] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.706481] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.709075] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.777069] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.779693] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.847320] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.849945] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.917877] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.920440] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   29.988098] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   29.990692] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   30.058685] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   30.061279] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   30.062774] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   30.064117] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   31.104278] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   31.134643] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   31.154754] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.157379] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   31.158905] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.161499] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   31.163024] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   31.175811] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.178375] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   31.185638] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   31.196014] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.198638] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   31.200195] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.202758] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   31.204254]  shadow-msm-sdcc0: no support for card's volts
[   31.205749] mmc0: error -22 whilst initialising SDIO card
[   31.207031] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.209655] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   31.211181] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.213745] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   31.215270] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.218109] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   31.219635] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   31.222198] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   31.223724] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   31.226196] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.228790] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   31.236297] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.238891] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.256439] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.259002] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.286804] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.289428] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.327026] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.329620] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.397216] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.399841] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.467834] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.470428] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.538055] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.540618] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.608673] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.611267] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.678863] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.681457] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.749450] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.752075] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.819671] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.822235] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.890258] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.892883] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   31.960632] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   31.963195] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.031097] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   32.033691] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.101287] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   32.103851] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.171874] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   32.174468] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.242095] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   32.244659] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.312683] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   32.315307] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   32.316802] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   32.318145] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   33.358276] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   33.388641] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   33.408752] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.411407] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   33.412902] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.415496] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   33.417022] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   33.429809] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.432373] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   33.439636] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   33.450012] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.452606] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   33.454132] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.456756] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   33.458251]  shadow-msm-sdcc0: no support for card's volts
[   33.459716] mmc0: error -22 whilst initialising SDIO card
[   33.461029] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.463653] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   33.465179] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.467742] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   33.469268] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.472106] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   33.473602] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   33.476196] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   33.477691] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   33.480194] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.482788] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   33.490295] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.492858] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.510406] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.513031] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.540802] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.543395] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.581024] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.583618] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.651245] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.653808] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.721832] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.724487] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.792053] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.794647] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.862670] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.865264] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   33.932861] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   33.935455] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.003448] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.006072] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.073669] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.076263] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.144256] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.146881] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.214477] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.217071] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.285095] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.287689] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.355285] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.357879] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.425872] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.428497] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.496093] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.498687] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.566680] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   34.569305] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   34.570800] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   34.572113] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   35.612274] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   35.642639] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   35.662750] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.665405] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   35.666931] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.669525] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   35.671051] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   35.683837] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.686431] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   35.693847] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   35.704040] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.706695] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   35.708221] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.710784] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   35.712310]  shadow-msm-sdcc0: no support for card's volts
[   35.713806] mmc0: error -22 whilst initialising SDIO card
[   35.715118] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.717712] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   35.719238] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.721832] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   35.723358] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.726226] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   35.727752] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   35.730346] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   35.731872] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   35.734405] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.736968] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   35.744476] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.747070] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   35.764617] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.767211] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   35.794982] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.797607] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   35.835235] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.837829] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   35.905426] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.908020] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   35.976013] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   35.978637] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.046234] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.048828] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.116821] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.119445] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.187042] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.189636] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.257629] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.260253] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.327850] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.330444] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.398437] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.401062] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.468658] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.471252] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.539245] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.541839] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.609466] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.612060] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.680084] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.682708] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.750274] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.752868] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.820861] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   36.823486] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   36.824981] mmc0: Card stuck being busy! __mmc_poll_for_busy
[   36.826324] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=0 regs=00000000/00000000
[   37.866455] shadow-sdcc: ios requested=0 actual=0 width=1bit mode=2 power=1 regs=00000000/00000002
[   37.896820] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   37.916961] shadow-sdcc: request CMD52 arg=00000c00 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.919586] shadow-sdcc: CMD52 arg=00000c00 ok status=02400040 resp=00000000
[   37.921112] shadow-sdcc: request CMD52 arg=80000c08 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.923706] shadow-sdcc: CMD52 arg=80000c08 ok status=02400040 resp=00000000
[   37.925262] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   37.938049] shadow-sdcc: request CMD0 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.940643] shadow-sdcc: CMD0 arg=00000000 ok status=02400080 resp=00000000
[   37.947875] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=2 power=2 regs=00009113/00000003
[   37.958251] shadow-sdcc: request CMD8 arg=000001aa data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.960906] shadow-sdcc: CMD8 arg=000001aa ok status=02400040 resp=00000000
[   37.962432] shadow-sdcc: request CMD5 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.965026] shadow-sdcc: CMD5 arg=00000000 ok status=02400040 resp=00000000
[   37.966522]  shadow-msm-sdcc0: no support for card's volts
[   37.968048] mmc0: error -22 whilst initialising SDIO card
[   37.969360] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.971923] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   37.973480] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.976074] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   37.977569] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.980438] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   37.981964] shadow-sdcc: request CMD55 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=2 power=2 regs=00009113/00000003
[   37.984558] shadow-sdcc: CMD55 arg=00000000 ok status=02400040 resp=00000000
[   37.986083] shadow-sdcc: ios requested=400000 actual=400000 width=1bit mode=1 power=2 regs=00009113/00000083
[   37.988586] shadow-sdcc: request CMD1 arg=00000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   37.991180] shadow-sdcc: CMD1 arg=00000000 ok status=02400040 resp=00000000
[   37.998687] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.001281] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.018829] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.021423] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.049194] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.051818] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.089416] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.092041] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.159637] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.162231] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.230224] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.232849] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.300445] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.303039] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.371032] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.373657] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.441253] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.443847] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.511840] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1bit mode=1 power=2 regs=00009113/00000083
[   38.514465] shadow-sdcc: CMD1 arg=40000000 ok status=02400040 resp=00000000
[   38.582061] shadow-sdcc: request CMD1 arg=40000000 data=none blocks=0 blksz=0 ios=400000Hz/1b

















