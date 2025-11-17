"""
Instruction Decoder Implementation
Decodes binary instructions according to the 8-bit computer ISA
"""

class InstructionDecoder:
    """Decodes binary instructions into opcode and operands"""

    def __init__(self):
        # Instruction opcodes (bottom 4 bits or full 8 bits)
        self.opcodes = {
            0b0000_0000: 'NOP',     # 8-bit opcode
            0b0001_0000: 'OUT',     # 8-bit opcode
            0b0010_0000: 'HLT',     # 8-bit opcode
            0b1111_1111: 'RST',     # 8-bit opcode
            0b0001: 'ADD',          # 4-bit opcode
            0b0010: 'SUB',          # 4-bit opcode
            0b0110: 'MOV',          # 4-bit opcode
            0b0111: 'AND',          # 4-bit opcode
            0b1000: 'OR',           # 4-bit opcode
            0b1001: 'XOR',          # 4-bit opcode
            0b1011: 'CMP',          # 4-bit opcode
        }

        # Special opcodes with sub-types
        self.special_opcodes = {
            0b0011: {  # INC/DEC
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
                0b0101: 'JNG', # 0101_0101 (JMG)
                0b0110: 'JML'  # 0110_0101
            },
            0b1010: {  # NOT
                0b00: 'NOT'   # RR00_1010
            },
            0b1100: {  # CMI
                0b00: 'CMI'   # RR00_1100
            }
        }

    def decode(self, instruction):
        """
        Decode a single instruction byte
        Returns: (opcode, operand_info, instruction_size)
        """
        opcode = instruction & 0x0F  # Bottom 4 bits
        upper_nibble = (instruction >> 4) & 0x0F  # Top 4 bits

        # Check for 8-bit opcodes first
        if instruction in [0x00, 0x10, 0x20, 0xFF]:
            return self._decode_8bit_opcode(instruction)

        # Check for special opcodes with sub-types
        if opcode in self.special_opcodes:
            return self._decode_special_opcode(instruction, opcode, upper_nibble)

        # Check for regular 4-bit opcodes
        if opcode in self.opcodes:
            return self._decode_4bit_opcode(instruction, opcode, upper_nibble)

        # Unknown instruction
        return ('UNKNOWN', {}, 1)

    def _decode_8bit_opcode(self, instruction):
        """Decode 8-bit opcodes (NOP, OUT, HLT, RST)"""
        opcode_name = self.opcodes.get(instruction, 'UNKNOWN')
        return (opcode_name, {}, 1)

    def _decode_special_opcode(self, instruction, opcode, upper_nibble):
        """Decode special opcodes with sub-types"""
        sub_opcodes = self.special_opcodes[opcode]

        if opcode == 0b0011:  # INC/DEC: RR10_0011 or RR11_0011
            sub_type = upper_nibble & 0b11  # Bottom 2 bits of upper nibble
            register = (upper_nibble >> 2) & 0b11  # Top 2 bits of upper nibble
            if sub_type in sub_opcodes:
                return (sub_opcodes[sub_type], {'register': register}, 1)

        elif opcode == 0b0100:  # LDI/LDM/SAV: RRTT_0100
            sub_type = upper_nibble & 0b11  # Bottom 2 bits of upper nibble
            register = (upper_nibble >> 2) & 0b11  # Top 2 bits of upper nibble
            if sub_type in sub_opcodes:
                return (sub_opcodes[sub_type], {'register': register}, 2)  # Has immediate/address

        elif opcode == 0b0101:  # Jump instructions: TTTT_0101
            if upper_nibble in sub_opcodes:
                return (sub_opcodes[upper_nibble], {}, 3)  # 11-bit address (2 bytes)

        elif opcode == 0b1010:  # NOT: RR00_1010
            register = (upper_nibble >> 2) & 0b11
            sub_type = upper_nibble & 0b11
            if sub_type in sub_opcodes:
                return (sub_opcodes[sub_type], {'register': register}, 1)

        elif opcode == 0b1100:  # CMI: RR00_1100
            register = (upper_nibble >> 2) & 0b11
            sub_type = upper_nibble & 0b11
            if sub_type in sub_opcodes:
                return (sub_opcodes[sub_type], {'register': register}, 2)  # Has immediate

        return ('UNKNOWN', {}, 1)

    def _decode_4bit_opcode(self, instruction, opcode, upper_nibble):
        """Decode 4-bit opcodes (ADD, SUB, MOV, AND, OR, XOR, CMP)"""
        opcode_name = self.opcodes[opcode]

        # These instructions have SSDD format (source, destination registers)
        dest_reg = upper_nibble & 0b11        # Bottom 2 bits
        source_reg = (upper_nibble >> 2) & 0b11  # Top 2 bits

        return (opcode_name, {
            'source_register': source_reg,
            'destination_register': dest_reg
        }, 1)

    def decodeProgram(self, binaryData, start_pc=0):
        """
        Decode an entire program
        Returns: list of (address, opcode, operands, raw_bytes)
        """
        instructions = []
        pc = start_pc

        while pc < len(binaryData):
            if pc >= len(binaryData):
                break

            # Get first instruction byte
            inst_byte = binaryData[pc]
            opcode, operands, size = self.decode(inst_byte)

            # Collect all bytes for this instruction
            raw_bytes = [inst_byte]

            # Get additional bytes if needed
            if size > 1 and pc + size <= len(binaryData):
                for i in range(1, size):
                    if pc + i < len(binaryData):
                        raw_bytes.append(binaryData[pc + i])

                # Add immediate/address values to operands
                if size == 2:  # Has immediate or memory address
                    operands['immediate'] = raw_bytes[1] if len(raw_bytes) > 1 else 0
                elif size == 3:  # Has 11-bit address (high, low)
                    if len(raw_bytes) >= 3:
                        high_addr = raw_bytes[1]
                        low_addr = raw_bytes[2]
                        operands['address'] = (high_addr << 8) | low_addr
                    else:
                        operands['address'] = 0

            instructions.append((pc, opcode, operands, raw_bytes))
            pc += size

        return instructions

    def register_name(self, regCode):
        """Convert register code to name"""
        regMap = {0b00: 'A', 0b01: 'B', 0b10: 'C', 0b11: 'D'}
        return regMap.get(regCode, f'R{regCode}')