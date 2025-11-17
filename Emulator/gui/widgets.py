"""
Custom GUI Widgets for the 8-bit Computer Emulator
"""

import tkinter as tk
from tkinter import ttk

class FourDigitSevenSegmentDisplay(tk.Frame):
    """4-digit 7-segment display widget that shows decimal values in signed/unsigned mode"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.value = 0
        self.enabled = False
        self.signedMode = True  # Default to signed mode (matching assembler default)

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack()

        # Mode selection
        mode_frame = tk.Frame(main_frame)
        mode_frame.pack(pady=(0, 10))

        tk.Label(mode_frame, text="Display Mode:", font=("Arial", 10, "bold")).pack(side="left")
        self.mode_var = tk.StringVar(value="Signed")  # Default to signed mode
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                 values=["Unsigned", "Signed"], width=10, state="readonly")
        mode_combo.pack(side="left", padx=(5, 0))
        mode_combo.bind("<<ComboboxSelected>>", self.onModeChange)

        # Create canvas for 4-digit display
        self.canvas = tk.Canvas(main_frame, width=320, height=100, bg='black', highlightthickness=1)
        self.canvas.pack()

        # 7-segment patterns (a,b,c,d,e,f,g)
        self.patterns = {
            0: (1,1,1,1,1,1,0),  # 0
            1: (0,1,1,0,0,0,0),  # 1
            2: (1,1,0,1,1,0,1),  # 2
            3: (1,1,1,1,0,0,1),  # 3
            4: (0,1,1,0,0,1,1),  # 4
            5: (1,0,1,1,0,1,1),  # 5
            6: (1,0,1,1,1,1,1),  # 6
            7: (1,1,1,0,0,0,0),  # 7
            8: (1,1,1,1,1,1,1),  # 8
            9: (1,1,1,1,0,1,1),  # 9
            '-': (0,0,0,0,0,0,1), # minus sign (only middle segment)
            ' ': (0,0,0,0,0,0,0), # blank/off
        }

        # Info label
        self.infoLabel = tk.Label(main_frame, text="Value: 0 (0x00)",
                                  font=("Courier", 10), fg="green")
        self.infoLabel.pack(pady=(5, 0))

        self.drawDisplay()

    def onModeChange(self, event=None):
        """Handle mode change"""
        self.signedMode = (self.mode_var.get() == "Signed")
        self.drawDisplay()

    def drawDisplay(self):
        """Draw the 4-digit 7-segment display"""
        self.canvas.delete("all")

        # Colors
        onColor = "#ff3030" if self.enabled else "#220000"
        offColor = "#220000"

        # Calculate what to display
        if self.signedMode:
            # Signed mode: -128 to +127
            if self.value > 127:
                # Treat as negative (two's complement)
                displayValue = -(256 - self.value)
            else:
                displayValue = self.value

            isNegative = displayValue < 0
            absValue = abs(displayValue)

            # Format: [-]XXX (sign + 3 digits)
            if absValue > 127:
                digits = ['-', 'E', 'R', 'R']  # Error
            else:
                digitStr = f"{absValue:03d}"
                if isNegative:
                    digits = ['-', digitStr[0], digitStr[1], digitStr[2]]
                else:
                    digits = [' ', digitStr[0], digitStr[1], digitStr[2]]
        else:
            # Unsigned mode: 0-255
            if self.value > 255:
                digits = ['E', 'R', 'R', 'R']  # Error
            else:
                digitStr = f"{self.value:03d}"
                digits = [' ', digitStr[0], digitStr[1], digitStr[2]]

        # Draw 4 digits
        digitSpacing = 80
        startX = 10

        for i, digitChar in enumerate(digits):
            # if digitChar == ' ':
            #     continue  # Skip blank digits

            xOffset = startX + (i * digitSpacing)

            if digitChar.isdigit():
                digitNum = int(digitChar)
                pattern = self.patterns.get(digitNum, (0,0,0,0,0,0,0))
            else:
                pattern = self.patterns.get(digitChar, (0,0,0,0,0,0,0))

            self.drawSingleDigit(xOffset, pattern, onColor, offColor)

        # Update info label
        if self.signedMode:
            signedVal = displayValue if 'displayValue' in locals() else 0
            self.infoLabel.config(text=f"Value: {signedVal} (0x{self.value:02X}) [Signed]")
        else:
            self.infoLabel.config(text=f"Value: {self.value} (0x{self.value:02X}) [Unsigned]")

    def drawSingleDigit(self, xOffset, pattern, onColor, offColor):
        """Draw a single 7-segment digit at given x offset"""
        # Segment coordinates relative to xOffset
        segments = {
            'a': [(xOffset + 10, 10), (xOffset + 50, 10), (xOffset + 45, 15), (xOffset + 15, 15)],      # top
            'b': [(xOffset + 50, 10), (xOffset + 55, 15), (xOffset + 55, 45), (xOffset + 50, 50)],      # top-right
            'c': [(xOffset + 50, 50), (xOffset + 55, 55), (xOffset + 55, 85), (xOffset + 50, 90)],      # bottom-right
            'd': [(xOffset + 50, 90), (xOffset + 10, 90), (xOffset + 15, 85), (xOffset + 45, 85)],      # bottom
            'e': [(xOffset + 10, 90), (xOffset + 5,  85), (xOffset + 5,  55), (xOffset + 10, 50)],      # bottom-left
            'f': [(xOffset + 10, 50), (xOffset + 5,  45), (xOffset + 5,  15), (xOffset + 10, 10)],      # top-left
            'g': [(xOffset + 10, 50), (xOffset + 50, 50), (xOffset + 45, 55), (xOffset + 15, 55)]       # middle
        }

        # Draw segments
        seg_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        for i, seg_name in enumerate(seg_names):
            color = onColor if pattern[i] else offColor
            self.canvas.create_polygon(segments[seg_name], fill=color, outline=color)

    def setValue(self, value, enabled=True):
        """Update the display value"""
        self.value = value & 0xFF  # Ensure 8-bit
        self.enabled = enabled
        self.drawDisplay()

    def setMode(self, signedMode):
        """Set display mode programmatically"""
        self.signedMode = signedMode
        self.mode_var.set("Signed" if signedMode else "Unsigned")
        self.drawDisplay()


# Keep old single-digit display for compatibility
class SevenSegmentDisplay(FourDigitSevenSegmentDisplay):
    """Legacy single-digit display - now redirects to 4-digit display"""
    pass
class RegisterDisplay(tk.Frame):
    """Display for the 4 CPU registers"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Title
        title = tk.Label(self, text="Registers", font=("Arial", 12, "bold"))
        title.pack()

        # Register frame
        reg_frame = tk.Frame(self)
        reg_frame.pack(fill="both", expand=True)

        # Create register displays
        self.register_vars = {}
        self.register_labels = {}

        for i, regName in enumerate(['A', 'B', 'C', 'D']):
            # Register name
            tk.Label(reg_frame, text=f"{regName}:", font=("Courier", 10, "bold")).grid(
                row=i, column=0, sticky="e", padx=(5,2))

            # Hex value
            self.register_vars[regName] = tk.StringVar(value="00")
            hex_label = tk.Label(reg_frame, textvariable=self.register_vars[regName],
                                font=("Courier", 10), fg="blue", width=4)
            hex_label.grid(row=i, column=1, padx=2)

            # Binary value
            self.register_labels[regName] = tk.Label(reg_frame, text="00000000",
                                                     font=("Courier", 8), fg="gray", width=10)
            self.register_labels[regName].grid(row=i, column=2, padx=2)

            # Decimal value
            tk.Label(reg_frame, text="(0)", font=("Arial", 8), fg="green", width=6).grid(
                row=i, column=3, padx=2)

    def updateRegisters(self, registers):
        """Update register display"""
        for regName, value in registers.items():
            if regName in self.register_vars:
                self.register_vars[regName].set(f"{value:02X}")
                self.register_labels[regName].config(text=f"{value:08b}")
                # Update decimal display
                for widget in self.winfo_children()[1].winfo_children():
                    if isinstance(widget, tk.Label) and widget.grid_info()['column'] == 3:
                        if widget.grid_info()['row'] == list(registers.keys()).index(regName):
                            widget.config(text=f"({value})")


class FlagsDisplay(tk.Frame):
    """Display for ALU flags"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Title
        tk.Label(self, text="ALU Flags", font=("Arial", 12, "bold")).pack()

        # Flags frame
        flags_frame = tk.Frame(self)
        flags_frame.pack()

        # Flag indicators
        self.flag_vars = {}
        flag_names = [('Z', 'Zero'), ('C', 'Carry'), ('N', 'Negative')]

        for i, (short, full) in enumerate(flag_names):
            frame = tk.Frame(flags_frame)
            frame.grid(row=0, column=i, padx=5)

            tk.Label(frame, text=short, font=("Arial", 8, "bold")).pack()

            self.flag_vars[short.lower()] = tk.StringVar(value="0")
            flag_label = tk.Label(frame, textvariable=self.flag_vars[short.lower()],
                                 font=("Courier", 16, "bold"), fg="red", width=2)
            flag_label.pack()

            tk.Label(frame, text=full, font=("Arial", 7)).pack()

    def updateFlags(self, flags):
        """Update flag display"""
        flag_map = {'zero': 'z', 'carry': 'c', 'negative': 'n'}
        for flag_name, value in flags.items():
            short_name = flag_map.get(flag_name)
            if short_name in self.flag_vars:
                self.flag_vars[short_name].set("1" if value else "0")


class MemoryDisplay(tk.Frame):
    """Display for memory contents"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Title
        tk.Label(self, text="RAM (16 bytes)", font=("Arial", 12, "bold")).pack()

        # Memory frame with scrollbar
        mem_frame = tk.Frame(self)
        mem_frame.pack(fill="both", expand=True)

        # Create text widget for memory display
        self.mem_text = tk.Text(mem_frame, width=50, height=10, font=("Courier", 9))
        scrollbar = tk.Scrollbar(mem_frame, orient="vertical", command=self.mem_text.yview)
        self.mem_text.configure(yscrollcommand=scrollbar.set)

        self.mem_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def updateMemory(self, ram_data):
        """Update memory display"""
        self.mem_text.delete(1.0, tk.END)

        # Display RAM in hex dump format
        for i in range(0, len(ram_data), 8):
            line = f"{i:02X}: "
            hex_part = ""
            ascii_part = ""

            for j in range(8):
                if i + j < len(ram_data):
                    byte_val = ram_data[i + j]
                    hex_part += f"{byte_val:02X} "
                    ascii_part += chr(byte_val) if 32 <= byte_val <= 126 else "."
                else:
                    hex_part += "   "
                    ascii_part += " "

            self.mem_text.insert(tk.END, f"{line}{hex_part} {ascii_part}\n")


class StatusDisplay(tk.Frame):
    """Display for CPU status information"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Title
        tk.Label(self, text="CPU Status", font=("Arial", 12, "bold")).pack()

        # Status frame
        status_frame = tk.Frame(self)
        status_frame.pack()

        # PC display
        pc_frame = tk.Frame(status_frame)
        pc_frame.grid(row=0, column=0, columnspan=2, pady=2)
        tk.Label(pc_frame, text="PC:", font=("Arial", 10)).pack(side="left")
        self.pc_var = tk.StringVar(value="0000")
        tk.Label(pc_frame, textvariable=self.pc_var, font=("Courier", 12, "bold"), fg="blue").pack(side="left")

        # Instruction count
        tk.Label(status_frame, text="Instructions:", font=("Arial", 9)).grid(row=1, column=0, sticky="e")
        self.inst_var = tk.StringVar(value="0")
        tk.Label(status_frame, textvariable=self.inst_var, font=("Courier", 9)).grid(row=1, column=1, sticky="w")

        # Cycle count
        tk.Label(status_frame, text="Cycles:", font=("Arial", 9)).grid(row=2, column=0, sticky="e")
        self.cycle_var = tk.StringVar(value="0")
        tk.Label(status_frame, textvariable=self.cycle_var, font=("Courier", 9)).grid(row=2, column=1, sticky="w")

        # Halted status
        self.halted_var = tk.StringVar(value="Ready")
        halted_label = tk.Label(status_frame, textvariable=self.halted_var, font=("Arial", 10, "bold"))
        halted_label.grid(row=3, column=0, columnspan=2, pady=2)

    def updateStatus(self, state):
        """Update status display"""
        self.pc_var.set(f"{state['pc']:04X}")
        self.inst_var.set(str(state['instructionCount']))
        self.cycle_var.set(str(state['cycleCount']))

        status_text = "HALTED" if state['halted'] else "Ready"
        self.halted_var.set(status_text)