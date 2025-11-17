class Memory:
    def __init__(self):
        self.ROM_SIZE = 2048  # 2KB ROM (11-bit addressing)
        self.RAM_SIZE = 16    # 16 bytes RAM (4-bit addressing)

        # Initialize memory
        self.rom = bytearray(self.ROM_SIZE)  # Program ROM
        self.ram = bytearray(self.RAM_SIZE)  # Data RAM

        # Fill ROM with NOP instructions initially
        for i in range(self.ROM_SIZE):
            self.rom[i] = 0x00  # NOP instruction


    def loadRom(self, binaryData, startAddress = 0):
        if startAddress >= self.ROM_SIZE:
            raise ValueError(f"Start address {startAddress} exceeds ROM size")

        # Load data into ROM
        for i, byte in enumerate(binaryData):
            if startAddress + i < self.ROM_SIZE:
                self.rom[startAddress + i] = byte
            else:
                break  # Don't overflow ROM


    def readRom(self, address):
        if 0 <= address < self.ROM_SIZE:
            return self.rom[address]
        return 0  # Return 0 for invalid addresses


    def readRam(self, address):
        address = address & 0x0F  # Ensure 4-bit addressing
        return self.ram[address]


    def writeRam(self, address, value):
        address = address & 0x0F  # Ensure 4-bit addressing
        self.ram[address] = value & 0xFF  # Ensure 8-bit value


    def getRomDump(self, start = 0, length = 32):
        end = min(start + length, self.ROM_SIZE)
        return list(self.rom[start:end])


    def getRamDump(self):
        return list(self.ram)


    def resetRam(self):
        self.ram = bytearray(self.RAM_SIZE)


    def __str__(self):
        romInfo = f"ROM: {len([b for b in self.rom[:100] if b != 0])} non-zero bytes"
        ramInfo = f"RAM: {self.ram[:8].hex().upper()}"
        return f"{romInfo}, {ramInfo}"
