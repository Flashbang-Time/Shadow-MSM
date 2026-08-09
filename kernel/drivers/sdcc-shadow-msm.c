// SPDX-License-Identifier: GPL-3.0-only
/*
 * Read-only MSM6290 SDCC identification probe for the ZTE K3765-Z.
 *
 * The exact AMSS image contains the legacy Qualcomm SDCC2 HAL and both
 * 0xA0400000/0xA0500000 controller bases.  This first probe deliberately
 * performs register reads only: it does not change clocks or GPIOs, issue a
 * card command, register a block device, mount media, or write any storage.
 */

#include <linux/init.h>
#include <linux/io.h>
#include <linux/kernel.h>
#include <linux/shadow_msm_trace.h>

#define SHADOW_SDCC_WINDOW	0x1000U

#define SHADOW_SDCC_POWER	0x000U
#define SHADOW_SDCC_CLOCK	0x004U
#define SHADOW_SDCC_DATACNT	0x030U
#define SHADOW_SDCC_STATUS	0x034U
#define SHADOW_SDCC_MASK0	0x03cU
#define SHADOW_SDCC_MASK1	0x040U
#define SHADOW_SDCC_FIFOCNT	0x044U
#define SHADOW_SDCC_VERSION	0x050U

static const phys_addr_t shadow_sdcc_bases[] = {
	0xA0400000UL,
	0xA0500000UL,
};

static int __init shadow_sdcc_probe_init(void)
{
	unsigned int index;

	shadow_msm_diag_emit(
		"Shadow-MSM: starting read-only SDCC register probe\r\n");

	for (index = 0; index < ARRAY_SIZE(shadow_sdcc_bases); index++) {
		void __iomem *base;
		char message[256];
		u32 power;
		u32 clock;
		u32 data_count;
		u32 status;
		u32 mask0;
		u32 mask1;
		u32 fifo_count;
		u32 version;

		base = ioremap(shadow_sdcc_bases[index], SHADOW_SDCC_WINDOW);
		if (!base) {
			snprintf(message, sizeof(message),
				 "Shadow-MSM: SDCC%u ioremap failed for 0x%08llX\r\n",
				 index + 1,
				 (unsigned long long)shadow_sdcc_bases[index]);
			shadow_msm_diag_emit(message);
			continue;
		}

		shadow_msm_watchdog_service();
		power = readl_relaxed(base + SHADOW_SDCC_POWER);
		clock = readl_relaxed(base + SHADOW_SDCC_CLOCK);
		data_count = readl_relaxed(base + SHADOW_SDCC_DATACNT);
		status = readl_relaxed(base + SHADOW_SDCC_STATUS);
		mask0 = readl_relaxed(base + SHADOW_SDCC_MASK0);
		mask1 = readl_relaxed(base + SHADOW_SDCC_MASK1);
		fifo_count = readl_relaxed(base + SHADOW_SDCC_FIFOCNT);
		version = readl_relaxed(base + SHADOW_SDCC_VERSION);
		shadow_msm_watchdog_service();

		snprintf(message, sizeof(message),
			 "Shadow-MSM: SDCC%u base=0x%08llX power=%08X "
			 "clock=%08X status=%08X datacnt=%08X mask0=%08X "
			 "mask1=%08X fifocnt=%08X version=%08X\r\n",
			 index + 1,
			 (unsigned long long)shadow_sdcc_bases[index],
			 power, clock, status, data_count, mask0, mask1,
			 fifo_count, version);
		shadow_msm_diag_emit(message);
		iounmap(base);
	}

	shadow_msm_diag_emit(
		"Shadow-MSM: read-only SDCC register probe complete\r\n");
	return 0;
}
device_initcall(shadow_sdcc_probe_init);
