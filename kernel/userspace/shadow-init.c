// SPDX-License-Identifier: GPL-3.0-only
/*
 * Minimal freestanding PID 1 for the Shadow-MSM RAM-only Linux probe.
 *
 * This binary uses only ARM EABI system calls.  It writes its boot identity
 * and exposes a tiny line-oriented recovery shell through /dev/shadowtrace.
 * The shell is intentionally self-contained: it has no filesystem, NAND,
 * network, dynamic linker, or external process dependency.
 */

#define SHADOW_SYS_READ		3
#define SHADOW_SYS_WRITE	4
#define SHADOW_SYS_OPEN		5
#define SHADOW_SYS_IOCTL	54
#define SHADOW_SYS_UNAME	122
#define SHADOW_SYS_SCHED_YIELD	158

#define SHADOW_O_RDWR		2
#define SHADOW_UTS_LENGTH	65
#define SHADOW_KEEPALIVE_IOCTL	0x534d0001UL
#define SHADOW_LINE_LENGTH	96
#define SHADOW_INPUT_LENGTH	64

struct shadow_utsname {
	char sysname[SHADOW_UTS_LENGTH];
	char nodename[SHADOW_UTS_LENGTH];
	char release[SHADOW_UTS_LENGTH];
	char version[SHADOW_UTS_LENGTH];
	char machine[SHADOW_UTS_LENGTH];
	char domainname[SHADOW_UTS_LENGTH];
};

static long shadow_syscall2(long number, long argument0, long argument1)
{
	register long r0 asm("r0") = argument0;
	register long r1 asm("r1") = argument1;
	register long r7 asm("r7") = number;

	asm volatile(
		"svc 0"
		: "+r" (r0)
		: "r" (r1), "r" (r7)
		: "memory");
	return r0;
}

static long shadow_syscall0(long number)
{
	register long r7 asm("r7") = number;
	register long r0 asm("r0");

	asm volatile(
		"svc 0"
		: "=r" (r0)
		: "r" (r7)
		: "memory");
	return r0;
}

static long shadow_syscall3(long number, long argument0, long argument1,
			    long argument2)
{
	register long r0 asm("r0") = argument0;
	register long r1 asm("r1") = argument1;
	register long r2 asm("r2") = argument2;
	register long r7 asm("r7") = number;

	asm volatile(
		"svc 0"
		: "+r" (r0)
		: "r" (r1), "r" (r2), "r" (r7)
		: "memory");
	return r0;
}

static unsigned long shadow_length(const char *text)
{
	unsigned long length = 0;

	while (text[length])
		length++;
	return length;
}

static void shadow_write_text(long descriptor, const char *text)
{
	unsigned long remaining = shadow_length(text);

	while (remaining) {
		long written = shadow_syscall3(
			SHADOW_SYS_WRITE,
			descriptor,
			(long)text,
			remaining);

		if (written <= 0)
			return;
		text += written;
		remaining -= written;
	}
}

static void shadow_write_field(long descriptor, const char *label,
			       const char *value)
{
	shadow_write_text(descriptor, label);
	shadow_write_text(descriptor, value);
	shadow_write_text(descriptor, "\r\n");
}

static int shadow_equals(const char *left, const char *right)
{
	while (*left && *right) {
		if (*left++ != *right++)
			return 0;
	}
	return *left == *right;
}

static int shadow_starts_with(const char *text, const char *prefix)
{
	while (*prefix)
		if (*text++ != *prefix++)
			return 0;
	return 1;
}

static void shadow_write_unsigned(long descriptor, unsigned long value)
{
	char reversed[10];
	char result[11];
	unsigned int count = 0;
	unsigned int index;

	if (!value) {
		shadow_write_text(descriptor, "0");
		return;
	}
	while (value && count < sizeof(reversed)) {
		reversed[count++] = '0' + value % 10;
		value /= 10;
	}
	for (index = 0; index < count; index++)
		result[index] = reversed[count - index - 1];
	result[count] = '\0';
	shadow_write_text(descriptor, result);
}

static void shadow_show_uname(long descriptor,
			      const struct shadow_utsname *identity)
{
	shadow_write_field(descriptor, "sysname : ", identity->sysname);
	shadow_write_field(descriptor, "release : ", identity->release);
	shadow_write_field(descriptor, "machine : ", identity->machine);
}

static void shadow_show_hardware(long descriptor)
{
	shadow_write_text(descriptor,
		"Board   : ZTE K3765-Z\r\n"
		"SoC     : Qualcomm MSM6290\r\n"
		"CPU     : ARM926EJ-S / ARMv5TEJ, MIDR 0x41069265\r\n"
		"RAM     : 32 MiB physical, Linux at 0x00200000\r\n"
		"Runtime : resident monitor at 0x00800000\r\n"
		"Boot    : volatile RAM-only handoff\r\n"
		"NAND    : untouched and not mounted\r\n");
}

static void shadow_run_command(long descriptor, const char *line,
			       const struct shadow_utsname *identity)
{
	long timer_irq_count;

	if (shadow_equals(line, "help")) {
		shadow_write_text(descriptor,
			"Commands: help uname hardware status about echo clear\r\n");
	} else if (shadow_equals(line, "uname")) {
		shadow_show_uname(descriptor, identity);
	} else if (shadow_equals(line, "hardware") ||
		   shadow_equals(line, "hw")) {
		shadow_show_hardware(descriptor);
	} else if (shadow_equals(line, "status")) {
		timer_irq_count = shadow_syscall3(
			SHADOW_SYS_IOCTL,
			descriptor,
			SHADOW_KEEPALIVE_IOCTL,
			0);
		shadow_write_text(descriptor, "Timer IRQ count: ");
		shadow_write_unsigned(
			descriptor,
			timer_irq_count > 0 ? timer_irq_count : 0);
		shadow_write_text(descriptor, "\r\nNAND operations: none\r\n");
	} else if (shadow_equals(line, "about")) {
		shadow_write_text(descriptor,
			"Shadow-MSM RAM-resident Linux bring-up shell\r\n"
			"GPL-3.0-only; no persistent-storage access\r\n");
	} else if (shadow_starts_with(line, "echo ")) {
		shadow_write_text(descriptor, line + 5);
		shadow_write_text(descriptor, "\r\n");
	} else if (shadow_equals(line, "clear")) {
		shadow_write_text(descriptor, "\033[2J\033[H");
	} else if (shadow_equals(line, "exit") ||
		   shadow_equals(line, "reboot")) {
		shadow_write_text(descriptor,
			"PID 1 remains active; power-cycle to return to stock firmware\r\n");
	} else {
		shadow_write_text(descriptor, "Unknown command: ");
		shadow_write_text(descriptor, line);
		shadow_write_text(descriptor, "\r\nType 'help' for commands.\r\n");
	}
}

void _start(void)
{
	static struct shadow_utsname identity;
	char input[SHADOW_INPUT_LENGTH];
	char line[SHADOW_LINE_LENGTH];
	unsigned int line_length = 0;
	unsigned int index;
	long descriptor;
	long received;
	long timer_irq_count;

	descriptor = shadow_syscall3(
		SHADOW_SYS_OPEN,
		(long)"/dev/shadowtrace",
		SHADOW_O_RDWR,
		0);

	if (descriptor >= 0) {
		timer_irq_count = shadow_syscall3(
			SHADOW_SYS_IOCTL,
			descriptor,
			SHADOW_KEEPALIVE_IOCTL,
			0);
		shadow_write_text(
			descriptor,
			"Shadow-MSM: entered freestanding PID 1 userspace\r\n");
		if (timer_irq_count > 0)
			shadow_write_text(
				descriptor,
				"Shadow-MSM: hardware timer IRQ observed\r\n");
		else
			shadow_write_text(
				descriptor,
				"Shadow-MSM: userspace watchdog keepalive active\r\n");

		if (shadow_syscall2(
			    SHADOW_SYS_UNAME,
			    (long)&identity,
			    0) == 0) {
			identity.sysname[SHADOW_UTS_LENGTH - 1] = '\0';
			identity.nodename[SHADOW_UTS_LENGTH - 1] = '\0';
			identity.release[SHADOW_UTS_LENGTH - 1] = '\0';
			identity.version[SHADOW_UTS_LENGTH - 1] = '\0';
			identity.machine[SHADOW_UTS_LENGTH - 1] = '\0';

			shadow_write_field(
				descriptor,
				"Shadow-MSM: sysname  ",
				identity.sysname);
			shadow_write_field(
				descriptor,
				"Shadow-MSM: release  ",
				identity.release);
			shadow_write_field(
				descriptor,
				"Shadow-MSM: machine  ",
				identity.machine);
		}
		shadow_write_text(
			descriptor,
			"Shadow-MSM: interactive PID 1 ready\r\n"
			"Type 'help' for commands.\r\n"
			"shadow-msm# ");
	}

	for (;;) {
		if (descriptor < 0) {
			shadow_syscall0(SHADOW_SYS_SCHED_YIELD);
			continue;
		}

		received = shadow_syscall3(
			SHADOW_SYS_READ,
			descriptor,
			(long)input,
			sizeof(input));
		if (received <= 0) {
			shadow_syscall3(
				SHADOW_SYS_IOCTL,
				descriptor,
				SHADOW_KEEPALIVE_IOCTL,
				0);
			shadow_syscall0(SHADOW_SYS_SCHED_YIELD);
			continue;
		}

		for (index = 0; index < (unsigned long)received; index++) {
			unsigned char character = input[index];

			if (character == '\r')
				continue;
			if (character == '\n') {
				line[line_length] = '\0';
				if (line_length)
					shadow_run_command(
						descriptor, line, &identity);
				line_length = 0;
				shadow_write_text(descriptor, "shadow-msm# ");
				continue;
			}
			if (character == 8 || character == 127) {
				if (line_length)
					line_length--;
				continue;
			}
			if (character >= 32 && character <= 126 &&
			    line_length < sizeof(line) - 1)
				line[line_length++] = character;
		}
	}
}
