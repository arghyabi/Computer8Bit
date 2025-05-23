import json

from Instructions import InsADD as ADD
from Instructions import InsSUB as SUB
from Instructions import InsJMP as JMP
from Instructions import InsJMZ as JMZ
from Instructions import InsJNZ as JNZ
from Instructions import InsOUT as OUT
from Instructions import InsDEC as DEC
from Instructions import InsINC as INC

insObjects = [ADD, SUB, JMP, JMZ, JNZ, OUT, DEC, INC]


class ParseInstructions:
    def __init__(self):
        self.InstructionParsedData = {}


    def parseEachInstruction(self):
        for ins in insObjects:
            textIns :str = ins.INS
            lines = textIns.split("\n")

            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
                    # print(f"Instruction Name: {instructionName}")
                    break

            addressMatrix  = []
            outputMatrix   = {"0":[],"1":[],"2":[]}
            microInsMatrix = {"in":[],"out":{"0":[],"1":[],"2":[]}}
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
        microcodeMatrix = {"0":[],"1":[],"2":[]}
        for chip in microcodeMatrix:
            for i in range(2048):
                microcodeMatrix[chip].append(0)
        microInsMatrix = None
        for instruction in self.InstructionParsedData:
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
    parser.generateAddressDataMap()

    # val = parser.getValueFromList(["1", "1", "0", "1", "0", "1", "0", "1"])
    # for item in val:
    # print(f"item: {val:08b}, {val}")
