import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cpu    import *
from gui.widgets import *

class EmulatorMainWindow:
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

        # Disassembly code display
        disassemblyCodeFrame = tk.LabelFrame(codeFrame, text = "Disassembly Code", font = ("Arial", 10, "bold"))
        disassemblyCodeFrame.pack(fill = "both", side = "right", expand = True, pady = 10)
        self.disassemblyTextbox = tk.Text(disassemblyCodeFrame, width = 10, height = 15, font = ("Courier", 9))
        disassemblyCodeScrollbar = tk.Scrollbar(disassemblyCodeFrame, orient = "vertical", command = self.disassemblyTextbox.yview)
        self.disassemblyTextbox.configure(yscrollcommand = disassemblyCodeScrollbar.set)

        self.disassemblyTextbox.pack(side = "left", fill = "both", expand = True)
        disassemblyCodeScrollbar.pack(side = "right", fill = "y")


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

        # Status
        self.statusLabel = tk.Label(controlFrame, text = "Ready to load program",
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

                # Try to load corresponding assembly file for display
                asmFile = filename.replace('.bin', '.s')
                if os.path.exists(asmFile):
                    self.loadAssemblyDisplay(asmFile)
                # Show disassembly
                self.showDisassembly(binaryData)

                self.statusLabel.config(text = f"Loaded: {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load program:\n{e}")


    def loadAssemblyDisplay(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
            self.assemblyTextbox.delete(1.0, tk.END)
            self.assemblyTextbox.insert(tk.END, content)
        except:
            pass


    def showDisassembly(self, binaryData):
        try:
            instructions = self.cpu.decoder.decodeProgram(binaryData)
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

        except Exception as e:
            self.disassemblyTextbox.delete(1.0, tk.END)
            self.disassemblyTextbox.insert(1.0, f"Disassembly failed: {e}")


    def toggleRun(self):
        if self.running:
            self.running = False
            self.runButton.config(text = "Run", bg = "green")
            self.statusLabel.config(text = "Stopped")
        else:
            self.running = True
            self.runButton.config(text = "Stop", bg = "red")
            self.statusLabel.config(text = "Running...")
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
            else:
                self.statusLabel.config(text = "Stopped")


    def stepCpu(self):
        if not self.cpu.halted:
            self.cpu.step()
            self.updateDisplay()
            self.statusLabel.config(text = f"Stepped - PC: {self.cpu.programCounter:04X}")
        else:
            self.statusLabel.config(text = "CPU is halted")


    def resetCpu(self):
        self.running = False
        self.runButton.config(text = "Run", bg = "green")
        self.cpu.reset()
        self.updateDisplay()
        self.statusLabel.config(text = "CPU reset")


    def hardReset(self):
        self.running = False
        self.runButton.config(text = "Run", bg = "green")
        self.cpu = CPU8Bit()  # Create new CPU instance
        self.updateDisplay()
        self.assemblyTextbox.delete(1.0, tk.END)
        self.disassemblyTextbox.delete(1.0, tk.END)
        self.statusLabel.config(text = "Hard reset - ready to load program")


    def updateDisplay(self):
        state = self.cpu.getState()

        # Update widgets
        self.registerDisplay.updateRegisters(state['registers'])
        self.flagsDisplay.updateFlags(state['alu_flags'])
        self.statusDisplay.updateStatus(state)
        self.memoryDisplay.updateMemory(state['ram'])
        self.sevenSegDisplay.setValue(state['seven_segment'], state['outputEnabled'])
        # Sync display mode with CPU mode
        self.sevenSegDisplay.setMode(state['signedMode'])


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
