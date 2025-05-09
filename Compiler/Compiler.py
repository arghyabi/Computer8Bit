import argparse
import os

class Compiler:
    def __init__(self, assemblyFile, outFile, silent):
        if not os.path.exists(assemblyFile):
            raise Exception(f"{assemblyFile} not found!!!")

        try:
            f = open(assemblyFile, 'r')
            assembly = f.read()
            f.close()
        except Exception as e:
            print(f"Not able to open the {assemblyFile}!!!")
            exit(-1)

        self.assemblyFile = assemblyFile
        self.assemblyMain = assembly
        self.outFile      = outFile
        self.silent       = silent
        self.registerList = ['A', 'B', 'C', 'D']
        self.registerDict = {
            'A': 0b00,
            'B': 0b01,
            'C': 0b10,
            'D': 0b11
        }
        self.instructionDict = {
            'ADD': 0b0000,
            'MOV': 0b0001,
            'SUB': 0b0100,
            'INC': 0b1000,
            'DEC': 0b1100
        }

        self.preProcess()
        self.compile()


    def preProcess(self):
        # split each line
        self.assemblyMain = self.assemblyMain.split("\n")
        self.assemblyLine = [line.strip() for line in self.assemblyMain]

        # remove comments
        self.assemblyLine = [line.split(";")[0] for line in self.assemblyLine]

        # make all upper case
        self.assemblyLine = [line.upper() for line in self.assemblyLine]

        # write intermediate file for debug
        if not self.silent:
            tempName = ".".join((self.assemblyFile).split(".")[:-1])
            tempName = f"{tempName}.i"
            f = open(tempName, "w")
            for line in self.assemblyLine:
                f.write(f"{line}\n")
            f.close()


    def compile(self):
        def errorPrint(index):
            errorLine = self.assemblyMain[index]
            raise Exception(f"'{errorLine}' at line no {index + 1} is not able to compile!!!")

        def printCompiledLine(line, value):
            binary = f"{value:08b}"
            print(f"Ins: '{line}'; Code: {binary[:4]}_{binary[4:]} : {hex(value)}")

        binArr = bytearray()

        for index, line in enumerate(self.assemblyLine):
            if not line:
                continue

            splitData   = line.split()
            opcode      = splitData[0]
            payloadList = splitData[1:]
            payloadLen  = len(payloadList)
            bitVal      = 0

            if opcode == "MOV":
                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index)
                # Ignore the instruction like 'mov a' or 'mov b' ..
                if payloadLen == 1:
                    continue
                if payloadLen != 2:
                    errorPrint(index)

                for payload in payloadList:
                    bitVal = bitVal << 2
                    bitVal = bitVal | self.registerDict[payload]

                bitVal = bitVal << 4
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    printCompiledLine(line, bitVal)

            elif opcode == "ADD" or opcode == "SUB" or opcode == "INC" or opcode == "DEC":
                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index)
                if payloadLen != 1:
                    errorPrint(index)

                payload = payloadList[0]
                bitVal = bitVal | self.registerDict[payload]

                bitVal = bitVal << 4
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    printCompiledLine(line, bitVal)
            else:
                errorPrint(index)

            binArr.append(bitVal)

        f = open(self.outFile, 'wb')
        f.write(binArr)
        f.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("assemblyFile", help="Assembly File")
    parser.add_argument("-o", "--out", default="out.bin", help="output Bin File")
    parser.add_argument("-s", "--silent", action ='store_true', help="Do not generate intermediate files")

    args = parser.parse_args()
    assemblyFile = args.assemblyFile
    outFile      = args.out
    silent       = args.silent

    compile = Compiler(assemblyFile, outFile, silent)

if __name__ == "__main__":
    main()
