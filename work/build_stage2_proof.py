# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
import hashlib

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_LITTLE_ENDIAN


OUTPUT = Path("outputs/k3765_stage2_proof.bin")
DISASSEMBLY = Path("outputs/k3765_stage2_proof.disasm.txt")
LOAD_ADDRESS = 0x01000000

# A deliberately inert second-stage proof:
#   return (r0 XOR r1) + r2 in r0
#
# It does not access a peripheral, alter interrupt/MMU state, or loop. Returning
# through LR proves the stage-0 call gate and register passing while the
# initialized ARMPRG runtime remains alive.
source = """
    eor r0, r0, r1
    add r0, r0, r2
    bx lr
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_ARM + KS_MODE_LITTLE_ENDIAN)
encoding, _ = ks.asm(source, addr=LOAD_ADDRESS)
payload = bytes(encoding)

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_bytes(payload)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
listing = [
    f"0x{ins.address:08X}: {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}"
    for ins in md.disasm(payload, LOAD_ADDRESS)
]
DISASSEMBLY.write_text("\n".join(listing) + "\n", encoding="ascii")

print(f"load_address=0x{LOAD_ADDRESS:08X}")
print(f"size={len(payload)}")
print(f"sha256={hashlib.sha256(payload).hexdigest()}")
