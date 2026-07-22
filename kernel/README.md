# K3765-Z Linux probe build

This directory builds the first deliberately limited Linux handoff probe for
the ZTE/Vodafone K3765-Z. It targets Linux v6.1 and the ARM926EJ-S CPU in the
MSM6290.

The resulting image is not expected to reach userspace yet. Its job is to
prove, with visible milestones, that:

1. BL1 enters the ARM zImage;
2. the decompressor runs;
3. execution reaches the decompressed kernel entry;
4. Linux recognizes the ARM926 processor;
5. Linux creates its initial page tables;
6. the ARM926 cache/TLB/control setup returns; and
7. execution reaches the MMU-enable boundary.
8. execution reaches the high virtual `__mmap_switched` path;
9. BSS initialization completes; and
10. execution branches into `start_kernel`.
11. early generic C initialization completes;
12. the device tree selects the K3765-Z machine; and
13. ARM memory discovery reaches the `paging_init` boundary.
14. the permanent page tables preserve the resident monitor mapping; and
15. `paging_init` returns to generic kernel startup.

The early trace patch borrows the initialized RAM-resident ARMPRG diagnostic
string routine only while the MMU is off. The device tree reserves
`0x00800000..0x008fffff` so the kernel image and allocator do not overwrite
that runtime during this experiment. Trace calls use a dedicated physical
stack at the top of that reservation. This is required because Linux
repurposes `r13` as the future virtual `__mmap_switched` address immediately
before calling the ARM926 processor setup function.

The DT deliberately exposes RAM from `0x00200000`, not the observed
`0x00100000`. Linux v6.1's ARM DT-assisted `AUTO_ZRELADDR` path rounds the
lowest memory address up to a 2 MiB boundary for phys/virt patching. Making
that alignment explicit gives a deterministic decompression target of
`0x00208000` and leaves the first MiB untouched.

## Reproducible build

The GitHub Actions workflow clones the official Linux `v6.1` tag, applies the
single patch in `patches/`, merges `k3765_probe.config` over
`multi_v5_defconfig`, builds with the Debian/Ubuntu
`arm-linux-gnueabi-` toolchain, compiles the probe DTB, and verifies all RAM
bounds and image headers.

Every change under `kernel/` triggers the same clean build; it can also be
started manually from the repository's Actions page.

To perform the same build on a Linux host:

```bash
git clone --depth 1 --branch v6.1 \
  https://github.com/torvalds/linux.git linux-v6.1

./kernel/build-k3765-probe.sh \
  ./linux-v6.1 \
  ./build/k3765-probe
```

Generated files appear under:

```text
build/k3765-probe/artifacts/
├── zImage-k3765-probe
├── Image-k3765-probe
├── k3765-z-probe.dtb
├── kernel.config
├── vmlinux-k3765-probe
├── System.map-k3765-probe
├── early-boot.disasm.txt
├── vmlinux.symbols.txt
├── ARTIFACTS.txt
└── SHA256SUMS
```

## Expected early log sequence

```text
Uncompressing Linux...
 done, booting the kernel.
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
Shadow-MSM: permanent table kept monitor identity map
Shadow-MSM: map_lowmem completed
Shadow-MSM: permanent kernel mappings completed
Shadow-MSM: DMA contiguous remap completed
Shadow-MSM: early fixmap shutdown completed
Shadow-MSM: vector pages allocated
Shadow-MSM: early trap vectors initialized
Shadow-MSM: static device mappings completed
Shadow-MSM: PCI I/O reservation completed
Shadow-MSM: device-map TLB flush completed
Shadow-MSM: device-map cache flush completed
Shadow-MSM: asynchronous aborts enabled
Shadow-MSM: ARM device mappings completed
Shadow-MSM: bootmem_init completed
Shadow-MSM: leaving paging_init
Shadow-MSM: paging_init completed
Shadow-MSM: setup_arch returned to start_kernel
```

For this diagnostic build only, the initial L1 table keeps a temporary
non-cacheable 1:1 section map using the ARM926 procinfo IO flags. Linux's
normal high virtual kernel mapping is installed over it, and `paging_init()`
later clears all but the single 2 MiB entry covering `0x00800000`. This keeps
the resident trace transport reachable across the first translation boundary
and permanent page-table construction. During `devicemaps_init()`, the trace
build also temporarily retains the bootstrap identity-mapped device entries
so ARMPRG's borrowed USB routine survives the architecture-wide TLB flush.
These mappings are strictly diagnostic aids and must be removed from a
production kernel once a native console is available.

No flash driver, NAND command, partition operation, or persistent-storage
write is part of this build path.
