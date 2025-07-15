import argparse
import os
import hexdump

MAX_VAL_8_BIT          = 256
MAX_ROM_ADDRESS_8_BIT  = 256
MAX_ROM_ADDRESS_11_BIT = 2048
MAX_MEM_ADDRESS_4_BIT  = 16

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
    def __init__(self, assemblyFile, outFile, silent, support8):
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
        self.support8BitAddress = support8
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
            # 0000
            'NOP': 0b0000_0000,
            'OUT': 0b0001_0000,
            'HLT': 0b0010_0000,
            # 0001
            'ADD':     0b_0001,
            # 0010
            'SUB':     0b_0010,
            # 0011
            'INC':   0b10_0011,
            'DEC':   0b11_0011,
            # 0100
            'LDI':   0b00_0100,
            'LDM':   0b01_0100,
            'SAV':   0b10_0100,
            # 0101
            'JMP': 0b0000_0101,
            'JMZ': 0b0001_0101,
            'JNZ': 0b0010_0101,
            'JMC': 0b0011_0101,
            # 0110
            'MOV':     0b_0110,
            # 0111
            'AND':     0b_0111,
            # 1000
            'OR' :     0b_1000,
            # 1001
            'XOR':     0b_1001,
            # 1010
            'NOT':   0b00_1010,
            # 1011
            'CMP':     0b_1011,
            # 1100
            'CMI':   0b00_1100,
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
            'JMP': 3,
            'JMZ': 3,
            'JNZ': 3,
            'JMC': 3,
            'AND': 1,
            'OR' : 1,
            'XOR': 1,
            'NOT': 1,
            'CMP': 1,
            'CMI': 2,
            'OUT': 1,
            'HLT': 1
        }

        if self.support8BitAddress:
            self.instructionSizeDict['JMP'] = 2
            self.instructionSizeDict['JMZ'] = 2
            self.instructionSizeDict['JNZ'] = 2
            self.instructionSizeDict['JMC'] = 2

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
        self.assemblyMain = str(self.assemblyMain).split("\n")
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


    def printCompiledLine(self, line, instruc, value1 = None, value2 = None):
        binary  = f"{instruc:08b}"
        tag     = next((key for key, instruc in self.tagDict.items() if instruc == self.addressIndex), None)
        if tag == None:
            tag = " "*self.tagMaxLength
        else:
            tag = f"{tag:{self.tagMaxLength}}"

        printLine = ""
        printLine += f"{tag} 0x{self.addressIndex:04X}: "
        printLine += f"{line:{self.sourceMaxLength}} | Code: "
        printLine += f"{binary[:4]}_{binary[4:]} "

        if value1 == None: # Value2 ofcourse null
            if self.support8BitAddress:
                printLine += f"            // 0x{instruc:02X}"
            else:
                printLine += f"                     // 0x{instruc:02X}"


        if value1 != None and value2 == None: # Only one value send
            binary = f"{value1:08b}"
            printLine += f" {binary[:4]}_{binary[4:]} "
            if self.support8BitAddress:
                printLine += f" // 0x{instruc:02X} 0x{value1:02X}"
            else:
                printLine += f"          // 0x{instruc:02X} 0x{value1:02X}"

        if value1 != None and value2 != None: # Both high and low address send
            binary1 = f"{value1:08b}"
            binary2 = f"{value2:08b}"
            printLine += f" {binary1[:4]}_{binary1[4:]} {binary2[:4]}_{binary2[4:]} "
            printLine += f"// 0x{instruc:02X} 0x{value1:02X} 0x{value2:02X}"

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
            splitData         = [element for item in splitData for element in item.split(',') if element]
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
            splitData   = [element for item in splitData for element in item.split(',') if element]
            opcode      = splitData[0]
            payloadList = splitData[1:]
            payloadLen  = len(payloadList)
            bitVal      = 0

            # remove if any ',' in the instruction
            payloadList = [part.replace(",", "") for part in payloadList]

            ## Parse ADD, SUB, MOV command | Format: SSDD_0001, SSDD_0010, SSDD_0110
            if opcode == "ADD" or opcode == "SUB" or opcode == "MOV":
                if payloadLen != 2:
                    errorPrint(index, f"2 payload expected!!, but found {payloadLen}")

                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index, f"'{payload}' is not a register!!")

                if payloadList[0] == payloadList[1]: # Ignore the 'mov a a' or 'mov b b'; its NOP ..
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


            ## Parse INC, DEC, NOT commands  | Format: RRTT_0011, RRTT_0011, RR00_1010
            elif opcode == "INC" or opcode == "DEC" or opcode == "NOT":
                if payloadLen != 1:
                    errorPrint(index, f"1 payload expected!!, but found {payloadLen}")

                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index, f"'{payload}' is not a register!!")

                payload = payloadList[0]
                bitVal = bitVal | self.registerDict[payload]

                bitVal = bitVal << 6 # INC, DEC are 6 bit
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1


            ## Parse JMP, JMZ, JNZ command | Format: 00TT_0101
            elif opcode == "JMP" or opcode == "JMZ" or opcode == "JNZ" or opcode == "JMC":
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

                if self.support8BitAddress:
                    if address >= MAX_ROM_ADDRESS_8_BIT:
                        errorPrint(index, "Max ROM address limit cross!!")
                else:
                    if address >= MAX_ROM_ADDRESS_11_BIT:
                        errorPrint(index, "Max ROM address limit cross!!")

                bitVal = self.instructionDict[opcode] # JMP, JMZ, JNZ are 8 bit

                if not self.silent:
                    if self.support8BitAddress:
                        self.printCompiledLine(line, bitVal, address)
                    else:
                        highAddress = address >> 8
                        lowAddress = address & 0xff
                        self.printCompiledLine(line, bitVal, highAddress, lowAddress)


                self.binArr.append(bitVal)
                self.addressIndex += 1

                if self.support8BitAddress:
                    self.binArr.append(address)
                    self.addressIndex += 1
                else:
                    highAddress = address >> 8
                    lowAddress = address & 0xff
                    self.binArr.append(highAddress)
                    self.binArr.append(lowAddress)
                    self.addressIndex += 2


            ## Parse LDI, CMI command | Format: RRTT_0100, RR00_1100
            elif opcode == "LDI" or opcode == "CMI":
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
                    immediateVal = 0

                if immediateVal >= MAX_VAL_8_BIT:
                    errorPrint(index, "Max value limit cross!!")

                bitVal = bitVal | self.registerDict[destReg]

                bitVal = bitVal << 6 # LDI, CMI is 6 bit
                bitVal = bitVal | self.instructionDict[opcode]

                if not self.silent:
                    self.printCompiledLine(line, bitVal, immediateVal)

                self.binArr.append(bitVal)
                self.addressIndex += 1

                self.binArr.append(immediateVal)
                self.addressIndex += 1


            ## Parse LDM, SAV command | Format: RRTT_0100
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
                    memAddress = 0

                if memAddress >= MAX_MEM_ADDRESS_4_BIT:
                    errorPrint(index, "Max memory address limit cross!!")

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


            ## Parse AND, OR, XOR, CMP command | Format: SSDD_0111, SSDD_1000, SSDD_1001, SSDD_1011
            elif opcode == "AND" or opcode == "OR" or opcode == "XOR" or opcode == "CMP":
                if payloadLen != 2:
                    errorPrint(index, f"2 payload expected!!, but found {payloadLen}")

                for payload in payloadList:
                    if payload not in self.registerList:
                        errorPrint(index, f"'{payload}' is not a register!!")

                for payload in payloadList:
                    bitVal = bitVal << 2
                    bitVal = bitVal | self.registerDict[payload]

                bitVal = bitVal << 4
                bitVal = bitVal | self.instructionDict[opcode]

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
    parser.add_argument("assemblyFile", help = "Assembly File")
    parser.add_argument("-o", "--out", default = "out.bin", help = "output Bin File")
    parser.add_argument("-s", "--silent", action = 'store_true', help = "Do not generate intermediate files")
    parser.add_argument("-s8", "--support8", action = 'store_true', help = "Support only 8 bit ROM address")

    args = parser.parse_args()
    assemblyFile = args.assemblyFile
    outFile      = args.out
    silent       = args.silent
    support8     = args.support8

    compile = Compiler(assemblyFile, outFile, silent, support8)

if __name__ == "__main__":
    main()
