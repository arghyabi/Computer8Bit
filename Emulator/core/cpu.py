"""
Main CPU Implementation
Complete 8-bit computer emulation with all components
"""

from .registers import RegisterFile
from .memory import Memory
from .alu import ALU
from .decoder import InstructionDecoder

class CPU8Bit:
    """Complete 8-bit CPU emulator"""

    def __init__(self):
        # Initialize components
        self.registers = RegisterFile()
        self.memory = Memory()
        self.alu = ALU()
        self.decoder = InstructionDecoder()

        # CPU state
        self.programCounter = 0
        self.instructionRegister = 0
        self.halted = False
        self.running = False

        # Hardware configuration
        self.signedMode = True  # Default to signed mode (matching assembler default)

        # Output
        self.sevenSegmentValue = 0
        self.outputEnabled = False        # Debug/statistics
        self.instructionCount = 0
        self.cycleCount = 0

    def reset(self):
        """Reset CPU to initial state"""
        self.registers.reset()
        self.memory.resetRam()  # Keep ROM loaded
        self.alu.reset()

        self.programCounter = 0
        self.instructionRegister = 0
        self.halted = False
        self.running = False
        # Keep signedMode setting through reset
        self.sevenSegmentValue = 0
        self.outputEnabled = False
        self.instructionCount = 0
        self.cycleCount = 0

    def loadProgram(self, binaryData, start_address=0):
        """Load binary program into ROM"""
        self.memory.loadRom(binaryData, start_address)
        self.reset()  # Reset CPU after loading new program

    def fetch(self):
        """Fetch instruction from ROM at current PC"""
        if self.programCounter >= self.memory.ROM_SIZE:
            self.halted = True
            return 0

        instruction = self.memory.readRom(self.programCounter)
        self.instructionRegister = instruction
        return instruction

    def step(self):
        """Execute one instruction"""
        if self.halted:
            return False

        # Fetch instruction
        instruction = self.fetch()

        # Decode instruction
        opcode, operands, size = self.decoder.decode(instruction)

        # Execute instruction
        success = self.execute(opcode, operands, size)

        # Update counters
        if success:
            self.instructionCount += 1
            self.cycleCount += 1  # Simplified - each instruction = 1 cycle

        return success

    def execute(self, opcode, operands, instruction_size):
        """Execute decoded instruction"""
        try:
            if opcode == 'NOP':
                self._executeNop()
            elif opcode == 'HLT':
                self._executeHlt()
            elif opcode == 'OUT':
                self._executeOut()
            elif opcode == 'RST':
                self._executeRst()
            elif opcode == 'ADD':
                self._executeAdd(operands)
            elif opcode == 'SUB':
                self._executeSub(operands)
            elif opcode == 'INC':
                self._executeInc(operands)
            elif opcode == 'DEC':
                self._executeDec(operands)
            elif opcode == 'MOV':
                self._executeMov(operands)
            elif opcode == 'LDI':
                self._executeLdi(operands)
            elif opcode == 'LDM':
                self._executeLdm(operands)
            elif opcode == 'SAV':
                self._executeSav(operands)
            elif opcode == 'AND':
                self._executeAnd(operands)
            elif opcode == 'OR':
                self._executeOr(operands)
            elif opcode == 'XOR':
                self._executeXor(operands)
            elif opcode == 'NOT':
                self._executeNot(operands)
            elif opcode == 'CMP':
                self._executeCmp(operands)
            elif opcode == 'CMI':
                self._executeCmi(operands)
            elif opcode in ['JMP', 'JMZ', 'JNZ', 'JMC', 'JME', 'JNG', 'JML']:
                self._executeJump(opcode, operands)
            else:
                print(f"Unknown instruction: {opcode}")
                self.programCounter += instruction_size
                return False

            # Advance PC for non-jump instructions
            if opcode not in ['JMP', 'JMZ', 'JNZ', 'JMC', 'JME', 'JNG', 'JML', 'HLT']:
                self.programCounter += instruction_size

            return True

        except Exception as e:
            print(f"Execution error: {e}")
            self.halted = True
            return False

    # Instruction implementations
    def _executeNop(self):
        """No operation"""
        pass

    def _executeHlt(self):
        """Halt execution"""
        self.halted = True

    def _executeOut(self):
        """Output register A to 7-segment display"""
        self.sevenSegmentValue = self.registers.readByName('A')
        self.outputEnabled = True

    def _executeRst(self):
        """Reset CPU"""
        self.reset()

    def _executeAdd(self, operands):
        """ADD D S - Add source to destination"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        result, carry = self.alu.add(dst_val, src_val)
        self.registers.write(operands['destination_register'], result)

    def _executeSub(self, operands):
        """SUB D S - Subtract source from destination"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        result, borrow = self.alu.subtract(dst_val, src_val)
        self.registers.write(operands['destination_register'], result)

    def _executeInc(self, operands):
        """INC R - Increment register"""
        current_val = self.registers.read(operands['register'])
        result = self.alu.increment(current_val)
        self.registers.write(operands['register'], result)

    def _executeDec(self, operands):
        """DEC R - Decrement register"""
        current_val = self.registers.read(operands['register'])
        result = self.alu.decrement(current_val)
        self.registers.write(operands['register'], result)

    def _executeMov(self, operands):
        """MOV D S - Move source to destination"""
        src_val = self.registers.read(operands['source_register'])
        self.registers.write(operands['destination_register'], src_val)

    def _executeLdi(self, operands):
        """LDI R VV - Load immediate value into register"""
        immediate_val = operands.get('immediate', self._getNextByte())
        self.registers.write(operands['register'], immediate_val)

    def _executeLdm(self, operands):
        """LDM R AA - Load from memory into register"""
        address = operands.get('immediate', self._getNextByte())
        value = self.memory.readRam(address)
        self.registers.write(operands['register'], value)

    def _executeSav(self, operands):
        """SAV R AA - Save register to memory"""
        address = operands.get('immediate', self._getNextByte())
        value = self.registers.read(operands['register'])
        self.memory.writeRam(address, value)

    def _executeAnd(self, operands):
        """AND D S - Bitwise AND"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        result = self.alu.logicalAnd(dst_val, src_val)
        self.registers.write(operands['destination_register'], result)

    def _executeOr(self, operands):
        """OR D S - Bitwise OR"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        result = self.alu.logicalOr(dst_val, src_val)
        self.registers.write(operands['destination_register'], result)

    def _executeXor(self, operands):
        """XOR D S - Bitwise XOR"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        result = self.alu.logicalXor(dst_val, src_val)
        self.registers.write(operands['destination_register'], result)

    def _executeNot(self, operands):
        """NOT R - Bitwise NOT (complement)"""
        current_val = self.registers.read(operands['register'])
        result = self.alu.logicalNot(current_val)
        self.registers.write(operands['register'], result)

    def _executeCmp(self, operands):
        """CMP D S - Compare destination with source"""
        src_val = self.registers.read(operands['source_register'])
        dst_val = self.registers.read(operands['destination_register'])
        self.alu.compare(dst_val, src_val)

    def _executeCmi(self, operands):
        """CMI R VV - Compare register with immediate value"""
        immediate_val = operands.get('immediate', self._getNextByte())
        reg_val = self.registers.read(operands['register'])
        self.alu.compare(reg_val, immediate_val)

    def _executeJump(self, opcode, operands):
        """Execute jump instructions"""
        target_address = operands.get('address', self._getJumpAddress())

        should_jump = False
        flags = self.alu.getFlags()

        if opcode == 'JMP':
            should_jump = True
        elif opcode == 'JMZ':
            should_jump = flags['zero']
        elif opcode == 'JNZ':
            should_jump = not flags['zero']
        elif opcode == 'JMC':
            should_jump = flags['carry']
        elif opcode == 'JME':
            should_jump = flags['zero']  # Equal means zero flag set
        elif opcode == 'JNG':  # Jump Not Greater (<=)
            should_jump = flags['zero'] or flags['negative']
        elif opcode == 'JML':  # Jump Less
            should_jump = flags['negative'] and not flags['zero']

        if should_jump:
            self.programCounter = target_address
        else:
            self.programCounter += 3  # Skip the 3-byte jump instruction

    def _getNextByte(self):
        """Get next byte from ROM (for immediate values)"""
        next_pc = self.programCounter + 1
        if next_pc < self.memory.ROM_SIZE:
            return self.memory.readRom(next_pc)
        return 0

    def _getJumpAddress(self):
        """Get 11-bit jump address from next two bytes"""
        high_byte = self._getNextByte()  # PC + 1
        low_byte = self.memory.readRom(self.programCounter + 2)  # PC + 2
        return (high_byte << 8) | low_byte

    def run(self, max_instructions=10000):
        """Run program until halt or max instructions"""
        self.running = True
        executed = 0

        while self.running and not self.halted and executed < max_instructions:
            if not self.step():
                break
            executed += 1

        self.running = False
        return executed

    def getState(self):
        """Get complete CPU state for debugging"""
        return {
            'registers': self.registers.getAllRegisters(),
            'pc': self.programCounter,
            'ir': self.instructionRegister,
            'halted': self.halted,
            'alu_flags': self.alu.getFlags(),
            'seven_segment': self.sevenSegmentValue,
            'outputEnabled': self.outputEnabled,
            'signedMode': self.signedMode,
            'instructionCount': self.instructionCount,
            'cycleCount': self.cycleCount,
            'ram': self.memory.getRamDump()
        }

    def setSignedMode(self, signedMode):
        """Set signed/unsigned display mode"""
        self.signedMode = signedMode

    def __str__(self):
        """String representation for debugging"""
        state = self.getState()
        return f"PC:{state['pc']:04X} {self.registers} {self.alu} 7SEG:{state['seven_segment']:02X}"