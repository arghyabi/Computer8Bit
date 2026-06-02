import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import yaml

CFG_VIRTUAL_PIN_CONFIG = "VirtualPinConfig"
CFG_INPUT_CONTROL = "InputControl"
CFG_OUTPUT_CONTROL = "OutputControl"
CFG_MICROCODE_CHIPS_PIN_MAP = "MicrocodeChipsPinMap"
CFG_INPUT_PIN_MAP = "InputPinMap"
CFG_OUTPUT_PIN_MAP = "OutputPinMap"
CFG_INS_CONFIG = "InsConfig"
CFG_INSTRUCTIONS = "Instructions"
CFG_SIGNAL_CFG_EXTRA = "Extra"
CFG_RESERVED_SIGNAL = "RESRV"

UCODE_0 = "uCode0"
UCODE_1 = "uCode1"
UCODE_2 = "uCode2"


@dataclass
class SignalLookupResult:
    SignalIndex: Any
    SectionType: Optional[str]


@dataclass
class ParsedConfigView:
    Instructions: List[str]
    InputControlSignals: Dict[str, Any]
    OutputControlSignals: Dict[str, Any]
    ExtraSignalsByChip: Dict[str, Dict[str, Any]]
    VirtualPinsByGroup: Dict[str, List[str]]


@dataclass
class ParsedTableRow:
    RawLine: str
    Cells: List[str] = field(default_factory=list)

    @property
    def IsEmpty(self) -> bool:
        return len(self.Cells) == 0

    @property
    def HasMinimumCells(self) -> bool:
        return len(self.Cells) >= 2

    @property
    def SignalType(self) -> Optional[str]:
        if not self.HasMinimumCells:
            return None
        return self.Cells[0]

    @property
    def SignalName(self) -> Optional[str]:
        if not self.HasMinimumCells:
            return None
        return self.Cells[1]

    @property
    def Values(self) -> List[str]:
        if len(self.Cells) <= 2:
            return []
        return self.Cells[2:]


def ParseTableRow(line: str) -> ParsedTableRow:
    return ParsedTableRow(
        RawLine=line,
        Cells=[item.strip() for item in line.split("|") if item.strip()]
    )


def ParseConfig(configPath: str) -> Dict[str, Any]:
    if not os.path.exists(configPath):
        raise FileNotFoundError(f"Pin Configuration file not found: {configPath}")

    with open(configPath, 'r') as filePointer:
        try:
            configData = yaml.safe_load(filePointer)
            return configData
        except yaml.YAMLError as error:
            raise ValueError(f"Error parsing YAML file: {error}")


def GetParsedConfigView(config: Dict[str, Any]) -> ParsedConfigView:
    virtualPinConfig = config.get(CFG_VIRTUAL_PIN_CONFIG, {})
    microcodeChipsPinMap = config.get(CFG_MICROCODE_CHIPS_PIN_MAP, {})
    outputPinMap = microcodeChipsPinMap.get(CFG_OUTPUT_PIN_MAP, {})

    # Extract virtual pin names from uCode1 output pin map
    uCode1Pins = outputPinMap.get(UCODE_1, {})
    virtualPinsByGroup: Dict[str, List[str]] = {
        CFG_INPUT_CONTROL: [],
        CFG_OUTPUT_CONTROL: []
    }
    
    # Virtual pins are in the output pin map for uCode1
    # ViInA-D are input control, ViOtA-D are output control
    for pinName in uCode1Pins.values():
        if pinName.startswith('ViIn'):
            virtualPinsByGroup[CFG_INPUT_CONTROL].append(pinName)
        elif pinName.startswith('ViOt'):
            virtualPinsByGroup[CFG_OUTPUT_CONTROL].append(pinName)

    # Get extra signals from uCode0 and uCode2 output pin maps
    extraSignalsByChip = {
        UCODE_0: outputPinMap.get(UCODE_0, {}),
        UCODE_2: outputPinMap.get(UCODE_2, {}),
    }

    return ParsedConfigView(
        Instructions=config.get(CFG_INS_CONFIG, {}).get(CFG_INSTRUCTIONS, []),
        InputControlSignals=virtualPinConfig.get(CFG_INPUT_CONTROL, {}),
        OutputControlSignals=virtualPinConfig.get(CFG_OUTPUT_CONTROL, {}),
        ExtraSignalsByChip=extraSignalsByChip,
        VirtualPinsByGroup=virtualPinsByGroup,
    )


def GetSignalIndex(signalName: str, config: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
    parsedConfig = GetParsedConfigView(config)
    lookupResult = SignalLookupResult(SignalIndex=-1, SectionType=None)

    # Check InputControl and OutputControl signals from VirtualPinConfig
    for sectionName, controls in [
        (CFG_INPUT_CONTROL, parsedConfig.InputControlSignals),
        (CFG_OUTPUT_CONTROL, parsedConfig.OutputControlSignals),
    ]:
        for signal, index in controls.items():
            if signal == signalName:
                lookupResult.SignalIndex = index
                lookupResult.SectionType = sectionName
                break
        if lookupResult.SignalIndex != -1:
            break

    if lookupResult.SignalIndex != -1:
        return lookupResult.SignalIndex, lookupResult.SectionType

    # Check extra signals from OutputPinMap (uCode0 and uCode2)
    for chipName in [UCODE_0, UCODE_2]:
        chipPins = parsedConfig.ExtraSignalsByChip.get(chipName, {})
        for pinName, signalNameInMap in chipPins.items():
            if signalNameInMap == signalName:
                # Return a placeholder index for extra signals
                return None, CFG_SIGNAL_CFG_EXTRA

    return -1, None


def GetAllSignalIndex(sectionName: str, config: Dict[str, Any]) -> Dict[str, Any]:
    parsedConfig = GetParsedConfigView(config)
    if sectionName == CFG_INPUT_CONTROL:
        return dict(parsedConfig.InputControlSignals)
    if sectionName == CFG_OUTPUT_CONTROL:
        return dict(parsedConfig.OutputControlSignals)
    return {}


def IsReservedSignal(signalName: str) -> bool:
    return signalName.startswith(CFG_RESERVED_SIGNAL)


def GetAllVirtualSignaList(config: Dict[str, Any]) -> List[str]:
    parsedConfig = GetParsedConfigView(config)

    signalList: List[str] = []
    for signal in parsedConfig.InputControlSignals:
        if IsReservedSignal(signal):
            continue
        signalList.append(signal)
    for signal in parsedConfig.OutputControlSignals:
        if IsReservedSignal(signal):
            continue
        signalList.append(signal)
    return signalList


def GetAllVirtualPins(config: Dict[str, Any]) -> Dict[str, List[str]]:
    parsedConfig = GetParsedConfigView(config)
    return dict(parsedConfig.VirtualPinsByGroup)


def GetAllInstructions(config: Dict[str, Any]) -> List[str]:
    """Get list of all instruction names"""
    insConfig = config.get(CFG_INS_CONFIG, {})
    instructions = insConfig.get(CFG_INSTRUCTIONS, {})
    if isinstance(instructions, dict):
        return list(instructions.keys())
    # Fallback for old list format
    return list(instructions) if instructions else []


def GetInstructionOpcode(instructionName: str, config: Dict[str, Any]) -> int:
    """Get the opcode value for a specific instruction
    
    Handles both numeric opcodes and string masks with 'x' for operand bits.
    For masks like '0bxxxx_0001', returns the base opcode (lower bits).
    """
    insConfig = config.get(CFG_INS_CONFIG, {})
    instructions = insConfig.get(CFG_INSTRUCTIONS, {})
    
    if isinstance(instructions, dict):
        insData = instructions.get(instructionName, {})
        if isinstance(insData, dict):
            opcode = insData.get('opcode', -1)
            # Handle binary string format (e.g., '0b00000000' or '0bxxxx_0001')
            if isinstance(opcode, str) and opcode.startswith('0b'):
                # Remove '0b' prefix and underscores
                binary_str = opcode[2:].replace('_', '')
                # Replace 'x' with '0' to get base opcode
                binary_str = binary_str.replace('x', '0')
                return int(binary_str, 2)
            if isinstance(opcode, int):
                return opcode
    return -1


def GetInstructionSize(instructionName: str, config: Dict[str, Any], support8BitAddress: bool = False) -> int:
    """Get the size in bytes for a specific instruction"""
    insConfig = config.get(CFG_INS_CONFIG, {})
    instructions = insConfig.get(CFG_INSTRUCTIONS, {})
    
    if isinstance(instructions, dict):
        insData = instructions.get(instructionName, {})
        if isinstance(insData, dict):
            if support8BitAddress and 'size_8bit' in insData:
                return insData.get('size_8bit', 1)
            return insData.get('size', 1)
    return 1


def GetAllInstructionOpcodes(config: Dict[str, Any]) -> Dict[str, int]:
    """Get a dictionary mapping instruction names to their base opcodes
    
    For masks like '0bxxxx_0001', returns the base opcode with 'x' bits as 0.
    """
    insConfig = config.get(CFG_INS_CONFIG, {})
    instructions = insConfig.get(CFG_INSTRUCTIONS, {})
    
    opcodeDict = {}
    if isinstance(instructions, dict):
        for insName, insData in instructions.items():
            if isinstance(insData, dict):
                opcode = insData.get('opcode', -1)
                # Handle binary string format (e.g., '0b00000000' or '0bxxxx_0001')
                if isinstance(opcode, str) and opcode.startswith('0b'):
                    # Remove '0b' prefix and underscores
                    binary_str = opcode[2:].replace('_', '')
                    # Replace 'x' with '0' to get base opcode
                    binary_str = binary_str.replace('x', '0')
                    opcodeDict[insName] = int(binary_str, 2)
                else:
                    opcodeDict[insName] = opcode
    return opcodeDict


def GetAllInstructionSizes(config: Dict[str, Any], support8BitAddress: bool = False) -> Dict[str, int]:
    """Get a dictionary mapping instruction names to their sizes in bytes"""
    insConfig = config.get(CFG_INS_CONFIG, {})
    instructions = insConfig.get(CFG_INSTRUCTIONS, {})
    
    sizeDict = {}
    if isinstance(instructions, dict):
        for insName, insData in instructions.items():
            if isinstance(insData, dict):
                if support8BitAddress and 'size_8bit' in insData:
                    sizeDict[insName] = insData.get('size_8bit', 1)
                else:
                    sizeDict[insName] = insData.get('size', 1)
    return sizeDict


if __name__ == "__main__":
    import os
    configPath = os.path.join(os.path.dirname(__file__), "MicroCodeConfig.yaml")
    try:
        configData = ParseConfig(configPath)
        print("=== Configuration loaded successfully ===\n")
        
        print("Signal Index for PCHI:", GetSignalIndex("PCHI", configData))
        print("\nAll Instructions:", GetAllInstructions(configData))
        print("\nAll Virtual Pins:", GetAllVirtualPins(configData))
        print("\nInput Control Signals:", GetAllSignalIndex("InputControl", configData))
        print("\nAll Virtual Signal List:", GetAllVirtualSignaList(configData))
        
        print("\n=== Instruction Opcodes ===")
        opcodes = GetAllInstructionOpcodes(configData)
        for ins, opcode in sorted(opcodes.items()):
            print(f"{ins:6s}: 0x{opcode:02X} (0b{opcode:08b})")
        
        print("\n=== Instruction Sizes ===")
        sizes = GetAllInstructionSizes(configData, support8BitAddress=False)
        for ins, size in sorted(sizes.items()):
            print(f"{ins:6s}: {size} byte(s)")
        
        print("\n=== Instruction Sizes (8-bit address mode) ===")
        sizes_8bit = GetAllInstructionSizes(configData, support8BitAddress=True)
        for ins, size in sorted(sizes_8bit.items()):
            print(f"{ins:6s}: {size} byte(s)")
            
    except Exception as error:
        print(f"Error: {error}")
        import traceback
        traceback.print_exc()
