# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


SOURCE = Path("firmware/armprg.bin")
EXPECTED_SOURCE_SIZE = 105_928
EXPECTED_SOURCE_SHA256 = (
    "3e8339725a77d416de292ac1506cd5d4b4fedc8937bda00a4ddf0437500c6b83"
)
OUTPUT = Path("outputs/armprg_rgb_control.bin")
DISASSEMBLY = Path("outputs/armprg_rgb_control.disasm.txt")

STOCK_LOAD_BASE = 0x00800000
HANDLER_ADDR = 0x00810DBC
HANDLER_OFFSET = HANDLER_ADDR - STOCK_LOAD_BASE
NEXT_HANDLER_ADDR = 0x00810F34
MESSAGE_ADDR = 0x0081763C
MESSAGE_OFFSET = MESSAGE_ADDR - STOCK_LOAD_BASE

PM_LED_INTENSITY = 0x00042B78
PM_MPP_I_SINK = 0x0003ED0C

stock = SOURCE.read_bytes()
source_sha256 = hashlib.sha256(stock).hexdigest()
if len(stock) != EXPECTED_SOURCE_SIZE or source_sha256 != EXPECTED_SOURCE_SHA256:
    raise SystemExit(
        "firmware/armprg.bin does not match the verified K3765-Z programmer "
        f"(size={len(stock):,}, sha256={source_sha256})"
    )
data = bytearray(stock)

# The stock pre-initialization dispatcher routes unsupported packets to the
# handler at 0x00810DBC. Replace that handler in place while preserving the
# entire initialized ARMPRG USB/watchdog runtime.
#
# Host packet:
#   1C MM
#
# MM is a four-bit output mask:
#   bit 0: PMIC LED channel 0 (observed green)
#   bit 1: PMIC LED channel 1 (observed blue)
#   bit 2: PMIC MPP current sink 1 (red candidate)
#   bit 3: PMIC MPP current sink 3 (red candidate)
#
# The MPP current level is held at the conservative stock test value 2. The
# output switch alone is changed between OFF (0) and ON (1). No NAND routine
# or NAND controller address is referenced by this callback.
asm_source = f"""
    push {{r4, lr}}
    ldrb r4, [r0, #7]
    and r4, r4, #15

    mov r0, #0
    tst r4, #1
    movne r1, #15
    moveq r1, #0
    bl 0x{PM_LED_INTENSITY:08X}

    mov r0, #1
    tst r4, #2
    movne r1, #15
    moveq r1, #0
    bl 0x{PM_LED_INTENSITY:08X}

    mov r0, #1
    mov r1, #2
    tst r4, #4
    movne r2, #1
    moveq r2, #0
    bl 0x{PM_MPP_I_SINK:08X}

    mov r0, #3
    mov r1, #2
    tst r4, #8
    movne r2, #1
    moveq r2, #0
    bl 0x{PM_MPP_I_SINK:08X}

    mov r0, #6
    ldr r1, =0x{MESSAGE_ADDR:08X}
    bl 0x00816398
    mov r0, #0
    pop {{r4, pc}}
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(asm_source, addr=HANDLER_ADDR)
handler = bytes(encoding)

if HANDLER_ADDR + len(handler) > NEXT_HANDLER_ADDR:
    raise SystemExit("RGB handler overlaps the next preserved stock handler")

data[HANDLER_OFFSET : HANDLER_OFFSET + len(handler)] = handler

old_message = b"Invalid Command\x00"
if data[MESSAGE_OFFSET : MESSAGE_OFFSET + len(old_message)] != old_message:
    raise SystemExit("stock diagnostic string did not match")
data[MESSAGE_OFFSET : MESSAGE_OFFSET + len(old_message)] = b"RGB_OK\x00".ljust(
    len(old_message), b"\x00"
)

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_bytes(data)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(handler, HANDLER_ADDR)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

changed = [index for index, (a, b) in enumerate(zip(stock, data)) if a != b]
allowed = set(
    range(HANDLER_OFFSET, HANDLER_OFFSET + len(handler))
) | set(range(MESSAGE_OFFSET, MESSAGE_OFFSET + len(old_message)))
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
print(f"changed_bytes={len(changed)}")
print(f"sha256={hashlib.sha256(data).hexdigest()}")
