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
OUTPUT = Path("outputs/armprg_pmic_led_control.bin")
DISASSEMBLY = Path("outputs/armprg_pmic_led_control.disasm.txt")

stock = SOURCE.read_bytes()
source_sha256 = hashlib.sha256(stock).hexdigest()
if len(stock) != EXPECTED_SOURCE_SIZE or source_sha256 != EXPECTED_SOURCE_SHA256:
    raise SystemExit(
        "firmware/armprg.bin does not match the verified K3765-Z programmer "
        f"(size={len(stock):,}, sha256={source_sha256})"
    )
data = bytearray(stock)
handler_addr = 0x00810DBC
handler_offset = handler_addr - 0x00800000
message_addr = 0x0081763C
message_offset = message_addr - 0x00800000

# The stock pre-initialization dispatcher calls 0x00810DBC for unsupported
# commands. Replace that handler in place and retain ARMPRG's normal runtime.
#
# Host payload:
#   1C 00 -> both channels off
#   1C 01 -> channel 0 at 15, channel 1 off
#   1C 02 -> channel 0 off, channel 1 at 15
#   1C 03 -> both channels at 15
#
# OEMSBL 0x00042B78 validates channel 0/1 and intensity 0..15, then performs
# masked writes to PMIC register 0x48. No NAND routine is referenced.
asm_source = f"""
    push {{r4, lr}}
    ldrb r4, [r0, #7]
    cmp r4, #1
    beq channel0
    cmp r4, #2
    beq channel1
    cmp r4, #3
    beq both

off:
    mov r0, #0
    mov r1, #0
    bl 0x00042B78
    mov r0, #1
    mov r1, #0
    bl 0x00042B78
    b reply

channel0:
    mov r0, #0
    mov r1, #15
    bl 0x00042B78
    mov r0, #1
    mov r1, #0
    bl 0x00042B78
    b reply

channel1:
    mov r0, #0
    mov r1, #0
    bl 0x00042B78
    mov r0, #1
    mov r1, #15
    bl 0x00042B78
    b reply

both:
    mov r0, #0
    mov r1, #15
    bl 0x00042B78
    mov r0, #1
    mov r1, #15
    bl 0x00042B78

reply:
    mov r0, #6
    ldr r1, =0x{message_addr:08X}
    bl 0x00816398
    mov r0, #0
    pop {{r4, pc}}
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(asm_source, addr=handler_addr)
handler = bytes(encoding)

# Keep the replacement before the next handler that remains in the table.
limit_addr = 0x00810F34
if handler_addr + len(handler) > limit_addr:
    raise SystemExit("LED handler overlaps the preserved 0x00810F34 handler")

data[handler_offset : handler_offset + len(handler)] = handler

old_message = b"Invalid Command\x00"
if data[message_offset : message_offset + len(old_message)] != old_message:
    raise SystemExit("stock diagnostic string did not match")
data[message_offset : message_offset + len(old_message)] = b"LED_OK\x00".ljust(
    len(old_message), b"\x00"
)

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_bytes(data)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(handler, handler_addr)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

print(f"size={len(data)}")
print(f"handler_size={len(handler)}")
print(f"handler_range=0x{handler_addr:08X}-0x{handler_addr + len(handler) - 1:08X}")
print(f"sha256={hashlib.sha256(data).hexdigest()}")
