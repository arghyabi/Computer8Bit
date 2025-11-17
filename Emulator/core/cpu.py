from .decoder   import InstructionDecoder
from .registers import RegisterFile
from .memory    import Memory
from .alu       import ALU


class CPU8Bit:
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


    def loadProgram(self, binaryData, startAddress = 0):
        self.memory.loadRom(binaryData, startAddress)
        self.reset()  # Reset CPU after loading new program


    def fetch(self):
        if self.programCounter >= self.memory.ROM_SIZE:
            self.halted = True
            return 0

        instruction = self.memory.readRom(self.programCounter)
        self.instructionRegister = instruction
        return instruction


    def step(self):
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


    def execute(self, opcode, operands, instructionSize):
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
                self.programCounter += instructionSize
                return False

            # Advance PC for non-jump instructions
            if opcode not in ['JMP', 'JMZ', 'JNZ', 'JMC', 'JME', 'JNG', 'JML', 'HLT']:
                self.programCounter += instructionSize

            return True

        except Exception as e:
            print(f"Execution error: {e}")
            self.halted = True
            return False


    # Instruction implementations
    def _executeNop(self):
        pass


    def _executeHlt(self):
        self.halted = True


    def _executeOut(self):
        self.sevenSegmentValue = self.registers.readByName('A')
        self.outputEnabled = True


    def _executeRst(self):
        self.reset()


    def _executeAdd(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        result, carry = self.alu.add(dstVal, srcVal)
        self.registers.write(operands['destinationRegister'], result)


    def _executeSub(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        result, borrow = self.alu.subtract(dstVal, srcVal)
        self.registers.write(operands['destinationRegister'], result)


    def _executeInc(self, operands):
        currentVal = self.registers.read(operands['register'])
        result = self.alu.increment(currentVal)
        self.registers.write(operands['register'], result)


    def _executeDec(self, operands):
        currentVal = self.registers.read(operands['register'])
        result = self.alu.decrement(currentVal)
        self.registers.write(operands['register'], result)


    def _executeMov(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        self.registers.write(operands['destinationRegister'], srcVal)


    def _executeLdi(self, operands):
        immediateVal = operands.get('immediate', self._getNextByte())
        self.registers.write(operands['register'], immediateVal)


    def _executeLdm(self, operands):
        address = operands.get('immediate', self._getNextByte())
        value = self.memory.readRam(address)
        self.registers.write(operands['register'], value)


    def _executeSav(self, operands):
        address = operands.get('immediate', self._getNextByte())
        value = self.registers.read(operands['register'])
        self.memory.writeRam(address, value)


    def _executeAnd(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        result = self.alu.logicalAnd(dstVal, srcVal)
        self.registers.write(operands['destinationRegister'], result)


    def _executeOr(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        result = self.alu.logicalOr(dstVal, srcVal)
        self.registers.write(operands['destinationRegister'], result)


    def _executeXor(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        result = self.alu.logicalXor(dstVal, srcVal)
        self.registers.write(operands['destinationRegister'], result)


    def _executeNot(self, operands):
        currentVal = self.registers.read(operands['register'])
        result = self.alu.logicalNot(currentVal)
        self.registers.write(operands['register'], result)


    def _executeCmp(self, operands):
        srcVal = self.registers.read(operands['sourceRegister'])
        dstVal = self.registers.read(operands['destinationRegister'])
        self.alu.compare(dstVal, srcVal)


    def _executeCmi(self, operands):
        immediateVal = operands.get('immediate', self._getNextByte())
        regVal = self.registers.read(operands['register'])
        self.alu.compare(regVal, immediateVal)


    def _executeJump(self, opcode, operands):
        targetAddress = operands.get('address', self._getJumpAddress())

        shouldJump = False
        flags = self.alu.getFlags()

        if opcode == 'JMP':
            shouldJump = True
        elif opcode == 'JMZ':
            shouldJump = flags['zero']
        elif opcode == 'JNZ':
            shouldJump = not flags['zero']
        elif opcode == 'JMC':
            shouldJump = flags['carry']
        elif opcode == 'JME':
            shouldJump = flags['zero']  # Equal means zero flag set
        elif opcode == 'JNG':  # Jump Not Greater (<=)
            shouldJump = flags['zero'] or flags['negative']
        elif opcode == 'JML':  # Jump Less
            shouldJump = flags['negative'] and not flags['zero']

        if shouldJump:
            self.programCounter = targetAddress
        else:
            self.programCounter += 3  # Skip the 3-byte jump instruction


    def _getNextByte(self):
        nextPc = self.programCounter + 1
        if nextPc < self.memory.ROM_SIZE:
            return self.memory.readRom(nextPc)
        return 0


    def _getJumpAddress(self):
        highByte = self._getNextByte()  # PC + 1
        lowByte  = self.memory.readRom(self.programCounter + 2)  # PC + 2
        return (highByte << 8) | lowByte


    def run(self, maxInstructions = 10000):
        self.running = True
        executed = 0

        while self.running and not self.halted and executed < maxInstructions:
            if not self.step():
                break
            executed += 1

        self.running = False
        return executed


    def getState(self):
        return {
            'registers'       : self.registers.getAllRegisters(),
            'pc'              : self.programCounter,
            'ir'              : self.instructionRegister,
            'halted'          : self.halted,
            'alu_flags'       : self.alu.getFlags(),
            'seven_segment'   : self.sevenSegmentValue,
            'outputEnabled'   : self.outputEnabled,
            'signedMode'      : self.signedMode,
            'instructionCount': self.instructionCount,
            'cycleCount'      : self.cycleCount,
            'ram'             : self.memory.getRamDump()
        }


    def setSignedMode(self, signedMode):
        self.signedMode = signedMode


    def __str__(self):
        state = self.getState()
        return f"PC:{state['pc']:04X} {self.registers} {self.alu} 7SEG:{state['seven_segment']:02X}"
