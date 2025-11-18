class RegisterFile:
    def __init__(self):
        self.reset()


    def reset(self):
        self.registers = {
            'A': 0,  # 0b00
            'B': 0,  # 0b01
            'C': 0,  # 0b10
            'D': 0   # 0b11
        }


    def read(self, regCode):
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        if regCode in regMap:
            return self.registers[regMap[regCode]]
        return 0


    def write(self, regCode, value):
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        if regCode in regMap:
            self.registers[regMap[regCode]] = value & 0xFF  # Ensure 8-bit


    def readByName(self, regName):
        return self.registers.get(regName.upper(), 0)


    def writeByName(self, regName, value):
        if regName.upper() in self.registers:
            self.registers[regName.upper()] = value & 0xFF


    def getAllRegisters(self):
        return self.registers.copy()


    def __str__(self):
        return f"A:{self.registers['A']:02X} B:{self.registers['B']:02X} C:{self.registers['C']:02X} D:{self.registers['D']:02X}"
