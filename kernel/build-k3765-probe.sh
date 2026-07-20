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
mkdir -p "${kernel_out}" "${artifacts}"

patch_file="${repo_root}/kernel/patches/0001-arm-shadow-msm-early-trace.patch"
config_file="${repo_root}/kernel/k3765_probe.config"
dts_file="${repo_root}/kernel/dts/k3765-z-probe.dts"

if git -C "${kernel_tree}" apply --reverse --check "${patch_file}" 2>/dev/null; then
	echo "Shadow-MSM early-trace patch is already applied"
else
	git -C "${kernel_tree}" apply --check "${patch_file}"
	git -C "${kernel_tree}" apply "${patch_file}"
fi

make -C "${kernel_tree}" \
	O="${kernel_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	multi_v5_defconfig

"${kernel_tree}/scripts/kconfig/merge_config.sh" \
	-m \
	-O "${kernel_out}" \
	"${kernel_out}/.config" \
	"${config_file}"

make -C "${kernel_tree}" \
	O="${kernel_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	olddefconfig

grep -q '^CONFIG_CPU_ARM926T=y$' "${kernel_out}/.config"
grep -q '^CONFIG_SHADOW_MSM_EARLY_TRACE=y$' "${kernel_out}/.config"
grep -q '^CONFIG_AUTO_ZRELADDR=y$' "${kernel_out}/.config"

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

find "${artifacts}" \
	-maxdepth 1 \
	-type f \
	! -name SHA256SUMS \
	-print0 |
	sort -z |
	xargs -0 sha256sum > "${artifacts}/SHA256SUMS"
