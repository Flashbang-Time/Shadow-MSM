# Local firmware input

Shadow-MSM does not redistribute Qualcomm, ZTE, Vodafone, or other vendor
firmware.

To build the stage-0 monitor and LED test runtimes, extract the matching
`armprg.bin` from a legally obtained K3765-Z stock updater and place it here:

```text
firmware/armprg.bin
```

The builders accept only the programmer verified during development:

```text
Size:    105,928 bytes
SHA-256: 3e8339725a77d416de292ac1506cd5d4b4fedc8937bda00a4ddf0437500c6b83
```

The firmware file is ignored by Git. Do not force-add it to a public
repository.

Although I will provide a publicly available firmware package [here.](https://rebyte.me/en/zte/95143/file-604028/)
