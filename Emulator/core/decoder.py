import os
import sys

# Add parent directory to path to import MicrocodeConfig
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Microcode'))
from MicrocodeConfig import ParseConfig, GetAllInstructionOpcodes, GetAllInstructionSizes


class InstructionDecoder:
    def __init__(self):
        # Load from centralized config
        configPath = os.path.join(os.path.dirname(__file__), '..', '..', 'Microcode', 'MicroCodeConfig.yaml')
        config = ParseConfig(configPath)
        opcodeDict = GetAllInstructionOpcodes(config)
        
        # Build opcode lookup tables from config
        self.opcodes = {}
        self.specialOpcodes = {
            0b0011: {},  # SHL/SHR/INC/DEC
            0b0100: {},  # LDI/LDM/SAV
            0b0101: {},  # Jump instructions
            0b1010: {},  # NOT
            0b1101: {},  # CMI/CMIS
            0b1110: {}   # PUSH/POP
        }
        
        # Populate from config
        for insName, opcode in opcodeDict.items():
            # 8-bit static opcodes
            if insName in ['NOP', 'OUT', 'HLT', 'OUTS', 'RTN', 'PSHV', 'CALL', 'RST']:
                self.opcodes[opcode] = insName
            # 4-bit opcodes (two-operand instructions)
            elif insName in ['ADD', 'SUB', 'MOV', 'AND', 'OR', 'XOR', 'CMP', 'CMPS']:
                self.opcodes[opcode & 0x0F] = insName
            # Special opcodes with sub-types
            elif insName in ['SHL', 'SHR', 'INC', 'DEC']:
                subType = (opcode >> 4) & 0b11
                self.specialOpcodes[0b0011][subType] = insName
            elif insName in ['LDI', 'LDM', 'SAV']:
                subType = (opcode >> 4) & 0b11
                self.specialOpcodes[0b0100][subType] = insName
            elif insName in ['JMP', 'JMZ', 'JNZ', 'JMC', 'JME', 'JMG', 'JML']:
                subType = (opcode >> 4) & 0x0F
                self.specialOpcodes[0b0101][subType] = insName
            elif insName == 'NOT':
                self.specialOpcodes[0b1010][0b00] = insName
            elif insName in ['CMI', 'CMIS']:
                subType = (opcode >> 4) & 0b11
                self.specialOpcodes[0b1101][subType] = insName
            elif insName in ['PUSH', 'POP']:
                subType = (opcode >> 4) & 0b11
                self.specialOpcodes[0b1110][subType] = insName


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
