import os

class BinaryLoader:
    @staticmethod
    def loadFile(filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")

        try:
            with open(filename, 'rb') as f:
                binaryData = f.read()

            fileInfo = {
                'filename': os.path.basename(filename),
                'filepath': filename,
                'size'    : len(binaryData),
                'sizeKb'  : len(binaryData) / 1024
            }

            return binaryData, fileInfo

        except Exception as e:
            raise Exception(f"Failed to load file: {e}")


    @staticmethod
    def validateProgram(binaryData, maxSize = 2048):
        issues = []

        if len(binaryData) == 0:
            issues.append("Empty file")

        if len(binaryData) > maxSize:
            issues.append(f"Program too large ({len(binaryData)} > {maxSize} bytes)")

        # Check for common issues
        if len(binaryData) > 0:
            # Check if program starts with valid instruction
            firstByte = binaryData[0]
            if firstByte == 0xFF:
                issues.append("Program starts with padding (0xFF)")

        return len(issues) == 0, issues


    @staticmethod
    def getProgramInfo(binaryData):
        if not binaryData:
            return {"instructions": 0, "size": 0, "nonZeroBytes": 0}

        # Count non-zero bytes (actual program vs padding)
        nonZeroBytes = sum(1 for b in binaryData if b != 0x00 and b != 0xFF)

        # Estimate instruction count (rough approximation)
        # This is simplified - actual count would require proper decoding
        estimatedInstructions = 0
        i = 0
        while i < len(binaryData):
            byte = binaryData[i]
            if byte == 0x00 or byte == 0xFF:  # Padding or NOP
                i += 1
                continue

            # Simple instruction size estimation based on opcode
            opcode = byte & 0x0F
            if opcode in [0x04, 0x0C]:  # LDI, LDM, SAV, CMI
                i += 2  # 2-byte instructions
            elif opcode == 0x05:  # Jump instructions
                i += 3  # 3-byte instructions
            else:
                i += 1  # 1-byte instructions

            estimatedInstructions += 1

        return {
            "size": len(binaryData),
            "nonZeroBytes": nonZeroBytes,
            "estimatedInstructions": estimatedInstructions,
            "paddingBytes": len(binaryData) - nonZeroBytes
        }


class AssemblyLoader:
    @staticmethod
    def loadAssembly(filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Assembly file not found: {filename}")

        try:
            with open(filename, 'r') as f:
                content = f.read()

            return content

        except Exception as e:
            raise Exception(f"Failed to load assembly file: {e}")


    @staticmethod
    def findAssemblyForBinary(binaryFilename):
        baseName = os.path.splitext(binaryFilename)[0]

        # Try common assembly extensions
        for ext in ['.s', '.asm', '.assembly']:
            asmFile = baseName + ext
            if os.path.exists(asmFile):
                return asmFile

        return None


def autoLoadProgram(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    _, ext = os.path.splitext(filename.lower())

    if ext == '.bin':
        # Load binary file
        binaryData, fileInfo = BinaryLoader.loadFile(filename)

        # Try to find assembly source
        asmFile = AssemblyLoader.findAssemblyForBinary(filename)
        assemblySource = None
        if asmFile:
            try:
                assemblySource = AssemblyLoader.loadAssembly(asmFile)
            except:
                pass

        return {
            'binaryData': binaryData,
            'fileInfo': fileInfo,
            'assemblySource': assemblySource,
            'assemblyFile': asmFile
        }

    elif ext in ['.s', '.asm', '.assembly']:
        # Load assembly and look for corresponding binary
        assemblySource = AssemblyLoader.loadAssembly(filename)

        # Look for compiled binary
        baseName = os.path.splitext(filename)[0]
        binFile = baseName + '.bin'

        if os.path.exists(binFile):
            binaryData, fileInfo = BinaryLoader.loadFile(binFile)
        else:
            raise Exception(f"No compiled binary found. Expected: {binFile}")

        return {
            'binaryData': binaryData,
            'fileInfo': fileInfo,
            'assemblySource': assemblySource,
            'assemblyFile': filename
        }
    else:
        raise Exception(f"Unsupported file type: {ext}")
