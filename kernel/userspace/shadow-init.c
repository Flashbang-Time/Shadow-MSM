// SPDX-License-Identifier: GPL-3.0-only
/*
 * Minimal freestanding PID 1 for the Shadow-MSM RAM-only Linux probe.
 *
 * This binary uses only ARM EABI system calls.  It writes its boot identity
 * and a bounded-rate heartbeat to /dev/shadowtrace, then remains PID 1
 * forever.  It has no filesystem, NAND, network, or process-launching code.
 */

#define SHADOW_SYS_WRITE	4
#define SHADOW_SYS_OPEN		5
#define SHADOW_SYS_UNAME	122
#define SHADOW_SYS_NANOSLEEP	162

#define SHADOW_O_WRONLY		1
#define SHADOW_UTS_LENGTH	65

struct shadow_timespec {
	long seconds;
	long nanoseconds;
};

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

void _start(void)
{
	static const struct shadow_timespec heartbeat_period = {
		.seconds = 1,
		.nanoseconds = 0,
	};
	static struct shadow_utsname identity;
	long descriptor;

	descriptor = shadow_syscall3(
		SHADOW_SYS_OPEN,
		(long)"/dev/shadowtrace",
		SHADOW_O_WRONLY,
		0);

	if (descriptor >= 0) {
		shadow_write_text(
			descriptor,
			"Shadow-MSM: entered freestanding PID 1 userspace\r\n");

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
	}

	for (;;) {
		shadow_syscall2(
			SHADOW_SYS_NANOSLEEP,
			(long)&heartbeat_period,
			0);
		if (descriptor >= 0)
			shadow_write_text(
				descriptor,
				"Shadow-MSM: PID 1 heartbeat\r\n");
	}
}
