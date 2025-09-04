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

SIGNAL_VALUE_HIGH = "1"
SIGNAL_VALUE_LOW  = "0"

MICROCODE_CFG_FILE = "MicroCodeConfig.yaml"
SIGNAL_CFG_INPUT  = "InputControl"
SIGNAL_CFG_OUTPUT = "OutputControl"
SIGNAL_CFG_EXTRA  = "Extra"

INDEX_OF_SIGNAL_TYPE = 0
INDEX_OF_SIGNAL_NAME = 1

microCodeMapFile = os.path.join("out", "microCodeMap.txt")

class ParseInstructions:
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
        self.insObjects = [ INC ]
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
            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
                    print(f"Instruction Name: {instructionName}")
                    break

            # autoGenInsDict[instructionName] = insFile

            addressMatrix  = []
            outputMatrix   = {"0":[],"1":[],"2":[], "3":[], "4": []}
            microInsMatrix = {"in":[],"out":{"0":[],"1":[],"2":[], "3":[], "4": []}}
            outCount = 0
            segmentCount = 0
            for line in lines:
                lineSplit = [item.strip() for item in line.split("|") if item.strip()]
                if len(lineSplit) < 2:
                    InsOtherLineList.append(line)
                    continue
                # print(line)
                signalType = lineSplit[INDEX_OF_SIGNAL_TYPE]
                signalName = lineSplit[INDEX_OF_SIGNAL_NAME]
                signalData = lineSplit[2:]

                if signalType not in [SIGNAL_TYPE_INPUT, SIGNAL_TYPE_OUTPUT]:
                    InsOtherLineList.append(line)
                    continue
                if signalName == "-":
                    InsOtherLineList.append(line)
                    continue

                # print(lineSplit)
                if signalType == SIGNAL_TYPE_INPUT:
                    # print(f"address: {lineSplit[2:]}")
                    # addressMatrix.append(lineSplit[2:])
                    # microInsMatrix["in"].append(signalName)
                    InsOtherLineList.append(line)
                elif signalType == SIGNAL_TYPE_OUTPUT:
                    pinIndex, sectionType = ParseConfig.getSignalIndex(signalName, self.uCodeConfig)
                    if pinIndex == -1:
                        print(f"ERROR: Signal '{signalName}' not found in configuration. Ignoring...")
                        raise Exception(f"Signal '{signalName}' not found in configuration.")
                    if sectionType == SIGNAL_CFG_EXTRA:
                        InsExtSignalLineList.append(line)
                        pass
                    if sectionType == SIGNAL_CFG_OUTPUT:
                        InsOutSignalLineList.append(lineSplit)
                        pass
                    elif sectionType == SIGNAL_CFG_INPUT:
                        InsInSignalLineList.append(lineSplit)
                        pass
                    else:
                        # print(f"Warning: Signal '{signalName}' has unknown section '{sectionType}'. Ignoring...")
                        continue

            # self.InstructionParsedData[instructionName] = {
            #     "microInsMatrix": microInsMatrix,
            #     "addressMatrix": addressMatrix,
            #     "outputMatrix": outputMatrix
            # }
        # print(json.dumps(self.InstructionParsedData, indent=4))
        # print(self.InstructionParsedData)

            # print("Auto-generated Instruction Lines:")
            # for line in InsOtherLineList:
            #     print(line)

            if len(InsInSignalLineList) > 16:
                print("\nError: Number of Input Control Signals exceeded 16")

            if len(InsOutSignalLineList) > 16:
                print("\nError: Number of Output Control Signals exceeded 16")

            print("\nInput Control Signals used:")
            for line in InsInSignalLineList:
                print(line)

            autogenInSignalDict = self.autogenInputSignalLines(InsInSignalLineList)

            # print(autogenInSignalDict)

            print("\nOutput Control Signals used:")
            for line in InsOutSignalLineList:
                print(line)

            autogenOutSignalDict = self.autogenOutputSignalLines(InsOutSignalLineList)

            # print(autogenOutSignalDict)

            # if len(autogenInSignalDict[0]) != len(autogenOutSignalDict[0]):
            #     print("\nError: Number of Input Control Signal columns and Output Control Signal columns are not matching")
                # raise Exception("Number of Input Control Signal columns and Output Control Signal columns are not matching")



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


    def getPossiableValueCombinations(self, comingValMatrix):
        valueList = list()
        valMatrix = []
        for index in range(len(comingValMatrix), 0 ,-1):
            valMatrix.append(comingValMatrix[index-1])
        maxVal = pow(2, len(valMatrix))

        for tryVal in range(maxVal):
            value = tryVal
            index = 0
            for item in valMatrix:
                if item == "1" or item == "0":
                    value = value & ~(1 << index)
                    value = value | (int(item) << index)
                index += 1
            if value not in valueList:
                valueList.append(value)
        return valueList


    def getValueFromList(self, comingValMatrix):
        valMatrix = []
        for index in range(len(comingValMatrix), 0 ,-1):
            valMatrix.append(comingValMatrix[index-1])
        value = 0
        for i in range(len(valMatrix)):
            if valMatrix[i] == "1":
                value = value | (1 << i)
        return value


    def generateAddressDataMap(self):
        # AllAddress = []
        microcodeMatrix = {"0":[],"1":[],"2":[], "3":[]}
        microcodeSize = 32768
        for chip in microcodeMatrix:
            for i in range(microcodeSize):
                microcodeMatrix[chip].append(0)
        microInsMatrix = None

        if os.path.exists(microCodeMapFile):
            os.remove(microCodeMapFile)

        if not os.path.exists("out"):
            os.mkdir("out")

        mapFilePointer = open(microCodeMapFile, "w")

        for instruction in self.InstructionParsedData:
            print("Processing Instruction:", instruction)
            addressMatrix = self.InstructionParsedData[instruction]["addressMatrix"]
            microInsMatrix = self.InstructionParsedData[instruction]["microInsMatrix"]
            addressDataMap = []
            for i in range(len(addressMatrix[0])):
                temp = []
                for row in addressMatrix:
                    temp.append(row[i])
                addressDataMap.append(temp)
            # print(f"...................... address {instruction}.......................")
            # print(addressDataMap)

            dataMatrix = self.InstructionParsedData[instruction]["outputMatrix"]

            for chip in microcodeMatrix:
                dataDataMap = []
                # chip = "0"
                for i in range(len(dataMatrix[chip][0])):
                    temp = []
                    for row in dataMatrix[chip]:
                        temp.append(row[i])
                    dataDataMap.append(temp)
                # print(f"......................val {instruction} chip {chip}.......................")
                # print(dataDataMap)
                mapFilePointer.write(f"\n\nInstruction: {instruction}; Chip: {chip}\n")
                mapIndex = 1
                for index in range(len(addressDataMap)):
                    addresses = self.getPossiableValueCombinations(addressDataMap[index])
                    # print(f"chip:{chip} | AddressMap: {addressDataMap[index]}")
                    # print(f"chip:{chip} | Addresses: {addresses}")
                    value = self.getValueFromList(dataDataMap[index])
                    for address in addresses:
                        # print(f"Address: 0x{address:04x} => Value: 0x{value:02x}")
                        microcodeMatrix[chip][address] = value
                        # if address not in AllAddress:
                        #     AllAddress.append(address)
                        # else:
                        #     raise Exception(f"Address: 0x{address:04x} already exists!!!")
                    # print(f"Address: {address:08b}, Value: {value:08b
                        mapFilePointer.write(f"chip_{chip}_ins_{instruction.lower()}_{mapIndex:04d} :: 0x{address:04x} => 0x{value:02x} //")
                        strAdd = str(f"{address:015b}")
                        strVal = str(f"{value:08b}")
                        mapFilePointer.write(f" {strAdd[:1]}_{strAdd[1:3]}_{strAdd[3:7]}_{strAdd[7:11]}.{strAdd[11:15]} :: {strAdd[:4]}.{strAdd[4:8]}\n")
                        mapIndex += 1
            print("Process done.")

        mapFilePointer.close()


            # break
        # print("=====================================")
        # print("Microcode Matrix:")
        # print(microcodeMatrix)

        # f = open("out.txt", "w")
        # for chip in microcodeMatrix:
        #     f.write(f"\n\nChip: {chip}\n")
        #     for i in range(2048):
        #         f.write(f"0x{i:04x} ({i:011b}) => 0x{microcodeMatrix[chip][i]:02x} // {microcodeMatrix[chip][i]:08b} // {microcodeMatrix[chip][i]}\n")
        # f.close()

        return microcodeMatrix, microInsMatrix



if __name__ == "__main__":
    parser = ParseInstructions()
    parser.parseEachInstruction()
    # print("=====================================")
    # parser.generateAddressDataMap()

    # val = parser.getValueFromList(["1", "1", "0", "1", "0", "1", "0", "1"])
    # for item in val:
    # print(f"item: {val:08b}, {val}")
