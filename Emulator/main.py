"""
8-bit Computer Emulator
Main application entry point

Usage:
    python main.py [binary_file.bin] [options]

Examples:
    python main.py                    # Start GUI without program (signed mode default)
    python main.py program.bin        # Start GUI, load program (signed mode default)
    python main.py program.bin -u     # Start GUI, load program (unsigned mode)
"""

import sys
import os
import argparse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import EmulatorMainWindow
from utils.loader import autoLoadProgram

def main():
    parser = argparse.ArgumentParser(description = "8-bit Computer Emulator")
    parser.add_argument("program", nargs = "?", help = "Binary program file to load (.bin)")
    parser.add_argument("-ng", "--no-gui",   action = "store_true", help = "Run without GUI (command line only)")
    parser.add_argument("-d",  "--debug",    action = "store_true", help = "Enable debug output")
    parser.add_argument("-u",  "--unsigned", action = "store_true", help = "Start in unsigned mode (0 to 255)")

    args = parser.parse_args()

    # Default to signed mode (matching assembler default), use unsigned only if specified
    initialSignedMode = not args.unsigned

    if args.no_gui:
        # Simple command line mode
        if not args.program or not os.path.exists(args.program):
            print("Error: Program file is required for command line mode")
            return 1

        try:
            from core.cpu import CPU8Bit
            # autoLoadProgram is already imported at the top

            # Create CPU and load program
            cpu = CPU8Bit()
            cpu.setSignedMode(initialSignedMode)
            programData = autoLoadProgram(args.program)
            cpu.loadProgram(programData['binaryData'])

            print(f"Loaded program: {args.program}")
            print(f"Mode: {'Signed (-128 to +127)' if initialSignedMode else 'Unsigned (0 to 255)'}")
            print("Program executed successfully")
            return 0

        except Exception as e:
            print(f"Error in command line mode: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1

    try:
        # Create and start GUI
        app = EmulatorMainWindow()

        # Set initial display mode
        app.cpu.setSignedMode(initialSignedMode)
        app.sevenSegDisplay.setMode(initialSignedMode)

        # Load program if specified
        if args.program:
            if os.path.exists(args.program):
                try:
                    programData = autoLoadProgram(args.program)
                    app.cpu.loadProgram(programData['binaryData'])
                    app.updateDisplay()

                    # Load assembly source if available
                    if programData['assemblySource']:
                        app.assemblyTextbox.delete(1.0, 'end')
                        app.assemblyTextbox.insert(1.0, programData['assemblySource'])
                    # Show disassembly
                    app.showDisassembly(programData['binaryData'])

                    app.statusLabel.config(text = f"Loaded: {os.path.basename(args.program)}")

                except Exception as e:
                    print(f"Error loading program: {e}")
                    app.statusLabel.config(text = f"Failed to load: {os.path.basename(args.program)}")
            else:
                print(f"Program file not found: {args.program}")

        # Start GUI
        app.run()
        return 0

    except KeyboardInterrupt:
        print("\nEmulator interrupted by user")
        return 1
    except Exception as e:
        print(f"Error starting emulator: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
