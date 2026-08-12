// SPDX-License-Identifier: GPL-3.0-only
/*
 * Minimal freestanding PID 1 for the Shadow-MSM RAM-only Linux probe.
 *
 * This binary uses only ARM EABI system calls.  It writes its boot identity,
 * attaches /dev/ttySHM0 to the three standard descriptors, mounts the
 * RAM-backed pseudo-filesystems, and execs a static BusyBox shell.  The old
 * /dev/shadowtrace bridge and tiny built-in command loop remain as recovery
 * fallbacks if the TTY or BusyBox cannot be used.
 */

#define SHADOW_SYS_READ		3
#define SHADOW_SYS_WRITE	4
#define SHADOW_SYS_OPEN		5
#define SHADOW_SYS_EXECVE	11
#define SHADOW_SYS_MOUNT	21
#define SHADOW_SYS_DUP2		63
#define SHADOW_SYS_SETSID	66
#define SHADOW_SYS_IOCTL	54
#define SHADOW_SYS_UNAME	122
#define SHADOW_SYS_SCHED_YIELD	158

#define SHADOW_O_RDWR		2
#define SHADOW_TIOCSCTTY	0x540E
#define SHADOW_UTS_LENGTH	65
#define SHADOW_KEEPALIVE_IOCTL	0x534d0001UL
#define SHADOW_LINE_LENGTH	96
#define SHADOW_INPUT_LENGTH	64
#define SHADOW_DECIMAL_PLACES	10

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

static long shadow_syscall5(long number, long argument0, long argument1,
			    long argument2, long argument3, long argument4)
{
	register long r0 asm("r0") = argument0;
	register long r1 asm("r1") = argument1;
	register long r2 asm("r2") = argument2;
	register long r3 asm("r3") = argument3;
	register long r4 asm("r4") = argument4;
	register long r7 asm("r7") = number;

	asm volatile(
		"svc 0"
		: "+r" (r0)
		: "r" (r1), "r" (r2), "r" (r3), "r" (r4), "r" (r7)
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
	static const unsigned long decimal_places[] = {
		1000000000UL, 100000000UL, 10000000UL, 1000000UL,
		100000UL, 10000UL, 1000UL, 100UL, 10UL, 1UL,
	};
	char result[11];
	unsigned int index;
	unsigned int count = 0;
	int started = 0;

	/*
	 * PID 1 is linked without libgcc.  Convert by bounded subtraction so
	 * ARM GCC cannot introduce the __aeabi_uidivmod runtime helper.
	 */
	for (index = 0; index < SHADOW_DECIMAL_PLACES; index++) {
		unsigned int digit = 0;

		while (value >= decimal_places[index]) {
			value -= decimal_places[index];
			digit++;
		}
		if (digit || started || index == 9) {
			result[count++] = '0' + digit;
			started = 1;
		}
	}
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

static void shadow_try_busybox(long descriptor, const char *device)
{
	static char *const arguments[] = {
		"/bin/busybox", "sh", "-i", 0,
	};
	static char *const environment[] = {
		"HOME=/root",
		"PATH=/bin:/sbin:/usr/bin:/usr/sbin",
		"PS1=shadow-msm# ",
		"SHELL=/bin/sh",
		"USER=root",
		"LOGNAME=root",
		"TERM=vt100",
		0,
	};
	long result;
	unsigned int standard_descriptor;

	shadow_write_text(descriptor, "Shadow-MSM: attaching BusyBox to ");
	shadow_write_text(descriptor, device);
	shadow_write_text(descriptor, "\r\n");
	for (standard_descriptor = 0; standard_descriptor < 3;
	     standard_descriptor++) {
		result = shadow_syscall2(
			SHADOW_SYS_DUP2, descriptor, standard_descriptor);
		if (result < 0) {
			shadow_write_text(
				descriptor,
				"Shadow-MSM: standard-descriptor setup failed; "
				"using recovery shell\r\n");
			return;
		}
	}
	/* All four mounts are volatile and optional. */
	shadow_syscall5(
		SHADOW_SYS_MOUNT,
		(long)"devtmpfs", (long)"/dev", (long)"devtmpfs", 0, 0);
	shadow_syscall5(
		SHADOW_SYS_MOUNT,
		(long)"proc", (long)"/proc", (long)"proc", 0, 0);
	shadow_syscall5(
		SHADOW_SYS_MOUNT,
		(long)"sysfs", (long)"/sys", (long)"sysfs", 0, 0);
	shadow_syscall5(
		SHADOW_SYS_MOUNT,
		(long)"tmpfs", (long)"/tmp", (long)"tmpfs", 0, 0);

	shadow_write_text(
		1,
		"Shadow-MSM: starting static BusyBox ARMv5 shell\r\n");
	result = shadow_syscall3(
		SHADOW_SYS_EXECVE,
		(long)arguments[0],
		(long)arguments,
		(long)environment);
	shadow_write_text(
		1,
		"Shadow-MSM: BusyBox exec failed; recovery shell active (error ");
	shadow_write_unsigned(1, result < 0 ? (unsigned long)-result : 0);
	shadow_write_text(1, ")\r\n");
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
	long session_result;
	long controlling_tty_result = -1;
	const char *device = "/dev/ttySHM0";
	int using_tty = 1;

	/* Become a session leader before opening the real console TTY. */
	session_result = shadow_syscall0(SHADOW_SYS_SETSID);
	descriptor = shadow_syscall3(
		SHADOW_SYS_OPEN,
		(long)device,
		SHADOW_O_RDWR,
		0);
	if (descriptor < 0) {
		using_tty = 0;
		device = "/dev/shadowtrace";
		descriptor = shadow_syscall3(
			SHADOW_SYS_OPEN,
			(long)device,
			SHADOW_O_RDWR,
			0);
	}
	if (descriptor >= 0 && using_tty)
		controlling_tty_result = shadow_syscall3(
			SHADOW_SYS_IOCTL,
			descriptor,
			SHADOW_TIOCSCTTY,
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
		if (using_tty && session_result >= 0 &&
		    controlling_tty_result >= 0)
			shadow_write_text(
				descriptor,
				"Shadow-MSM: controlling ttySHM0 acquired\r\n");
		else if (using_tty)
			shadow_write_text(
				descriptor,
				"Shadow-MSM: ttySHM0 open; controlling-TTY "
				"claim failed\r\n");
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
		shadow_try_busybox(descriptor, device);
		shadow_write_text(
			descriptor,
			"Shadow-MSM: interactive recovery PID 1 ready\r\n"
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
