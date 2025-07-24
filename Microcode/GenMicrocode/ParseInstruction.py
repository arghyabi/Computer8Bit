import os

CHIP_AT28C16  = "AT28C16"
CHIP_AT28C256 = "AT28C256"

microCodeMapFile = os.path.join("out", "microCodeMap.txt")

class ParseInstructions:
    def __init__(self, chipName):
        self.chipName = chipName

        if self.chipName == CHIP_AT28C16:
            from Instructions.Input_11_bit import InsOUT as OUT
            from Instructions.Input_11_bit import InsADD as ADD
            from Instructions.Input_11_bit import InsSUB as SUB
            from Instructions.Input_11_bit import InsINC as INC
            from Instructions.Input_11_bit import InsDEC as DEC
            from Instructions.Input_11_bit import InsLDI as LDI
            from Instructions.Input_11_bit import InsLDM as LDM
            from Instructions.Input_11_bit import InsSAV as SAV
            from Instructions.Input_11_bit import InsJMP as JMP
            from Instructions.Input_11_bit import InsJMZ as JMZ
            from Instructions.Input_11_bit import InsJNZ as JNZ
            from Instructions.Input_11_bit import InsJMC as JMC

            self.insObjects = [OUT, ADD, SUB, INC, DEC, LDI, LDM, SAV, JMP, JMZ, JNZ, JMC]

        if self.chipName == CHIP_AT28C256:
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
            from Instructions.Input_15_bit import InsRST as RST

            self.insObjects = [
                NOP,
                OUT,
                HLT,
                ADD,
                SUB,
                INC,
                DEC,
                LDI,
                LDM,
                SAV,
                JMP,
                JMZ,
                JNZ,
                JMC,
                MOV,
                AND,
                OR,
                XOR,
                NOT,
                RST,
            ]
        self.InstructionParsedData = {}


    def parseEachInstruction(self):
        for ins in self.insObjects:
            insFile = ins.__file__
            if insFile:
                print("Reading File:", "/".join((insFile).split(os.path.sep)[-2:]))

            textIns :str = ins.INS
            lines = textIns.split("\n")

            instructionName = None
            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
                    # print(f"Instruction Name: {instructionName}")
                    break

            addressMatrix  = []
            if self.chipName == CHIP_AT28C16:
                outputMatrix   = {"0":[],"1":[],"2":[]}
                microInsMatrix = {"in":[],"out":{"0":[],"1":[],"2":[]}}
            if self.chipName == CHIP_AT28C256:
                outputMatrix   = {"0":[],"1":[],"2":[], "3":[]}
                microInsMatrix = {"in":[],"out":{"0":[],"1":[],"2":[], "3":[]}}
            outCount = 0
            chipCount = 0
            for line in lines:
                lineSplit = [item.strip() for item in line.split("|") if item.strip()]
                if len(lineSplit) == 0:
                    continue
                # print(lineSplit)
                if lineSplit[0] == "I":
                    # print(f"address: {lineSplit[2:]}")
                    addressMatrix.append(lineSplit[2:])
                    microInsMatrix["in"].append(lineSplit[1])
                elif lineSplit[0] == "O":
                    # print(f"Output: {lineSplit[2:]}")
                    if chipCount == 0:
                        outputMatrix["0"].append(lineSplit[2:])
                        microInsMatrix["out"]["0"].append(lineSplit[1])
                    elif chipCount == 1:
                        outputMatrix["1"].append(lineSplit[2:])
                        microInsMatrix["out"]["1"].append(lineSplit[1])
                    elif chipCount == 2:
                        outputMatrix["2"].append(lineSplit[2:])
                        microInsMatrix["out"]["2"].append(lineSplit[1])
                    if self.chipName == CHIP_AT28C256:
                        if chipCount == 3:
                            outputMatrix["3"].append(lineSplit[2:])
                            microInsMatrix["out"]["3"].append(lineSplit[1])
                    outCount += 1
                    if outCount == 8:
                        chipCount += 1
                        outCount = 0

            # print(f"Address Matrix: {addressMatrix}")
            # print("=====================================")
            # print(f"Output Matrix: {outputMatrix}")

            self.InstructionParsedData[instructionName] = {
                "microInsMatrix": microInsMatrix,
                "addressMatrix": addressMatrix,
                "outputMatrix": outputMatrix
            }
        # print(json.dumps(self.InstructionParsedData, indent=4))
        # print(self.InstructionParsedData)


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
        if self.chipName == CHIP_AT28C16:
            microcodeMatrix = {"0":[],"1":[],"2":[]}
            microcodeSize = 2048
        if self.chipName == CHIP_AT28C256:
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
    parser = ParseInstructions("AT28C256")
    parser.parseEachInstruction()
    # print("=====================================")
    parser.generateAddressDataMap()

    # val = parser.getValueFromList(["1", "1", "0", "1", "0", "1", "0", "1"])
    # for item in val:
    # print(f"item: {val:08b}, {val}")
