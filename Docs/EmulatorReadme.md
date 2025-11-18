# 8-Bit Computer Emulator

A software emulator for the custom 8-bit computer, providing cycle-accurate emulation of the hardware design.

## Features

- **Complete ISA Implementation**: All 22+ instructions (NOP, ADD, SUB, MOV, JMP, etc.)
- **4 General Purpose Registers**: A, B, C, D with 8-bit capacity
- **Memory System**: ROM (2KB) and RAM (16 bytes) emulation
- **ALU Operations**: Arithmetic, Logic, and Comparison operations
- **Control Signals**: Full emulation of 32 hardware control signals
- **4-Digit 7-Segment Display**: Visual output matching hardware behavior
  - **Unsigned mode**: 0-255 (displays 0 to 255)
  - **Signed mode**: -128 to +127 (displays negative values with minus sign)
  - **Mode selection**: Dropdown to switch between modes
- **GUI Interface**: Real-time register and memory viewing
- **Debugging Tools**: Step execution, breakpoints, state inspection

## Architecture

```
Emulator/
├── core/              # CPU emulation core
│   ├── cpu.py         # Main CPU class
│   ├── alu.py         # ALU operations
│   ├── memory.py      # ROM/RAM emulation
│   ├── registers.py   # Register file
│   └── decoder.py     # Instruction decoder
├── gui/               # User interface
│   ├── main_window.py # Main GUI window
│   ├── widgets.py     # Custom widgets
│   └── display.py     # 7-segment display
├── utils/             # Utilities
│   ├── loader.py      # Binary file loader
│   └── helpers.py     # Helper functions
└── main.py            # Application entry point
```

## Usage

```bash
python main.py [binary_file.bin] [options]

Options:
  -u, --unsigned  Start in unsigned mode (0 to 255)
  --debug         Enable debug output

Note: Signed mode (-128 to +127) is the default, matching the assembler behavior.
```

## Controls

- **Run**: Execute program continuously
- **Step**: Execute one instruction
- **Reset**: Reset CPU state
- **Load**: Load new binary file

## Integration

Works seamlessly with the existing assembler:
```bash
# Compile assembly (signed mode - default)
python Compiler/Assembler.py program.s -o program.bin

# Compile assembly (unsigned mode)  
python Compiler/Assembler.py program.s -o program.bin --unsigned

# Run in emulator (signed mode - default)
python Emulator/main.py program.bin

# Run in emulator (unsigned mode)
python Emulator/main.py program.bin --unsigned
```