# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
import hashlib
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


SOURCE = Path("firmware/armprg.bin")
EXPECTED_SOURCE_SIZE = 105_928
EXPECTED_SOURCE_SHA256 = (
    "3e8339725a77d416de292ac1506cd5d4b4fedc8937bda00a4ddf0437500c6b83"
)
OUTPUT = Path("outputs/armprg_stage0_monitor.bin")
DISASSEMBLY = Path("outputs/armprg_stage0_monitor.disasm.txt")

STOCK_LOAD_BASE = 0x00800000
# Command 0x1C is known from the RGB tests to enter the stock unsupported-command
# callback at 0x00810DBC with r0 pointing at the decoded packet. Keep that proven
# ABI: replace its first instruction with a branch into a larger reclaimed area.
TRAMPOLINE_ADDR = 0x00810DBC
TRAMPOLINE_OFFSET = TRAMPOLINE_ADDR - STOCK_LOAD_BASE

# Reclaim the contiguous command-0x03/0x05/0x07 handler group for the monitor.
# Those handlers are not used by the stage-0 host.
HANDLER_ADDR = 0x00811374
HANDLER_OFFSET = HANDLER_ADDR - STOCK_LOAD_BASE
INPUT_HANDLER_ADDR = 0x00811594
INPUT_HANDLER_OFFSET = INPUT_HANDLER_ADDR - STOCK_LOAD_BASE
# Command 0x09 is not used by the RAM-only monitor. Reclaim only its isolated
# handler and helpers, stopping before the active USB vtable function at
# 0x00811778. Raw pointer and direct-branch scans of the verified programmer
# show no other callers into this interval.
NEXT_PRESERVED_FUNCTION = 0x00811778
BANNER_ADDR = 0x00811768
BANNER_OFFSET = BANNER_ADDR - STOCK_LOAD_BASE
BANNER = b"K3765-S0-V1\x00"

# The final reserved monitor page is shared with Linux as a one-way host-input
# ring. Both sides touch it only through the resident non-cacheable identity
# mapping, avoiding a cacheable/non-cacheable alias.
INPUT_MAILBOX_ADDR = 0x008FF800
INPUT_MAILBOX_MAGIC = 0x534D494E  # "SMIN"
INPUT_RING_MASK = 0xFF
INPUT_PACKET_LIMIT = 64

COMMAND_TABLE_ADDR = 0x00819700
COMMAND_TABLE_OFFSET = COMMAND_TABLE_ADDR - STOCK_LOAD_BASE
COMMAND_TABLE_ENTRIES = 28

MESSAGE_ADDR = 0x0081763C
MESSAGE_OFFSET = MESSAGE_ADDR - STOCK_LOAD_BASE
HEX_TABLE_ADDR = 0x008175C6
PRINT_STRING = 0x00816CF4

SAFE_RAM_START = 0x01000000
SAFE_RAM_END = 0x02000000

stock = SOURCE.read_bytes()
source_sha256 = hashlib.sha256(stock).hexdigest()
if len(stock) != EXPECTED_SOURCE_SIZE or source_sha256 != EXPECTED_SOURCE_SHA256:
    raise SystemExit(
        "firmware/armprg.bin does not match the verified K3765-Z programmer "
        f"(size={len(stock):,}, sha256={source_sha256})"
    )
data = bytearray(stock)

# Command 0x1C is routed to the stock invalid-command callback during the
# initialized ARMPRG session. Replace that callback in-place.
#
# Packet payload:
#   1C 00                         banner
#   1C 01..0B                    CPU/system-register query
#   1C 0C <addr:u32> <len:u32>   CRC32 over bounded SDRAM
#   1C 0D <pc:u32> <r0> <r1> <r2> call bounded ARM second stage
#   1C 0E <bytes...>              enqueue host input for Linux PID 1
#
# All multibyte host fields are little-endian. CRC/call addresses are limited
# to 0x01000000..0x01FFFFFF. The callback has no NAND command or controller
# reference.
asm_source = f"""
    push {{r4, r5, r6, lr}}
    mov r4, r0
    ldrh r5, [r4, #4]
    cmp r5, #2
    blo bad
    ldrb r5, [r4, #6]
    cmp r5, #0x1C
    bne bad
    ldrb r5, [r4, #7]

    cmp r5, #0
    beq banner
    cmp r5, #1
    beq get_midr
    cmp r5, #2
    beq get_ctr
    cmp r5, #3
    beq get_tcmtr
    cmp r5, #4
    beq get_cpsr
    cmp r5, #5
    beq get_sctlr
    cmp r5, #6
    beq get_ttbr
    cmp r5, #7
    beq get_dacr
    cmp r5, #8
    beq get_dfsr
    cmp r5, #9
    beq get_ifsr
    cmp r5, #10
    beq get_far
    cmp r5, #11
    beq get_sp
    cmp r5, #12
    beq crc32_range
    cmp r5, #13
    beq call_stage2
    cmp r5, #14
    beq mailbox_input
    ldr r0, =0xBAD00000
    b reply_hex

mailbox_input:
    b 0x{INPUT_HANDLER_ADDR:08X}

banner:
    ldr r0, =0x{BANNER_ADDR:08X}
    bl 0x{PRINT_STRING:08X}
    b success

get_midr:
    mrc p15, 0, r0, c0, c0, 0
    b reply_hex
get_ctr:
    mrc p15, 0, r0, c0, c0, 1
    b reply_hex
get_tcmtr:
    mrc p15, 0, r0, c0, c0, 2
    b reply_hex
get_cpsr:
    mrs r0, cpsr
    b reply_hex
get_sctlr:
    mrc p15, 0, r0, c1, c0, 0
    b reply_hex
get_ttbr:
    mrc p15, 0, r0, c2, c0, 0
    b reply_hex
get_dacr:
    mrc p15, 0, r0, c3, c0, 0
    b reply_hex
get_dfsr:
    mrc p15, 0, r0, c5, c0, 0
    b reply_hex
get_ifsr:
    mrc p15, 0, r0, c5, c0, 1
    b reply_hex
get_far:
    mrc p15, 0, r0, c6, c0, 0
    b reply_hex
get_sp:
    mov r0, sp
    b reply_hex

crc32_range:
    ldr r1, [r4, #8]
    ldr r2, [r4, #12]
    ldr r3, =0x{SAFE_RAM_START:08X}
    cmp r1, r3
    blo bad
    adds r3, r1, r2
    bcs bad
    ldr r6, =0x{SAFE_RAM_END:08X}
    cmp r3, r6
    bhi bad
    mvn r0, #0
    ldr r6, =0xEDB88320
crc_byte:
    cmp r2, #0
    beq crc_done
    ldrb r3, [r1], #1
    eor r0, r0, r3
    mov r5, #8
crc_bit:
    tst r0, #1
    mov r0, r0, lsr #1
    eorne r0, r0, r6
    subs r5, r5, #1
    bne crc_bit
    subs r2, r2, #1
    b crc_byte
crc_done:
    mvn r0, r0
    b reply_hex

call_stage2:
    ldr r6, [r4, #8]
    tst r6, #3
    bne bad
    ldr r5, =0x{SAFE_RAM_START:08X}
    cmp r6, r5
    blo bad
    ldr r5, =0x{SAFE_RAM_END:08X}
    cmp r6, r5
    bhs bad
    ldr r0, [r4, #12]
    ldr r1, [r4, #16]
    ldr r2, [r4, #20]
    blx r6
    b reply_hex

bad:
    ldr r0, =0xBAD00001

reply_hex:
    ldr r1, =0x{MESSAGE_ADDR:08X}
    ldr r2, =0x{HEX_TABLE_ADDR:08X}
    mov r3, #8
hex_loop:
    mov r5, r0, lsr #28
    ldrb r5, [r2, r5]
    strb r5, [r1], #1
    mov r0, r0, lsl #4
    subs r3, r3, #1
    bne hex_loop
    mov r5, #0
    strb r5, [r1]
    ldr r0, =0x{MESSAGE_ADDR:08X}
    bl 0x{PRINT_STRING:08X}

success:
    mov r0, #0
    pop {{r4, r5, r6, pc}}
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(asm_source, addr=HANDLER_ADDR)
handler = bytes(encoding)

if HANDLER_ADDR + len(handler) > INPUT_HANDLER_ADDR:
    raise SystemExit(
        f"stage-0 handler is {len(handler)} bytes and overlaps "
        f"input extension at 0x{INPUT_HANDLER_ADDR:08X}"
    )

input_source = f"""
    ldr r0, =0x{INPUT_MAILBOX_ADDR:08X}
    ldr r1, [r0]
    ldr r6, =0x{INPUT_MAILBOX_MAGIC:08X}
    cmp r1, r6
    beq mailbox_ready
    str r6, [r0]
    mov r1, #0
    str r1, [r0, #4]
    str r1, [r0, #8]

mailbox_ready:
    ldrh r2, [r4, #4]
    cmp r2, #2
    bls mailbox_done
    sub r2, r2, #2
    cmp r2, #{INPUT_PACKET_LIMIT}
    movhi r2, #{INPUT_PACKET_LIMIT}
    add r4, r4, #8
    ldr r3, [r0, #4]
    ldr r5, [r0, #8]

mailbox_loop:
    add r6, r3, #1
    and r6, r6, #0x{INPUT_RING_MASK:02X}
    cmp r6, r5
    beq mailbox_commit
    ldrb r1, [r4], #1
    add ip, r0, #12
    strb r1, [ip, r3]
    mov r3, r6
    subs r2, r2, #1
    bne mailbox_loop

mailbox_commit:
    str r3, [r0, #4]

mailbox_done:
    mov r0, #0
    pop {{r4, r5, r6, pc}}
"""
input_encoding, _ = ks.asm(input_source, addr=INPUT_HANDLER_ADDR)
input_handler = bytes(input_encoding)
if INPUT_HANDLER_ADDR + len(input_handler) > BANNER_ADDR:
    raise SystemExit(
        f"input handler is {len(input_handler)} bytes and overlaps "
        f"banner at 0x{BANNER_ADDR:08X}"
    )

trampoline, _ = ks.asm(f"b 0x{HANDLER_ADDR:08X}", addr=TRAMPOLINE_ADDR)
trampoline = bytes(trampoline)
if len(trampoline) != 4:
    raise SystemExit("stage-0 trampoline was not one ARM instruction")

if BANNER_ADDR + len(BANNER) > NEXT_PRESERVED_FUNCTION:
    raise SystemExit("stage-0 banner overlaps active USB vtable function")

data[TRAMPOLINE_OFFSET : TRAMPOLINE_OFFSET + len(trampoline)] = trampoline
data[HANDLER_OFFSET : HANDLER_OFFSET + len(handler)] = handler
data[
    INPUT_HANDLER_OFFSET : INPUT_HANDLER_OFFSET + len(input_handler)
] = input_handler
data[BANNER_OFFSET : BANNER_OFFSET + len(BANNER)] = BANNER

# Remove every path from the live dispatcher to the stock storage handlers.
# All 28 protocol commands now enter the bounded Shadow-MSM callback, whose
# first operation rejects every command byte except 0x1c.
for index in range(COMMAND_TABLE_ENTRIES):
    offset = COMMAND_TABLE_OFFSET + index * 4
    original = struct.unpack_from("<I", stock, offset)[0]
    if not STOCK_LOAD_BASE <= original < STOCK_LOAD_BASE + len(stock):
        raise SystemExit(
            f"command table entry {index + 1} is not a verified code pointer: "
            f"0x{original:08X}"
        )
    struct.pack_into("<I", data, offset, HANDLER_ADDR)

old_message = b"Invalid Command\x00"
if data[MESSAGE_OFFSET : MESSAGE_OFFSET + len(old_message)] != old_message:
    raise SystemExit("stock diagnostic string did not match")
data[MESSAGE_OFFSET : MESSAGE_OFFSET + len(old_message)] = b"00000000\x00".ljust(
    len(old_message), b"\x00"
)

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_bytes(data)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(handler, HANDLER_ADDR)
]
listing.extend(("", "input mailbox extension:"))
listing.extend(
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(input_handler, INPUT_HANDLER_ADDR)
)
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

changed = [index for index, (a, b) in enumerate(zip(stock, data)) if a != b]
allowed = set(
    range(HANDLER_OFFSET, HANDLER_OFFSET + len(handler))
) | set(
    range(TRAMPOLINE_OFFSET, TRAMPOLINE_OFFSET + len(trampoline))
) | set(
    range(INPUT_HANDLER_OFFSET, INPUT_HANDLER_OFFSET + len(input_handler))
) | set(
    range(BANNER_OFFSET, BANNER_OFFSET + len(BANNER))
) | set(
    range(
        COMMAND_TABLE_OFFSET,
        COMMAND_TABLE_OFFSET + COMMAND_TABLE_ENTRIES * 4,
    )
) | set(range(MESSAGE_OFFSET, MESSAGE_OFFSET + len(old_message))) | set(
    ()
)
outside = [index for index in changed if index not in allowed]
if outside:
    raise SystemExit(f"unexpected changes outside patch regions: {outside[:8]}")

print(f"stock_size={len(stock)}")
print(f"output_size={len(data)}")
print(f"handler_size={len(handler)}")
print(
    f"handler_range=0x{HANDLER_ADDR:08X}-"
    f"0x{HANDLER_ADDR + len(handler) - 1:08X}"
)
print(f"input_handler_size={len(input_handler)}")
print(
    f"input_handler_range=0x{INPUT_HANDLER_ADDR:08X}-"
    f"0x{INPUT_HANDLER_ADDR + len(input_handler) - 1:08X}"
)
print(f"input_mailbox=0x{INPUT_MAILBOX_ADDR:08X}")
print(f"command_table_entries_locked={COMMAND_TABLE_ENTRIES}")
print(f"changed_bytes={len(changed)}")
print(f"sha256={hashlib.sha256(data).hexdigest()}")
