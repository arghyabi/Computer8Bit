import os
import importlib
import glob

import ParseConfig

SIGNAL_TYPE_INPUT  = "I"
SIGNAL_TYPE_OUTPUT = "O"
SIGNAL_TYPE_HEADER = "X"
SIGNAL_TYPE_IGNORE = "---"

SIGNAL_VALUE_HIGH = "1"
SIGNAL_VALUE_LOW  = "0"

MICROCODE_CFG_FILE = "MicroCodeConfig.yaml"
SIGNAL_CFG_INPUT  = "InputControl"
SIGNAL_CFG_OUTPUT = "OutputControl"
SIGNAL_CFG_EXTRA  = "Extra"

INDEX_OF_SIGNAL_TYPE = 0
INDEX_OF_SIGNAL_NAME = 1


class GenAutoInstructions:
    def __init__(self):
        self.uCodeConfig = ParseConfig.parseConfig(MICROCODE_CFG_FILE)

        self.insObjects = []
        instructionDir = os.path.join(os.path.dirname(__file__), "Instructions")
        instructionFiles = glob.glob(os.path.join(instructionDir, "Ins*.py"))

        for filePath in sorted(instructionFiles):
            moduleFilename = os.path.basename(filePath)
            moduleName = moduleFilename[:-3]  # Remove .py extension

            try:
                # Import the module dynamically
                module = importlib.import_module(f"Instructions.{moduleName}")
                self.insObjects.append(module)
            except ImportError as e:
                print(f"Failed to import {moduleName}: {e}")

        print(f"Total instructions imported: {len(self.insObjects)} \n")

        self.insObjects.sort(key = lambda x: x.__name__)
        self.instructionParsedData = {}


    def autogenEachInstruction(self):
        allInsFromConfig = ParseConfig.getAllInstructions(self.uCodeConfig)
        # create a dict to check all ins are parsed or not
        allInsDict = {}
        for ins in allInsFromConfig:
            allInsDict[ins] = False

        for ins in self.insObjects:
            insFile = ins.__file__
            textIns :str = ins.INS
            lines = textIns.split("\n")

            insOtherLineList     = []
            insInSignalLineList  = []
            insOutSignalLineList = []
            insExtSignalLineList = []
            instructionName = None
            otherLineIndex  = -1
            ignoreAutogen = False

            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
                    if instructionName not in allInsFromConfig:
                        print(f"Warning: Instruction '{instructionName}' not found in configuration. Ignoring...")
                        ignoreAutogen = True
                    else:
                        allInsDict[instructionName] = True
                    break

            if ignoreAutogen:
                continue

            for line in lines:
                otherLineIndex += 1
                lineSplit = [item.strip() for item in line.split("|") if item.strip()]
                if len(lineSplit) < 2:
                    insOtherLineList.append((line, otherLineIndex))
                    continue

                signalType = lineSplit[INDEX_OF_SIGNAL_TYPE]
                signalName = lineSplit[INDEX_OF_SIGNAL_NAME]

                if signalType == SIGNAL_TYPE_IGNORE or signalName == "-":
                    continue

                if signalType == SIGNAL_TYPE_OUTPUT:
                    pinIndex, sectionType = ParseConfig.getSignalIndex(signalName, self.uCodeConfig)
                    if pinIndex == -1:
                        print(f"ERROR: Signal '{signalName}' not found in configuration. Ignoring...")
                        raise Exception(f"Signal '{signalName}' not found in configuration.")

                    if sectionType == SIGNAL_CFG_EXTRA:
                        insExtSignalLineList.append(line)

                    if sectionType == SIGNAL_CFG_OUTPUT:
                        insOutSignalLineList.append(lineSplit)

                    if sectionType == SIGNAL_CFG_INPUT:
                        insInSignalLineList.append(lineSplit)
                else:
                    insOtherLineList.append((line, otherLineIndex))


            if len(insInSignalLineList) > 16:
                print("\nError: Number of Input Control Signals exceeded 16")

            if len(insOutSignalLineList) > 16:
                print("\nError: Number of Output Control Signals exceeded 16")

            autogenInSignalDict  = self.autogenInputSignalLines(insInSignalLineList)
            autogenOutSignalDict = self.autogenOutputSignalLines(insOutSignalLineList)

            self.createAutoGenInstructionFile(insFile,
                                                instructionName,
                                                insOtherLineList,
                                                autogenInSignalDict,
                                                autogenOutSignalDict,
                                                insInSignalLineList,
                                                insExtSignalLineList)

        # Check if any instruction in config is not parsed
        for ins in allInsDict:
            if not allInsDict[ins]:
                raise Exception(f"ERROR: Instruction '{ins}' defined in configuration but not found in any instruction file.")



    # Auto-generate virtual Input Control Signals with help of the config file
    # This is a internal logic to generate the autogen Instruction Files.
    def autogenInputSignalLines(self, inSignalLineList):
        virtualPins = ParseConfig.getAllVirtualPins(self.uCodeConfig)
        autogenSignalDict = {}
        for signal in virtualPins["InputControlPins"]:
            autogenSignalDict[signal] = []

        totalColumnNo = len(inSignalLineList[0])
        signalIndexDict =  ParseConfig.getAllSignalIndex(SIGNAL_CFG_INPUT, self.uCodeConfig)
        for columnNo in range(totalColumnNo):
            highFound = False
            for line in inSignalLineList:
                signalName = line[INDEX_OF_SIGNAL_NAME]
                item = line[columnNo]
                if item not in [SIGNAL_VALUE_HIGH, SIGNAL_VALUE_LOW]:
                    highFound = True # Mark as found to avoid all zero
                    continue
                if item == SIGNAL_VALUE_HIGH and highFound:
                    print(f"Warning: Multiple HIGH signals found in column {columnNo}. Using the last one.")
                    break
                if item == SIGNAL_VALUE_HIGH:
                    highFound = True
                    index = signalIndexDict[signalName]
                    for signal in virtualPins["InputControlPins"]:
                        autogenSignalDict[signal].append((index & 1))
                        index = index >> 1
            if not highFound:
                for signal in virtualPins["InputControlPins"]:
                    autogenSignalDict[signal].append(0)

        return autogenSignalDict


    # Auto-generate virtual Output Control Signals with help of the config file
    # This is a internal logic to generate the autogen Instruction Files.
    def autogenOutputSignalLines(self, outSignalLineList):
        virtualPins = ParseConfig.getAllVirtualPins(self.uCodeConfig)
        autogenSignalDict = {}
        for signal in virtualPins["OutputControlPins"]:
            autogenSignalDict[signal] = []

        totalColumnNo = len(outSignalLineList[0])
        signalIndexDict =  ParseConfig.getAllSignalIndex(SIGNAL_CFG_OUTPUT, self.uCodeConfig)
        for columnNo in range(totalColumnNo):
            highFound = False
            for line in outSignalLineList:
                signalName = line[INDEX_OF_SIGNAL_NAME]
                item = line[columnNo]
                if item not in [SIGNAL_VALUE_HIGH, SIGNAL_VALUE_LOW]:
                    highFound = True # Mark as found to avoid all zero
                    continue
                if item == SIGNAL_VALUE_HIGH and highFound:
                    print(f"Warning: Multiple HIGH signals found in column {columnNo}. Using the last one.")
                    break
                if item == SIGNAL_VALUE_HIGH:
                    highFound = True
                    index = signalIndexDict[signalName]
                    for signal in virtualPins["OutputControlPins"]:
                        autogenSignalDict[signal].append((index & 1))
                        index = index >> 1
            if not highFound:
                for signal in virtualPins["OutputControlPins"]:
                    autogenSignalDict[signal].append(0)

        return autogenSignalDict


    def createAutoGenInstructionFile(self,
                                     insFile,
                                     instructionName,
                                     insOtherLineList,
                                     autogenInSignalDict,
                                     autogenOutSignalDict,
                                     insInSignalLineList,
                                     insExtSignalLineList):
        # Merging all the data together and create a autogen Instruction File
        if not os.path.exists("out"):
            os.mkdir("out")
        if not os.path.exists("out/autogen"):
            os.mkdir("out/autogen")
        f = open(os.path.join("out", "autogen", f"Autogen_{instructionName}.py"), "w")
        f.write(f"# Auto-generated Instruction File for {instructionName}\n")
        f.write(f"# Generated from {insFile}\n\n")

        f.write("INS = '''")
        for (line, index) in insOtherLineList[:-2]:
            f.write(f"{line}\n")

        for signal in autogenInSignalDict:
            values = autogenInSignalDict[signal]
            f.write(f"| O | {signal} | " + " | ".join([str(v) for v in values]) + " |\n")


        for signal in autogenOutSignalDict:
            values = autogenOutSignalDict[signal]
            f.write(f"| O | {signal} | " + " | ".join([str(v) for v in values]) + " |\n")
        f.write(f"|---|-------|" + "|".join(["---"] * len(insInSignalLineList[0][2:])) + "|\n")

        count = 0
        for line in insExtSignalLineList:
            f.write(f"{line}\n")
            count += 1
            if count == 8:
                f.write(f"|---|-------|" + "|".join(["---"] * len(insInSignalLineList[0][2:])) + "|\n")
                count = 0

        for _ in range(8 - count):
            f.write(f"| O |  -    | " + " | ".join(["-"] * len(insInSignalLineList[0][2:])) + " |\n")

        for (line, index) in insOtherLineList[-2:]:
            f.write(f"{line}\n")
        f.write("'''\n")
        f.close()


if __name__ == "__main__":
    autoGen = GenAutoInstructions()
    autoGen.autogenEachInstruction()
