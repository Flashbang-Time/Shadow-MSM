# Upstream Neofetch provenance

`neofetch` is copied byte-for-byte from the official archived repository:

- Repository: `https://github.com/dylanaraps/neofetch`
- Commit: `ccd5d9f52609bbdcd5d8fa78c4fdb0f12954125f`
- Version reported by the script: `Neofetch 7.1.0`
- Git blob: `48b96d215e38fb8e3750b68833229057153ca7a6`
- SHA-256: `2a272bbaa1275f21835fd3258fb8032ccdc98348e6ccb9cf58acacd366340170`
- License: MIT; see `NEOFETCH_LICENSE.md`

The LF-preserved script is byte-identical to that Git blob; it is not rewritten
or emulated. Shadow-MSM includes a static ARMEL
Bash runtime because upstream Neofetch requires Bash 3.2 or newer.

Physical K3765-Z verification on 2026-08-10 produced:

```text
GNU bash, version 5.2.37(1)-release (arm-unknown-linux-gnueabi)
Neofetch 7.1.0
```

The complete upstream ASCII and system-information display then rendered over
`ttySHM0` with the Linux kernel and payload running entirely from SDRAM.
