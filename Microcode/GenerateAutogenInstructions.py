import os
import re
import importlib
import glob
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import MicrocodeConfig

SIGNAL_TYPE_INPUT  = "I"
SIGNAL_TYPE_OUTPUT = "O"
SIGNAL_TYPE_HEADER = "X"
SIGNAL_TYPE_IGNORE = "---"

SIGNAL_VALUE_HIGH = "1"
SIGNAL_VALUE_LOW  = "0"

MICROCODE_CFG_FILE = "MicroCodeConfig.yaml"
SIGNAL_CFG_INPUT  = MicrocodeConfig.CFG_INPUT_CONTROL
SIGNAL_CFG_OUTPUT = MicrocodeConfig.CFG_OUTPUT_CONTROL
SIGNAL_CFG_EXTRA  = "Extra"

UCODE_0 = MicrocodeConfig.UCODE_0
UCODE_1 = MicrocodeConfig.UCODE_1
UCODE_2 = MicrocodeConfig.UCODE_2
CFG_MICROCODE_CHIPS = MicrocodeConfig.CFG_MICROCODE_CHIPS
CFG_INPUT_VIR_CTRL_PINS = MicrocodeConfig.CFG_INPUT_VIR_CTRL_PINS
CFG_OUTPUT_VIR_CTRL_PINS = MicrocodeConfig.CFG_OUTPUT_VIR_CTRL_PINS

EXPECTED_VIRTUAL_PIN_COUNT = 4
EXPECTED_INPUT_CONTROL_SIGNAL_LIMIT = 16
EXPECTED_OUTPUT_CONTROL_SIGNAL_LIMIT = 16

INDEX_OF_SIGNAL_TYPE = 0
INDEX_OF_SIGNAL_NAME = 1


@dataclass
class ParsedInstructionRows:
    OtherLines: List[Tuple[str, int]] = field(default_factory=list)
    InputSignalRows: List[List[str]] = field(default_factory=list)
    OutputSignalRows: List[List[str]] = field(default_factory=list)
    ExtraSignalLinesByChip: Dict[str, List[str]] = field(
        default_factory=lambda: {UCODE_0: [], UCODE_2: []}
    )
    ExtraSignalLineMap: Dict[str, str] = field(default_factory=dict)
    SeenSignals: set[str] = field(default_factory=set)


@dataclass
class ParsedInstructionSource:
    InstructionName: str
    InstructionFile: str
    Rows: ParsedInstructionRows = field(default_factory=ParsedInstructionRows)


LOGGER = logging.getLogger(__name__)


class GenAutoInstructions:
    def __init__(self):
        """
        Load the microcode configuration and import all instruction source modules.
        The imported modules are sorted and validated early so generation fails
        fast if the instruction set or config structure is inconsistent.
        """
        self.UCodeConfig = MicrocodeConfig.ParseConfig(MICROCODE_CFG_FILE)

        self.InsObjects = []
        self.InstructionModulesByName = {}
        instructionDir = os.path.join(os.path.dirname(__file__), "Instructions")
        instructionFiles = glob.glob(os.path.join(instructionDir, "Ins*.py"))

        for filePath in sorted(instructionFiles):
            moduleFilename = os.path.basename(filePath)
            moduleName = moduleFilename[:-3]

            try:
                module = importlib.import_module(f"Instructions.{moduleName}")
                self.InsObjects.append(module)
            except ImportError as error:
                LOGGER.error(f"Failed to import {moduleName}: {error}")

        LOGGER.info(f"Total instructions imported: {len(self.InsObjects)}")

        self.InsObjects.sort(key=lambda item: item.__name__)
        self.InstructionParsedData = {}
        self.ValidateConfigStructure()
        self.ValidateInstructionModuleConsistency()


    def ValidateInstructionSignalCompleteness(self, instructionName, instructionFile, allSignalDict):
        """
        Enforce the project rule that every instruction file must declare every
        configured signal row. Unused signals are still required so all source
        tables remain complete, uniform, and easy to compare by eye.
        """
        missingSignals = sorted([signal for signal, found in allSignalDict.items() if not found])
        if missingSignals:
            raise Exception(
                f"ERROR: Instruction '{instructionName}' in file '{instructionFile}' is missing required signal rows. "
                f"Every instruction file must declare every configured signal row, even when unused. "
                f"Missing signals: {missingSignals}"
            )


    def CreateSignalPresenceMap(self):
        signalPresenceMap = {}
        for signalName in MicrocodeConfig.GetAllSignalList(self.UCodeConfig):
            signalPresenceMap[signalName] = False
        for signalName in self.GetConfiguredExtraSignals():
            if MicrocodeConfig.IsReservedSignal(signalName):
                continue
            signalPresenceMap[signalName] = False
        return signalPresenceMap


    def GetInstructionNameFromModule(self, module, configuredInstructions, parsedInstructionFlags):
        instructionName = None
        for line in module.INS.split("\n"):
            if "INSTRUCTION:" in line:
                instructionName = line.split(":")[-1].strip()
                break

        if instructionName is None:
            raise Exception(f"ERROR: Missing INSTRUCTION declaration in {module.__file__}.")

        if instructionName not in configuredInstructions:
            raise Exception(f"ERROR: Instruction '{instructionName}' found in instruction file but not listed in configuration.")

        parsedInstructionFlags[instructionName] = True
        return instructionName


    def ParseInstructionRows(self, instructionName, instructionFile, lines, signalPresenceMap):
        """
        Parse one instruction table into grouped row buckets used by autogen.
        The method separates normal lines, input-control rows, output-control
        rows, and extra-chip rows while also tracking signal completeness.
        """
        parsedRows = ParsedInstructionRows()
        otherLineIndex = -1

        for line in lines:
            otherLineIndex += 1
            lineSplit = [item.strip() for item in line.split("|") if item.strip()]
            if len(lineSplit) < 2:
                parsedRows.OtherLines.append((line, otherLineIndex))
                continue

            signalType = lineSplit[INDEX_OF_SIGNAL_TYPE]
            signalName = lineSplit[INDEX_OF_SIGNAL_NAME]

            if signalType == SIGNAL_TYPE_IGNORE or signalName == "-":
                continue

            if signalType == SIGNAL_TYPE_OUTPUT:
                pinIndex, sectionType = MicrocodeConfig.GetSignalIndex(signalName, self.UCodeConfig)
                if pinIndex == -1:
                    raise Exception(f"ERROR: Signal '{signalName}' not found in configuration.")

                if signalName in parsedRows.SeenSignals:
                    raise Exception(f"ERROR: Duplicate signal '{signalName}' found in instruction '{instructionName}'.")
                parsedRows.SeenSignals.add(signalName)

                if MicrocodeConfig.IsReservedSignal(signalName):
                    continue
                if sectionType == SIGNAL_CFG_EXTRA:
                    parsedRows.ExtraSignalLineMap[signalName] = line
                elif sectionType == SIGNAL_CFG_OUTPUT:
                    parsedRows.OutputSignalRows.append(lineSplit)
                elif sectionType == SIGNAL_CFG_INPUT:
                    parsedRows.InputSignalRows.append(lineSplit)

                signalPresenceMap[signalName] = True
            else:
                parsedRows.OtherLines.append((line, otherLineIndex))

        self.PopulateOrderedExtraSignalLines(parsedRows)
        self.ValidateInstructionSignalCompleteness(instructionName, instructionFile, signalPresenceMap)
        return parsedRows


    def PopulateOrderedExtraSignalLines(self, parsedRows: ParsedInstructionRows):
        microcodeChips = self.UCodeConfig.get(CFG_MICROCODE_CHIPS, {})
        for chipName in [UCODE_0, UCODE_2]:
            for signalName in microcodeChips.get(chipName, {}):
                if MicrocodeConfig.IsReservedSignal(signalName):
                    continue
                if signalName in parsedRows.ExtraSignalLineMap:
                    parsedRows.ExtraSignalLinesByChip[chipName].append(parsedRows.ExtraSignalLineMap[signalName])


    def ValidateInstructionControlSignalLimits(self, instructionName, parsedRows: ParsedInstructionRows):
        """
        Validate that the instruction stays within the supported virtual-control
        encoding width. Input and output control groups are limited to sixteen
        logical signals because they are encoded through four virtual pins each.
        """
        if len(parsedRows.InputSignalRows) > EXPECTED_INPUT_CONTROL_SIGNAL_LIMIT:
            raise Exception(f"ERROR: Number of Input Control Signals exceeded {EXPECTED_INPUT_CONTROL_SIGNAL_LIMIT} in instruction '{instructionName}'.")

        if len(parsedRows.OutputSignalRows) > EXPECTED_OUTPUT_CONTROL_SIGNAL_LIMIT:
            raise Exception(f"ERROR: Number of Output Control Signals exceeded {EXPECTED_OUTPUT_CONTROL_SIGNAL_LIMIT} in instruction '{instructionName}'.")


    def AutogenEachInstruction(self):
        """
        Generate normalized autogen instruction files from the handwritten
        instruction sources. This stage validates completeness, derives virtual
        control rows, and emits output in physical chip order.
        """
        configuredInstructions = MicrocodeConfig.GetAllInstructions(self.UCodeConfig)
        parsedInstructionFlags = {instructionName: False for instructionName in configuredInstructions}

        for module in self.InsObjects:
            instructionFile = module.__file__
            instructionName = self.GetInstructionNameFromModule(module, configuredInstructions, parsedInstructionFlags)
            signalPresenceMap = self.CreateSignalPresenceMap()
            parsedSource = ParsedInstructionSource(
                InstructionName=instructionName,
                InstructionFile=instructionFile
            )
            parsedSource.Rows = self.ParseInstructionRows(
                instructionName,
                instructionFile,
                module.INS.split("\n"),
                signalPresenceMap
            )

            self.ValidateInstructionControlSignalLimits(instructionName, parsedSource.Rows)

            totalColumnNo = self.GetInstructionColumnCount(
                instructionName,
                parsedSource.Rows.InputSignalRows,
                parsedSource.Rows.OutputSignalRows,
                parsedSource.Rows.ExtraSignalLinesByChip
            )

            autogenInSignalDict = self.AutogenInputSignalLines(
                parsedSource.Rows.InputSignalRows,
                instructionName,
                totalColumnNo
            )
            autogenOutSignalDict = self.AutogenOutputSignalLines(
                parsedSource.Rows.OutputSignalRows,
                instructionName,
                totalColumnNo
            )

            self.CreateAutoGenInstructionFile(
                instructionFile,
                instructionName,
                parsedSource.Rows.OtherLines,
                autogenInSignalDict,
                autogenOutSignalDict,
                totalColumnNo,
                parsedSource.Rows.ExtraSignalLinesByChip
            )

        for instructionName, isParsed in parsedInstructionFlags.items():
            if not isParsed:
                raise Exception(f"ERROR: Instruction '{instructionName}' defined in configuration but not found in any instruction file.")


    def GetConfiguredExtraSignals(self):
        microcodeChips = self.UCodeConfig.get(CFG_MICROCODE_CHIPS, {})
        extraSignals = []
        for chipName in [UCODE_0, UCODE_2]:
            for signalName in microcodeChips.get(chipName, {}):
                if MicrocodeConfig.IsReservedSignal(signalName):
                    continue
                extraSignals.append(signalName)
        return extraSignals


    def ValidateConfigStructure(self):
        """
        Validate the minimum config structure required by the generator.
        This checks virtual-pin groups, expected pin counts, and duplicate
        signal definitions before any instruction parsing begins.
        """
        virtualPins = MicrocodeConfig.GetAllVirtualPins(self.UCodeConfig)

        if CFG_INPUT_VIR_CTRL_PINS not in virtualPins:
            raise Exception(f"ERROR: Missing '{CFG_INPUT_VIR_CTRL_PINS}' in {UCODE_1} configuration.")
        if CFG_OUTPUT_VIR_CTRL_PINS not in virtualPins:
            raise Exception(f"ERROR: Missing '{CFG_OUTPUT_VIR_CTRL_PINS}' in {UCODE_1} configuration.")

        if len(virtualPins[CFG_INPUT_VIR_CTRL_PINS]) != EXPECTED_VIRTUAL_PIN_COUNT:
            raise Exception(f"ERROR: '{CFG_INPUT_VIR_CTRL_PINS}' must contain exactly {EXPECTED_VIRTUAL_PIN_COUNT} pins.")
        if len(virtualPins[CFG_OUTPUT_VIR_CTRL_PINS]) != EXPECTED_VIRTUAL_PIN_COUNT:
            raise Exception(f"ERROR: '{CFG_OUTPUT_VIR_CTRL_PINS}' must contain exactly {EXPECTED_VIRTUAL_PIN_COUNT} pins.")

        allConfiguredSignals = MicrocodeConfig.GetAllSignalList(self.UCodeConfig) + self.GetConfiguredExtraSignals()
        duplicateSignals = [signal for signal in set(allConfiguredSignals) if allConfiguredSignals.count(signal) > 1]
        if duplicateSignals:
            raise Exception(f"ERROR: Duplicate signal definitions found in configuration: {sorted(duplicateSignals)}")


    def ValidateInstructionModuleConsistency(self):
        """
        Cross-check instruction modules against the YAML instruction list.
        File names, declared instruction names, and discovered modules must
        all agree so the generation pipeline stays deterministic.
        """
        configuredInstructions = set(MicrocodeConfig.GetAllInstructions(self.UCodeConfig))
        discoveredInstructions = set()
        declaredInstructionNames = set()

        for module in self.InsObjects:
            moduleFilename = os.path.basename(module.__file__)
            expectedInstructionName = re.sub(r"^Ins", "", moduleFilename[:-3])

            if not hasattr(module, "INS"):
                raise Exception(f"ERROR: Missing INS definition in {moduleFilename}.")

            textIns = module.INS
            declaredInstructionName = None
            for line in textIns.split("\n"):
                if "INSTRUCTION:" in line:
                    declaredInstructionName = line.split(":")[-1].strip()
                    break

            if declaredInstructionName is None:
                raise Exception(f"ERROR: Missing INSTRUCTION declaration in {moduleFilename}.")

            if declaredInstructionName != expectedInstructionName:
                raise Exception(
                    f"ERROR: Instruction file name and declared instruction mismatch in {moduleFilename}. "
                    f"Expected '{expectedInstructionName}', found '{declaredInstructionName}'."
                )

            if declaredInstructionName in declaredInstructionNames:
                raise Exception(f"ERROR: Duplicate instruction declaration found for '{declaredInstructionName}'.")
            declaredInstructionNames.add(declaredInstructionName)
            discoveredInstructions.add(declaredInstructionName)
            self.InstructionModulesByName[declaredInstructionName] = module

        missingInConfig = sorted(discoveredInstructions - configuredInstructions)
        if missingInConfig:
            raise Exception(f"ERROR: Instruction files found but not listed in configuration: {missingInConfig}")

        missingInstructionFiles = sorted(configuredInstructions - discoveredInstructions)
        if missingInstructionFiles:
            raise Exception(f"ERROR: Instructions listed in configuration but missing instruction files: {missingInstructionFiles}")


    def GetInstructionColumnCount(self, instructionName, inSignalLineList, outSignalLineList, extraSignalLineDict):
        candidateRowLists = [
            inSignalLineList,
            outSignalLineList,
            extraSignalLineDict[UCODE_0],
            extraSignalLineDict[UCODE_2],
        ]

        for rowList in candidateRowLists:
            if rowList:
                firstRow = rowList[0]
                if isinstance(firstRow, list):
                    return len(firstRow) - 2
                lineSplit = [item.strip() for item in firstRow.split("|") if item.strip()]
                if len(lineSplit) >= 3:
                    return len(lineSplit) - 2

        raise Exception(
            f"ERROR: Instruction '{instructionName}' does not contain any signal rows. "
            f"At least one input, output, or extra signal row is required."
        )


    def ValidateGeneratedSignalWidths(self, instructionName, totalColumnNo, signalGroups):
        """Ensure every generated signal row matches the instruction column width."""
        for groupName, signalDict in signalGroups.items():
            for signalName, values in signalDict.items():
                if len(values) != totalColumnNo:
                    raise Exception(
                        f"ERROR: Generated {groupName} signal '{signalName}' in instruction "
                        f"'{instructionName}' has {len(values)} columns, expected {totalColumnNo}."
                    )


    def AutogenVirtualSignalLines(self, signalLineList, instructionName, totalColumnNo, signalConfigKey, virtualPinConfigKey):
        """
        Auto-generate virtual control signal rows from the selected physical signal group.
        Every generated virtual row must span the full instruction width.
        """
        virtualPins = MicrocodeConfig.GetAllVirtualPins(self.UCodeConfig)
        virtualPinNames = virtualPins[virtualPinConfigKey]
        autogenSignalDict = {signal: [] for signal in virtualPinNames}

        signalIndexDict = MicrocodeConfig.GetAllSignalIndex(signalConfigKey, self.UCodeConfig)
        for columnNo in range(totalColumnNo):
            selectedSignalName = None

            for line in signalLineList:
                signalName = line[INDEX_OF_SIGNAL_NAME]
                item = line[columnNo]
                if item not in [SIGNAL_VALUE_HIGH, SIGNAL_VALUE_LOW]:
                    continue

                if item == SIGNAL_VALUE_HIGH:
                    if selectedSignalName is not None:
                        LOGGER.warning(
                            f"Multiple HIGH signals found in column {columnNo} of {instructionName}. "
                            f"Using the last one."
                        )
                    selectedSignalName = signalName

            if selectedSignalName is None:
                defaultValue = 1
                for signal in virtualPinNames:
                    autogenSignalDict[signal].append(defaultValue)
                continue

            index = signalIndexDict[selectedSignalName]
            for signal in virtualPinNames:
                autogenSignalDict[signal].append(index & 1)
                index >>= 1

        self.ValidateGeneratedSignalWidths(
            instructionName,
            totalColumnNo,
            {virtualPinConfigKey: autogenSignalDict}
        )
        return autogenSignalDict


    def AutogenInputSignalLines(self, inSignalLineList, instructionName, totalColumnNo):
        return self.AutogenVirtualSignalLines(
            inSignalLineList,
            instructionName,
            totalColumnNo,
            SIGNAL_CFG_INPUT,
            CFG_INPUT_VIR_CTRL_PINS
        )


    def AutogenOutputSignalLines(self, outSignalLineList, instructionName, totalColumnNo):
        return self.AutogenVirtualSignalLines(
            outSignalLineList,
            instructionName,
            totalColumnNo,
            SIGNAL_CFG_OUTPUT,
            CFG_OUTPUT_VIR_CTRL_PINS
        )


    def CreateAutoGenInstructionFile(self,
                                     insFile,
                                     instructionName,
                                     insOtherLineList,
                                     autogenInSignalDict,
                                     autogenOutSignalDict,
                                     totalColumnNo,
                                     insExtSignalLineDict):
        """
        Write one autogenerated instruction module to the `out/autogen` folder.
        The emitted table is arranged in physical EEPROM order so later parsing
        can map rows directly onto the three microcode chips.
        """
        if not os.path.exists("out"):
            os.mkdir("out")
        if not os.path.exists("out/autogen"):
            os.mkdir("out/autogen")
        with open(os.path.join("out", "autogen", f"Autogen_{instructionName}.py"), "w") as filePointer:
            filePointer.write(f"# Auto-generated Instruction File for {instructionName}\n")
            filePointer.write(f"# Generated from {insFile}\n\n")

            filePointer.write("INS = '''")
            for (line, index) in insOtherLineList[:-2]:
                filePointer.write(f"{line}\n")

            self.ValidateGeneratedSignalWidths(
                instructionName,
                totalColumnNo,
                {
                    "input virtual": autogenInSignalDict,
                    "output virtual": autogenOutSignalDict,
                }
            )

            uCode0ExtraLines = insExtSignalLineDict[UCODE_0]
            uCode2ExtraLines = insExtSignalLineDict[UCODE_2]

            for line in uCode0ExtraLines:
                filePointer.write(f"{line}\n")
            for _ in range(8 - len(uCode0ExtraLines)):
                filePointer.write(f"| O |  -    | " + " | ".join(["-"] * totalColumnNo) + " |\n")
            filePointer.write(f"|---|-------|" + "|".join(["---"] * totalColumnNo) + "|\n")

            for signal in autogenInSignalDict:
                values = autogenInSignalDict[signal]
                filePointer.write(f"| O | {signal} | " + " | ".join([str(value) for value in values]) + " |\n")

            for signal in autogenOutSignalDict:
                values = autogenOutSignalDict[signal]
                filePointer.write(f"| O | {signal} | " + " | ".join([str(value) for value in values]) + " |\n")
            filePointer.write(f"|---|-------|" + "|".join(["---"] * totalColumnNo) + "|\n")

            for line in uCode2ExtraLines:
                filePointer.write(f"{line}\n")

            for _ in range(8 - len(uCode2ExtraLines)):
                filePointer.write(f"| O |  -    | " + " | ".join(["-"] * totalColumnNo) + " |\n")

            for (line, index) in insOtherLineList[-2:]:
                filePointer.write(f"{line}\n")
            filePointer.write("'''\n")


if __name__ == "__main__":
    autoGen = GenAutoInstructions()
    autoGen.AutogenEachInstruction()
