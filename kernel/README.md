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
5. Linux creates its initial page tables; and
6. execution reaches the MMU-enable boundary.

The early trace patch borrows the initialized RAM-resident ARMPRG diagnostic
string routine only while the MMU is off. The device tree reserves
`0x00800000..0x008fffff` so the kernel image and allocator do not overwrite
that runtime during this experiment.

## Reproducible build

The GitHub Actions workflow clones the official Linux `v6.1` tag, applies the
single patch in `patches/`, merges `k3765_probe.config` over
`multi_v5_defconfig`, builds with the Debian/Ubuntu
`arm-linux-gnueabi-` toolchain, compiles the probe DTB, and verifies all RAM
bounds and image headers.

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
Shadow-MSM: enabling the Linux MMU next
```

No flash driver, NAND command, partition operation, or persistent-storage
write is part of this build path.
