# Shadow-MSM

**Shadow-MSM** is a unified, non-persistent development framework for Qualcomm MSM6290 basebands. It provides an out-of-band execution environment designed to turn proprietary modem hardware into a fully controllable, Linux-capable research platform without modifying the onboard NAND flash.

By leveraging custom DLOAD protocol hooks, Shadow-MSM enables stable, RAM-resident bootloader staging and low-level hardware exploration.

---

## Architecture

The framework is divided into two primary domains to ensure modular development:

* **`/bootloader`**: Contains the ARM926EJ-S native code (BL1/Stage-0 stubs) responsible for hardware initialization and execution within the verified `0x01000000` RAM window.
* **`/tools`**: A host-side Python orchestration suite. It manages DLOAD handshake synchronization, automated device resets, payload injection, and binary integrity verification (CRC32).
* **`/docs`**: Comprehensive documentation, including PMIC (PM6658) register mappings, hardware pinouts, and detailed breakdowns of the proprietary DLOAD/HDLC protocols.

---

## Key Features

* **Non-Destructive Execution**: Entirely RAM-resident; the factory NAND remains untouched and the device is never permanently altered.
* **Automated Workflow**: Includes an automated reset and injection loop, eliminating the need for physical USB intervention during the development cycle.
* **Integrity Focused**: Built-in CRC32 verification to ensure payload stability before jumping to execution.
* **Linux-Ready**: Designed as the foundational layer for booting custom kernels on the MSM6290.

---

## Getting Started

1. **Dependencies**: Ensure your environment has the necessary serial/USB headers for DLOAD communication.
2. **Toolchain**: Use the provided Python scripts in `/tools` to initialize the DLOAD handshake.
3. **Staging**: Deploy the BL1 stub to the target RAM window to establish the Shadow-MSM monitor.
4. **Execution**: Once the integrity check verifies the binary, execute the jump to the entry point at `0x01000000`.

---

## License

Shadow-MSM is licensed under the **GNU General Public License v3.0 (GPLv3)**. 

See the `LICENSE` file for more information.

---

*Developed for the K3765-Z and compatible MSM6290 platforms.*
