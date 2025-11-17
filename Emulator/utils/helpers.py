def formatHex(value, width = 2):
    return f"{value:0{width}X}"


def formatBinary(value, width = 8):
    return f"{value:0{width}b}"


def formatAddress(address):
    return f"{address:04X}"


def clamp8bit(value):
    return max(0, min(255, int(value)))


def twoComplement8bit(value):
    if value < 0:
        return (256 + value) & 0xFF
    return value & 0xFF


def fromTwoComplement8bit(value):
    if value & 0x80:  # If MSB is set
        return value - 256
    return value


def parseNumber(text):
    text = text.strip().upper()

    try:
        if text.startswith('0X'):
            return int(text, 16), True
        elif text.startswith('0B'):
            return int(text, 2), True
        elif text.startswith('$'):
            return int(text[1:], 16), True
        elif text.startswith('%'):
            return int(text[1:], 2), True
        else:
            return int(text), True
    except ValueError:
        return 0, False


def instructionCycles(opcode):
    cycleMap = {
        'NOP': 1, 'HLT': 1, 'OUT': 2, 'RST': 1,
        'ADD': 3, 'SUB': 3, 'AND': 3, 'OR': 3, 'XOR': 3, 'CMP': 3,
        'INC': 2, 'DEC': 2, 'NOT': 2,
        'MOV': 2, 'LDI': 3, 'LDM': 4, 'SAV': 4, 'CMI': 3,
        'JMP': 3, 'JMZ': 3, 'JNZ': 3, 'JMC': 3, 'JME': 3, 'JNG': 3, 'JML': 3
    }
    return cycleMap.get(opcode, 1)


def formatInstruction(opcode, operands, decoder = None):
    instStr = opcode

    if 'sourceRegister' in operands and 'destinationRegister' in operands:
        if decoder:
            src = decoder.registerName(operands['sourceRegister'])
            dst = decoder.registerName(operands['destinationRegister'])
        else:
            src = f"R{operands['sourceRegister']}"
            dst = f"R{operands['destinationRegister']}"
        instStr += f" {dst} {src}"

    elif 'register' in operands:
        if decoder:
            reg = decoder.registerName(operands['register'])
        else:
            reg = f"R{operands['register']}"
        instStr += f" {reg}"

        if 'immediate' in operands:
            instStr += f" 0x{operands['immediate']:02X}"

    elif 'address' in operands:
        instStr += f" 0x{operands['address']:04X}"

    return instStr


def createHexDump(data, startAddress = 0, bytesPerLine = 16):
    lines = []

    for i in range(0, len(data), bytesPerLine):
        addr = startAddress + i
        lineData = data[i:i+bytesPerLine]

        # Address
        line = f"{addr:04X}: "

        # Hex bytes
        hexPart = ""
        for j in range(bytesPerLine):
            if j < len(lineData):
                hexPart += f"{lineData[j]:02X} "
            else:
                hexPart += "   "
            if j == 7:  # Add space in middle
                hexPart += " "

        # ASCII representation
        asciiPart = ""
        for byte in lineData:
            if 32 <= byte <= 126:
                asciiPart += chr(byte)
            else:
                asciiPart += "."

        line += hexPart + " " + asciiPart
        lines.append(line)

    return "\n".join(lines)


def validateRegisterCode(regCode):
    return 0 <= regCode <= 3


def validateAddress(address, maxAddress = 2047):
    return 0 <= address <= maxAddress


def formatFlags(flags):
    flagChars = ""
    flagChars += "Z" if flags.get('zero', False) else "-"
    flagChars += "C" if flags.get('carry', False) else "-"
    flagChars += "N" if flags.get('negative', False) else "-"
    return flagChars


class CircularBuffer:
    def __init__(self, size = 100):
        self.size = size
        self.buffer = []
        self.index = 0

    def add(self, item):
        if len(self.buffer) < self.size:
            self.buffer.append(item)
        else:
            self.buffer[self.index] = item
            self.index = (self.index + 1) % self.size


    def get_recent(self, count = 10):
        if not self.buffer:
            return []

        if len(self.buffer) <= count:
            return self.buffer[:]

        # Get items in order
        if len(self.buffer) == self.size:
            # Buffer is full, get from current position backwards
            items = []
            for i in range(count):
                idx = (self.index - 1 - i) % self.size
                if idx >= 0:
                    items.insert(0, self.buffer[idx])
            return items
        else:
            # Buffer not full, get last items
            return self.buffer[-count:]


    def clear(self):
        self.buffer.clear()
        self.index = 0


def safeInt(value, default = 0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
