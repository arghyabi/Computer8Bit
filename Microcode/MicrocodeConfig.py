import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import yaml

CFG_PIN_CONFIG = "PinConfig"
CFG_INPUT_CONTROL = "InputControl"
CFG_OUTPUT_CONTROL = "OutputControl"
CFG_MICROCODE_CHIPS = "MicrocodeChips"
CFG_INPUT_VIR_CTRL_PINS = "InputVirCtrlPins"
CFG_OUTPUT_VIR_CTRL_PINS = "OutputVirCtrlPins"
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
    pinConfig = config.get(CFG_PIN_CONFIG, {})
    microcodeChips = config.get(CFG_MICROCODE_CHIPS, {})
    uCode1Config = microcodeChips.get(UCODE_1, {})

    virtualPinsByGroup: Dict[str, List[str]] = {}
    for sectionName in [CFG_INPUT_VIR_CTRL_PINS, CFG_OUTPUT_VIR_CTRL_PINS]:
        pins = uCode1Config.get(sectionName, {})
        virtualPinsByGroup[sectionName] = list(pins.keys())

    return ParsedConfigView(
        Instructions=config.get(CFG_INS_CONFIG, {}).get(CFG_INSTRUCTIONS, []),
        InputControlSignals=pinConfig.get(CFG_INPUT_CONTROL, {}),
        OutputControlSignals=pinConfig.get(CFG_OUTPUT_CONTROL, {}),
        ExtraSignalsByChip={
            UCODE_0: microcodeChips.get(UCODE_0, {}),
            UCODE_2: microcodeChips.get(UCODE_2, {}),
        },
        VirtualPinsByGroup=virtualPinsByGroup,
    )


def GetSignalIndex(signalName: str, config: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
    parsedConfig = GetParsedConfigView(config)
    lookupResult = SignalLookupResult(SignalIndex=-1, SectionType=None)

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

    for chipName in [UCODE_0, UCODE_2]:
        chipSignals = parsedConfig.ExtraSignalsByChip.get(chipName, {})
        for signal, index in chipSignals.items():
            if signal == signalName:
                return index, CFG_SIGNAL_CFG_EXTRA

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


def GetAllSignalList(config: Dict[str, Any]) -> List[str]:
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
    parsedConfig = GetParsedConfigView(config)
    return list(parsedConfig.Instructions)


if __name__ == "__main__":
    configPath = "MicroCodeConfig.yaml"
    try:
        configData = ParseConfig(configPath)
        print(configData)
        print(GetSignalIndex("PCHI", configData))
        print(GetAllInstructions(configData))
        print(GetAllVirtualPins(configData))
        print(GetAllSignalIndex("InputControl", configData))
        print(GetAllSignalList(configData))
    except Exception as error:
        print(f"Error: {error}")
