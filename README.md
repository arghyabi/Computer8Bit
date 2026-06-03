# 8-Bit Computer from Scratch (Built with Logic Gates)

Welcome to the documentation repository for my custom-built **8-bit computer**, constructed entirely from logic gates
and basic components. This project is a deep dive into computer architecture, taking inspiration from classic
microprocessors and educational systems, but designed from the ground up with a custom Instruction Set Architecture (ISA),
 control logic, and microcode.

![Top-Level Architecture](Images/BlockDiagram/TopLevelArchitecture.svg)

## 🔧 Project Overview

This project is about understanding and constructing the fundamental building blocks of a computer:

- Registers and ALU
- Program Counter and Memory
- Instruction Decoder and Control Unit
- Microcoded Control Logic
- Arithmetic, Logic, and Comparison Units
- Bus-based Data Architecture
- Seven-Segment Display Output

## 🧠 Key Components

- **Registers A-D**: General-purpose 8-bit registers.
- **ALU**: Supports operations like ADD, SUB, AND, OR, XOR, NOT, CMP.
- **Program Counter**: Controls instruction flow with PCI, PCC, and PCE control signals.
- **RAM**: General memory with input/output controls (MeI, MeO).
- **Microcode ROM / Control Unit**: Controls signal sequencing for instruction execution.
- **Instruction Register**: Stores the current instruction fetched from memory.
- **Temp Registers**: Temporary internal storage for multi-step operations.
- **Flag Register**: Holds status flags (Zero, Carry).
- **7-Segment Display**: Used for displaying output values in decimal format.

## 📁 Repository Structure

```
.
├── Compiler/                        # Assembler for the custom ISA
│   └── Assembler.py                 # Main assembler (uses YAML config)
├── Config.yaml                      # Central version management
├── Datasheets/                      # IC datasheets (74LS series, EEPROM)
├── Docs/                            # Documentation
│   ├── HwDesign.md                  # Hardware design details
│   ├── ISA.md                       # Instruction Set Architecture
│   ├── SignalInfo.md                # Control signals reference
│   ├── MicrocodeFlow.md             # Microcode compilation flow
│   └── *.md                         # Additional documentation
├── EepromFlasher/                   # EEPROM programming tool
│   ├── App/                         # GUI application (Python)
│   └── Firmware/                    # Arduino firmware
├── Emulator/                        # Software emulator
│   ├── main.py                      # Emulator entry point
│   ├── core/                        # CPU emulation core
│   │   ├── decoder.py               # Instruction decoder (uses YAML config)
│   │   ├── alu.py                   # ALU implementation
│   │   └── *.py                     # Other core components
│   └── gui/                         # GUI components
├── Gen7segDriver/                   # 7-segment display driver generator
├── Images/                          # Visual assets
│   ├── BlockDiagram/                # Architecture diagrams
│   └── Schematic/                   # Circuit schematics
├── Microcode/                       # Microcode generation system
│   ├── GenMicrocode.py              # Main microcode generator
│   ├── MicroCodeConfig.yaml         # Instruction definitions (single source of truth)
│   ├── Instructions/                # Individual instruction implementations
│   └── Inspector/                   # Microcode Inspection tools
└── .github/workflows/               # CI/CD automation
    └── version-check.yaml           # Version management enforcement
```

## 🛠 Features

- Complete microcoded control unit for all supported instructions.
- Instruction decoder and sequencer implemented with logic.
- Custom ISA with binary opcode support.
- Support for logic-level debugging and test forcing.
- Graphical output via 7-segment display.
- **Centralized configuration**: Single YAML file defines all instructions
- **Version management**: Automated CI/CD checks for version consistency
- **Software emulator**: Test programs without hardware
- **Professional toolchain**: Assembler, emulator, flasher, and inspector


## 🧾 Instruction Set

Documentation about the supported instructions (ADD, SUB, AND, OR, MOV, JMP, etc.) is available in the
**[`ISA.md`](Docs/ISA.md)** file.

Each instruction is defined with:
- Opcode
- Control signal sequences
- Clock cycles
- Examples


## 🛠 Control Signals
Documentation about all the control signal is available in the **[`SignalInfo.md`](Docs/SignalInfo.md)** file.

In the **[`HwDesign.md`](Docs/HwDesign.md)** file, placement of the signals ins the bus is shown visually.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PyYAML (`pip install pyyaml`)
- Optional: hexdump (`pip install hexdump`)

### Compile Assembly Code
```bash
python Compiler/Assembler.py program.S -o program.bin
```

### Run in Emulator
```bash
python main.py                          # Start GUI without program (signed mode default)
python main.py program.bin              # Start GUI, load program (signed mode default)
python main.py program.bin -u           # Start GUI, load program (unsigned mode)
python main.py program.bin -m hardware  # Start GUI, load program, use hardware mode
```
**Note**: The `-m hardware` flag enables hardware mode, which uses the actual hardware instead of the emulator. This is useful for testing the hardware implementation. The default mode is software mode.

### Generate Microcode
```bash
cd Microcode
python GenMicrocode.py
```

### Flash to EEPROM
```bash
python EepromFlasher/App/Main.py
```

## 📋 Version Management

This project uses strict version control enforced by CI/CD:

- **Config.yaml**: Central version file tracking all components
- **Automated checks**: Every PR must update relevant version numbers
- **Component tracking**: Compiler, Emulator, Flasher, ISA, Inspector, 7Segment, Document

See `.github/workflows/version-check.yaml` for implementation details.

## 📸 Visuals

- Block Diagram: `Images/BlockDiagram/TopLevelArchitecture.svg`
- Schematics: `Images/Schematic/`
- Future updates may include breadboard photos, logic analyzer screenshots, and waveforms.

## 🎯 Goals

- Learn computer architecture hands-on.
- Build a fully functional 8-bit computer using only logic gates.
- Design and implement a custom ISA.
- Create professional development tools (assembler, emulator, debugger).
- Maintain clean, documented, version-controlled codebase.

## 📬 Feedback & Contributions

This is a personal learning project, but contributions, discussions, and feedback are welcome! Feel free to open an
issue or pull request if you'd like to contribute.

### Contributing Guidelines
1. Update `Config.yaml` with new version numbers
2. Ensure all CI checks pass
3. Follow existing code style
4. Document new features

---

**Built with ❤️ from logic gates.**
