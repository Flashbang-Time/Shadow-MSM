// SPDX-License-Identifier: GPL-3.0-only
/*
 * ttySHM0: RAM-only TTY/console bridge for the ZTE K3765-Z.
 *
 * The byte transport is the initialized resident ARMPRG monitor.  Linux owns
 * the line discipline, canonical input, echo, and signal handling; the
 * monitor only moves bounded byte chunks between USB and SDRAM.  No storage
 * command is reachable from this driver.
 */

#include <linux/console.h>
#include <linux/errno.h>
#include <linux/interrupt.h>
#include <linux/minmax.h>
#include <linux/module.h>
#include <linux/shadow_msm_trace.h>
#include <linux/string.h>
#include <linux/tty.h>
#include <linux/tty_driver.h>
#include <linux/tty_flip.h>
#include <linux/tty_port.h>
#include <linux/workqueue.h>

#define SHADOW_TTY_MAJOR	241
#define SHADOW_TTY_MINORS	1
#define SHADOW_TTY_TX_CHUNK	96U
#define SHADOW_TTY_RX_CHUNK	64U
#define SHADOW_TTY_WRITE_ROOM	4096U
#define SHADOW_TTY_POLL_DELAY	1U

struct shadow_tty_state {
	struct tty_port port;
	struct delayed_work poll_work;
	bool polling;
};

static struct shadow_tty_state shadow_tty;
static struct tty_driver *shadow_tty_driver;

static void shadow_tty_emit(const unsigned char *buffer, unsigned int count)
{
	char message[SHADOW_TTY_TX_CHUNK + 1];

	while (count) {
		unsigned int chunk = min_t(unsigned int, count,
					   SHADOW_TTY_TX_CHUNK);

		memcpy(message, buffer, chunk);
		message[chunk] = '\0';
		shadow_msm_diag_emit(message);
		buffer += chunk;
		count -= chunk;
	}
}

static void shadow_tty_poll(struct work_struct *work)
{
	struct shadow_tty_state *state = container_of(
		to_delayed_work(work), struct shadow_tty_state, poll_work);
	unsigned char input[SHADOW_TTY_RX_CHUNK];
	int room;
	size_t count;

	if (!READ_ONCE(state->polling))
		return;

	room = tty_buffer_request_room(&state->port, sizeof(input));
	if (room > 0) {
		count = shadow_msm_diag_receive(input,
					min_t(size_t, room, sizeof(input)));
		if (count) {
			tty_insert_flip_string(&state->port, input, count);
			tty_flip_buffer_push(&state->port);
		}
	}

	if (READ_ONCE(state->polling))
		schedule_delayed_work(&state->poll_work,
				      SHADOW_TTY_POLL_DELAY);
}

static int shadow_tty_activate(struct tty_port *port, struct tty_struct *tty)
{
	struct shadow_tty_state *state = container_of(
		port, struct shadow_tty_state, port);

	shadow_msm_diag_input_reset();
	WRITE_ONCE(state->polling, true);
	schedule_delayed_work(&state->poll_work, 0);
	shadow_msm_diag_emit("Shadow-MSM: ttySHM0 activated\r\n");
	return 0;
}

static void shadow_tty_shutdown(struct tty_port *port)
{
	struct shadow_tty_state *state = container_of(
		port, struct shadow_tty_state, port);

	WRITE_ONCE(state->polling, false);
	cancel_delayed_work_sync(&state->poll_work);
}

static const struct tty_port_operations shadow_tty_port_operations = {
	.activate = shadow_tty_activate,
	.shutdown = shadow_tty_shutdown,
};

static int shadow_tty_open(struct tty_struct *tty, struct file *file)
{
	tty->driver_data = &shadow_tty;
	return tty_port_open(&shadow_tty.port, tty, file);
}

static void shadow_tty_close(struct tty_struct *tty, struct file *file)
{
	struct shadow_tty_state *state = tty->driver_data;

	tty_port_close(&state->port, tty, file);
}

static void shadow_tty_hangup(struct tty_struct *tty)
{
	struct shadow_tty_state *state = tty->driver_data;

	tty_port_hangup(&state->port);
}

static int shadow_tty_write(struct tty_struct *tty,
			    const unsigned char *buffer, int count)
{
	if (count > 0)
		shadow_tty_emit(buffer, count);
	return count;
}

static unsigned int shadow_tty_write_room(struct tty_struct *tty)
{
	return SHADOW_TTY_WRITE_ROOM;
}

static unsigned int shadow_tty_chars_in_buffer(struct tty_struct *tty)
{
	return 0;
}

static int shadow_tty_ioctl(struct tty_struct *tty, unsigned int command,
			    unsigned long argument)
{
	(void)argument;
	if (command == SHADOW_MSM_KEEPALIVE_IOCTL)
		return (int)shadow_msm_keepalive();
	return -ENOIOCTLCMD;
}

static const struct tty_operations shadow_tty_operations = {
	.open = shadow_tty_open,
	.close = shadow_tty_close,
	.write = shadow_tty_write,
	.write_room = shadow_tty_write_room,
	.chars_in_buffer = shadow_tty_chars_in_buffer,
	.ioctl = shadow_tty_ioctl,
	.hangup = shadow_tty_hangup,
};

static struct tty_driver *shadow_console_device(struct console *console,
						int *index)
{
	*index = 0;
	return shadow_tty_driver;
}

static int shadow_console_setup(struct console *console, char *options)
{
	if (console->index > 0)
		return -ENODEV;
	console->index = 0;
	return 0;
}

static void shadow_console_write(struct console *console, const char *buffer,
				 unsigned int count)
{
	/* The borrowed polling transport is deliberately process-context only. */
	if (in_interrupt() || !count)
		return;
	shadow_tty_emit((const unsigned char *)buffer, count);
}

static struct console shadow_console = {
	.name = "ttySHM",
	.write = shadow_console_write,
	.device = shadow_console_device,
	.setup = shadow_console_setup,
	.flags = CON_PRINTBUFFER,
	.index = -1,
};

static int __init shadow_tty_init(void)
{
	int result;

	shadow_tty_driver = tty_alloc_driver(
		SHADOW_TTY_MINORS,
		TTY_DRIVER_RESET_TERMIOS | TTY_DRIVER_REAL_RAW);
	if (IS_ERR(shadow_tty_driver))
		return PTR_ERR(shadow_tty_driver);

	tty_port_init(&shadow_tty.port);
	shadow_tty.port.ops = &shadow_tty_port_operations;
	INIT_DELAYED_WORK(&shadow_tty.poll_work, shadow_tty_poll);

	shadow_tty_driver->driver_name = "shadow-msm-tty";
	shadow_tty_driver->name = "ttySHM";
	shadow_tty_driver->major = SHADOW_TTY_MAJOR;
	shadow_tty_driver->minor_start = 0;
	shadow_tty_driver->type = TTY_DRIVER_TYPE_CONSOLE;
	shadow_tty_driver->subtype = SYSTEM_TYPE_CONSOLE;
	shadow_tty_driver->init_termios = tty_std_termios;
	shadow_tty_driver->init_termios.c_cflag =
		B115200 | CS8 | CREAD | CLOCAL;
	shadow_tty_driver->init_termios.c_iflag = ICRNL | IXON;
	shadow_tty_driver->init_termios.c_oflag = OPOST | ONLCR;
	shadow_tty_driver->init_termios.c_lflag =
		ISIG | ICANON | ECHO | ECHOE | ECHOK | ECHOCTL | IEXTEN;
	tty_set_operations(shadow_tty_driver, &shadow_tty_operations);
	tty_port_link_device(&shadow_tty.port, shadow_tty_driver, 0);

	result = tty_register_driver(shadow_tty_driver);
	if (result) {
		tty_port_destroy(&shadow_tty.port);
		tty_driver_kref_put(shadow_tty_driver);
		return result;
	}

	register_console(&shadow_console);
	shadow_msm_diag_emit(
		"Shadow-MSM: ttySHM0 Linux TTY console registered\r\n");
	return 0;
}
device_initcall(shadow_tty_init);

static void __exit shadow_tty_exit(void)
{
	unregister_console(&shadow_console);
	tty_unregister_driver(shadow_tty_driver);
	tty_driver_kref_put(shadow_tty_driver);
	tty_port_destroy(&shadow_tty.port);
}
module_exit(shadow_tty_exit);

MODULE_DESCRIPTION("Shadow-MSM RAM-only TTY console");
MODULE_LICENSE("GPL");
