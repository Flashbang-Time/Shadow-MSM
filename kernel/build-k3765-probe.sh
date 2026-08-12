#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only

set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
	echo "usage: $0 <linux-v6.1-tree> <busybox-1.36.1-tree> [output-directory] [bash-static-armel]" >&2
	exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
kernel_tree="$(cd "$1" && pwd)"
busybox_tree="$(cd "$2" && pwd)"
output_root="${3:-"${repo_root}/build/k3765-probe"}"
mkdir -p "${output_root}"
output_root="$(cd "${output_root}" && pwd)"
kernel_out="${output_root}/kernel"
busybox_out="${output_root}/busybox"
artifacts="${output_root}/artifacts"
bl1_build="${output_root}/bl1"
mkdir -p \
	"${kernel_out}" \
	"${busybox_out}" \
	"${artifacts}" \
	"${bl1_build}"
python_cmd="${SHADOW_MSM_PYTHON:-python3}"

config_file="${repo_root}/kernel/k3765_probe.config"
dts_file="${repo_root}/kernel/dts/k3765-z-probe.dts"
shadow_timer_driver="${repo_root}/kernel/drivers/timer-shadow-msm.c"
shadow_tty_driver="${repo_root}/kernel/drivers/tty-shadow-msm.c"
shadow_sdcc_probe="${repo_root}/kernel/drivers/sdcc-shadow-msm.c"
shadow_init_source="${repo_root}/kernel/userspace/shadow-init.c"
shadow_neofetch_source="${repo_root}/kernel/userspace/neofetch"
shadow_neofetch_license="${repo_root}/kernel/userspace/NEOFETCH_LICENSE.md"
shadow_neofetch_sha256=2a272bbaa1275f21835fd3258fb8032ccdc98348e6ccb9cf58acacd366340170
bl1_builder="${repo_root}/work/build_linux_image_bl1.py"
shadow_init_binary="${output_root}/shadow-init"
busybox_binary="${busybox_out}/busybox"
bash_binary="${4:-${SHADOW_MSM_BASH_STATIC:-}}"
busybox_build_log="${output_root}/busybox-build.log"
initramfs_list="${output_root}/shadow-initramfs.list"
initramfs_config="${output_root}/shadow-initramfs.config"
os_release_file="${output_root}/shadow-msm-os-release"

if [[ -z "${bash_binary}" || ! -f "${bash_binary}" ]]; then
	echo "a static ARMEL Bash binary is required for upstream Neofetch" >&2
	exit 2
fi
bash_binary="$(readlink -f "${bash_binary}")"
arm-linux-gnueabi-readelf -h "${bash_binary}" |
	grep -Eq 'Machine:[[:space:]]+ARM'
arm-linux-gnueabi-readelf -h "${bash_binary}" |
	grep -Eq 'Type:[[:space:]]+EXEC'
if arm-linux-gnueabi-readelf -l "${bash_binary}" | grep -q INTERP; then
	echo "Bash unexpectedly contains a dynamic interpreter" >&2
	exit 1
fi
printf '%s  %s\n' "${shadow_neofetch_sha256}" "${shadow_neofetch_source}" |
	sha256sum --check --status

if [[ "${SHADOW_MSM_PATCHES_ALREADY_APPLIED:-0}" != 1 ]]; then
	for patch_file in "${repo_root}"/kernel/patches/*.patch; do
		if git -C "${kernel_tree}" apply --reverse --check \
			"${patch_file}" 2>/dev/null; then
			echo "$(basename "${patch_file}") is already applied"
		else
			git -C "${kernel_tree}" apply --check "${patch_file}"
			git -C "${kernel_tree}" apply "${patch_file}"
		fi
	done
fi

# Stage the device-specific RAM-only clockevent/IRQ driver into Linux v6.1.
install -m 0644 \
	"${shadow_timer_driver}" \
	"${kernel_tree}/drivers/clocksource/timer-shadow-msm.c"
if ! grep -q 'timer-shadow-msm.o' \
	"${kernel_tree}/drivers/clocksource/Makefile"; then
	printf '\nobj-$(CONFIG_SHADOW_MSM_EARLY_TRACE) += timer-shadow-msm.o\n' \
		>> "${kernel_tree}/drivers/clocksource/Makefile"
fi

# Stage the RAM-only ttySHM0 line-discipline/console bridge.  It reuses only
# the bounded resident transport and contains no storage operation.
install -m 0644 \
	"${shadow_tty_driver}" \
	"${kernel_tree}/drivers/tty/tty-shadow-msm.c"
if ! grep -q 'tty-shadow-msm.o' "${kernel_tree}/drivers/tty/Makefile"; then
	printf '\nobj-$(CONFIG_SHADOW_MSM_EARLY_TRACE) += tty-shadow-msm.o\n' \
		>> "${kernel_tree}/drivers/tty/Makefile"
fi

# Stage the polling SDCC host used during removable-card bring-up.
install -m 0644 \
	"${shadow_sdcc_probe}" \
	"${kernel_tree}/drivers/clocksource/sdcc-shadow-msm.c"
if ! grep -q 'sdcc-shadow-msm.o' \
	"${kernel_tree}/drivers/clocksource/Makefile"; then
	printf '\nobj-$(CONFIG_SHADOW_MSM_EARLY_TRACE) += sdcc-shadow-msm.o\n' \
		>> "${kernel_tree}/drivers/clocksource/Makefile"
fi

# Build a pinned static ARMv5 BusyBox.  It runs entirely from the built-in
# initramfs while allowing an explicitly requested removable card to be
# mounted from the interactive shell.
make -C "${busybox_tree}" \
	O="${busybox_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	defconfig

set_busybox_bool() {
	local symbol="$1"
	local value="$2"

	sed -i \
		-e "/^${symbol}=.*/d" \
		-e "/^# ${symbol} is not set$/d" \
		"${busybox_out}/.config"
	if [[ "${value}" == "y" ]]; then
		echo "${symbol}=y" >> "${busybox_out}/.config"
	else
		echo "# ${symbol} is not set" >> "${busybox_out}/.config"
	fi
}

set_busybox_bool CONFIG_STATIC y
set_busybox_bool CONFIG_PIE n
set_busybox_bool CONFIG_ASH y
set_busybox_bool CONFIG_SH_IS_ASH y
set_busybox_bool CONFIG_FEATURE_SH_STANDALONE y
set_busybox_bool CONFIG_FEATURE_SH_NOFORK y
# The kernel intentionally has CONFIG_NET disabled.  BusyBox tc also relies
# on legacy CBQ UAPI definitions absent from current Debian cross-headers.
set_busybox_bool CONFIG_TC n

make -C "${busybox_tree}" \
	O="${busybox_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	oldconfig </dev/null
set +e
make -C "${busybox_tree}" \
	O="${busybox_out}" \
	ARCH=arm \
	CROSS_COMPILE=arm-linux-gnueabi- \
	-j1 > "${busybox_build_log}" 2>&1
busybox_status=$?
set -e
if [[ ${busybox_status} -ne 0 ]]; then
	tail -n 160 "${busybox_build_log}"
	busybox_error="$(tail -n 35 "${busybox_build_log}")"
	busybox_error="${busybox_error//'%'/'%25'}"
	busybox_error="${busybox_error//$'\r'/'%0D'}"
	busybox_error="${busybox_error//$'\n'/'%0A'}"
	echo "::error title=BusyBox ARMv5 build failed::${busybox_error}"
	exit "${busybox_status}"
fi

arm-linux-gnueabi-readelf -h "${busybox_binary}" |
	grep -Eq 'Machine:[[:space:]]+ARM'
arm-linux-gnueabi-readelf -h "${busybox_binary}" |
	grep -Eq 'Type:[[:space:]]+EXEC'
if arm-linux-gnueabi-readelf -l "${busybox_binary}" |
	grep -q 'INTERP'; then
	echo "BusyBox unexpectedly contains a dynamic interpreter" >&2
	exit 1
fi

# Leave one ELF-header page below .text, keeping every load segment at or
# above the conventional ARM userspace floor of 0x00010000.
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
	-Wl,-z,max-page-size=0x1000 \
	-Wl,-e,_start \
	-Wl,-Ttext=0x00011000 \
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
if ! arm-linux-gnueabi-readelf -l "${shadow_init_binary}" |
	grep -Eq 'LOAD[[:space:]]+0x[0-9a-f]+[[:space:]]+0x00010000'; then
	echo "shadow-init first load segment is not safely above address zero" >&2
	exit 1
fi

cat > "${os_release_file}" <<'EOF'
NAME="Shadow-MSM"
ID=shadow-msm
VERSION="0.1 RAM-only"
PRETTY_NAME="Shadow-MSM 0.1 RAM-only"
HOME_URL="https://github.com/Flashbang-Time/Shadow-MSM"
EOF

printf '%s\n' \
	'dir /bin 0755 0 0' \
	'dir /dev 0755 0 0' \
	'dir /etc 0755 0 0' \
	'dir /mnt 0755 0 0' \
	'dir /mnt/sd 0755 0 0' \
	'dir /proc 0555 0 0' \
	'dir /root 0700 0 0' \
	'dir /run 0755 0 0' \
	'dir /sbin 0755 0 0' \
	'dir /sys 0555 0 0' \
	'dir /tmp 1777 0 0' \
	'dir /usr 0755 0 0' \
	'dir /usr/bin 0755 0 0' \
	'dir /usr/share 0755 0 0' \
	'dir /usr/share/doc 0755 0 0' \
	'dir /usr/share/doc/neofetch 0755 0 0' \
	'dir /usr/sbin 0755 0 0' \
	'dir /var 0755 0 0' \
	'nod /dev/console 0600 0 0 c 5 1' \
	'nod /dev/null 0666 0 0 c 1 3' \
	'nod /dev/tty 0666 0 0 c 5 0' \
	'nod /dev/zero 0666 0 0 c 1 5' \
	'nod /dev/ttySHM0 0600 0 0 c 241 0' \
	'nod /dev/shadowtrace 0600 0 0 c 240 0' \
	"file /init ${shadow_init_binary} 0755 0 0" \
	"file /bin/busybox ${busybox_binary} 0755 0 0" \
	"file /bin/bash ${bash_binary} 0755 0 0" \
	"file /usr/bin/neofetch ${shadow_neofetch_source} 0755 0 0" \
	"file /usr/share/doc/neofetch/LICENSE.md ${shadow_neofetch_license} 0644 0 0" \
	"file /etc/os-release ${os_release_file} 0644 0 0" \
	> "${initramfs_list}"

printf '%s\n' \
	'slink /bin/neofetch ../usr/bin/neofetch 0777 0 0' \
	'slink /usr/bin/env /bin/busybox 0777 0 0' \
	>> "${initramfs_list}"

for applet in \
	'[' '[[' ash awk basename blkid cat chmod clear cp cut date dd df dirname \
	dmesg du echo env expr false free grep head hexdump hostname id kill \
	ln ls md5sum mkdir mknod mount mv od pidof printf ps pwd readlink rm \
	realpath rmdir sed seq sh sha256sum sleep sort stat strings stty sync \
	tail tar test touch tr true tty uname uniq uptime wc which whoami xargs; do
	printf 'slink /bin/%s busybox 0777 0 0\n' "${applet}" \
		>> "${initramfs_list}"
done
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
grep -q '^CONFIG_RD_XZ=y$' "${kernel_out}/.config"
grep -q '^CONFIG_INITRAMFS_COMPRESSION_XZ=y$' "${kernel_out}/.config"
grep -q '^CONFIG_BINFMT_ELF=y$' "${kernel_out}/.config"
grep -q '^CONFIG_PROC_FS=y$' "${kernel_out}/.config"
grep -q '^CONFIG_SYSFS=y$' "${kernel_out}/.config"
grep -q '^CONFIG_TMPFS=y$' "${kernel_out}/.config"
grep -q '^CONFIG_TTY=y$' "${kernel_out}/.config"
grep -q '^CONFIG_BLOCK=y$' "${kernel_out}/.config"
grep -q '^CONFIG_MMC=y$' "${kernel_out}/.config"
grep -q '^CONFIG_MMC_BLOCK=y$' "${kernel_out}/.config"
grep -q '^CONFIG_EXFAT_FS=y$' "${kernel_out}/.config"
grep -q '^CONFIG_VFAT_FS=y$' "${kernel_out}/.config"
if grep -q '^CONFIG_CMA=y$' "${kernel_out}/.config"; then
	echo "CMA unexpectedly enabled" >&2
	exit 1
fi
if grep -q '^CONFIG_DMA_CMA=y$' "${kernel_out}/.config"; then
	echo "DMA CMA unexpectedly enabled" >&2
	exit 1
fi
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
cp "${busybox_binary}" "${artifacts}/busybox-armv5-static"
cp "${busybox_out}/.config" "${artifacts}/busybox.config"
cp "${bash_binary}" "${artifacts}/bash-static-armel"
cp "${shadow_neofetch_source}" "${artifacts}/neofetch-upstream"
cp "${shadow_neofetch_license}" "${artifacts}/NEOFETCH_LICENSE.md"

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
	--symbols "${artifacts}/System.map-k3765-probe" \
	--report "${artifacts}/ARTIFACTS.txt"

{
	echo "PID 1 size: $(stat -c '%s' "${shadow_init_binary}")"
	echo "PID 1 SHA256: $(sha256sum "${shadow_init_binary}" | cut -d' ' -f1)"
	echo "PID 1 device: /dev/ttySHM0 (TTY major 241, minor 0)"
	echo "PID 1 fallback: /dev/shadowtrace (character major 240, minor 0)"
	echo "PID 1 handoff: static BusyBox sh -i with TTY and recovery-shell fallback"
	echo "BusyBox size: $(stat -c '%s' "${busybox_binary}")"
	echo "BusyBox SHA256: $(sha256sum "${busybox_binary}" | cut -d' ' -f1)"
	echo "Bash size: $(stat -c '%s' "${bash_binary}")"
	echo "Bash SHA256: $(sha256sum "${bash_binary}" | cut -d' ' -f1)"
	echo "Neofetch upstream commit: ccd5d9f52609bbdcd5d8fa78c4fdb0f12954125f"
	echo "Neofetch SHA256: ${shadow_neofetch_sha256}"
	echo "Mounted filesystems: proc, sysfs, tmpfs (all volatile/pseudo)"
	echo "Removable storage: polling PL180 SDCC0 host, one block per request"
	echo "NAND access: not configured"
} >> "${artifacts}/ARTIFACTS.txt"

find "${artifacts}" \
	-maxdepth 1 \
	-type f \
	! -name SHA256SUMS \
	-print0 |
	sort -z |
	xargs -0 sha256sum > "${artifacts}/SHA256SUMS"
