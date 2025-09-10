import os
import importlib
import glob

CHIP_AT28C16  = "AT28C16"
CHIP_AT28C256 = "AT28C256"

microCodeMapFile = os.path.join("out", "microCodeMap.txt")

class ParseInstructions:
    def __init__(self):
        self.insObjects = []
        autogenDir = os.path.join(os.path.dirname(__file__), "out", "autogen")
        autogenFiles = glob.glob(os.path.join(autogenDir, "Autogen_*.py"))

        for filePath in sorted(autogenFiles):
            moduleFilename = os.path.basename(filePath)
            moduleName = moduleFilename[:-3]  # Remove .py extension

            try:
                # Import the module dynamically
                module = importlib.import_module(f"out.autogen.{moduleName}")
                self.insObjects.append(module)
            except ImportError as e:
                print(f"Failed to import {moduleName}: {e}")

        print(f"Total autogen instructions imported: {len(self.insObjects)} \n")

        self.insObjects.sort(key = lambda x: x.__name__)
        self.instructionParsedData = {}


    def parseEachInstruction(self):
        for ins in self.insObjects:
            textIns :str = ins.INS
            lines = textIns.split("\n")

            instructionName = None
            for line in lines:
                if "INSTRUCTION:" in line:
                    instructionName = line.split(":")[-1].strip()
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

                if lineSplit[0] == "I":
                    addressMatrix.append(lineSplit[2:])
                    microInsMatrix["in"].append(lineSplit[1])

                elif lineSplit[0] == "O":
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


            self.instructionParsedData[instructionName] = {
                "microInsMatrix": microInsMatrix,
                "addressMatrix": addressMatrix,
                "outputMatrix": outputMatrix
            }


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
        microcodeMatrix = {"0":[],"1":[],"2":[]}
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

        totalInstructions = len(self.instructionParsedData)

        doneCount = 0
        for instruction in self.instructionParsedData:
            print(f"Processing Instruction: {instruction}{' ' * 100}")
            percent = (doneCount / totalInstructions) * 100
            barLength = 40
            filledLength = int(barLength * percent // 100)
            bar = '#' * filledLength + '-' * (barLength - filledLength)
            print(f"\t Progress: [{bar}] {percent:6.2f}%", end="\r")
            addressMatrix = self.instructionParsedData[instruction]["addressMatrix"]
            microInsMatrix = self.instructionParsedData[instruction]["microInsMatrix"]
            addressDataMap = []
            for i in range(len(addressMatrix[0])):
                temp = []
                for row in addressMatrix:
                    temp.append(row[i])
                addressDataMap.append(temp)

            dataMatrix = self.instructionParsedData[instruction]["outputMatrix"]

            for chip in microcodeMatrix:
                dataDataMap = []
                for i in range(len(dataMatrix[chip][0])):
                    temp = []
                    for row in dataMatrix[chip]:
                        temp.append(row[i])
                    dataDataMap.append(temp)

                mapFilePointer.write(f"\n\nInstruction: {instruction}; Chip: {chip}\n")
                mapIndex = 1
                for index in range(len(addressDataMap)):
                    addresses = self.getPossiableValueCombinations(addressDataMap[index])
                    value = self.getValueFromList(dataDataMap[index])
                    for address in addresses:
                        microcodeMatrix[chip][address] = value
                        mapFilePointer.write(f"chip_{chip}_ins_{instruction.lower()}_{mapIndex:04d} :: 0x{address:04x} => 0x{value:02x} //")
                        strAdd = str(f"{address:015b}")
                        strVal = str(f"{value:08b}")
                        mapFilePointer.write(f" {strAdd[:1]}_{strAdd[1:3]}_{strAdd[3:7]}_{strAdd[7:11]}.{strAdd[11:15]} :: {strAdd[:4]}.{strAdd[4:8]}\n")
                        mapIndex += 1
            doneCount += 1

        print(f"{' ' * 150}")

        mapFilePointer.close()

        return microcodeMatrix, microInsMatrix



if __name__ == "__main__":
    parser = ParseInstructions()
    parser.parseEachInstruction()
    parser.generateAddressDataMap()

