import os
import glob
import logging
from typing import Dict, List, Tuple

import MicrocodeConfig

LOGGER = logging.getLogger(__name__)

# Input sections: 2 (Ukwn0/1) + 1 (Flag) + 4 (Seqn0-3) + 8 (InsR0-7) = 15 signals
# Output sections: 8 (uCode0) + 8 (InputControl first half) + 8 (InputControl second half) + 
#                  8 (OutputControl first half) + 8 (OutputControl second half) + 8 (uCode2) = 48 signals


class InstructionNormalizer:
    def __init__(self, configPath: str):
        """Initialize the normalizer with YAML configuration."""
        self.config = MicrocodeConfig.ParseConfig(configPath)
        self.inputPinMap = self._GetInputPinMap()
        self.outputPinMap = self._GetOutputPinMap()
        
    def _GetInputPinMap(self) -> List[str]:
        """Get ordered list of input signals from A14 to A0 (top to bottom in instruction files)."""
        pinMap = self.config.get("MicrocodeChipsPinMap", {}).get("InputPinMap", {})
        # Sort by address in reverse (A14, A13, ..., A0) for top-to-bottom display order
        sortedPins = sorted(pinMap.items(), key=lambda x: int(x[0][1:]), reverse=True)
        return [signal for _, signal in sortedPins]
    
    def _GetOutputPinMap(self) -> Dict[str, List[str]]:
        """Get ordered list of output signals for each chip preserving YAML order."""
        outputMap = self.config.get("MicrocodeChipsPinMap", {}).get("OutputPinMap", {})
        result = {}
        
        for chipName in ["uCode0", "uCode1", "uCode2"]:
            chipPins = outputMap.get(chipName, {})
            # Preserve the order as written in YAML (don't sort)
            result[chipName] = list(chipPins.values())
        
        return result
    
    def _GetVirtualPinSignals(self) -> Tuple[List[str], List[str]]:
        """Get InputControl and OutputControl signals from VirtualPinConfig."""
        virtualConfig = self.config.get("VirtualPinConfig", {})
        
        inputControl = virtualConfig.get("InputControl", {})
        outputControl = virtualConfig.get("OutputControl", {})
        
        # Sort by value to get proper order
        inputSignals = [sig for sig, _ in sorted(inputControl.items(), key=lambda x: x[1])]
        outputSignals = [sig for sig, _ in sorted(outputControl.items(), key=lambda x: x[1])]
        
        return inputSignals, outputSignals
    
    def ParseInstructionFile(self, filePath: str) -> Dict:
        """Parse an instruction file and extract signal data."""
        with open(filePath, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find and preserve header lines (INSTRUCTION, separator, CLOCK header)
        instructionName = None
        headerLines = []
        inHeader = True
        
        for line in lines:
            if 'INSTRUCTION:' in line:
                instructionName = line.split(':')[-1].strip()
                headerLines.append(line)
            elif inHeader and ('===' in line or 'CLOCK' in line):
                headerLines.append(line)
            elif line.strip().startswith('| I |') or line.strip().startswith('| O |'):
                inHeader = False
        
        if not instructionName:
            raise Exception(f"No INSTRUCTION found in {filePath}")
        
        # Parse signal rows
        signalData = {}
        columnCount = 0
        for line in lines:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) < 3:
                continue
            
            signalType = parts[0]
            if signalType not in ['I', 'O']:
                continue
            
            signalName = parts[1]
            values = parts[2:]
            
            signalData[signalName] = {
                'type': signalType,
                'values': values
            }
            columnCount = len(values)
        
        return {
            'name': instructionName,
            'signals': signalData,
            'columnCount': columnCount,
            'headerLines': headerLines
        }
    
    def GenerateNormalizedTable(self, parsedData: Dict) -> str:
        """Generate normalized instruction table according to YAML order."""
        instructionName = parsedData['name']
        signals = parsedData['signals']
        columnCount = parsedData['columnCount']
        headerLines = parsedData['headerLines']
        
        # Use preserved header lines from original file
        lines = ["INS = '''"]
        lines.extend(headerLines)
        
        # INPUT SECTION
        # Get input signals from YAML InputPinMap in order (A14 to A0, already correct)
        inputSignals = self.inputPinMap
        
        # Group signals by type for proper separator placement, preserving order
        unknownSignals = [s for s in inputSignals if s.startswith('Ukwn')]
        flagSignals = [s for s in inputSignals if s == 'Flag']
        seqnSignals = [s for s in inputSignals if s.startswith('Seqn')]
        insrSignals = [s for s in inputSignals if s.startswith('InsR')]
        
        # Section 1: Unknown signals (Ukwn0, Ukwn1)
        for signalName in unknownSignals:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| I | {signalName:<5} | {values} |")
            else:
                values = ' | '.join(['0'] * columnCount)
                lines.append(f"| I | {signalName:<5} | {values} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 2: Flag signal
        for signalName in flagSignals:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| I | {signalName:<5} | {values} |")
            else:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| I | {signalName:<5} | {values} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 3: Sequence signals (Seqn0-3)
        for signalName in seqnSignals:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| I | {signalName:<5} | {values} |")
            else:
                # Generate sequence pattern
                seqBit = int(signalName[-1])
                values = []
                for col in range(columnCount):
                    values.append('1' if (col >> seqBit) & 1 else '0')
                valuesStr = ' | '.join(values)
                lines.append(f"| I | {signalName:<5} | {valuesStr} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 4: Instruction register signals (InsR0-7) - from YAML order
        for signalName in insrSignals:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| I | {signalName:<5} | {values} |")
            else:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| I | {signalName:<5} | {values} |")
        
        lines.append('|===|=======|' + '===|' * columnCount)
        
        # OUTPUT SECTION
        # Get virtual pin signals
        inputControlSignals, outputControlSignals = self._GetVirtualPinSignals()
        
        # Section 1: uCode0 (8 signals) - read from YAML OutputPinMap in IO0-IO7 order
        ucode0Pins = self.outputPinMap.get('uCode0', [])
        for signalName in ucode0Pins:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| O | {signalName:<5} | {values} |")
            elif 'RESRV' in signalName:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| O |  -    | {values} |")
            else:
                values = ' | '.join(['0'] * columnCount)
                lines.append(f"| O | {signalName:<5} | {values} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 2 & 3: InputControl (16 signals split into 8+8)
        for i, signalName in enumerate(inputControlSignals):
            if i == 8:
                lines.append('|---|-------|' + '---|' * columnCount)
            
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| O | {signalName:<5} | {values} |")
            elif 'RESRV' in signalName:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| O |  -    | {values} |")
            else:
                values = ' | '.join(['0'] * columnCount)
                lines.append(f"| O | {signalName:<5} | {values} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 4 & 5: OutputControl (16 signals split into 8+8)
        for i, signalName in enumerate(outputControlSignals):
            if i == 8:
                lines.append('|---|-------|' + '---|' * columnCount)
            
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| O | {signalName:<5} | {values} |")
            elif 'RESRV' in signalName:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| O |  -    | {values} |")
            else:
                values = ' | '.join(['0'] * columnCount)
                lines.append(f"| O | {signalName:<5} | {values} |")
        
        lines.append('|---|-------|' + '---|' * columnCount)
        
        # Section 6: uCode2 (8 signals) - read from YAML OutputPinMap in IO0-IO7 order
        ucode2Pins = self.outputPinMap.get('uCode2', [])
        for signalName in ucode2Pins:
            if signalName in signals:
                values = ' | '.join(signals[signalName]['values'])
                lines.append(f"| O | {signalName:<5} | {values} |")
            elif 'RESRV' in signalName:
                values = ' | '.join(['-'] * columnCount)
                lines.append(f"| O |  -    | {values} |")
            else:
                values = ' | '.join(['0'] * columnCount)
                lines.append(f"| O | {signalName:<5} | {values} |")
        
        # Add closing separator (same as opening separator from header)
        closingSeparator = [line for line in headerLines if '===' in line]
        if closingSeparator:
            lines.append(closingSeparator[0])
        lines.append("'''")
        
        return '\n'.join(lines)
    
    def NormalizeAllInstructions(self, outputDir: str = "", overwriteSource: bool = False):
        """Normalize all instruction files in YAML order.
        
        Args:
            outputDir: Output directory for normalized files. If None, uses out/normalized.
            overwriteSource: If True, overwrites source files in Instructions/ directory.
        """
        instructionDir = os.path.join(os.path.dirname(__file__), "Instructions")
        
        if overwriteSource:
            outputDir = instructionDir
            LOGGER.info("⚠️  OVERWRITE MODE: Will update source files in Instructions/")
        else:
            if outputDir is None:
                outputDir = os.path.join(os.path.dirname(__file__), "out", "normalized")
            
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
        
        # Get instruction order from YAML config
        insConfig = self.config.get("InsConfig", {})
        instructions = insConfig.get("Instructions", {})
        instructionOrder = list(instructions.keys())
        
        LOGGER.info(f"Normalizing {len(instructionOrder)} instruction files in YAML order...")
        
        for instructionName in instructionOrder:
            filePath = os.path.join(instructionDir, f"Ins{instructionName}.py")
            if not os.path.exists(filePath):
                LOGGER.warning(f"  ⚠ File not found: Ins{instructionName}.py")
                continue
            
            fileName = f"Ins{instructionName}.py"
            LOGGER.info(f"  Processing: {fileName}")
            
            try:
                parsedData = self.ParseInstructionFile(filePath)
                normalizedContent = self.GenerateNormalizedTable(parsedData)
                
                outputPath = os.path.join(outputDir, fileName)
                with open(outputPath, 'w') as f:
                    f.write(normalizedContent + '\n')
                
                LOGGER.info(f"    ✓ Normalized: {fileName}")
            except Exception as e:
                LOGGER.error(f"    ✗ Failed to normalize {fileName}: {e}")
        
        LOGGER.info(f"Normalization complete. Output in: {outputDir}")


def Main():
    """Main entry point for normalization."""
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # Check for --overwrite flag
    overwriteSource = "--overwrite" in sys.argv
    
    configPath = os.path.join(os.path.dirname(__file__), "MicroCodeConfig.yaml")
    normalizer = InstructionNormalizer(configPath)
    normalizer.NormalizeAllInstructions(overwriteSource=overwriteSource)


if __name__ == "__main__":
    Main()

# Made with Bob
