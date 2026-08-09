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
#include <linux/fs.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/irq.h>
#include <linux/irqchip.h>
#include <linux/irqdomain.h>
#include <linux/minmax.h>
#include <linux/mm.h>
#include <linux/of.h>
#include <linux/of_address.h>
#include <linux/of_irq.h>
#include <linux/sched.h>
#include <linux/sched/signal.h>
#include <linux/sched_clock.h>
#include <linux/shadow_msm_trace.h>
#include <linux/uaccess.h>

#include <asm/cputype.h>
#include <asm/exception.h>
#include <asm/irq.h>
#include <asm/memory.h>

extern struct mm_struct init_mm;

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
#define SHADOW_MSM_WATCHDOG_RESET	0x0c
#define SHADOW_MSM_TIMER_STATUS		0xc0
#define SHADOW_MSM_TIMER_MATCH		0xc4
#define SHADOW_MSM_TIMER_MIN_DELTA	6U

#define SHADOW_MSM_TRACE_MAJOR		240
#define SHADOW_MSM_TRACE_CHUNK		96U
#define SHADOW_MSM_INPUT_MAILBOX	0x008ff800UL
#define SHADOW_MSM_INPUT_MAGIC		0x534d494eU
#define SHADOW_MSM_INPUT_RING_SIZE	256U
#define SHADOW_MSM_INPUT_RING_MASK	(SHADOW_MSM_INPUT_RING_SIZE - 1U)
#define SHADOW_MSM_INPUT_CHUNK		64U

struct shadow_msm_input_mailbox {
	u32 magic;
	u32 head;
	u32 tail;
	u8 data[SHADOW_MSM_INPUT_RING_SIZE];
};

static void __iomem *shadow_irq_base;
static void __iomem *shadow_timer_base;
static struct irq_domain *shadow_irq_domain;
static DEFINE_RAW_SPINLOCK(shadow_irq_lock);
static DEFINE_RAW_SPINLOCK(shadow_diag_lock);

static bool shadow_timer_periodic;
static u32 shadow_timer_period;
static int shadow_timer_linux_irq;
static unsigned long shadow_timer_irq_count;
static bool shadow_user_return_seen;
static bool shadow_first_syscall_seen;

void shadow_msm_watchdog_service(void)
{
	if (likely(shadow_timer_base))
		writel_relaxed(1, shadow_timer_base +
			       SHADOW_MSM_WATCHDOG_RESET);
}

static __always_inline void shadow_msm_set_ttbr(unsigned long ttbr)
{
	unsigned long zero = 0;

	/*
	 * Match the exact ARM926 switch_mm sequence emitted by proc-arm926.S:
	 * invalidate both caches, drain the write buffer, replace TTBR, then
	 * invalidate the unified TLB.  The surrounding caller has IRQs masked.
	 */
	asm volatile(
		"mcr p15, 0, %1, c7, c6, 0\n\t"
		"mcr p15, 0, %1, c7, c5, 0\n\t"
		"mcr p15, 0, %1, c7, c10, 4\n\t"
		"mcr p15, 0, %0, c2, c0, 0\n\t"
		"mcr p15, 0, %1, c8, c7, 0\n\t"
		:
		: "r" (ttbr), "r" (zero)
		: "memory");
}

void shadow_msm_diag_emit(const char *message)
{
	unsigned long flags;
	unsigned long saved_ttbr;
	unsigned long init_ttbr = virt_to_phys(init_mm.pgd);
	bool borrowed_init_mm;

	shadow_msm_watchdog_service();
	raw_spin_lock_irqsave(&shadow_diag_lock, flags);
	asm volatile(
		"mrc p15, 0, %0, c2, c0, 0"
		: "=r" (saved_ttbr));

	borrowed_init_mm =
		(saved_ttbr & 0xffffc000UL) !=
		(init_ttbr & 0xffffc000UL);
	if (borrowed_init_mm)
		shadow_msm_set_ttbr(init_ttbr);

	((void (*)(const char *))0x00816cf4UL)(message);

	if (borrowed_init_mm)
		shadow_msm_set_ttbr(saved_ttbr);
	raw_spin_unlock_irqrestore(&shadow_diag_lock, flags);
	shadow_msm_watchdog_service();
}

/*
 * Run one iteration of the initialized ARMPRG receive/dispatch loop and copy
 * any host bytes deposited by monitor command 0x1c/0x0e. The mailbox and the
 * resident runtime are accessed only while init_mm's proven non-cacheable
 * identity map is active; the caller's normal kernel stack remains mapped in
 * the upper half of init_mm.
 */
size_t shadow_msm_diag_receive(char *buffer, size_t limit)
{
	struct shadow_msm_input_mailbox *mailbox;
	unsigned long flags;
	unsigned long saved_ttbr;
	unsigned long init_ttbr = virt_to_phys(init_mm.pgd);
	bool borrowed_init_mm;
	u32 head;
	u32 tail;
	size_t count = 0;

	shadow_msm_watchdog_service();
	raw_spin_lock_irqsave(&shadow_diag_lock, flags);
	asm volatile(
		"mrc p15, 0, %0, c2, c0, 0"
		: "=r" (saved_ttbr));

	borrowed_init_mm =
		(saved_ttbr & 0xffffc000UL) !=
		(init_ttbr & 0xffffc000UL);
	if (borrowed_init_mm)
		shadow_msm_set_ttbr(init_ttbr);

	((void (*)(void))0x00814214UL)();
	mailbox = (struct shadow_msm_input_mailbox *)
		SHADOW_MSM_INPUT_MAILBOX;
	if (READ_ONCE(mailbox->magic) == SHADOW_MSM_INPUT_MAGIC) {
		head = READ_ONCE(mailbox->head) & SHADOW_MSM_INPUT_RING_MASK;
		tail = READ_ONCE(mailbox->tail) & SHADOW_MSM_INPUT_RING_MASK;
		while (tail != head && count < limit) {
			buffer[count++] = READ_ONCE(mailbox->data[tail]);
			tail = (tail + 1U) & SHADOW_MSM_INPUT_RING_MASK;
		}
		if (count)
			WRITE_ONCE(mailbox->tail, tail);
	}

	if (borrowed_init_mm)
		shadow_msm_set_ttbr(saved_ttbr);
	raw_spin_unlock_irqrestore(&shadow_diag_lock, flags);
	shadow_msm_watchdog_service();
	return count;
}

void shadow_msm_diag_input_reset(void)
{
	struct shadow_msm_input_mailbox *mailbox;
	unsigned long flags;
	unsigned long saved_ttbr;
	unsigned long init_ttbr = virt_to_phys(init_mm.pgd);
	bool borrowed_init_mm;

	raw_spin_lock_irqsave(&shadow_diag_lock, flags);
	asm volatile(
		"mrc p15, 0, %0, c2, c0, 0"
		: "=r" (saved_ttbr));
	borrowed_init_mm =
		(saved_ttbr & 0xffffc000UL) !=
		(init_ttbr & 0xffffc000UL);
	if (borrowed_init_mm)
		shadow_msm_set_ttbr(init_ttbr);

	mailbox = (struct shadow_msm_input_mailbox *)
		SHADOW_MSM_INPUT_MAILBOX;
	WRITE_ONCE(mailbox->head, 0);
	WRITE_ONCE(mailbox->tail, 0);
	WRITE_ONCE(mailbox->magic, SHADOW_MSM_INPUT_MAGIC);

	if (borrowed_init_mm)
		shadow_msm_set_ttbr(saved_ttbr);
	raw_spin_unlock_irqrestore(&shadow_diag_lock, flags);
}

unsigned long shadow_msm_keepalive(void)
{
	shadow_msm_watchdog_service();
	return READ_ONCE(shadow_timer_irq_count);
}

static __always_inline void shadow_trace(const char *message)
{
	shadow_msm_diag_emit(message);
}

/*
 * These two hooks are called from the ARM exception-entry assembly.  Besides
 * locating the exact first userspace boundary, they close the watchdog gap
 * between execve("/init") and PID 1's first private keepalive ioctl.
 */
void shadow_msm_user_return_checkpoint(void)
{
	shadow_msm_watchdog_service();
	if (!READ_ONCE(shadow_user_return_seen)) {
		WRITE_ONCE(shadow_user_return_seen, true);
		shadow_trace(
			"Shadow-MSM: returning to PID 1 userspace\r\n");
	}
}

void shadow_msm_first_syscall_checkpoint(void)
{
	shadow_msm_watchdog_service();
	if (!READ_ONCE(shadow_first_syscall_seen)) {
		WRITE_ONCE(shadow_first_syscall_seen, true);
		shadow_trace(
			"Shadow-MSM: PID 1 entered its first syscall\r\n");
	}
}

static __always_inline void shadow_watchdog_pet(void)
{
	/*
	 * The exact stock ARMPRG main loop at 0x008141e0 writes 1 to
	 * 0x8000540c before and after processing each command.  A RAM-only
	 * second-stage test reproduced that write for more than 30 seconds
	 * without reset.  The same write before timer setup and on every
	 * clockevent keeps Linux inside the proven watchdog window.
	 */
	shadow_msm_watchdog_service();
}

static void shadow_trace_hex(const char *prefix, unsigned long value)
{
	static const char digits[] = "0123456789ABCDEF";
	char message[64];
	unsigned int digit;
	unsigned int length = 0;

	while (*prefix && length < sizeof(message) - 13)
		message[length++] = *prefix++;
	message[length++] = '0';
	message[length++] = 'x';
	for (digit = 0; digit < 8; digit++)
		message[length++] = digits[(value >> ((7 - digit) * 4)) & 0xf];
	message[length++] = '\r';
	message[length++] = '\n';
	message[length] = '\0';
	shadow_trace(message);
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

	/*
	 * The resident monitor's diagnostic transport is polling-based and is
	 * not re-entrant.  Never call shadow_trace() from hard-IRQ context.
	 * Process-context boot checkpoints provide the safe progress signal.
	 */

	shadow_timer_irq_count++;
	shadow_watchdog_pet();

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

	shadow_watchdog_pet();

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

static int shadow_trace_open(struct inode *inode, struct file *file)
{
	shadow_trace("Shadow-MSM: PID 1 opened /dev/shadowtrace\r\n");
	return 0;
}

static ssize_t shadow_trace_write(struct file *file,
				  const char __user *buffer,
				  size_t length,
				  loff_t *position)
{
	char message[SHADOW_MSM_TRACE_CHUNK + 1];
	size_t total = 0;

	/*
	 * The stock monitor routine expects a NUL-terminated string.  Keep each
	 * copy bounded and invoke it only from this userspace process context.
	 */
	while (length) {
		size_t count = min_t(size_t, length, SHADOW_MSM_TRACE_CHUNK);

		if (copy_from_user(message, buffer, count))
			return total ? (ssize_t)total : -EFAULT;
		message[count] = '\0';
		shadow_trace(message);

		buffer += count;
		length -= count;
		total += count;
	}

	return total;
}

static ssize_t shadow_trace_read(struct file *file,
				 char __user *buffer,
				 size_t length,
				 loff_t *position)
{
	char message[SHADOW_MSM_INPUT_CHUNK];
	size_t count;

	if (!length)
		return 0;
	length = min_t(size_t, length, sizeof(message));

	for (;;) {
		count = shadow_msm_diag_receive(message, length);
		if (count)
			break;
		if (file->f_flags & O_NONBLOCK)
			return -EAGAIN;
		if (signal_pending(current))
			return -ERESTARTSYS;
		schedule_timeout_interruptible(1);
	}

	if (copy_to_user(buffer, message, count))
		return -EFAULT;
	return count;
}

static long shadow_trace_ioctl(struct file *file,
			       unsigned int command,
			       unsigned long argument)
{
	if (command != SHADOW_MSM_KEEPALIVE_IOCTL)
		return -ENOTTY;

	return shadow_msm_keepalive();
}

static const struct file_operations shadow_trace_operations = {
	.open = shadow_trace_open,
	.read = shadow_trace_read,
	.write = shadow_trace_write,
	.unlocked_ioctl = shadow_trace_ioctl,
	.llseek = no_llseek,
};

static int __init shadow_trace_device_init(void)
{
	int result;

	result = register_chrdev(
		SHADOW_MSM_TRACE_MAJOR,
		"shadowtrace",
		&shadow_trace_operations);
	if (result < 0)
		return result;
	shadow_msm_diag_input_reset();

	shadow_trace(
		"Shadow-MSM: /dev/shadowtrace process bridge registered\r\n");
	shadow_trace(
		"Shadow-MSM: RAM-only host input bridge registered\r\n");
	shadow_trace(
		"Shadow-MSM: hardware ZTE K3765-Z / Qualcomm MSM6290\r\n");
	shadow_trace_hex("Shadow-MSM: CPU MIDR ", read_cpuid_id());
	shadow_trace(
		"Shadow-MSM: physical RAM window 0x00000000-0x01FFFFFF\r\n");
	return 0;
}
device_initcall(shadow_trace_device_init);
