import os
import yaml

from .decoder import InstructionDecoder
from .registers import RegisterFile
from .memory import Memory
from .alu import ALU


class HardwareCPU:
    DEFAULT_MICROCODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Microcode', 'out'))
    DEFAULT_SEVENSEG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Gen7segDriver', 'decimal_display_segments.bin'))
    DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Microcode', 'MicroCodeConfig.yaml'))

    def __init__(self,
                 microcodeDir=None,
                 sevenSegPath=None,
                 configPath=None,
                 enable_signal_logging=True,
                 log_callback=None):
        self.registers = RegisterFile()
        self.memory = Memory()
        self.alu = ALU()
        self.decoder = InstructionDecoder()

        self.microcodeDir = microcodeDir or self.DEFAULT_MICROCODE_DIR
        self.sevenSegPath = sevenSegPath or self.DEFAULT_SEVENSEG_PATH
        self.configPath = configPath or self.DEFAULT_CONFIG_PATH

        self.enable_signal_logging = enable_signal_logging
        self.log_callback = log_callback if log_callback is not None else print

        self.microcodeBanks = [bytearray(), bytearray(), bytearray()]
        self.sevenSegRom = None
        self.inputSignalByCode = {}
        self.outputSignalByCode = {}

        self.flagSelect = (0, 0, 0)
        self.memoryAddress = 0
        self.bus = 0
        self.temp1 = 0
        self.temp2 = 0
        self.pcLowRegister = 0
        self.pcHighRegister = 0
        self.sevenSegmentValue = 0
        self.sevenSegmentPatterns = None
        self.outputEnabled = False
        self.signedMode = True

        self._loadConfig()
        self._loadMicrocodeBanks()
        self._loadSevenSegRom()
        self.reset()

    def setLogCallback(self, callback):
        self.log_callback = callback if callback is not None else print

    def _loadConfig(self):
        if not os.path.exists(self.configPath):
            raise FileNotFoundError(f"Microcode config not found: {self.configPath}")

        with open(self.configPath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.inputSignalByCode.clear()
        self.outputSignalByCode.clear()

        pinConfig = config.get('PinConfig', {})
        for signalName, index in pinConfig.get('InputControl', {}).items():
            if index is None:
                continue
            self.inputSignalByCode[int(index)] = signalName

        for signalName, index in pinConfig.get('OutputControl', {}).items():
            if index is None:
                continue
            self.outputSignalByCode[int(index)] = signalName

    def _loadMicrocodeBanks(self):
        for chipIndex in range(3):
            filename = os.path.join(self.microcodeDir, f"Microcode_{chipIndex}.bin")
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Microcode bank missing: {filename}")
            with open(filename, 'rb') as f:
                data = f.read()
            if len(data) != 2 ** 15:
                raise ValueError(f"Microcode bank {filename} must be 32768 bytes")
            self.microcodeBanks[chipIndex] = bytearray(data)

    def _loadSevenSegRom(self):
        if not os.path.exists(self.sevenSegPath):
            self._generateSevenSegRom()

        with open(self.sevenSegPath, 'rb') as f:
            data = f.read()

        if len(data) != 2048:
            raise ValueError(f"7-seg ROM must be 2048 bytes: {self.sevenSegPath}")

        self.sevenSegRom = data

    def _generateSevenSegRom(self):
        os.makedirs(os.path.dirname(self.sevenSegPath), exist_ok=True)

        segment_map = [
            0b01111110,  # 0
            0b00001100,  # 1
            0b10110110,  # 2
            0b10011110,  # 3
            0b11001100,  # 4
            0b11011010,  # 5
            0b11111010,  # 6
            0b00001110,  # 7
            0b11111110,  # 8
            0b11011110,  # 9
            0b10000000,  # -
            0b00000000   # blank
        ]

        eeprom = bytearray(2048)
        THOUSAND_ADD = 0b000 << 8
        HUNDRED_ADD = 0b010 << 8
        TEN_ADD = 0b001 << 8
        UNIT_ADD = 0b011 << 8
        SIGN = 0b100 << 8

        def genReverseNegativeNum(num):
            return (num - 1) ^ 0xFF

        for index in range(256):
            num = index
            unit = num % 10
            ten = (num // 10) % 10
            hundred = (num // 100) % 10

            eeprom[UNIT_ADD + index] = segment_map[unit]
            eeprom[HUNDRED_ADD + index] = segment_map[hundred] if hundred else segment_map[11]
            eeprom[TEN_ADD + index] = segment_map[ten] if ten or hundred else segment_map[11]
            eeprom[THOUSAND_ADD + index] = segment_map[11]

        for index in range(256):
            num = genReverseNegativeNum(index)
            unit = num % 10
            ten = (num // 10) % 10
            hundred = (num // 100) % 10

            eeprom[SIGN + THOUSAND_ADD + index] = segment_map[11]
            eeprom[SIGN + TEN_ADD + index] = segment_map[11]
            eeprom[SIGN + HUNDRED_ADD + index] = segment_map[11]
            eeprom[SIGN + UNIT_ADD + index] = segment_map[unit]

            if ten:
                eeprom[SIGN + TEN_ADD + index] = segment_map[ten]
                eeprom[SIGN + HUNDRED_ADD + index] = segment_map[10]
            else:
                eeprom[SIGN + TEN_ADD + index] = segment_map[10]

            if hundred:
                eeprom[SIGN + HUNDRED_ADD + index] = segment_map[hundred]
                eeprom[SIGN + THOUSAND_ADD + index] = segment_map[10]

        with open(self.sevenSegPath, 'wb') as f:
            f.write(bytes(eeprom))

    def _compute_flag_input(self):
        select = self.flagSelect
        zero = self.alu.flags['zero']
        carry = self.alu.flags['carry']
        negative = self.alu.flags['negative']
        greater = (not zero) and (not negative)
        less = negative
        equal = zero

        code = (select[0] << 2) | (select[1] << 1) | select[2]

        if code == 0b000:
            return 1 if zero else 0
        if code == 0b001:
            return 1 if carry else 0
        if code == 0b010:
            return 1 if greater else 0
        if code == 0b011:
            return 1 if less else 0
        if code == 0b100:
            return 1 if equal else 0
        return 0

    def _get_microcode_address(self):
        flagBit = self._compute_flag_input()
        seq = self.sequenceCounter & 0x0F
        ir = self.instructionRegister & 0xFF
        address = (flagBit << 12) | (seq << 8) | ir
        return address

    def _decode_microcode_outputs(self, bank0, bank1, bank2, address):
        signals = {
            'PCL': bool(bank0 & 0x80),
            'PCC': bool(bank0 & 0x40),
            'AdSu': bool(bank0 & 0x20),
            'Cin': bool(bank0 & 0x10),
            'SpC': bool(bank0 & 0x08),
            'SpUd': bool(bank2 & 0x80),
            'FlSe0': bool(bank2 & 0x40),
            'FlSe1': bool(bank2 & 0x20),
            'FlSe2': bool(bank2 & 0x10),
            'HLT': bool(bank2 & 0x08),
        }

        vi_in_code = (((bank1 >> 7) & 1) << 0) | (((bank1 >> 6) & 1) << 1) | (((bank1 >> 5) & 1) << 2) | (((bank1 >> 4) & 1) << 3)
        vi_out_code = (((bank1 >> 3) & 1) << 0) | (((bank1 >> 2) & 1) << 1) | (((bank1 >> 1) & 1) << 2) | (((bank1 >> 0) & 1) << 3)

        signals['virtual_input'] = self.inputSignalByCode.get(vi_in_code)
        signals['virtual_output'] = self.outputSignalByCode.get(vi_out_code)

        if signals['virtual_input']:
            signals[signals['virtual_input']] = True
        if signals['virtual_output']:
            signals[signals['virtual_output']] = True

        return signals

    def _get_active_signals(self, signals):
        """Return a list of signal names that are HIGH (True)"""
        active = []
        exclude_signals = {'RESRV'}  # Skip non-real signals
        for sig_name, sig_value in signals.items():
            if sig_value is True and sig_name not in exclude_signals:  # Only True booleans, skip None or strings and excluded signals
                active.append(sig_name)
        return sorted(active)

    def _log_signals(self, signals, cycle_num):
        """Print active signals for this cycle in a formatted line"""
        active = self._get_active_signals(signals)
        if active:
            signal_str = " ".join(active)
        else:
            signal_str = "(no signals)"
        self.log_callback(f"    [Cycle {cycle_num}] {signal_str}")

    def _log_instruction_start(self):
        """Print instruction header when starting a new instruction"""
        opcode = self.memory.readRom(self.programCounter)
        mnemonic, operands, size = self.decoder.decode(opcode)

        # Format the instruction with operands
        if mnemonic == 'LDI' or mnemonic == 'LDM' or mnemonic == 'SAV':
            reg_name = ['A', 'B', 'C', 'D'][operands.get('register', 0)]
            immediate = self.memory.readRom(self.programCounter + 1)
            self.log_callback(f"\n{mnemonic} {reg_name} {immediate}:")
        elif mnemonic in ['INC', 'DEC', 'NOT', 'CMI']:
            reg_name = ['A', 'B', 'C', 'D'][operands.get('register', 0)]
            self.log_callback(f"\n{mnemonic} {reg_name}:")
        elif mnemonic in ['ADD', 'SUB', 'MOV', 'AND', 'OR', 'XOR', 'CMP']:
            src_reg = ['A', 'B', 'C', 'D'][operands.get('sourceRegister', 0)]
            dst_reg = ['A', 'B', 'C', 'D'][operands.get('destinationRegister', 0)]
            self.log_callback(f"\n{mnemonic} {dst_reg} {src_reg}:")
        else:
            self.log_callback(f"\n{mnemonic}:")

    def _alu_result(self, adsu, cin):
        if adsu:
            result, carryOut = self.alu.subtract(self.temp1, self.temp2, cin)
        else:
            result, carryOut = self.alu.add(self.temp1, self.temp2, cin)
        return result, carryOut

    def _compute_bus_value(self, signals):
        virtual_output = signals.get('virtual_output')
        if virtual_output == 'rAO':
            return self.registers.readByName('A')
        if virtual_output == 'rBO':
            return self.registers.readByName('B')
        if virtual_output == 'rCO':
            return self.registers.readByName('C')
        if virtual_output == 'rDO':
            return self.registers.readByName('D')
        if virtual_output == 'PCO':
            return self.programCounter & 0xFF
        if virtual_output == 'RomO':
            return self.memory.readRom(self.programCounter)
        if virtual_output == 'MeO':
            return self.memory.readRam(self.memoryAddress)
        if virtual_output == 'AdSuO':
            result, _ = self._alu_result(signals['AdSu'], int(signals['Cin']))
            return result
        if virtual_output == 'AndO':
            return self.temp1 & self.temp2
        if virtual_output == 'OrO':
            return self.temp1 | self.temp2
        if virtual_output == 'XorO':
            return self.temp1 ^ self.temp2

        # No output source is driving the bus in this micro-step.
        return 0

    def _apply_control_signals(self, signals):
        if signals.get('SpO') or signals.get('Seg7E') or signals.get('SpL'):
            self.outputEnabled = True
        self.sevenSegmentPatterns = None

        if signals.get('rAI'):
            self.registers.writeByName('A', self.bus)
        if signals.get('rBI'):
            self.registers.writeByName('B', self.bus)
        if signals.get('rCI'):
            self.registers.writeByName('C', self.bus)
        if signals.get('rDI'):
            self.registers.writeByName('D', self.bus)
        if signals.get('T1I'):
            self.temp1 = self.bus & 0xFF
        if signals.get('T2I'):
            self.temp2 = self.bus & 0xFF
        if signals.get('PCLI'):
            self.pcLowRegister = self.bus & 0xFF
        if signals.get('PCHI'):
            self.pcHighRegister = self.bus & 0x07
        if signals.get('IRI'):
            self.instructionRegister = self.bus & 0xFF
        if signals.get('Seg7E'):
            self.sevenSegmentValue = self.registers.readByName('A')
        if signals.get('SpL'):
            self.sevenSegmentValue = self.bus & 0xFF

        if signals.get('MdI'):
            self.memoryAddress = self.bus & 0x0F

        if signals.get('MeI') and signals.get('MdI'):
            self.memory.writeRam(self.memoryAddress, self.bus)

        if signals.get('PCL'):
            self.programCounter = ((self.pcHighRegister << 8) | self.pcLowRegister) & 0x7FF

        if signals.get('PCC'):
            self.programCounter = (self.programCounter + 1) & 0x7FF

        if signals.get('FlgU'):
            result, carryOut = self._alu_result(signals['AdSu'], int(signals['Cin']))
            self.alu._updateFlags(result, carryOut)

        if signals.get('Seg7E') or signals.get('SpO') or signals.get('SpL'):
            self._update_seven_segment_patterns()

        if signals.get('SpUd'):
            self.signedMode = False
        else:
            self.signedMode = True

        if signals.get('HLT'):
            self.halted = True

    def _update_seven_segment_patterns(self):
        if not self.sevenSegRom:
            return
        if self.signedMode and self.sevenSegmentValue > 127:
            index = self.sevenSegmentValue & 0xFF
            offset = 0x400
        else:
            index = self.sevenSegmentValue & 0xFF
            offset = 0

        thousand = self.sevenSegRom[offset + 0 + index]
        hundred = self.sevenSegRom[offset + 512 + index]
        ten = self.sevenSegRom[offset + 256 + index]
        unit = self.sevenSegRom[offset + 768 + index]
        self.sevenSegmentPatterns = [thousand, hundred, ten, unit]

    def loadProgram(self, binaryData, startAddress=0):
        self.memory.loadRom(binaryData, startAddress)
        self.reset()

    def reset(self):
        self.registers.reset()
        self.memory.resetRam()
        self.alu.reset()
        self.programCounter = 0
        self.pcLowRegister = 0
        self.pcHighRegister = 0
        self.instructionRegister = 0
        self.sequenceCounter = 0
        self.halted = False
        self.running = False
        self.flagSelect = (0, 0, 0)
        self.memoryAddress = 0
        self.bus = 0
        self.temp1 = 0
        self.temp2 = 0
        self.sevenSegmentValue = 0
        self.sevenSegmentPatterns = None
        self.outputEnabled = False
        self.instructionCount = 0
        self.cycleCount = 0
        self.currentInstructionStarted = False

    def step(self):
        if self.halted:
            return False

        address = self._get_microcode_address()
        bank0 = self.microcodeBanks[0][address]
        bank1 = self.microcodeBanks[1][address]
        bank2 = self.microcodeBanks[2][address]

        signals = self._decode_microcode_outputs(bank0, bank1, bank2, address)

        # Log instruction start before logging signals
        if self.sequenceCounter == 0 and not self.currentInstructionStarted and self.enable_signal_logging:
            self._log_instruction_start()

        if self.enable_signal_logging:
            self._log_signals(signals, self.cycleCount)

        bus_value = self._compute_bus_value(signals)
        self.bus = bus_value & 0xFF

        self._apply_control_signals(signals)

        next_seq = 0 if signals.get('SqR') else ((self.sequenceCounter + 1) & 0x0F)
        if signals.get('SqR') and self.currentInstructionStarted:
            self.instructionCount += 1
            self.currentInstructionStarted = False
        elif signals.get('HLT') and self.currentInstructionStarted:
            self.instructionCount += 1
            self.currentInstructionStarted = False

        if self.sequenceCounter == 0 and not self.currentInstructionStarted:
            self.currentInstructionStarted = True

        self.sequenceCounter = next_seq
        self.cycleCount += 1

        self.flagSelect = (int(signals.get('FlSe0', False)),
                           int(signals.get('FlSe1', False)),
                           int(signals.get('FlSe2', False)))

        return not self.halted

    def run(self, maxInstructions=10000):
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
            'registers': self.registers.getAllRegisters(),
            'executionMode': 'hardware',
            'cycleType': 'micro',
            'pc': self.programCounter,
            'ir': self.instructionRegister,
            'halted': self.halted,
            'alu_flags': self.alu.getFlags(),
            'seven_segment': self.sevenSegmentValue,
            'seven_segment_patterns': self.sevenSegmentPatterns,
            'outputEnabled': self.outputEnabled,
            'signedMode': self.signedMode,
            'instructionCount': self.instructionCount,
            'cycleCount': self.cycleCount,
            'ram': self.memory.getRamDump()
        }

    def setSignedMode(self, signedMode):
        self.signedMode = signedMode

    def __str__(self):
        state = self.getState()
        return f"PC:{state['pc']:04X} {self.registers} {self.alu} 7SEG:{state['seven_segment']:02X}"
