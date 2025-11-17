"""
8-bit Register File Implementation
Manages the 4 general-purpose registers (A, B, C, D)
"""

class RegisterFile:
    """Emulates the 4 general-purpose 8-bit registers"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all registers to 0"""
        self.registers = {
            'A': 0,  # 0b00
            'B': 0,  # 0b01
            'C': 0,  # 0b10
            'D': 0   # 0b11
        }

    def read(self, regCode):
        """
        Read register value by register code
        regCode: 0b00=A, 0b01=B, 0b10=C, 0b11=D
        """
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        if regCode in regMap:
            return self.registers[regMap[regCode]]
        return 0

    def write(self, regCode, value):
        """
        Write value to register by register code
        regCode: 0b00=A, 0b01=B, 0b10=C, 0b11=D
        value: 8-bit value (0-255)
        """
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        if regCode in regMap:
            self.registers[regMap[regCode]] = value & 0xFF  # Ensure 8-bit

    def readByName(self, regName):
        """Read register by name ('A', 'B', 'C', 'D')"""
        return self.registers.get(regName.upper(), 0)

    def writeByName(self, regName, value):
        """Write to register by name ('A', 'B', 'C', 'D')"""
        if regName.upper() in self.registers:
            self.registers[regName.upper()] = value & 0xFF

    def getAllRegisters(self):
        """Return copy of all register values"""
        return self.registers.copy()

    def __str__(self):
        """String representation for debugging"""
        return f"A:{self.registers['A']:02X} B:{self.registers['B']:02X} C:{self.registers['C']:02X} D:{self.registers['D']:02X}"