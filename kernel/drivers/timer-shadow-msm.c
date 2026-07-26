// SPDX-License-Identifier: GPL-3.0-only
/*
 * RAM-only MSM6290 timer/interrupt bring-up for the ZTE K3765-Z.
 *
 * The register layout and IRQ routing below were recovered from the exact
 * OEMSBL shipped in DL_K3765-Z_VDF_SG_EUV1.00.00.  This deliberately exposes
 * only timer IRQ 0x22; it does not initialize, mask, or acknowledge any other
 * interrupt source.
 */

#include <linux/bitops.h>
#include <linux/clockchips.h>
#include <linux/clocksource.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/irq.h>
#include <linux/irqchip.h>
#include <linux/irqdomain.h>
#include <linux/of.h>
#include <linux/of_address.h>
#include <linux/of_irq.h>
#include <linux/sched_clock.h>

#include <asm/exception.h>
#include <asm/irq.h>

#define SHADOW_MSM_TIMER_RATE		32768U
#define SHADOW_MSM_TIMER_IRQ		0x22U
#define SHADOW_MSM_TIMER_VECTOR		0x1bU
#define SHADOW_MSM_TIMER_BIT		BIT(2)
#define SHADOW_MSM_SPURIOUS_VECTOR	0x3fU

#define SHADOW_MSM_IRQ_ACTIVE		0x9c
#define SHADOW_MSM_IRQ_BANK1_RAW	0x78
#define SHADOW_MSM_IRQ_BANK1_MASK	0x34
#define SHADOW_MSM_IRQ_BANK1_CLEAR	0x04

#define SHADOW_MSM_TIMER_COUNT		0x08
#define SHADOW_MSM_TIMER_STATUS		0xc0
#define SHADOW_MSM_TIMER_MATCH		0xc4
#define SHADOW_MSM_TIMER_MIN_DELTA	6U

static void __iomem *shadow_irq_base;
static void __iomem *shadow_timer_base;
static struct irq_domain *shadow_irq_domain;
static DEFINE_RAW_SPINLOCK(shadow_irq_lock);

static bool shadow_timer_periodic;
static u32 shadow_timer_period;
static int shadow_timer_linux_irq;

static __always_inline void shadow_trace(const char *message)
{
	((void (*)(const char *))0x00816cf4UL)(message);
}

static u32 shadow_timer_read_count(void)
{
	u32 first;
	u32 second;

	/*
	 * OEMSBL uses two equal consecutive reads to avoid sampling the
	 * asynchronous 32.768-kHz counter during a transition.
	 */
	first = readl_relaxed(shadow_timer_base + SHADOW_MSM_TIMER_COUNT);
	do {
		second = readl_relaxed(shadow_timer_base +
				      SHADOW_MSM_TIMER_COUNT);
		if (first == second)
			return second;
		first = second;
	} while (1);
}

static void shadow_irq_ack(struct irq_data *data)
{
	writel_relaxed(SHADOW_MSM_TIMER_BIT,
		       shadow_irq_base + SHADOW_MSM_IRQ_BANK1_CLEAR);
}

static void shadow_irq_mask(struct irq_data *data)
{
	unsigned long flags;
	u32 value;

	raw_spin_lock_irqsave(&shadow_irq_lock, flags);
	value = readl_relaxed(shadow_irq_base + SHADOW_MSM_IRQ_BANK1_MASK);
	value &= ~SHADOW_MSM_TIMER_BIT;
	writel_relaxed(value, shadow_irq_base + SHADOW_MSM_IRQ_BANK1_MASK);
	raw_spin_unlock_irqrestore(&shadow_irq_lock, flags);
}

static void shadow_irq_unmask(struct irq_data *data)
{
	unsigned long flags;
	u32 value;

	raw_spin_lock_irqsave(&shadow_irq_lock, flags);
	value = readl_relaxed(shadow_irq_base + SHADOW_MSM_IRQ_BANK1_MASK);
	value |= SHADOW_MSM_TIMER_BIT;
	writel_relaxed(value, shadow_irq_base + SHADOW_MSM_IRQ_BANK1_MASK);
	raw_spin_unlock_irqrestore(&shadow_irq_lock, flags);
}

static struct irq_chip shadow_irq_chip = {
	.name		= "shadow-msm6290",
	.irq_ack	= shadow_irq_ack,
	.irq_mask	= shadow_irq_mask,
	.irq_unmask	= shadow_irq_unmask,
};

static int shadow_irq_domain_map(struct irq_domain *domain,
				 unsigned int linux_irq,
				 irq_hw_number_t hardware_irq)
{
	if (hardware_irq != SHADOW_MSM_TIMER_IRQ)
		return -EINVAL;

	irq_set_chip_and_handler(linux_irq, &shadow_irq_chip,
				 handle_level_irq);
	irq_set_noprobe(linux_irq);
	return 0;
}

static const struct irq_domain_ops shadow_irq_domain_ops = {
	.map	= shadow_irq_domain_map,
	.xlate	= irq_domain_xlate_onecell,
};

static void __exception_irq_entry shadow_handle_irq(struct pt_regs *regs)
{
	unsigned int guard = 0;
	u32 vector;

	while (guard++ < 8) {
		vector = readl_relaxed(shadow_irq_base +
				      SHADOW_MSM_IRQ_ACTIVE);
		if (vector == SHADOW_MSM_SPURIOUS_VECTOR)
			return;

		/*
		 * OEMSBL's active-vector register returns a descriptor index,
		 * not its public logical IRQ number.  Descriptor 0x1b is the
		 * sole entry whose logical IRQ is 0x22.
		 */
		if (vector != SHADOW_MSM_TIMER_VECTOR)
			return;

		generic_handle_domain_irq(shadow_irq_domain,
					  SHADOW_MSM_TIMER_IRQ);
	}
}

static int __init shadow_irq_of_init(struct device_node *node,
				     struct device_node *parent)
{
	shadow_irq_base = of_iomap(node, 0);
	if (!shadow_irq_base)
		return -ENXIO;

	shadow_irq_domain = irq_domain_add_linear(
		node, SHADOW_MSM_TIMER_IRQ + 1,
		&shadow_irq_domain_ops, NULL);
	if (!shadow_irq_domain) {
		iounmap(shadow_irq_base);
		shadow_irq_base = NULL;
		return -ENOMEM;
	}

	irq_create_mapping(shadow_irq_domain, SHADOW_MSM_TIMER_IRQ);
	set_handle_irq(shadow_handle_irq);
	shadow_trace("Shadow-MSM: MSM6290 timer IRQ route registered\r\n");
	return 0;
}
IRQCHIP_DECLARE(shadow_msm6290_irq, "qcom,msm6290-shadow-irq",
		shadow_irq_of_init);

static u64 shadow_clocksource_read(struct clocksource *source)
{
	return shadow_timer_read_count();
}

static u64 notrace shadow_sched_clock_read(void)
{
	return shadow_timer_read_count();
}

static struct clocksource shadow_clocksource = {
	.name	= "shadow-msm6290-counter",
	.rating	= 200,
	.read	= shadow_clocksource_read,
	.mask	= CLOCKSOURCE_MASK(32),
	.flags	= CLOCK_SOURCE_IS_CONTINUOUS,
};

static int shadow_timer_program(u32 delta)
{
	u32 now;
	u32 match;
	unsigned int guard;

	if (delta < SHADOW_MSM_TIMER_MIN_DELTA)
		delta = SHADOW_MSM_TIMER_MIN_DELTA;

	now = shadow_timer_read_count();
	match = now + delta;
	writel_relaxed(match, shadow_timer_base + SHADOW_MSM_TIMER_MATCH);

	/*
	 * OEMSBL waits for status bit 0 after loading a match value.  Bound
	 * the wait so a clockevent programming failure cannot wedge Linux.
	 */
	for (guard = 0; guard < 1024; guard++)
		if (readl_relaxed(shadow_timer_base +
				  SHADOW_MSM_TIMER_STATUS) & BIT(0))
			return 0;

	return -ETIME;
}

static int shadow_clockevent_shutdown(struct clock_event_device *event)
{
	shadow_timer_periodic = false;
	return 0;
}

static int shadow_clockevent_set_periodic(struct clock_event_device *event)
{
	shadow_timer_periodic = true;
	return shadow_timer_program(shadow_timer_period);
}

static int shadow_clockevent_set_oneshot(struct clock_event_device *event)
{
	shadow_timer_periodic = false;
	return 0;
}

static int shadow_clockevent_next(unsigned long delta,
				  struct clock_event_device *event)
{
	return shadow_timer_program((u32)delta);
}

static struct clock_event_device shadow_clockevent = {
	.name			= "shadow-msm6290-event",
	.features		= CLOCK_EVT_FEAT_PERIODIC |
				  CLOCK_EVT_FEAT_ONESHOT,
	.rating			= 200,
	.set_state_shutdown	= shadow_clockevent_shutdown,
	.set_state_periodic	= shadow_clockevent_set_periodic,
	.set_state_oneshot	= shadow_clockevent_set_oneshot,
	.tick_resume		= shadow_clockevent_shutdown,
	.set_next_event		= shadow_clockevent_next,
};

static irqreturn_t shadow_timer_interrupt(int irq, void *device)
{
	struct clock_event_device *event = device;

	if (shadow_timer_periodic)
		shadow_timer_program(shadow_timer_period);

	event->event_handler(event);
	return IRQ_HANDLED;
}

static int __init shadow_timer_of_init(struct device_node *node)
{
	int result;

	shadow_timer_base = of_iomap(node, 0);
	if (!shadow_timer_base)
		return -ENXIO;

	shadow_timer_linux_irq = irq_of_parse_and_map(node, 0);
	if (shadow_timer_linux_irq <= 0) {
		result = -EINVAL;
		goto unmap;
	}

	result = clocksource_register_hz(&shadow_clocksource,
					 SHADOW_MSM_TIMER_RATE);
	if (result)
		goto unmap;

	sched_clock_register(shadow_sched_clock_read, 32,
			     SHADOW_MSM_TIMER_RATE);

	/*
	 * Clear only the timer's controller latch, then put its first match
	 * one second ahead before request_irq() unmasks the route.
	 */
	writel_relaxed(SHADOW_MSM_TIMER_BIT,
		       shadow_irq_base + SHADOW_MSM_IRQ_BANK1_CLEAR);
	result = shadow_timer_program(SHADOW_MSM_TIMER_RATE);
	if (result)
		goto unregister_clocksource;

	shadow_clockevent.irq = shadow_timer_linux_irq;
	shadow_clockevent.cpumask = cpu_possible_mask;
	shadow_timer_period = DIV_ROUND_CLOSEST(SHADOW_MSM_TIMER_RATE, HZ);

	result = request_irq(shadow_timer_linux_irq, shadow_timer_interrupt,
			     IRQF_TIMER | IRQF_IRQPOLL,
			     "shadow-msm6290-timer", &shadow_clockevent);
	if (result)
		goto unregister_clocksource;

	clockevents_config_and_register(&shadow_clockevent,
					SHADOW_MSM_TIMER_RATE,
					SHADOW_MSM_TIMER_MIN_DELTA,
					0x7fffffffU);

	shadow_trace("Shadow-MSM: MSM6290 32.768-kHz clockevent registered\r\n");
	return 0;

unregister_clocksource:
	clocksource_unregister(&shadow_clocksource);
unmap:
	iounmap(shadow_timer_base);
	shadow_timer_base = NULL;
	return result;
}
TIMER_OF_DECLARE(shadow_msm6290_timer, "qcom,msm6290-shadow-timer",
		 shadow_timer_of_init);
