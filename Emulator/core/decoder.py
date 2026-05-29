class InstructionDecoder:
    def __init__(self):
        # Instruction opcodes (bottom 4 bits or full 8 bits)
        self.opcodes = {
            0b0000_0000: 'NOP',     # 8-bit opcode
            0b0001_0000: 'OUT',     # 8-bit opcode
            0b0010_0000: 'HLT',     # 8-bit opcode
            0b0011_0000: 'OUTS',    # 8-bit opcode
            0b0010_1110: 'RTN',     # 8-bit opcode
            0b0011_1110: 'PSHV',    # 8-bit opcode prefix with immediate
            0b0111_1110: 'CALL',    # 8-bit opcode prefix with address
            0b1111_1111: 'RST',     # 8-bit opcode
            0b0001: 'ADD',          # 4-bit opcode
            0b0010: 'SUB',          # 4-bit opcode
            0b0110: 'MOV',          # 4-bit opcode
            0b0111: 'AND',          # 4-bit opcode
            0b1000: 'OR',           # 4-bit opcode
            0b1001: 'XOR',          # 4-bit opcode
            0b1011: 'CMP',          # 4-bit opcode
            0b1100: 'CMPS',         # 4-bit opcode
        }

        # Special opcodes with sub-types
        self.specialOpcodes = {
            0b0011: {  # SHL/SHR/INC/DEC
                0b00: 'SHL',  # RR00_0011
                0b01: 'SHR',  # RR01_0011
                0b10: 'INC',  # RR10_0011
                0b11: 'DEC'   # RR11_0011
            },
            0b0100: {  # LDI/LDM/SAV
                0b00: 'LDI',  # RR00_0100
                0b01: 'LDM',  # RR01_0100
                0b10: 'SAV'   # RR10_0100
            },
            0b0101: {  # Jump instructions
                0b0000: 'JMP', # 0000_0101
                0b0001: 'JMZ', # 0001_0101
                0b0010: 'JNZ', # 0010_0101
                0b0011: 'JMC', # 0011_0101
                0b0100: 'JME', # 0100_0101
                0b0101: 'JMG', # 0101_0101
                0b0110: 'JML'  # 0110_0101
            },
            0b1010: {  # NOT
                0b00: 'NOT'   # RR00_1010
            },
            0b1101: {  # CMI/CMIS
                0b00: 'CMI',   # RR00_1101
                0b01: 'CMIS'   # RR01_1101
            },
            0b1110: {  # PUSH/POP
                0b00: 'PUSH',  # RR00_1110
                0b01: 'POP'    # RR01_1110
            }
        }


    def decode(self, instruction):
        opcode      = instruction & 0x0F  # Bottom 4 bits
        upperNibble = (instruction >> 4) & 0x0F  # Top 4 bits

        # Check for 8-bit opcodes first
        if instruction in [0x00, 0x10, 0x20, 0x30, 0x2E, 0x3E, 0x7E, 0xFF]:
            return self._decode8bitOpcode(instruction)

        # Check for special opcodes with sub-types
        if opcode in self.specialOpcodes:
            return self._decodeSpecialOpcode(instruction, opcode, upperNibble)

        # Check for regular 4-bit opcodes
        if opcode in self.opcodes:
            return self._decode4bitOpcode(instruction, opcode, upperNibble)

        # Unknown instruction
        return ('UNKNOWN', {}, 1)


    def _decode8bitOpcode(self, instruction):
        opcodeName = self.opcodes.get(instruction, 'UNKNOWN')
        return (opcodeName, {}, 1)


    def _decodeSpecialOpcode(self, instruction, opcode, upperNibble):
        subOpcodes = self.specialOpcodes[opcode]

        if opcode == 0b0011:  # SHL/SHR/INC/DEC: RRTT_0011
            subType  = upperNibble & 0b11  # Bottom 2 bits of upper nibble
            register = (upperNibble >> 2) & 0b11  # Top 2 bits of upper nibble
            if subType in subOpcodes:
                return (subOpcodes[subType], {'register': register}, 1)

        elif opcode == 0b0100:  # LDI/LDM/SAV: RRTT_0100
            subType  = upperNibble & 0b11  # Bottom 2 bits of upper nibble
            register = (upperNibble >> 2) & 0b11  # Top 2 bits of upper nibble
            if subType in subOpcodes:
                return (subOpcodes[subType], {'register': register}, 2)  # Has immediate/address

        elif opcode == 0b0101:  # Jump instructions: TTTT_0101
            if upperNibble in subOpcodes:
                return (subOpcodes[upperNibble], {}, 3)  # 11-bit address (2 bytes)

        elif opcode == 0b1010:  # NOT: RR00_1010
            register = (upperNibble >> 2) & 0b11
            subType  = upperNibble & 0b11
            if subType in subOpcodes:
                return (subOpcodes[subType], {'register': register}, 1)

        elif opcode == 0b1101:  # CMI/CMIS: RRTT_1101
            register = (upperNibble >> 2) & 0b11
            subType  = upperNibble & 0b11
            if subType in subOpcodes:
                return (subOpcodes[subType], {'register': register}, 2)  # Has immediate
        elif opcode == 0b1110:  # PUSH/POP: RRTT_1110
            register = (upperNibble >> 2) & 0b11
            subType  = upperNibble & 0b11
            if subType in subOpcodes:
                return (subOpcodes[subType], {'register': register}, 1)

        return ('UNKNOWN', {}, 1)


    def _decode4bitOpcode(self, instruction, opcode, upperNibble):
        opcodeName = self.opcodes[opcode]

        # These instructions use DDSS in upper nibble:
        # destination in bits [7:6], source in bits [5:4]
        destinationReg = (upperNibble >> 2) & 0b11  # Top 2 bits
        sourceReg = upperNibble & 0b11              # Bottom 2 bits

        return (opcodeName, {
            'sourceRegister': sourceReg,
            'destinationRegister': destinationReg
        }, 1)


    def decodeProgram(self, binaryData, startPc = 0):
        instructions = []
        pc = startPc

        while pc < len(binaryData):
            if pc >= len(binaryData):
                break

            # Get first instruction byte
            instByte = binaryData[pc]
            opcode, operands, size = self.decode(instByte)

            # Collect all bytes for this instruction
            rawBytes = [instByte]

            # Get additional bytes if needed
            if size > 1 and pc + size <= len(binaryData):
                for i in range(1, size):
                    if pc + i < len(binaryData):
                        rawBytes.append(binaryData[pc + i])

                # Add immediate/address values to operands
                if size == 2:  # Has immediate or memory address
                    operands['immediate'] = rawBytes[1] if len(rawBytes) > 1 else 0
                elif size == 3:  # Has 11-bit address (high, low)
                    if len(rawBytes) >= 3:
                        highAddr = rawBytes[1]
                        lowAddr = rawBytes[2]
                        operands['address'] = (highAddr << 8) | lowAddr
                    else:
                        operands['address'] = 0

            instructions.append((pc, opcode, operands, rawBytes))
            pc += size

        return instructions


    def registerName(self, regCode):
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        return regMap.get(regCode, f'R{regCode}')
