# Local firmware input

Shadow-MSM does not redistribute Qualcomm, ZTE, Vodafone, or other vendor
firmware.

To build the stage-0 monitor and LED test runtimes, statically extract the
matching `armprg.bin` from a legally obtained K3765-Z stock updater and place
it here:

```text
firmware/armprg.bin
```

The builders accept only the programmer verified during development:

```text
Size:    105,928 bytes
SHA-256: 3e8339725a77d416de292ac1506cd5d4b4fedc8937bda00a4ddf0437500c6b83
```

In the verified Vodafone updater, this file is the PE resource mapped by the
updater as:

```text
SOURCEMBN resource 165 -> armprg.bin
```

Do not run the updater merely to obtain the file. Extract its PE resources
statically, preserve the original package unchanged, and verify the resulting
programmer before building:

```powershell
(Get-Item .\firmware\armprg.bin).Length
Get-FileHash .\firmware\armprg.bin -Algorithm SHA256
```

`armprg.bin` is used only as a hash-verified local build input. The generated
stage-0 monitor remains RAM-resident. Its live 28-entry protocol dispatch
table is replaced with a single bounded Shadow-MSM handler, which rejects
every command other than `0x1c`. Linux terminal input uses only subcommand
`0x0e` and a 256-byte ring inside the device tree's reserved monitor RAM.
The current host tools contain no NAND erase or program implementation.

The firmware file and generated OEM-derived runtime are ignored by Git. Do
not force-add either one to a public repository. Only original Shadow-MSM
source, documentation, hashes, maps, and user-produced test logs belong in
the public tree.
I also provide a
[public mirror of the matching firmware package](https://rebyte.me/en/zte/95143/file-604028/).
Treat mirrors as untrusted input and verify the extracted programmer against
the size and SHA-256 above before building.
