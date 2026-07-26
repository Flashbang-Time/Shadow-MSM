#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
	echo "usage: $0 <linux-v6.1-tree> [output-directory]" >&2
	exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
kernel_tree="$(cd "$1" && pwd)"
output_root="${2:-"${repo_root}/build/k3765-probe"}"
mkdir -p "${output_root}"
output_root="$(cd "${output_root}" && pwd)"
kernel_out="${output_root}/kernel"
artifacts="${output_root}/artifacts"
bl1_build="${output_root}/bl1"
mkdir -p "${kernel_out}" "${artifacts}" "${bl1_build}"
python_cmd="${SHADOW_MSM_PYTHON:-python3}"

config_file="${repo_root}/kernel/k3765_probe.config"
dts_file="${repo_root}/kernel/dts/k3765-z-probe.dts"
shadow_timer_driver="${repo_root}/kernel/drivers/timer-shadow-msm.c"
shadow_init_source="${repo_root}/kernel/userspace/shadow-init.c"
bl1_builder="${repo_root}/work/build_linux_image_bl1.py"
shadow_init_binary="${output_root}/shadow-init"
initramfs_list="${output_root}/shadow-initramfs.list"
initramfs_config="${output_root}/shadow-initramfs.config"

for patch_file in "${repo_root}"/kernel/patches/*.patch; do
	if git -C "${kernel_tree}" apply --reverse --check \
		"${patch_file}" 2>/dev/null; then
		echo "$(basename "${patch_file}") is already applied"
	else
		git -C "${kernel_tree}" apply --check "${patch_file}"
		git -C "${kernel_tree}" apply "${patch_file}"
	fi
done

# Stage the device-specific RAM-only clockevent/IRQ driver into Linux v6.1.
install -m 0644 \
	"${shadow_timer_driver}" \
	"${kernel_tree}/drivers/clocksource/timer-shadow-msm.c"
if ! grep -q 'timer-shadow-msm.o' \
	"${kernel_tree}/drivers/clocksource/Makefile"; then
	printf '\nobj-$(CONFIG_SHADOW_MSM_EARLY_TRACE) += timer-shadow-msm.o\n' \
		>> "${kernel_tree}/drivers/clocksource/Makefile"
fi

arm-linux-gnueabi-gcc \
	-march=armv5te \
	-marm \
	-Os \
	-ffreestanding \
	-ffunction-sections \
	-fdata-sections \
	-fno-builtin \
	-fno-pic \
	-fno-pie \
	-fno-stack-protector \
	-fno-unwind-tables \
	-fno-asynchronous-unwind-tables \
	-nostdlib \
	-static \
	-no-pie \
	-Wl,--build-id=none \
	-Wl,--gc-sections \
	-Wl,-e,_start \
	-Wl,-Ttext=0x00010000 \
	-o "${shadow_init_binary}" \
	"${shadow_init_source}"

arm-linux-gnueabi-readelf -h "${shadow_init_binary}" |
	grep -Eq 'Type:[[:space:]]+EXEC'
arm-linux-gnueabi-readelf -h "${shadow_init_binary}" |
	grep -Eq 'Machine:[[:space:]]+ARM'
if arm-linux-gnueabi-readelf -l "${shadow_init_binary}" |
	grep -q 'INTERP'; then
	echo "shadow-init unexpectedly contains a dynamic interpreter" >&2
	exit 1
fi

printf '%s\n' \
	'dir /dev 0755 0 0' \
	'nod /dev/shadowtrace 0600 0 0 c 240 0' \
	"file /init ${shadow_init_binary} 0755 0 0" \
	> "${initramfs_list}"
printf 'CONFIG_INITRAMFS_SOURCE="%s"\n' "${initramfs_list}" \
	> "${initramfs_config}"

make -C "${kernel_tree}" \
	O="${kernel_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	multi_v5_defconfig

"${kernel_tree}/scripts/kconfig/merge_config.sh" \
	-m \
	-O "${kernel_out}" \
	"${kernel_out}/.config" \
	"${config_file}" \
	"${initramfs_config}"

make -C "${kernel_tree}" \
	O="${kernel_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	olddefconfig

grep -q '^CONFIG_CPU_ARM926T=y$' "${kernel_out}/.config"
grep -q '^CONFIG_SHADOW_MSM_EARLY_TRACE=y$' "${kernel_out}/.config"
grep -q '^CONFIG_AUTO_ZRELADDR=y$' "${kernel_out}/.config"
grep -q '^CONFIG_BLK_DEV_INITRD=y$' "${kernel_out}/.config"
grep -q '^CONFIG_BINFMT_ELF=y$' "${kernel_out}/.config"
grep -Fqx \
	"CONFIG_INITRAMFS_SOURCE=\"${initramfs_list}\"" \
	"${kernel_out}/.config"

make -C "${kernel_tree}" \
	O="${kernel_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	-j"$(nproc)" \
	zImage

dtc -I dts -O dtb -o "${artifacts}/k3765-z-probe.dtb" "${dts_file}"
cp "${kernel_out}/arch/arm/boot/zImage" "${artifacts}/zImage-k3765-probe"
cp "${kernel_out}/arch/arm/boot/Image" "${artifacts}/Image-k3765-probe"
cp "${kernel_out}/.config" "${artifacts}/kernel.config"
cp "${kernel_out}/vmlinux" "${artifacts}/vmlinux-k3765-probe"
cp "${kernel_out}/System.map" "${artifacts}/System.map-k3765-probe"
cp "${shadow_init_binary}" "${artifacts}/shadow-init"

# BL1 contains exact sparse fingerprints of the Image. Rebuild it for every
# kernel artifact so a stale bootloader cannot reject or misidentify a new
# Image during the physical RAM-only handoff.
(
	cd "${bl1_build}"
	"${python_cmd}" \
		"${bl1_builder}" \
		"${artifacts}/Image-k3765-probe"
)
install -m 0644 \
	"${bl1_build}/outputs/k3765_bl1_linux_image.bin" \
	"${artifacts}/k3765_bl1_linux_image.bin"
install -m 0644 \
	"${bl1_build}/outputs/k3765_bl1_linux_image.map.txt" \
	"${artifacts}/k3765_bl1_linux_image.map.txt"
install -m 0644 \
	"${bl1_build}/outputs/k3765_bl1_linux_image.disasm.txt" \
	"${artifacts}/k3765_bl1_linux_image.disasm.txt"

arm-linux-gnueabi-objdump -dr \
	"${kernel_out}/arch/arm/kernel/head.o" \
	"${kernel_out}/arch/arm/mm/proc-arm926.o" \
	> "${artifacts}/early-boot.disasm.txt"

arm-linux-gnueabi-nm -n "${kernel_out}/vmlinux" \
	> "${artifacts}/vmlinux.symbols.txt"

python3 "${repo_root}/kernel/verify_probe.py" \
	--zimage "${artifacts}/zImage-k3765-probe" \
	--image "${artifacts}/Image-k3765-probe" \
	--dtb "${artifacts}/k3765-z-probe.dtb" \
	--report "${artifacts}/ARTIFACTS.txt"

{
	echo "PID 1 size: $(stat -c '%s' "${shadow_init_binary}")"
	echo "PID 1 SHA256: $(sha256sum "${shadow_init_binary}" | cut -d' ' -f1)"
	echo "PID 1 device: /dev/shadowtrace (character major 240, minor 0)"
	echo "PID 1 storage access: none"
} >> "${artifacts}/ARTIFACTS.txt"

find "${artifacts}" \
	-maxdepth 1 \
	-type f \
	! -name SHA256SUMS \
	-print0 |
	sort -z |
	xargs -0 sha256sum > "${artifacts}/SHA256SUMS"
