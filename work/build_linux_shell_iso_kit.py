#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

"""Assemble the offline Shadow-MSM K3765-Z Linux shell ISO directory."""

import argparse
from datetime import datetime
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "armprg_stage0_monitor.bin": (
        105_928,
        "588e897f46a3d7dfe4f5f989bcc85ab3b4604b4f7ccacd5d802b53be226f4f52",
    ),
    "Image-k3765-probe": (
        4_564_500,
        "60a99e09134738428dd0f3693c5bd2fd72bd8926403d9afc6b0851dab38a974f",
    ),
    "k3765_bl1_linux_image.bin": (
        5_933,
        "53bba2751e32ee044ced5522eb9676abdd38f76c2637841fd12274c2da2f64cc",
    ),
    "k3765-z-probe.dtb": (
        883,
        "1025f0a145c4c830b2e7820caea92f2a28d07177665893d172a3c87ab7fdf76e",
    ),
}

EXPECTED_DRIVER = {
    "ZTEusbdiag.cat": (
        19_183,
        "b3c8094d800433725472302769bd0deea82147d810277fa827deb81c74a34d6e",
    ),
    "zteusbdiag.inf": (
        8_050,
        "728b70e0b5710c66ca153c525af6ed726705355c084b5c936aee2333a286f3d8",
    ),
    "ZTEusbser6k.sys": (
        119_680,
        "12aa44ac32404744b0f19f1f01da29f66436860e47257a2bf63f2293e0b9fe14",
    ),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_copy(source, destination, expected=None):
    if not source.is_file():
        raise RuntimeError(f"missing source file: {source}")
    if expected is not None:
        expected_size, expected_hash = expected
        actual_size = source.stat().st_size
        actual_hash = sha256(source)
        if actual_size != expected_size:
            raise RuntimeError(
                f"{source.name}: size {actual_size:,} != {expected_size:,}"
            )
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"{source.name}: SHA-256 {actual_hash} != {expected_hash}"
            )
    shutil.copy2(source, destination)


def find_serial_package():
    try:
        import serial
    except ImportError as error:
        raise RuntimeError(
            "pyserial 3.5 must be installed on the build workstation so it "
            "can be vendored into the offline kit"
        ) from error
    return Path(serial.__file__).resolve().parent


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        required=True,
        help="extracted successful GitHub Actions artifact directory",
    )
    parser.add_argument(
        "--monitor",
        type=Path,
        default=REPO_ROOT / "outputs" / "armprg_stage0_monitor.bin",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "build" / "Shadow-MSM-Linux-ISO",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    artifact_dir = args.artifact_dir.resolve()
    monitor = args.monitor.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(
            f"refusing to overwrite existing output directory: {output}"
        )
    output.mkdir(parents=True)

    files = {
        "SHADOW_MSM_BOOT.py": REPO_ROOT / "outputs" / "k3765_linux_shell.py",
        "README.md": REPO_ROOT / "outputs" / "LINUX_SHELL_ISO_README.md",
        "LICENSE-GPLv3.txt": REPO_ROOT / "LICENSE",
        "armprg_stage0_monitor.bin": monitor,
        "Image-k3765-probe": artifact_dir / "Image-k3765-probe",
        "k3765_bl1_linux_image.bin": (
            artifact_dir / "k3765_bl1_linux_image.bin"
        ),
        "k3765-z-probe.dtb": artifact_dir / "k3765-z-probe.dtb",
        "ARTIFACTS.txt": artifact_dir / "ARTIFACTS.txt",
    }
    for destination_name, source in files.items():
        expected = EXPECTED.get(destination_name)
        checked_copy(source, output / destination_name, expected)

    driver_source = REPO_ROOT / "work" / "zte-download-driver"
    driver_output = output / "driver" / "zteusbdiag-2009"
    driver_output.mkdir(parents=True)
    for name, expected in EXPECTED_DRIVER.items():
        checked_copy(driver_source / name, driver_output / name, expected)
    (output / "driver" / "README.txt").write_text(
        "ZTE Diagnostics Interface driver\n"
        "Original INF: zteusbdiag.inf\n"
        "Provider: ZTE Corporation\n"
        "DriverVer: 09/18/2009,1.2059.0.7\n"
        "Supported K3765-Z personalities:\n"
        "  USB\\VID_19D2&PID_2002&MI_00 (normal diagnostics)\n"
        "  USB\\VID_19D2&PID_0016&MI_00 (legacy downloader)\n"
        "The CAT/INF/SYS files are the original signed vendor package and "
        "are not covered by Shadow-MSM's GPLv3 license.\n",
        encoding="utf-8",
    )

    serial_source = find_serial_package()
    vendor = output / "vendor"
    shutil.copytree(
        serial_source,
        vendor / "serial",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    metadata_candidates = list(
        serial_source.parent.glob("pyserial-*.dist-info/METADATA")
    )
    if metadata_candidates:
        shutil.copy2(
            metadata_candidates[0], vendor / "pyserial-METADATA.txt"
        )

    (output / "BOOT_LINUX.cmd").write_bytes((
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "py -3.9 SHADOW_MSM_BOOT.py\r\n"
        "if errorlevel 1 pause\r\n"
    ).encode("ascii"))
    (output / "ATTACH_SHELL.cmd").write_bytes((
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "py -3.9 SHADOW_MSM_BOOT.py --attach\r\n"
        "if errorlevel 1 pause\r\n"
    ).encode("ascii"))
    (output / "VERIFY_KIT.cmd").write_bytes((
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "py -3.9 -S SHADOW_MSM_BOOT.py --dry-run\r\n"
        "pause\r\n"
    ).encode("ascii"))
    (output / "INSTALL_ZTE_DRIVER.cmd").write_bytes((
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "py -3.9 SHADOW_MSM_BOOT.py --install-driver\r\n"
        "if errorlevel 1 echo Right-click this file and choose Run as administrator.\r\n"
        "pause\r\n"
    ).encode("ascii"))
    (output / "BUILD_INFO.txt").write_text(
        "Shadow-MSM K3765-Z Linux shell ISO kit\n"
        f"Built: {datetime.now().isoformat(timespec='seconds')}\n"
        f"Source commit: {git_commit()}\n"
        "Payload source: GitHub Actions run 31330993698\n"
        "Artifact ZIP SHA-256: "
        "55d257e6462a8290199f5ff5c8f52f8ed81846c1420e104f16f359d54dfe8dcb\n"
        "Linux runtime end: 0x00680D58\n"
        "Runtime-to-monitor gap: 1569448 bytes\n"
        "Runtime persistence: volatile SDRAM only\n"
        "NAND/CEFS operations: not implemented\n",
        encoding="utf-8",
    )
    checksum_lines = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        relative = path.relative_to(output).as_posix()
        checksum_lines.append(f"{sha256(path)}  {relative}")
    (output / "SHA256SUMS").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="ascii",
    )

    total = sum(path.stat().st_size for path in output.rglob("*") if path.is_file())
    print(f"output={output}")
    print(f"files={sum(1 for path in output.rglob('*') if path.is_file())}")
    print(f"bytes={total}")
    print(f"sha256sums={sha256(output / 'SHA256SUMS')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
