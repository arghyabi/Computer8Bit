import os
import sys
import yaml

from StyleSheet import StyleSheet
from widgets import LedWidget, SignalWidget, BitCheckBox

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)


# ============================================================
# Main Window
# ============================================================

class VerifyWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Microcode Verify Tool")
        self.resize(1800, 950)

        self.yamlConfig = {}
        self.microcodeData = [[], [], []]

        self.inputSignalMap = {}
        self.outputSignalMap = {}

        self.signalWidgets = {}

        self.allSignals = []

        self.SetupUi()

    # ========================================================

    def SetupUi(self):

        self.setStyleSheet(StyleSheet.mainWindowStyle)

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(6)
        mainLayout.setContentsMargins(6, 6, 6, 6)

        # ====================================================
        # TOP CONTROL AREA
        # ====================================================

        topLayout = QHBoxLayout()
        topLayout.setSpacing(6)

        # ----------------------------------------------------
        # Instruction Group
        # ----------------------------------------------------

        instructionGroup = QGroupBox("Instruction")

        instructionLayout = QVBoxLayout()

        self.instructionCombo = QComboBox()
        self.instructionCombo.currentIndexChanged.connect(self.UpdateInstructionBits)

        instructionLayout.addWidget(self.instructionCombo)

        bitLayout = QHBoxLayout()

        self.instructionBits = []

        for bit in range(7, -1, -1):

            checkBox = BitCheckBox(str(bit))
            checkBox.stateChanged.connect(self.UpdateAddress)

            self.instructionBits.append(checkBox)
            bitLayout.addWidget(checkBox)

        instructionLayout.addLayout(bitLayout)

        instructionGroup.setLayout(instructionLayout)

        # ----------------------------------------------------
        # Flag Group
        # ----------------------------------------------------

        flagGroup = QGroupBox("Flag")

        flagLayout = QVBoxLayout()

        self.flagCheckBox = BitCheckBox("Flag Bit")
        self.flagCheckBox.stateChanged.connect(self.UpdateAddress)

        flagLayout.addWidget(self.flagCheckBox)
        flagLayout.addStretch()

        flagGroup.setLayout(flagLayout)

        # ----------------------------------------------------
        # Unknown Group
        # ----------------------------------------------------

        unknownGroup = QGroupBox("Unknown")

        unknownLayout = QVBoxLayout()

        self.unknownBit0 = BitCheckBox("U0")
        self.unknownBit1 = BitCheckBox("U1")

        self.unknownBit0.stateChanged.connect(self.UpdateAddress)
        self.unknownBit1.stateChanged.connect(self.UpdateAddress)

        unknownLayout.addWidget(self.unknownBit0)
        unknownLayout.addWidget(self.unknownBit1)
        unknownLayout.addStretch()

        unknownGroup.setLayout(unknownLayout)

        # ----------------------------------------------------
        # Sequence Group
        # ----------------------------------------------------

        sequenceGroup = QGroupBox("Sequence")

        sequenceLayout = QVBoxLayout()

        self.sequenceSpin = QSpinBox()
        self.sequenceSpin.setRange(0, 15)

        self.sequenceSpin.valueChanged.connect(self.UpdateAddress)

        sequenceLayout.addWidget(self.sequenceSpin)
        sequenceLayout.addStretch()

        sequenceGroup.setLayout(sequenceLayout)

        # ----------------------------------------------------
        # File Group
        # ----------------------------------------------------

        fileGroup = QGroupBox("Files")

        fileLayout = QVBoxLayout()

        yamlButton = QPushButton("Load YAML")
        yamlButton.clicked.connect(self.LoadYaml)

        ucode0Button = QPushButton("Load uCode0")
        ucode0Button.clicked.connect(lambda: self.LoadMicrocode(0))

        ucode1Button = QPushButton("Load uCode1")
        ucode1Button.clicked.connect(lambda: self.LoadMicrocode(1))

        ucode2Button = QPushButton("Load uCode2")
        ucode2Button.clicked.connect(lambda: self.LoadMicrocode(2))

        self.addressLabel = QLabel("Address: 0")

        fileLayout.addWidget(yamlButton)
        fileLayout.addWidget(ucode0Button)
        fileLayout.addWidget(ucode1Button)
        fileLayout.addWidget(ucode2Button)
        fileLayout.addStretch()
        fileLayout.addWidget(self.addressLabel)

        fileGroup.setLayout(fileLayout)

        # ----------------------------------------------------

        topLayout.addWidget(instructionGroup, 4)
        topLayout.addWidget(flagGroup, 2)
        topLayout.addWidget(unknownGroup, 2)
        topLayout.addWidget(sequenceGroup, 2)
        topLayout.addWidget(fileGroup, 2)

        # ====================================================
        # MICROCODE VIEW
        # ====================================================

        middleLayout = QHBoxLayout()

        self.microcodeViews = []

        for index in range(3):

            group = QGroupBox(f"uCode{index}")

            layout = QVBoxLayout()

            view = QListWidget()

            self.microcodeViews.append(view)

            layout.addWidget(view)

            group.setLayout(layout)

            middleLayout.addWidget(group)

        # ====================================================
        # SIGNAL STATUS
        # ====================================================

        signalGroup = QGroupBox("Signal Status")

        signalLayout = QGridLayout()
        signalLayout.setSpacing(2)

        signalGroup.setLayout(signalLayout)

        self.signalGridLayout = signalLayout

        # ====================================================

        mainLayout.addLayout(topLayout, 2)
        mainLayout.addLayout(middleLayout, 6)
        mainLayout.addWidget(signalGroup, 2)

        self.setLayout(mainLayout)

    # ========================================================

    def LoadYaml(self):

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Load YAML",
            "",
            "YAML Files (*.yaml *.yml)"
        )

        if not filePath:
            return

        with open(filePath, "r") as file:
            self.yamlConfig = yaml.safe_load(file)

        self.BuildInstructionList()
        self.BuildSignalMap()
        self.BuildSignalWidgets()

    # ========================================================

    def BuildInstructionList(self):

        self.instructionCombo.clear()

        instructions = self.yamlConfig["InsConfig"]["Instructions"]

        # New format: dictionary with instruction details
        for instructionName in instructions.keys():
            self.instructionCombo.addItem(instructionName)

    # ========================================================

    def BuildSignalMap(self):

        self.inputSignalMap.clear()
        self.outputSignalMap.clear()

        # Use new VirtualPinConfig structure
        inputConfig = self.yamlConfig["VirtualPinConfig"]["InputControl"]
        outputConfig = self.yamlConfig["VirtualPinConfig"]["OutputControl"]

        for signal, value in inputConfig.items():
            self.inputSignalMap[value] = signal

        for signal, value in outputConfig.items():
            self.outputSignalMap[value] = signal

        self.allSignals = []

        for signal in inputConfig.keys():
            if "RESRV" not in signal:
                self.allSignals.append(signal)

        for signal in outputConfig.keys():
            if "RESRV" not in signal:
                self.allSignals.append(signal)

        # Use new MicrocodeChipsPinMap -> OutputPinMap structure
        outputPinMap = self.yamlConfig["MicrocodeChipsPinMap"]["OutputPinMap"]
        
        for signal in outputPinMap["uCode0"].values():
            if "RESRV" not in signal:
                self.allSignals.append(signal)

        for signal in outputPinMap["uCode2"].values():
            if "RESRV" not in signal:
                self.allSignals.append(signal)

    # ========================================================

    def BuildSignalWidgets(self):

        while self.signalGridLayout.count():

            item = self.signalGridLayout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.signalWidgets.clear()

        row = 0
        column = 0

        for signal in self.allSignals:

            widget = SignalWidget(signal)

            self.signalWidgets[signal] = widget

            self.signalGridLayout.addWidget(widget, row, column)

            column += 1

            if column >= 10:
                column = 0
                row += 1

    # ========================================================

    def LoadMicrocode(self, index):

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Load BIN",
            "",
            "BIN Files (*.bin)"
        )

        if not filePath:
            return

        with open(filePath, "rb") as file:
            data = file.read()

        self.microcodeData[index] = list(data)

        self.UpdateMicrocodeView(index)

        self.UpdateAddress()

    # ========================================================

    def UpdateMicrocodeView(self, index):

        view = self.microcodeViews[index]

        view.clear()

        data = self.microcodeData[index]

        for address, value in enumerate(data):

            itemText = (
                f"{address:04X}    "
                f"{value:02X}    "
                f"{value:08b}"
            )

            item = QListWidgetItem(itemText)

            view.addItem(item)

    # ========================================================

    def UpdateInstructionBits(self):

        instructionName = self.instructionCombo.currentText()
        
        if not instructionName:
            return
        
        # Get the opcode value for this instruction from the YAML config
        instructions = self.yamlConfig.get("InsConfig", {}).get("Instructions", {})
        
        # New format: get opcode from instruction data
        insData = instructions.get(instructionName, {})
        if isinstance(insData, dict):
            opcode = insData.get('opcode', 0)
            # Handle string format like "0bxxxx_0001" or "0b0000_0000"
            if isinstance(opcode, str) and opcode.startswith('0b'):
                # Remove '0b' prefix and underscores
                binary_str = opcode[2:].replace('_', '')
                # Replace 'x' with '0' to get base opcode
                binary_str = binary_str.replace('x', '0')
                value = int(binary_str, 2)
            else:
                value = opcode if isinstance(opcode, int) else 0
        else:
            value = 0

        for bit in range(8):

            state = (value >> bit) & 1

            self.instructionBits[7 - bit].setChecked(bool(state))

        self.UpdateAddress()

    # ========================================================

    def GetInstructionValue(self):

        value = 0

        for index, checkBox in enumerate(self.instructionBits):

            if checkBox.isChecked():
                value |= (1 << index)

        return value

    # ========================================================

    def CalculateAddress(self):

        instruction = self.GetInstructionValue()

        flag = 1 if self.flagCheckBox.isChecked() else 0

        unknown = 0

        if self.unknownBit0.isChecked():
            unknown |= 1

        if self.unknownBit1.isChecked():
            unknown |= 2

        sequence = self.sequenceSpin.value()
        
        address = (
            (unknown << 13)
            |
            (flag << 12)
            |
            (sequence << 8)
            |
            instruction
        )

        return address

    # ========================================================

    def UpdateAddress(self):

        address = self.CalculateAddress()

        self.addressLabel.setText(
            f"Address: {address} (0x{address:04X})"
        )

        self.HighlightAddress(address)
        self.DecodeSignals(address)

    # ========================================================

    def HighlightAddress(self, address):

        for view in self.microcodeViews:

            if address < view.count():

                view.setCurrentRow(address)

    # ========================================================

    def DecodeSignals(self, address):

        activeSignals = set()

        # Get OutputPinMap from new structure
        outputPinMap = self.yamlConfig["MicrocodeChipsPinMap"]["OutputPinMap"]

        # ====================================================
        # uCode0
        # ====================================================

        if len(self.microcodeData[0]) > address:

            value = self.microcodeData[0][address]

            # Get signal names from OutputPinMap in order IO0-IO7
            ucode0Pins = outputPinMap["uCode0"]
            ucode0Signals = [ucode0Pins[f"IO{i}"] for i in range(8)]

            for bit in range(8):

                if value & (1 << bit):

                    signal = ucode0Signals[bit]

                    if "RESRV" not in signal:
                        activeSignals.add(signal)

        # ====================================================
        # uCode1
        # ====================================================

        if len(self.microcodeData[1]) > address:

            value = self.microcodeData[1][address]

            # Correct bit layout: upper nibble = OUTPUT, lower nibble = INPUT
            outputCode = (value >> 4) & 0x0F   # Upper nibble (bits 4-7)
            inputCode = value & 0x0F          # Lower nibble (bits 0-3)

            if inputCode in self.inputSignalMap:

                signal = self.inputSignalMap[inputCode]

                if "RESRV" not in signal:
                    activeSignals.add(signal)

            if outputCode in self.outputSignalMap:

                signal = self.outputSignalMap[outputCode]

                if "RESRV" not in signal:
                    activeSignals.add(signal)

        # ====================================================
        # uCode2
        # ====================================================

        if len(self.microcodeData[2]) > address:

            value = self.microcodeData[2][address]

            # Get signal names from OutputPinMap in order IO0-IO7
            ucode2Pins = outputPinMap["uCode2"]
            ucode2Signals = [ucode2Pins[f"IO{i}"] for i in range(8)]

            for bit in range(8):

                if value & (1 << bit):

                    signal = ucode2Signals[bit]

                    if "RESRV" not in signal:
                        activeSignals.add(signal)

        # ====================================================
        # Update LEDs
        # ====================================================

        for signal, widget in self.signalWidgets.items():

            widget.SetState(signal in activeSignals)
