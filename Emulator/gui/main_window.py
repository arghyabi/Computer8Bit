"""
Main Window for the 8-bit Computer Emulator
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cpu import CPU8Bit
from gui.widgets import FourDigitSevenSegmentDisplay, RegisterDisplay, FlagsDisplay, MemoryDisplay, StatusDisplay

class EmulatorMainWindow:
    """Main window for the 8-bit computer emulator"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("8-bit Computer Emulator")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Initialize CPU
        self.cpu = CPU8Bit()

        # GUI state
        self.running = False
        self.stepMode = True

        # Create GUI
        self.createMenu()
        self.createWidgets()
        self.createControls()

        # Update display
        self.updateDisplay()

    def createMenu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Program...", command=self.loadProgram)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # CPU menu
        cpu_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CPU", menu=cpu_menu)
        cpu_menu.add_command(label="Reset", command=self.resetCpu)
        cpu_menu.add_command(label="Hard Reset", command=self.hardReset)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.showAbout)

    def createWidgets(self):
        """Create main GUI widgets"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - CPU state
        left_frame = tk.Frame(main_frame, relief="ridge", bd=2)
        left_frame.pack(side="left", fill="y", padx=(0,5))

        # Registers
        self.register_display = RegisterDisplay(left_frame)
        self.register_display.pack(pady=5)

        # Flags
        self.flags_display = FlagsDisplay(left_frame)
        self.flags_display.pack(pady=5)

        # Status
        self.status_display = StatusDisplay(left_frame)
        self.status_display.pack(pady=5)

        # Memory
        self.memory_display = MemoryDisplay(left_frame)
        self.memory_display.pack(pady=5, fill="both", expand=True)

        # Center panel - 7-segment display
        center_frame = tk.Frame(main_frame, relief="ridge", bd=2)
        center_frame.pack(side="left", fill="both", expand=True, padx=5)

        # 7-segment display
        display_frame = tk.Frame(center_frame)
        display_frame.pack(expand=True)

        tk.Label(display_frame, text="4-Digit 7-Segment Display", font=("Arial", 14, "bold")).pack(pady=10)
        self.sevenSegDisplay = FourDigitSevenSegmentDisplay(display_frame)
        self.sevenSegDisplay.pack(pady=20)

        # Connect display mode change to CPU mode
        self.sevenSegDisplay.mode_var.trace('w', self._on_display_mode_change)

        # Assembly code display
        code_frame = tk.LabelFrame(center_frame, text="Assembly Code", font=("Arial", 10, "bold"))
        code_frame.pack(fill="both", expand=True, pady=10)

        self.codeText = tk.Text(code_frame, width=50, height=15, font=("Courier", 9))
        code_scrollbar = tk.Scrollbar(code_frame, orient="vertical", command=self.codeText.yview)
        self.codeText.configure(yscrollcommand=code_scrollbar.set)

        self.codeText.pack(side="left", fill="both", expand=True)
        code_scrollbar.pack(side="right", fill="y")

    def createControls(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", pady=5)

        # File operations
        file_frame = tk.LabelFrame(control_frame, text="File")
        file_frame.pack(side="left", padx=5)

        tk.Button(file_frame, text="Load Program", command=self.loadProgram).pack(side="left", padx=2)

        # Execution controls
        exec_frame = tk.LabelFrame(control_frame, text="Execution")
        exec_frame.pack(side="left", padx=5)

        self.run_button = tk.Button(exec_frame, text="Run", command=self.toggleRun, bg="green", fg="white")
        self.run_button.pack(side="left", padx=2)

        tk.Button(exec_frame, text="Step", command=self.stepCpu).pack(side="left", padx=2)
        tk.Button(exec_frame, text="Reset", command=self.resetCpu).pack(side="left", padx=2)

        # Speed control
        speed_frame = tk.LabelFrame(control_frame, text="Speed")
        speed_frame.pack(side="left", padx=5)

        tk.Label(speed_frame, text="Delay (ms):").pack(side="left")
        self.speed_var = tk.StringVar(value="100")
        speed_entry = tk.Entry(speed_frame, textvariable=self.speed_var, width=8)
        speed_entry.pack(side="left", padx=2)

        # Status
        self.statusLabel = tk.Label(control_frame, text="Ready to load program",
                                    relief="sunken", anchor="w")
        self.statusLabel.pack(side="right", fill="x", expand=True, padx=5)

    def loadProgram(self):
        """Load binary program file"""
        filename = filedialog.askopenfilename(
            title="Select Program File",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'rb') as f:
                    binaryData = f.read()

                self.cpu.loadProgram(binaryData)
                self.updateDisplay()

                # Try to load corresponding assembly file for display
                asmFile = filename.replace('.bin', '.s')
                if os.path.exists(asmFile):
                    self.loadAssemblyDisplay(asmFile)
                else:
                    # Show disassembly
                    self.showDisassembly(binaryData)

                self.statusLabel.config(text=f"Loaded: {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load program:\n{e}")

    def loadAssemblyDisplay(self, filename):
        """Load assembly source for display"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
            self.codeText.delete(1.0, tk.END)
            self.codeText.insert(1.0, content)
        except:
            pass

    def showDisassembly(self, binaryData):
        """Show disassembled code"""
        try:
            instructions = self.cpu.decoder.decodeProgram(binaryData)
            self.codeText.delete(1.0, tk.END)

            self.codeText.insert(tk.END, "; Disassembly\n")
            for addr, opcode, operands, raw_bytes in instructions:
                hex_bytes = " ".join(f"{b:02X}" for b in raw_bytes)

                # Format instruction
                inst_str = opcode
                if 'source_register' in operands and 'destination_register' in operands:
                    src = self.cpu.decoder.register_name(operands['source_register'])
                    dst = self.cpu.decoder.register_name(operands['destination_register'])
                    inst_str += f" {dst} {src}"
                elif 'register' in operands:
                    reg = self.cpu.decoder.register_name(operands['register'])
                    inst_str += f" {reg}"
                    if 'immediate' in operands:
                        inst_str += f" 0x{operands['immediate']:02X}"
                elif 'address' in operands:
                    inst_str += f" 0x{operands['address']:04X}"

                line = f"{addr:04X}: {hex_bytes:<8} {inst_str}\n"
                self.codeText.insert(tk.END, line)

        except Exception as e:
            self.codeText.delete(1.0, tk.END)
            self.codeText.insert(1.0, f"Disassembly failed: {e}")

    def toggleRun(self):
        """Toggle run/stop execution"""
        if self.running:
            self.running = False
            self.run_button.config(text="Run", bg="green")
            self.statusLabel.config(text="Stopped")
        else:
            self.running = True
            self.run_button.config(text="Stop", bg="red")
            self.statusLabel.config(text="Running...")
            self.runContinuous()

    def runContinuous(self):
        """Run CPU continuously"""
        if self.running and not self.cpu.halted:
            self.cpu.step()
            self.updateDisplay()

            # Schedule next step
            try:
                delay = int(self.speed_var.get())
            except:
                delay = 100

            self.root.after(delay, self.runContinuous)
        else:
            self.running = False
            self.run_button.config(text="Run", bg="green")
            if self.cpu.halted:
                self.statusLabel.config(text="Program halted")
            else:
                self.statusLabel.config(text="Stopped")

    def stepCpu(self):
        """Execute single instruction"""
        if not self.cpu.halted:
            self.cpu.step()
            self.updateDisplay()
            self.statusLabel.config(text=f"Stepped - PC: {self.cpu.programCounter:04X}")
        else:
            self.statusLabel.config(text="CPU is halted")

    def resetCpu(self):
        """Reset CPU state"""
        self.running = False
        self.run_button.config(text="Run", bg="green")
        self.cpu.reset()
        self.updateDisplay()
        self.statusLabel.config(text="CPU reset")

    def hardReset(self):
        """Hard reset - clear everything"""
        self.running = False
        self.run_button.config(text="Run", bg="green")
        self.cpu = CPU8Bit()  # Create new CPU instance
        self.updateDisplay()
        self.codeText.delete(1.0, tk.END)
        self.statusLabel.config(text="Hard reset - ready to load program")

    def updateDisplay(self):
        """Update all GUI displays with current CPU state"""
        state = self.cpu.getState()

        # Update widgets
        self.register_display.updateRegisters(state['registers'])
        self.flags_display.updateFlags(state['alu_flags'])
        self.status_display.updateStatus(state)
        self.memory_display.updateMemory(state['ram'])
        self.sevenSegDisplay.setValue(state['seven_segment'], state['outputEnabled'])
        # Sync display mode with CPU mode
        self.sevenSegDisplay.setMode(state['signedMode'])

    def _on_display_mode_change(self, *args):
        """Handle display mode change from 7-segment display"""
        signedMode = (self.sevenSegDisplay.mode_var.get() == "Signed")
        self.cpu.setSignedMode(signedMode)

    def showAbout(self):
        """Show about dialog"""
        about_text = """8-bit Computer Emulator

A software emulator for the custom 8-bit computer project.

Features:
• Complete ISA implementation
• Real-time register and memory viewing
• 7-segment display emulation
• Step-by-step execution
• Assembly code display

Built for the Computer8Bit project
https://github.com/arghyabi/Computer8Bit
"""
        messagebox.showinfo("About", about_text)

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = EmulatorMainWindow()
    app.run()

if __name__ == "__main__":
    main()