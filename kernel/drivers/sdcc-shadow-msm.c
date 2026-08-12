// SPDX-License-Identifier: GPL-3.0-only
/*
 * Polling PL180 MMC host for the MSM6290 SDCC0 in the ZTE K3765-Z.
 *
 * The interrupt-controller route for SDCC0 is not known yet.  This driver
 * therefore completes one request at a time by polling the standard PL180
 * status/FIFO registers.  It deliberately exposes at most one 512-byte block
 * per request, which is slow but keeps first read/write bring-up simple and
 * bounded.  The NAND controller is unrelated and is never mapped here.
 */

#include <linux/bitops.h>
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/init.h>
#include <linux/io.h>
#include <linux/jiffies.h>
#include <linux/kernel.h>
#include <linux/mmc/host.h>
#include <linux/mmc/mmc.h>
#include <linux/scatterlist.h>
#include <linux/shadow_msm_trace.h>
#include <linux/string.h>

#define SHADOW_SDCC_BASE	0x50000000UL
#define SHADOW_SDCC_WINDOW	0x1000U
#define SHADOW_CLK_BASE		0x80000000UL
#define SHADOW_CLK_WINDOW	0x1000U
#define SHADOW_SDCC_MCLK	16000000U
#define SHADOW_SDCC_IDENT_CLOCK	400000U
#define SHADOW_SDCC_TRANSFER_CLOCK	4000000U
#define SHADOW_MAX_TRANSFER	512U

/* MSM6290 clock/TLMM registers recovered from the stock AMSS image. */
#define SHADOW_CLK_GATES	0x004U
#define SHADOW_SDCC0_MD		0x0f4U
#define SHADOW_SDCC0_NS		0x0f8U
#define SHADOW_TLMM_PIN		0x920U
#define SHADOW_TLMM_CONFIG	0x924U
#define SHADOW_TLMM_PULL_24_31	0xab8U
#define SHADOW_TLMM_PULL_32_39	0xabcU
#define SHADOW_TLMM_PULL_96_103	0xadcU

/* ARM PrimeCell PL180 register layout, confirmed by peripheral ID 0x41180. */
#define MCI_POWER		0x000U
#define MCI_CLOCK		0x004U
#define MCI_ARGUMENT		0x008U
#define MCI_COMMAND		0x00cU
#define MCI_RESPCMD		0x010U
#define MCI_RESPONSE0		0x014U
#define MCI_RESPONSE1		0x018U
#define MCI_RESPONSE2		0x01cU
#define MCI_RESPONSE3		0x020U
#define MCI_DATATIMER		0x024U
#define MCI_DATALENGTH		0x028U
#define MCI_DATACTRL		0x02cU
#define MCI_DATACNT		0x030U
#define MCI_STATUS		0x034U
#define MCI_CLEAR		0x038U
#define MCI_MASK0		0x03cU
#define MCI_MASK1		0x040U
#define MCI_FIFOCOUNT		0x048U
#define MCI_FIFO		0x080U

#define MCI_PWR_OFF		0x00U
#define MCI_PWR_UP		0x02U
#define MCI_PWR_ON		0x03U
#define MCI_PWR_ROD		BIT(7)

#define MCI_CLK_ENABLE		BIT(8)
#define MCI_CLK_BYPASS		BIT(10)
#define MCI_CLK_WIDEBUS_4	BIT(11)
#define MCI_CLK_QCOM_FLOWENA	BIT(12)
#define MCI_CLK_QCOM_FBCLK	BIT(15)

#define MCI_CMD_RESPONSE	BIT(6)
#define MCI_CMD_LONG_RESPONSE	BIT(7)
#define MCI_CMD_ENABLE		BIT(10)
#define MCI_CMD_QCOM_DATA	BIT(12)

#define MCI_DATA_ENABLE		BIT(0)
#define MCI_DATA_READ		BIT(1)
#define MCI_DATA_BLOCK_SHIFT	4

#define MCI_STAT_CMD_CRC_FAIL	BIT(0)
#define MCI_STAT_DATA_CRC_FAIL	BIT(1)
#define MCI_STAT_CMD_TIMEOUT	BIT(2)
#define MCI_STAT_DATA_TIMEOUT	BIT(3)
#define MCI_STAT_TX_UNDERRUN	BIT(4)
#define MCI_STAT_RX_OVERRUN	BIT(5)
#define MCI_STAT_CMD_RESP_END	BIT(6)
#define MCI_STAT_CMD_SENT	BIT(7)
#define MCI_STAT_DATA_END	BIT(8)
#define MCI_STAT_START_BIT_ERR	BIT(9)
#define MCI_STAT_DATA_BLOCK_END	BIT(10)
#define MCI_STAT_TX_FIFO_HALF	BIT(14)
#define MCI_STAT_RX_ACTIVE	BIT(13)
#define MCI_STAT_TX_FIFO_FULL	BIT(16)
#define MCI_STAT_TX_FIFO_EMPTY	BIT(18)
#define MCI_STAT_TX_DATA_AVAIL	BIT(20)
#define MCI_STAT_RX_DATA_AVAIL	BIT(21)

#define MCI_CLEAR_ALL		0x7ffU
#define MCI_CMD_ERRORS		(MCI_STAT_CMD_CRC_FAIL | \
				 MCI_STAT_CMD_TIMEOUT)
#define MCI_DATA_ERRORS		(MCI_STAT_DATA_CRC_FAIL | \
				 MCI_STAT_DATA_TIMEOUT | \
				 MCI_STAT_TX_UNDERRUN | \
				 MCI_STAT_RX_OVERRUN | \
				 MCI_STAT_START_BIT_ERR)

#define SHADOW_CMD_TIMEOUT_MS	2000U
#define SHADOW_DATA_TIMEOUT_MS	5000U

struct shadow_sdcc_host {
	struct mmc_host *mmc;
	void __iomem *base;
	void __iomem *clock;
	u32 actual_clock;
	u32 bounce[SHADOW_MAX_TRANSFER / sizeof(u32)];
};

static struct device *shadow_sdcc_device;

static bool shadow_sdcc_trace_opcode(u32 opcode)
{
	/* Sector I/O and the once-per-second status poll are intentionally quiet. */
	return opcode != MMC_SEND_STATUS &&
	       opcode != MMC_READ_SINGLE_BLOCK &&
	       opcode != MMC_WRITE_BLOCK;
}

static void shadow_sdcc_emit(const char *text)
{
	pr_info("shadow-sdcc: %s\n", text);
}

static void shadow_tlmm_mux(struct shadow_sdcc_host *host, u32 gpio,
			    u32 function)
{
	writel_relaxed(gpio, host->clock + SHADOW_TLMM_PIN);
	wmb();
	writel_relaxed(function << 2, host->clock + SHADOW_TLMM_CONFIG);
	wmb();
}

static void shadow_tlmm_pull(struct shadow_sdcc_host *host, u32 offset,
			     u32 mask, u32 value)
{
	u32 config = readl_relaxed(host->clock + offset);

	config &= ~mask;
	config |= value;
	writel_relaxed(config, host->clock + offset);
	wmb();
}

static void shadow_sdcc_prepare_hardware(struct shadow_sdcc_host *host)
{
	u32 gates;

	/* CLK, CMD, DATA0, DATA1, DATA2, DATA3. */
	shadow_tlmm_mux(host, 31, 3);
	shadow_tlmm_mux(host, 30, 3);
	shadow_tlmm_mux(host, 32, 3);
	shadow_tlmm_mux(host, 99, 1);
	shadow_tlmm_mux(host, 100, 1);
	shadow_tlmm_mux(host, 101, 1);

	/* Preserve all unrelated GPIO pull/drive nibbles. */
	shadow_tlmm_pull(host, SHADOW_TLMM_PULL_24_31,
			  GENMASK(31, 24), 0x17000000U);
	shadow_tlmm_pull(host, SHADOW_TLMM_PULL_32_39,
			  GENMASK(3, 0), 0x00000007U);
	shadow_tlmm_pull(host, SHADOW_TLMM_PULL_96_103,
			  GENMASK(23, 12), 0x00777000U);

	/* Stock slot-0 source clock: 16 MHz.  Gate bits are active low. */
	writel_relaxed(0x0002fff0U, host->clock + SHADOW_SDCC0_MD);
	writel_relaxed(0xfff20114U, host->clock + SHADOW_SDCC0_NS);
	gates = readl_relaxed(host->clock + SHADOW_CLK_GATES);
	gates &= ~(BIT(7) | BIT(8));
	writel_relaxed(gates, host->clock + SHADOW_CLK_GATES);
	wmb();

	writel_relaxed(0, host->base + MCI_COMMAND);
	writel_relaxed(0, host->base + MCI_DATACTRL);
	writel_relaxed(0, host->base + MCI_MASK0);
	writel_relaxed(0, host->base + MCI_MASK1);
	writel_relaxed(MCI_CLEAR_ALL, host->base + MCI_CLEAR);
	writel_relaxed(MCI_PWR_OFF, host->base + MCI_POWER);
	writel_relaxed(0, host->base + MCI_CLOCK);
	wmb();
	shadow_msm_watchdog_service();
}

static int shadow_sdcc_wait_status(struct shadow_sdcc_host *host, u32 wanted,
				   u32 errors, unsigned int timeout_ms,
				   u32 *last_status)
{
	unsigned long deadline = jiffies + msecs_to_jiffies(timeout_ms);
	u32 status;

	do {
		status = readl_relaxed(host->base + MCI_STATUS);
		if (status & errors) {
			*last_status = status;
			return -EIO;
		}
		if (status & wanted) {
			*last_status = status;
			return 0;
		}
		shadow_msm_watchdog_service();
		cpu_relax();
	} while (!time_after(jiffies, deadline));

	*last_status = readl_relaxed(host->base + MCI_STATUS);
	return -ETIMEDOUT;
}

static int shadow_sdcc_command(struct shadow_sdcc_host *host,
			       struct mmc_command *cmd)
{
	u32 command = cmd->opcode & 0x3fU;
	u32 terminal;
	u32 status;
	int error;

	writel_relaxed(0, host->base + MCI_COMMAND);
	writel_relaxed(MCI_CLEAR_ALL, host->base + MCI_CLEAR);

	terminal = MCI_STAT_CMD_SENT;
	if (cmd->flags & MMC_RSP_PRESENT) {
		command |= MCI_CMD_RESPONSE;
		terminal = MCI_STAT_CMD_RESP_END;
		if (cmd->flags & MMC_RSP_136)
			command |= MCI_CMD_LONG_RESPONSE;
	}
	if (cmd->data)
		command |= MCI_CMD_QCOM_DATA;
	command |= MCI_CMD_ENABLE;

	writel_relaxed(cmd->arg, host->base + MCI_ARGUMENT);
	wmb();
	writel_relaxed(command, host->base + MCI_COMMAND);
	wmb();

	error = shadow_sdcc_wait_status(host, terminal, MCI_CMD_ERRORS,
					SHADOW_CMD_TIMEOUT_MS, &status);
	if (error == -EIO) {
		if (status & MCI_STAT_CMD_TIMEOUT)
			error = -ETIMEDOUT;
		else if ((status & MCI_STAT_CMD_CRC_FAIL) &&
			 (cmd->flags & MMC_RSP_CRC))
			error = -EILSEQ;
		else
			error = 0;
	}

	if (!error && (cmd->flags & MMC_RSP_PRESENT)) {
		cmd->resp[0] = readl_relaxed(host->base + MCI_RESPONSE0);
		cmd->resp[1] = readl_relaxed(host->base + MCI_RESPONSE1);
		cmd->resp[2] = readl_relaxed(host->base + MCI_RESPONSE2);
		cmd->resp[3] = readl_relaxed(host->base + MCI_RESPONSE3);
	}

	/* Preserve any data-path completion which arrived with the response. */
	writel_relaxed(status & (MCI_STAT_CMD_CRC_FAIL |
				 MCI_STAT_CMD_TIMEOUT |
				 MCI_STAT_CMD_RESP_END |
				 MCI_STAT_CMD_SENT),
		       host->base + MCI_CLEAR);
	cmd->error = error;
	if (error)
		pr_err("shadow-sdcc: CMD%u arg=%08x failed %d status=%08x\n",
		       cmd->opcode, cmd->arg, error, status);
	else if (shadow_sdcc_trace_opcode(cmd->opcode))
		pr_info("shadow-sdcc: CMD%u arg=%08x ok status=%08x resp=%08x\n",
			cmd->opcode, cmd->arg, status, cmd->resp[0]);
	return error;
}

static int shadow_sdcc_start_data(struct shadow_sdcc_host *host,
				  struct mmc_data *data)
{
	u32 control;
	u32 size = data->blksz * data->blocks;

	if (!is_power_of_2(data->blksz) || size > SHADOW_MAX_TRANSFER ||
	    data->blocks != 1)
		return -EINVAL;

	writel_relaxed(0, host->base + MCI_DATACTRL);
	writel_relaxed(MCI_CLEAR_ALL, host->base + MCI_CLEAR);
	writel_relaxed(0xffffffffU, host->base + MCI_DATATIMER);
	writel_relaxed(size, host->base + MCI_DATALENGTH);

	/* Qualcomm's PL180 integration stores the literal byte count here. */
	control = data->blksz << MCI_DATA_BLOCK_SHIFT;
	if (data->flags & MMC_DATA_READ)
		control |= MCI_DATA_READ;
	control |= MCI_DATA_ENABLE;
	wmb();
	writel_relaxed(control, host->base + MCI_DATACTRL);
	wmb();
	return 0;
}

static int shadow_sdcc_transfer_data(struct shadow_sdcc_host *host,
				     struct mmc_data *data)
{
	unsigned long deadline = jiffies +
		msecs_to_jiffies(SHADOW_DATA_TIMEOUT_MS);
	u8 *buffer = (u8 *)host->bounce;
	u32 size = data->blksz * data->blocks;
	u32 transferred = 0;
	u32 status = 0;
	int error = 0;

	if (data->flags & MMC_DATA_WRITE) {
		if (sg_copy_to_buffer(data->sg, data->sg_len, buffer, size) != size)
			return -EFAULT;
	}

	while (transferred < size && !time_after(jiffies, deadline)) {
		u32 word = 0;
		u32 count = min_t(u32, sizeof(word), size - transferred);

		status = readl_relaxed(host->base + MCI_STATUS);
		if (status & MCI_DATA_ERRORS) {
			if (status & MCI_STAT_DATA_TIMEOUT)
				error = -ETIMEDOUT;
			else if (status & MCI_STAT_DATA_CRC_FAIL)
				error = -EILSEQ;
			else
				error = -EIO;
			break;
		}

		if (data->flags & MMC_DATA_READ) {
			if (!(status & MCI_STAT_RX_DATA_AVAIL))
				goto keep_waiting;
			word = readl_relaxed(host->base + MCI_FIFO);
			memcpy(buffer + transferred, &word, count);
		} else {
			if (status & MCI_STAT_TX_FIFO_FULL)
				goto keep_waiting;
			if (!(status & (MCI_STAT_TX_FIFO_HALF |
					MCI_STAT_TX_FIFO_EMPTY |
					MCI_STAT_TX_DATA_AVAIL)))
				goto keep_waiting;
			memcpy(&word, buffer + transferred, count);
			writel_relaxed(word, host->base + MCI_FIFO);
		}
		transferred += count;

keep_waiting:
		shadow_msm_watchdog_service();
		cpu_relax();
	}

	if (!error && transferred != size)
		error = -ETIMEDOUT;

	if (!error) {
		error = shadow_sdcc_wait_status(
			host, MCI_STAT_DATA_END,
			MCI_DATA_ERRORS, SHADOW_DATA_TIMEOUT_MS, &status);
		if (error == -EIO) {
			if (status & MCI_STAT_DATA_TIMEOUT)
				error = -ETIMEDOUT;
			else if (status & MCI_STAT_DATA_CRC_FAIL)
				error = -EILSEQ;
		}
	}

	if (!error && (data->flags & MMC_DATA_READ) &&
	    sg_copy_from_buffer(data->sg, data->sg_len, buffer, size) != size)
		error = -EFAULT;

	if (!error)
		data->bytes_xfered = size;
	else
		pr_err("shadow-sdcc: data %s failed %d status=%08x count=%u/%u hw=%u fifo=%u dctrl=%08x clock=%08x\n",
		       data->flags & MMC_DATA_READ ? "read" : "write",
		       error, status, transferred, size,
		       readl_relaxed(host->base + MCI_DATACNT),
		       readl_relaxed(host->base + MCI_FIFOCOUNT),
		       readl_relaxed(host->base + MCI_DATACTRL),
		       readl_relaxed(host->base + MCI_CLOCK));

	writel_relaxed(0, host->base + MCI_DATACTRL);
	writel_relaxed(status & MCI_CLEAR_ALL, host->base + MCI_CLEAR);
	data->error = error;
	return error;
}

static void shadow_sdcc_request(struct mmc_host *mmc,
				struct mmc_request *request)
{
	struct shadow_sdcc_host *host = mmc_priv(mmc);
	struct mmc_data *data = request->data;
	int error = 0;

	if (shadow_sdcc_trace_opcode(request->cmd->opcode))
		pr_info("shadow-sdcc: request CMD%u arg=%08x data=%s blocks=%u blksz=%u ios=%uHz/%ubit mode=%u power=%u regs=%08x/%08x\n",
			request->cmd->opcode, request->cmd->arg,
			data ? (data->flags & MMC_DATA_READ ? "read" : "write") : "none",
			data ? data->blocks : 0, data ? data->blksz : 0,
			mmc->ios.clock, 1U << mmc->ios.bus_width,
			mmc->ios.bus_mode, mmc->ios.power_mode,
			readl_relaxed(host->base + MCI_CLOCK),
			readl_relaxed(host->base + MCI_POWER));

	if (request->sbc) {
		error = shadow_sdcc_command(host, request->sbc);
		if (error)
			goto done;
	}

	if (data) {
		data->bytes_xfered = 0;
		data->error = 0;
		if (data->flags & MMC_DATA_READ) {
			error = shadow_sdcc_start_data(host, data);
			if (error) {
				data->error = error;
				request->cmd->error = error;
				goto done;
			}
		}
	}

	error = shadow_sdcc_command(host, request->cmd);
	if (error) {
		if (data) {
			data->error = error;
			writel_relaxed(0, host->base + MCI_DATACTRL);
		}
		goto done;
	}

	if (data) {
		if (data->flags & MMC_DATA_WRITE) {
			error = shadow_sdcc_start_data(host, data);
			if (error) {
				data->error = error;
				goto done;
			}
		}
		error = shadow_sdcc_transfer_data(host, data);
	}

	if (request->stop) {
		int stop_error = shadow_sdcc_command(host, request->stop);

		if (!error)
			error = stop_error;
	}

done:
	shadow_msm_watchdog_service();
	mmc_request_done(mmc, request);
}

static void shadow_sdcc_set_ios(struct mmc_host *mmc, struct mmc_ios *ios)
{
	struct shadow_sdcc_host *host = mmc_priv(mmc);
	u32 clock = 0;
	u32 power = MCI_PWR_OFF;
	u32 divisor;

	if (ios->clock) {
		if (ios->clock >= SHADOW_SDCC_MCLK) {
			clock = MCI_CLK_BYPASS;
			host->actual_clock = SHADOW_SDCC_MCLK;
		} else {
			divisor = SHADOW_SDCC_MCLK / (2 * ios->clock);
			if (divisor)
				divisor--;
			divisor = min_t(u32, divisor, 255);
			clock = divisor;
			host->actual_clock = SHADOW_SDCC_MCLK /
				(2 * (divisor + 1));
		}
		clock |= MCI_CLK_ENABLE | MCI_CLK_QCOM_FLOWENA |
			 MCI_CLK_QCOM_FBCLK;
	} else {
		host->actual_clock = 0;
	}

	if (ios->bus_width == MMC_BUS_WIDTH_4)
		clock |= MCI_CLK_WIDEBUS_4;

	switch (ios->power_mode) {
	case MMC_POWER_UP:
		power = MCI_PWR_UP;
		break;
	case MMC_POWER_ON:
		power = MCI_PWR_ON;
		break;
	case MMC_POWER_OFF:
	default:
		power = MCI_PWR_OFF;
		break;
	}
	if (ios->bus_mode == MMC_BUSMODE_OPENDRAIN)
		power |= MCI_PWR_ROD;

	writel_relaxed(clock, host->base + MCI_CLOCK);
	writel_relaxed(power, host->base + MCI_POWER);
	wmb();
	mmc->actual_clock = host->actual_clock;
	shadow_msm_watchdog_service();
	pr_info("shadow-sdcc: ios requested=%u actual=%u width=%ubit mode=%u power=%u regs=%08x/%08x\n",
		ios->clock, host->actual_clock, 1U << ios->bus_width,
		ios->bus_mode, ios->power_mode, clock, power);
	if (ios->power_mode == MMC_POWER_UP)
		mdelay(2);
}

static int shadow_sdcc_get_cd(struct mmc_host *mmc)
{
	return 1;
}

static int shadow_sdcc_get_ro(struct mmc_host *mmc)
{
	return 0;
}

static const struct mmc_host_ops shadow_sdcc_ops = {
	.request = shadow_sdcc_request,
	.set_ios = shadow_sdcc_set_ios,
	.get_cd = shadow_sdcc_get_cd,
	.get_ro = shadow_sdcc_get_ro,
};

static int __init shadow_sdcc_init(void)
{
	struct shadow_sdcc_host *host;
	struct mmc_host *mmc;
	int error;

	shadow_sdcc_emit("registering polling PL180 host");
	shadow_sdcc_device = root_device_register("shadow-msm-sdcc0");
	if (IS_ERR(shadow_sdcc_device))
		return PTR_ERR(shadow_sdcc_device);

	mmc = mmc_alloc_host(sizeof(*host), shadow_sdcc_device);
	if (!mmc) {
		error = -ENOMEM;
		goto unregister_device;
	}

	host = mmc_priv(mmc);
	host->mmc = mmc;
	host->base = ioremap(SHADOW_SDCC_BASE, SHADOW_SDCC_WINDOW);
	host->clock = ioremap(SHADOW_CLK_BASE, SHADOW_CLK_WINDOW);
	if (!host->base || !host->clock) {
		error = -ENOMEM;
		goto unmap;
	}

	shadow_sdcc_prepare_hardware(host);
	mmc->ops = &shadow_sdcc_ops;
	/* Initialize at the SD-mandated ceiling, then run well below 25 MHz. */
	mmc->f_min = SHADOW_SDCC_IDENT_CLOCK;
	mmc->f_max = SHADOW_SDCC_TRANSFER_CLOCK;
	mmc->ocr_avail = MMC_VDD_32_33 | MMC_VDD_33_34;
	mmc->caps = MMC_CAP_NEEDS_POLL;
	mmc->max_segs = 16;
	mmc->max_seg_size = SHADOW_MAX_TRANSFER;
	mmc->max_req_size = SHADOW_MAX_TRANSFER;
	mmc->max_blk_size = SHADOW_MAX_TRANSFER;
	mmc->max_blk_count = 1;

	error = mmc_add_host(mmc);
	if (error)
		goto unmap;

	pr_info("shadow-sdcc: mmc host %s ready at 0x%08lx, polling mode\n",
		mmc_hostname(mmc), SHADOW_SDCC_BASE);
	return 0;

unmap:
	if (host->clock)
		iounmap(host->clock);
	if (host->base)
		iounmap(host->base);
	mmc_free_host(mmc);
unregister_device:
	root_device_unregister(shadow_sdcc_device);
	shadow_sdcc_device = NULL;
	return error;
}
device_initcall(shadow_sdcc_init);
