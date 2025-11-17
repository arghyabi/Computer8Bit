"""
Memory System Implementation
Handles ROM (2KB) and RAM (16 bytes) emulation
"""

class Memory:
    """Emulates the ROM and RAM memory system"""

    def __init__(self):
        self.ROM_SIZE = 2048  # 2KB ROM (11-bit addressing)
        self.RAM_SIZE = 16    # 16 bytes RAM (4-bit addressing)

        # Initialize memory
        self.rom = bytearray(self.ROM_SIZE)  # Program ROM
        self.ram = bytearray(self.RAM_SIZE)  # Data RAM

        # Fill ROM with NOP instructions initially
        for i in range(self.ROM_SIZE):
            self.rom[i] = 0x00  # NOP instruction

    def loadRom(self, binaryData, start_address=0):
        """
        Load binary program into ROM
        binaryData: bytearray of compiled program
        start_address: starting address to load at
        """
        if start_address >= self.ROM_SIZE:
            raise ValueError(f"Start address {start_address} exceeds ROM size")

        # Load data into ROM
        for i, byte in enumerate(binaryData):
            if start_address + i < self.ROM_SIZE:
                self.rom[start_address + i] = byte
            else:
                break  # Don't overflow ROM

    def readRom(self, address):
        """Read byte from ROM at given address"""
        if 0 <= address < self.ROM_SIZE:
            return self.rom[address]
        return 0  # Return 0 for invalid addresses

    def readRam(self, address):
        """Read byte from RAM at given address (4-bit addressing)"""
        address = address & 0x0F  # Ensure 4-bit addressing
        return self.ram[address]

    def writeRam(self, address, value):
        """Write byte to RAM at given address (4-bit addressing)"""
        address = address & 0x0F  # Ensure 4-bit addressing
        self.ram[address] = value & 0xFF  # Ensure 8-bit value

    def getRomDump(self, start=0, length=32):
        """Get ROM dump for debugging (default: first 32 bytes)"""
        end = min(start + length, self.ROM_SIZE)
        return list(self.rom[start:end])

    def getRamDump(self):
        """Get complete RAM dump"""
        return list(self.ram)

    def resetRam(self):
        """Clear all RAM contents"""
        self.ram = bytearray(self.RAM_SIZE)

    def __str__(self):
        """String representation for debugging"""
        rom_info = f"ROM: {len([b for b in self.rom[:100] if b != 0])} non-zero bytes"
        ram_info = f"RAM: {self.ram[:8].hex().upper()}"
        return f"{rom_info}, {ram_info}"