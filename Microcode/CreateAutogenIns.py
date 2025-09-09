import os

from Instructions.Input_15_bit import InsNOP as NOP
from Instructions.Input_15_bit import InsOUT as OUT
from Instructions.Input_15_bit import InsHLT as HLT
from Instructions.Input_15_bit import InsADD as ADD
from Instructions.Input_15_bit import InsSUB as SUB
from Instructions.Input_15_bit import InsINC as INC
from Instructions.Input_15_bit import InsDEC as DEC
from Instructions.Input_15_bit import InsLDI as LDI
from Instructions.Input_15_bit import InsLDM as LDM
from Instructions.Input_15_bit import InsSAV as SAV
from Instructions.Input_15_bit import InsJMP as JMP
from Instructions.Input_15_bit import InsJMZ as JMZ
from Instructions.Input_15_bit import InsJNZ as JNZ
from Instructions.Input_15_bit import InsJMC as JMC
from Instructions.Input_15_bit import InsMOV as MOV
from Instructions.Input_15_bit import InsAND as AND
from Instructions.Input_15_bit import InsOR  as  OR
from Instructions.Input_15_bit import InsXOR as XOR
from Instructions.Input_15_bit import InsNOT as NOT
from Instructions.Input_15_bit import InsCMP as CMP
from Instructions.Input_15_bit import InsCMI as CMI
from Instructions.Input_15_bit import InsRST as RST


import ParseConfig

# CHIP_AT28C16  = "AT28C16"
# CHIP_AT28C256 = "AT28C256"

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

microCodeMapFile = os.path.join("out", "microCodeMap.txt")

class GenAutoInstructions:
    def __init__(self):
        self.uCodeConfig = ParseConfig.parseConfig(MICROCODE_CFG_FILE)
        self.insObjects = [
            LDM,
            NOP,
            OUT,
            HLT,
            ADD,
            SUB,
            INC,
            DEC,
            LDI,
            SAV,
            JMP,
            JMZ,
            JNZ,
            JMC,
            MOV,
            AND,
            OR ,
            XOR,
            NOT,
            CMP,
            CMI,
            RST,
        ]
        # self.insObjects = [ INC ]
        self.InstructionParsedData = {}


    def parseEachInstruction(self):
        autoGenInsDict = {}
        for ins in self.insObjects:
            insFile = ins.__file__
            if insFile:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("Reading File:", "/".join((insFile).split(os.path.sep)[-2:]))

            textIns :str = ins.INS
            lines = textIns.split("\n")

            InsOtherLineList = []
            InsInSignalLineList = []
            InsOutSignalLineList = []
            InsExtSignalLineList = []
            instructionName = None
            OtherLineIndex = -1
            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
                    print(f"Instruction Name: {instructionName}")
                    break


            for line in lines:
                OtherLineIndex += 1
                lineSplit = [item.strip() for item in line.split("|") if item.strip()]
                if len(lineSplit) < 2:
                    InsOtherLineList.append((line, OtherLineIndex))
                    continue

                signalType = lineSplit[INDEX_OF_SIGNAL_TYPE]
                signalName = lineSplit[INDEX_OF_SIGNAL_NAME]
                signalData = lineSplit[2:]

                if signalType == SIGNAL_TYPE_IGNORE or signalName == "-":
                    continue

                if signalType == SIGNAL_TYPE_OUTPUT:
                    pinIndex, sectionType = ParseConfig.getSignalIndex(signalName, self.uCodeConfig)
                    if pinIndex == -1:
                        print(f"ERROR: Signal '{signalName}' not found in configuration. Ignoring...")
                        raise Exception(f"Signal '{signalName}' not found in configuration.")

                    if sectionType == SIGNAL_CFG_EXTRA:
                        InsExtSignalLineList.append(line)

                    if sectionType == SIGNAL_CFG_OUTPUT:
                        InsOutSignalLineList.append(lineSplit)

                    if sectionType == SIGNAL_CFG_INPUT:
                        InsInSignalLineList.append(lineSplit)
                else:
                    InsOtherLineList.append((line, OtherLineIndex))


            # print("Auto-generated Instruction Lines:")
            # for (line, index) in InsOtherLineList:
            #     print(line, index)

            if len(InsInSignalLineList) > 16:
                print("\nError: Number of Input Control Signals exceeded 16")

            if len(InsOutSignalLineList) > 16:
                print("\nError: Number of Output Control Signals exceeded 16")

            # print("\nInput Control Signals used:")
            # for line in InsInSignalLineList:
            #     print(line)

            autogenInSignalDict = self.autogenInputSignalLines(InsInSignalLineList)

            # print(autogenInSignalDict)

            # print("\nOutput Control Signals used:")
            # for line in InsOutSignalLineList:
            #     print(line)

            autogenOutSignalDict = self.autogenOutputSignalLines(InsOutSignalLineList)

            # print(autogenOutSignalDict)

            self.createAutoGenInstructionFile(insFile,
                                                instructionName,
                                                InsOtherLineList,
                                                autogenInSignalDict,
                                                autogenOutSignalDict,
                                                InsInSignalLineList,
                                                InsExtSignalLineList)




    # Auto-generate virtual Input Control Signals with help of the config file
    # This is a internal logic to generate the autogen Instruction Files.
    def autogenInputSignalLines(self, InSignalLineList):
        virtualPins = ParseConfig.getAllVirtualPins(self.uCodeConfig)
        autogenSignalDict = {}
        for signal in virtualPins["InputControlPins"]:
            autogenSignalDict[signal] = []

        totalColumnNo = len(InSignalLineList[0])
        signalIndexDict =  ParseConfig.getAllSignalIndex(SIGNAL_CFG_INPUT, self.uCodeConfig)
        for columnNo in range(totalColumnNo):
            highFound = False
            for line in InSignalLineList:
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

        # for signal, values in autogenSignalDict.items():
        #     print(signal, values)

        return autogenSignalDict


    # Auto-generate virtual Output Control Signals with help of the config file
    # This is a internal logic to generate the autogen Instruction Files.
    def autogenOutputSignalLines(self, OutSignalLineList):
        virtualPins = ParseConfig.getAllVirtualPins(self.uCodeConfig)
        autogenSignalDict = {}
        for signal in virtualPins["OutputControlPins"]:
            autogenSignalDict[signal] = []

        totalColumnNo = len(OutSignalLineList[0])
        signalIndexDict =  ParseConfig.getAllSignalIndex(SIGNAL_CFG_OUTPUT, self.uCodeConfig)
        for columnNo in range(totalColumnNo):
            highFound = False
            for line in OutSignalLineList:
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

        # for signal, values in autogenSignalDict.items():
        #     print(signal, values)

        return autogenSignalDict


    def createAutoGenInstructionFile(self,
                                     insFile,
                                     instructionName,
                                     InsOtherLineList,
                                     autogenInSignalDict,
                                     autogenOutSignalDict,
                                     InsInSignalLineList,
                                     InsExtSignalLineList):
        # Merging all the data together and create a autogen Instruction File
        if not os.path.exists("out"):
            os.mkdir("out")
        if not os.path.exists("out/autogen"):
            os.mkdir("out/autogen")
        f = open(os.path.join("out", "autogen", f"Autogen_{instructionName}.py"), "w")
        f.write(f"# Auto-generated Instruction File for {instructionName}\n")
        f.write(f"# Generated from {insFile}\n\n")

        f.write("INS = '''")
        for (line, index) in InsOtherLineList[:-2]:
            f.write(f"{line}\n")

        for signal in autogenInSignalDict:
            values = autogenInSignalDict[signal]
            f.write(f"| O | {signal} | " + " | ".join([str(v) for v in values]) + " |\n")


        for signal in autogenOutSignalDict:
            values = autogenOutSignalDict[signal]
            f.write(f"| O | {signal} | " + " | ".join([str(v) for v in values]) + " |\n")
        f.write(f"|---|-------|" + "|".join(["---"] * len(InsInSignalLineList[0][2:])) + "|\n")

        count = 0
        for line in InsExtSignalLineList:
            f.write(f"{line}\n")
            count += 1
            if count == 8:
                f.write(f"|---|-------|" + "|".join(["---"] * len(InsInSignalLineList[0][2:])) + "|\n")
                count = 0

        for _ in range(8 - count):
            f.write(f"| O |  -    | " + " | ".join(["-"] * len(InsInSignalLineList[0][2:])) + " |\n")

        for (line, index) in InsOtherLineList[-2:]:
            f.write(f"{line}\n")
        f.write("'''\n")
        f.close()


if __name__ == "__main__":
    parser = GenAutoInstructions()
    parser.parseEachInstruction()
    # print("=====================================")
    # parser.generateAddressDataMap()

    # val = parser.getValueFromList(["1", "1", "0", "1", "0", "1", "0", "1"])
    # for item in val:
    # print(f"item: {val:08b}, {val}")
