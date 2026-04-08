import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.software_cpu import SoftwareCPU
from core.hardware_cpu import HardwareCPU
from gui.widgets import *


class ToolTip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self._show)
        self.widget.bind("<Leave>", self._hide)

    def set_text(self, text):
        self.text = text

    def _show(self, event=None):
        if self.tip_window is not None or not self.text:
            return

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#FFFDE7",
            foreground="#111111",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            padx=6,
            pady=4
        )
        label.pack()

        # Ensure tooltip stays within visible screen bounds.
        tw.update_idletasks()

        screen_w = self.widget.winfo_screenwidth()
        screen_h = self.widget.winfo_screenheight()
        tip_w = tw.winfo_width()
        tip_h = tw.winfo_height()

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

        # If not enough room below, show above the widget.
        if y + tip_h > screen_h - 8:
            y = self.widget.winfo_rooty() - tip_h - 8

        # Clamp within screen margins.
        x = max(8, min(x, screen_w - tip_w - 8))
        y = max(8, min(y, screen_h - tip_h - 8))

        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self, event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None

class EmulatorMainWindow:
    def __init__(self, mode='software'):
        self.root = tk.Tk()
        self.root.title("8-bit Computer Emulator")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        # Initialize CPU
        self.mode = mode
        if self.mode == 'hardware':
            self.cpu = HardwareCPU(enable_signal_logging=True, log_callback=self.appendConsole)
        else:
            self.cpu = SoftwareCPU(enable_execution_logging=True, log_callback=self.appendConsole)

        # GUI state
        self.running = False
        self.stepMode = True

        # Create GUI
        self.createMenu()
        self.createWidgets()
        self.createControls()

        # Attach GUI console logger
        self.cpu.setLogCallback(self.appendConsole)

        # Update display
        self.updateDisplay()


    def createMenu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu = menubar)

        # File menu
        fileMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "File", menu = fileMenu)
        fileMenu.add_command(label = "Load Program...", command = self.loadProgram)
        fileMenu.add_separator()
        fileMenu.add_command(label = "Exit", command = self.root.quit)

        # CPU menu
        cpuMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "CPU", menu = cpuMenu)
        cpuMenu.add_command(label = "Reset", command = self.resetCpu)
        cpuMenu.add_command(label = "Hard Reset", command = self.hardReset)

        # Help menu
        helpMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "Help", menu = helpMenu)
        helpMenu.add_command(label = "About", command = self.showAbout)


    def createWidgets(self):
        # Main container
        mainFrame = tk.Frame(self.root)
        mainFrame.pack(fill = "both", expand = True, padx = 5, pady = 5)

        # Left panel - CPU state
        leftFrame = tk.Frame(mainFrame, relief = "ridge", bd = 2)
        leftFrame.pack(side = "left", fill = "y", padx = (0,5))

        # Registers
        self.registerDisplay = RegisterDisplay(leftFrame)
        self.registerDisplay.pack(pady = 20)

        # Flags
        self.flagsDisplay = FlagsDisplay(leftFrame)
        self.flagsDisplay.pack(pady = 20)

        # Status
        self.statusDisplay = StatusDisplay(leftFrame)
        self.statusDisplay.pack(pady = 20)

        # Memory
        self.memoryDisplay = MemoryDisplay(leftFrame)
        self.memoryDisplay.pack(pady = 20, fill = "both", expand = True)

        # Center panel - 7-segment display
        centerFrame = tk.Frame(mainFrame, relief = "ridge", bd = 2)
        centerFrame.pack(side = "left", fill = "both", expand = True, padx = 5)

        # 7-segment display
        displayFrame = tk.Frame(centerFrame)
        displayFrame.pack(expand = True)

        tk.Label(displayFrame, text = "4-Digit 7-Segment Display", font = ("Arial", 14, "bold")).pack(pady = 10)
        self.sevenSegDisplay = FourDigitSevenSegmentDisplay(displayFrame)
        self.sevenSegDisplay.pack(pady = 20)

        # Connect display mode change to CPU mode
        self.sevenSegDisplay.modeVar.trace('w', self._on_display_mode_change)

        # code display section
        codeFrame = tk.Frame(centerFrame)
        codeFrame.pack(fill = "both", expand = True)

        # Assembly code display
        assemblyCodeFrame = tk.LabelFrame(codeFrame, text = "Assembly Code", font = ("Arial", 10, "bold"))
        assemblyCodeFrame.pack(fill = "both",side = "right", expand = True, pady = 10)

        self.assemblyTextbox = tk.Text(assemblyCodeFrame, width = 10, height = 15, font = ("Courier", 9))
        assemblyCodeScrollbar = tk.Scrollbar(assemblyCodeFrame, orient = "vertical", command = self.assemblyTextbox.yview)
        self.assemblyTextbox.configure(yscrollcommand = assemblyCodeScrollbar.set)

        self.assemblyTextbox.pack(side = "left", fill = "both", expand = True)
        assemblyCodeScrollbar.pack(side = "right", fill = "y")
        self.assemblyTextbox.config(state = "disabled")

        # Disassembly code display
        disassemblyCodeFrame = tk.LabelFrame(codeFrame, text = "Disassembly Code", font = ("Arial", 10, "bold"))
        disassemblyCodeFrame.pack(fill = "both", side = "right", expand = True, pady = 10)
        self.disassemblyTextbox = tk.Text(disassemblyCodeFrame, width = 10, height = 15, font = ("Courier", 9))
        disassemblyCodeScrollbar = tk.Scrollbar(disassemblyCodeFrame, orient = "vertical", command = self.disassemblyTextbox.yview)
        self.disassemblyTextbox.configure(yscrollcommand = disassemblyCodeScrollbar.set)

        self.disassemblyTextbox.pack(side = "left", fill = "both", expand = True)
        disassemblyCodeScrollbar.pack(side = "right", fill = "y")
        self.disassemblyTextbox.config(state = "disabled")

        # Console output
        consoleFrame = tk.LabelFrame(centerFrame, text = "Console", font = ("Arial", 10, "bold"))
        consoleFrame.pack(fill = "both", expand = True, pady = 10)

        self.consoleTextbox = tk.Text(consoleFrame, width = 10, height = 10,
                                      font = ("Courier", 9), bg = "#111", fg = "#eee")
        consoleScrollbar = tk.Scrollbar(consoleFrame, orient = "vertical", command = self.consoleTextbox.yview)
        self.consoleTextbox.configure(yscrollcommand = consoleScrollbar.set)

        self.consoleTextbox.pack(side = "left", fill = "both", expand = True)
        consoleScrollbar.pack(side = "right", fill = "y")
        self.consoleTextbox.config(state = "disabled")


    def createControls(self):
        controlFrame = tk.Frame(self.root)
        controlFrame.pack(fill = "x", pady = 5)

        # File operations
        fileFrame = tk.LabelFrame(controlFrame, text = "File")
        fileFrame.pack(side = "left", padx = 5)

        tk.Button(fileFrame, text = "Load Program", command = self.loadProgram).pack(side = "left", padx = 2)

        # Execution controls
        execFrame = tk.LabelFrame(controlFrame, text = "Execution")
        execFrame.pack(side = "left", padx = 5)

        self.runButton = tk.Button(execFrame, text = "Run", command = self.toggleRun, bg = "green", fg = "white")
        self.runButton.pack(side = "left", padx = 2)

        tk.Button(execFrame, text = "Step", command = self.stepCpu).pack(side = "left", padx = 2)
        tk.Button(execFrame, text = "Reset", command = self.resetCpu).pack(side = "left", padx = 2)

        # Speed control
        speedFrame = tk.LabelFrame(controlFrame, text = "Speed")
        speedFrame.pack(side = "left", padx = 5)

        tk.Label(speedFrame, text = "Delay (ms):").pack(side = "left")
        self.speedVar = tk.StringVar(value = "100")
        speedEntry = tk.Entry(speedFrame, textvariable = self.speedVar, width = 8)
        speedEntry.pack(side = "left", padx = 2)

        # Mode indicator
        modeFrame = tk.LabelFrame(controlFrame, text = "Mode")
        modeFrame.pack(side = "left", padx = 5)
        self.modeIndicator = tk.Label(modeFrame, text = "SOFTWARE",
                          font = ("Arial", 9, "bold"),
                          bg = "#1E88E5", fg = "white",
                          width = 10, relief = "ridge", bd = 2)
        self.modeIndicator.pack(side = "left", padx = 2, pady = 2)
        self.modeTooltip = ToolTip(self.modeIndicator)

        # Status
        self.statusLabel = tk.Label(controlFrame,
                                    text = f"Ready to load program ({self.mode} mode)",
                                    relief = "sunken", anchor = "w")
        self.statusLabel.pack(side = "right", fill = "x", expand = True, padx = 5)


    def loadProgram(self):
        filename = filedialog.askopenfilename(
            title = "Select Program File",
            filetypes = [("Binary files", "*.bin"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'rb') as f:
                    binaryData = f.read()

                self.cpu.loadProgram(binaryData)
                self.updateDisplay()
                self.appendConsole(f"Loaded program: {os.path.basename(filename)}")

                # Try to load corresponding assembly file for display
                asmFile = filename.replace('.bin', '.s')
                if os.path.exists(asmFile):
                    self.loadAssemblyDisplay(asmFile)
                # Show disassembly
                self.showDisassembly(binaryData)

                self.statusLabel.config(text = f"Loaded: {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load program:\n{e}")


    def appendConsole(self, text):
        self.consoleTextbox.config(state = "normal")
        self.consoleTextbox.insert(tk.END, text + "\n")
        self.consoleTextbox.see(tk.END)
        self.consoleTextbox.config(state = "disabled")

    def clearConsole(self):
        self.consoleTextbox.config(state = "normal")
        self.consoleTextbox.delete(1.0, tk.END)
        self.consoleTextbox.config(state = "disabled")

    def loadAssemblyDisplay(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
            self.assemblyTextbox.config(state = "normal")
            self.assemblyTextbox.delete(1.0, tk.END)
            self.assemblyTextbox.insert(tk.END, content)
            self.assemblyTextbox.config(state = "disabled")
        except:
            pass


    def showDisassembly(self, binaryData):
        try:
            instructions = self.cpu.decoder.decodeProgram(binaryData)
            self.disassemblyTextbox.config(state = "normal")
            self.disassemblyTextbox.delete(1.0, tk.END)

            self.disassemblyTextbox.insert(tk.END, "; Disassembly\n")
            lastRaw = []
            codeFound = False
            lines = ""
            for addr, opcode, operands, rawBytes in instructions[::-1]:
                if rawBytes == [0xff] and not codeFound:
                    lastRaw = rawBytes
                    continue
                else:
                    codeFound = True
                    if lastRaw != []:
                        hex_bytes = " ".join(f"{b:02X}" for b in lastRaw)
                        line = f"{(addr+len(rawBytes)):04X}: {hex_bytes:<8} RST\n"
                        lines = line + lines
                        lastRaw = []

                hex_bytes = " ".join(f"{b:02X}" for b in rawBytes)

                # Format instruction
                instStr = opcode
                if 'sourceRegister' in operands and 'destinationRegister' in operands:
                    src = self.cpu.decoder.registerName(operands['sourceRegister'])
                    dst = self.cpu.decoder.registerName(operands['destinationRegister'])
                    instStr += f" {dst} {src}"
                elif 'register' in operands:
                    reg = self.cpu.decoder.registerName(operands['register'])
                    instStr += f" {reg}"
                    if 'immediate' in operands:
                        instStr += f" 0x{operands['immediate']:02X}"
                elif 'address' in operands:
                    instStr += f" 0x{operands['address']:04X}"

                line = f"{addr:04X}: {hex_bytes:<8} {instStr}\n"
                lines = line + lines
            self.disassemblyTextbox.insert(tk.END, lines)
            self.disassemblyTextbox.config(state = "disabled")

        except Exception as e:
            self.disassemblyTextbox.config(state = "normal")
            self.disassemblyTextbox.delete(1.0, tk.END)
            self.disassemblyTextbox.insert(1.0, f"Disassembly failed: {e}")
            self.disassemblyTextbox.config(state = "disabled")


    def toggleRun(self):
        if self.running:
            self.running = False
            self.runButton.config(text = "Run", bg = "green")
            self.statusLabel.config(text = "Stopped")
            self.appendConsole("Run stopped")
        else:
            self.running = True
            self.runButton.config(text = "Stop", bg = "red")
            self.statusLabel.config(text = "Running...")
            self.appendConsole(f"Run started ({self.mode} mode)")
            self.runContinuous()


    def runContinuous(self):
        if self.running and not self.cpu.halted:
            self.cpu.step()
            self.updateDisplay()

            # Schedule next step
            try:
                delay = int(self.speedVar.get())
            except:
                delay = 100

            self.root.after(delay, self.runContinuous)
        else:
            self.running = False
            self.runButton.config(text = "Run", bg = "green")
            if self.cpu.halted:
                self.statusLabel.config(text = "Program halted")
                self.appendConsole("Program halted")
            else:
                self.statusLabel.config(text = "Stopped")


    def stepCpu(self):
        if not self.cpu.halted:
            self.cpu.step()
            self.updateDisplay()
            self.statusLabel.config(text = f"Stepped - PC: {self.cpu.programCounter:04X}")
            self.appendConsole(f"Stepped - PC: {self.cpu.programCounter:04X}")
        else:
            self.statusLabel.config(text = "CPU is halted")


    def resetCpu(self):
        self.running = False
        self.runButton.config(text = "Run", bg = "green")
        self.cpu.reset()
        self.updateDisplay()
        self.statusLabel.config(text = "CPU reset")
        self.appendConsole("CPU reset")


    def hardReset(self):
        self.running = False
        self.runButton.config(text = "Run", bg = "green")
        if self.mode == 'hardware':
            self.cpu = HardwareCPU(enable_signal_logging=True, log_callback=self.appendConsole)
        else:
            self.cpu = SoftwareCPU(enable_execution_logging=True, log_callback=self.appendConsole)
        self.cpu.setSignedMode(self.sevenSegDisplay.signedMode)
        self.updateDisplay()
        self.assemblyTextbox.config(state = "normal")
        self.assemblyTextbox.delete(1.0, tk.END)
        self.assemblyTextbox.config(state = "disabled")
        self.disassemblyTextbox.config(state = "normal")
        self.disassemblyTextbox.delete(1.0, tk.END)
        self.disassemblyTextbox.config(state = "disabled")
        self.statusLabel.config(text = "Hard reset - ready to load program")
        self.clearConsole()
        self.appendConsole("Hard reset - ready to load program")


    def updateDisplay(self):
        state = self.cpu.getState()

        # Update widgets
        self.registerDisplay.updateRegisters(state['registers'])
        self.flagsDisplay.updateFlags(state['alu_flags'])
        self.statusDisplay.updateStatus(state)
        self.memoryDisplay.updateMemory(state['ram'])
        if state.get('seven_segment_patterns'):
            self.sevenSegDisplay.setPatterns(state['seven_segment_patterns'], state['outputEnabled'])
        else:
            self.sevenSegDisplay.setValue(state['seven_segment'], state['outputEnabled'])
        self._updateModeIndicator(state)
        # Sync display mode with CPU mode
        self.sevenSegDisplay.setMode(state['signedMode'])


    def _updateModeIndicator(self, state):
        mode = state.get('executionMode', self.mode)
        if mode == 'hardware':
            self.modeIndicator.config(text = "HARDWARE", bg = "#2E7D32")
            self.modeTooltip.set_text(
                "Hardware mode:\n"
                "- Executes generated microcode step-by-step\n"
                "- Cycle count = micro-cycles\n"
                "- Console shows control-signal logs\n\n"
                "How to switch mode:\n"
                "Restart emulator with: python main.py -m software"
            )
        else:
            self.modeIndicator.config(text = "SOFTWARE", bg = "#1E88E5")
            self.modeTooltip.set_text(
                "Software mode:\n"
                "- Executes instruction behavior directly\n"
                "- Cycle count = instruction cycles\n"
                "- Console shows instruction logs\n\n"
                "How to switch mode:\n"
                "Restart emulator with: python main.py -m hardware"
            )


    def _on_display_mode_change(self, *args):
        signedMode = (self.sevenSegDisplay.modeVar.get() == "Signed")
        self.cpu.setSignedMode(signedMode)


    def showAbout(self):
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
        self.root.mainloop()


def main():
    app = EmulatorMainWindow()
    app.run()


if __name__ == "__main__":
    main()
