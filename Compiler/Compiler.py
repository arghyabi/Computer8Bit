import argparse
import os
import hexdump

MAX_VAL_8_BIT     = 255
MAX_ADDRESS_8_BIT = 255

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def isHex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


class Compiler:
    def __init__(self, assemblyFile, outFile, silent):
        if not os.path.exists(assemblyFile):
            print(f"{assemblyFile} not found!!!")
            exit(-1)

        try:
            f = open(assemblyFile, 'r')
            assembly = f.read()
            f.close()
        except Exception as e:
            print(f"Not able to open the {assemblyFile}!!!")
            exit(-1)

        self.assemblyFile       = assemblyFile
        self.assemblyMain       = assembly
        self.outFile            = outFile
        self.silent             = silent
        self.tagDict            = dict()
        self.binArr             = bytearray()
        self.sourceMaxLength    = 0
        self.tagMaxLength       = 0
        self.addressIndex       = 0
        self.logBuffer          = []
        self.registerList       = ['A', 'B', 'C', 'D']
        self.registerDict       = {
            'A': 0b00,
            'B': 0b01,
            'C': 0b10,
            'D': 0b11
        }
        self.instructionDict = {
            'NOP': 0b0000_0000,
            'ADD':   0b00_0001,
            'SUB':   0b01_0001,
            'INC':   0b10_0001,
            'DEC':   0b11_0001,
            'MOV':     0b_0101,
            'LDI':   0b00_0010,
            'LDM':   0b01_0010,
            'SAV':   0b10_0010,
            'JMP': 0b0000_0011,
            'JMZ': 0b0001_0011,
            'JNZ': 0b0010_0011,
            'OUT': 0b0001_0000,
            'HLT': 0b0010_0000
        }

        self.instructionSizeDict = {
            'NOP': 1,
            'ADD': 1,
            'SUB': 1,
            'INC': 1,
            'DEC': 1,
            'MOV': 1,
            'LDI': 2,
            'LDM': 2,
            'SAV': 2,
            'JMP': 2,
            'JMZ': 2,
            'JNZ': 2,
            'OUT': 1,
            'HLT': 1
        }

        self.preProcess()
        self.compile()

        if not self.silent:
            print()
            for item in self.logBuffer:
                print(item)

            print("\nTAGs")
            for key, value in self.tagDict.items():
                print(f"0x{value:04X}: {key}")

            print("\n\n  Binary  ", end = "")
            for col in range(0x8):
                print(f"{col:02X} ", end = "")
            print(" ", end = "")
            for col in range(0x8, 0x10):
                print(f"{col:02X} ", end = "")
            print("\n          ------------------------------------------------")

            hexdump.hexdump(self.binArr)


    def preProcess(self):
        # split each line
        self.assemblyMain = self.assemblyMain.split("\n")
        self.assemblyLine = [line.strip() for line in self.assemblyMain]

        # remove comments
        self.assemblyLine = [line.split(";")[0] for line in self.assemblyLine]

        # make all upper case
        self.assemblyLine = [line.upper() for line in self.assemblyLine]

        # get mex size of lines
        for line in self.assemblyLine:
            length = len(line)
            if length > self.sourceMaxLength:
                self.sourceMaxLength = length

        # write intermediate file for debug
        if not self.silent:
            tempName = ".".join((self.assemblyFile).split(".")[:-1])
            tempName = f"{tempName}.i"
            f = open(tempName, "w")
            for line in self.assemblyLine:
                f.write(f"{line}\n")
            f.close()


    def printCompiledLine(self, line, value, value2 = None):
        binary  = f"{value:08b}"
        tag     = next((key for key, value in self.tagDict.items() if value == self.addressIndex), None)
        if tag == None:
            tag = " "*self.tagMaxLength
        else:
            tag = f"{tag:{self.tagMaxLength}}"

        printLine = ""
        printLine += f"{tag} 0x{self.addressIndex:04X}: "
        printLine += f"{line:{self.sourceMaxLength}} | Code: "
        printLine += f"{binary[:4]}_{binary[4:]} "

        if value2 != None:
            binary2 = f"{value2:08b}"
            printLine += f" {binary2[:4]}_{binary2[4:]} "
            printLine += f"// 0x{value:02X} 0x{value2:02X}"
        else:
            printLine += f"           // 0x{value:02X}"

        self.logBuffer.append(printLine)


    def compile(self):
        def errorPrint(index, error = None):
            errorLine = self.assemblyMain[index]
            if error != None:
                errorString = f"'{errorLine}' at line no {index + 1} is not able to compile!!!\nERROR: {error}"
            else:
                errorString = f"'{errorLine}' at line no {index + 1} is not able to compile!!!"
            
            print(errorString)
            exit(-1)


        ## Parsing logic the tags first
        self.addressIndex = 0
        for index, line in enumerate(self.assemblyLine):
            if not line:
                continue

            splitData         = line.split()
            opcode            = splitData[0]

            if len(splitData) == 1 and line[-1] == ":":
                tag = line[:-1].upper()
                self.tagDict[tag] = self.addressIndex
                if len(tag) > self.tagMaxLength:
                    self.tagMaxLength = len(tag)
                continue
            if opcode in self.instructionSizeDict:
                self.addressIndex += self.instructionSizeDict[opcode]
            else:
                errorPrint(index, f"'{opcode}' is not supported instruction!!")


        ## Parsing for each line
        self.addressIndex = 0
        for index, line in enumerate(self.assemblyLine):
            if not line:
                continue

            splitData   = line.split()
            opcode      = splitData[0]
            payloadList = splitData[1:]
            payloadLen  = len(payloadList)
            bitVal      = 0

            ## Parse MOV command | Format: SSDD_0101
            if opcode == "MOV":
                if payloadLen > 2:
                    errorPrint(index, f"2 payload expected!!, but found {payloadLen}")

                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index, f"'{payload}' is not a register!!")

                if payloadLen == 1 or payloadList[0] == payloadList[1]: # Ignore the 'mov a' or 'mov b' or 'mov c c'; its NOP ..
                    pass
                
                if payloadLen == 2:
                    for payload in payloadList:
                        bitVal = bitVal << 2
                        bitVal = bitVal | self.registerDict[payload]

                    bitVal = bitVal << 4
                    bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1


            ## Parse ADD, SUB, INC, DEC commands  | Format: RRTT_0001
            elif opcode == "ADD" or opcode == "SUB" or opcode == "INC" or opcode == "DEC":
                if payloadLen != 1:
                    errorPrint(index, f"1 payload expected!!, but found {payloadLen}")

                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index, f"'{payload}' is not a register!!")

                payload = payloadList[0]
                bitVal = bitVal | self.registerDict[payload]

                bitVal = bitVal << 6 # ADD, SUB, INC, DEC are 6 bit
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1


            ## Parse JMP, JMZ, JNZ command | Format: 00TT_0011
            elif opcode == "JMP" or opcode == "JMZ" or opcode == "JNZ":
                if payloadLen != 1:
                    errorPrint(index, f"1 payload expected!!, but found {payloadLen}")

                payload = payloadList[0]
                address = 0xFF # Default value
                if isInt(payload):
                    address = int(payload)
                elif isHex(payload):
                    address = int(payload, 16)
                elif payload in self.tagDict:
                    address = self.tagDict[payload]
                else:
                    errorPrint(index, f"'{payload}' is not a proper address")
                
                if address > MAX_ADDRESS_8_BIT:
                    errorPrint(index, "Max address limit cross!!")

                bitVal = self.instructionDict[opcode] # JMP, JMZ, JNZ are 8 bit

                if not self.silent:
                    self.printCompiledLine(line, bitVal, address)

                self.binArr.append(bitVal)
                self.addressIndex += 1

                self.binArr.append(address)
                self.addressIndex += 1


            ## Parse LDI command | Format: RRTT_0010
            elif opcode == "LDI":
                if payloadLen != 2:
                    errorPrint(index, f"2 payload expected!!, but found {payloadLen}")

                destReg = payloadList[0]
                if destReg not in self.registerList:
                        errorPrint(index, "Destination register not found!!")

                immediateVal = payloadList[1]
                if isInt(immediateVal):
                    immediateVal = int(immediateVal)
                elif isHex(immediateVal):
                    immediateVal = int(immediateVal, 16)
                else:
                    errorPrint(index, f"{immediateVal} is not a int or hex value!!")

                if immediateVal > MAX_VAL_8_BIT:
                    errorPrint(index, "Max value limit cross!!")

                bitVal = bitVal | self.registerDict[destReg]

                bitVal = bitVal << 6 # LDI is 6 bit
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal, immediateVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1

                self.binArr.append(immediateVal)
                self.addressIndex += 1


            ## Parse LDM, SAV command | Format: RRTT_0010
            elif opcode == "LDM" or opcode == "SAV":
                if payloadLen != 2:
                    errorPrint(index, f"2 payload expected!! but found {payloadLen}")

                destReg = payloadList[0]
                if destReg not in self.registerList:
                        errorPrint(index, "Destination register not found!!")

                memAddress = payloadList[1]
                if isInt(memAddress):
                    memAddress = int(memAddress)
                elif isHex(memAddress):
                    memAddress = int(memAddress, 16)
                else:
                    errorPrint(index, f"{memAddress} is not a int or hex value!!")

                if memAddress > MAX_ADDRESS_8_BIT:
                    errorPrint(index, "Max address limit cross!!")

                bitVal = bitVal | self.registerDict[destReg]

                bitVal = bitVal << 6 # LDM, SAV are 6 bit
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal, memAddress)

                self.binArr.append(bitVal)
                self.addressIndex += 1

                self.binArr.append(memAddress)
                self.addressIndex += 1


            ## Parse HLT, NOP, OUT commands | Format: 00TT_0000
            elif opcode == "HLT" or opcode == "NOP" or opcode == "OUT":
                if payloadLen != 0:
                    errorPrint(index, f"No payload expected!! but found {payloadLen}")

                bitVal = self.instructionDict[opcode] # HLT, NOP, OUT are 8 bit

                if not self.silent:
                    self.printCompiledLine(line, bitVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1


            # Looks like a TAG
            elif opcode[-1] == ":":
                pass
            else:
                errorPrint(index, "No supported instruction found!!")

        f = open(self.outFile, 'wb')
        f.write(self.binArr)
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
