# 8-Bit Computer Emulator

A complete software emulation of the custom 8-bit computer hardware.

## Quick Start

```bash
# Run with GUI (default)
python main.py program.bin

# Run without GUI
python main.py program.bin --no-gui

# Run in unsigned mode
python main.py program.bin --unsigned
```

## Structure

- `main.py` - Entry point and command-line interface
- `core/` - CPU emulation engine (registers, ALU, memory, decoder)
- `gui/` - Graphical user interface (main window, widgets)
- `utils/` - Helper utilities (program loader, common functions)

## Documentation

Complete documentation is available in the `/Docs` folder:
- `EmulatorReadme.md` - Detailed usage guide
- `DisplayImplementation.md` - 7-segment display implementation
- `SignedModeDefault.md` - Signed/unsigned mode explanation

## Requirements

- Python 3.6+
- tkinter (usually included with Python)