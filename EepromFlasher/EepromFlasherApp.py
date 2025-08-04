import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import filedialog, ttk
import time
import os


CHIP_AT28C16  = "AT28C16"
CHIP_AT28C256 = "AT28C256"
SIZE_AT28C16  = 2048
SIZE_AT28C256 = 32768

class MicrocodeFlasher:
    def __init__(self):
        self.isChipSeleted  = False
        self.isPortSeleted  = False

        self.finalChipType  = None
        self.finalUsbPort   = None
        self.finalWriteFile = None
        self.finalReadFile  = None
        self.finalChipSize  = 0

        self.writeAbort     = False
        self.readAbort      = False

        self.guiSetupMain()


    def selectChipType(self, itSelf:ttk.Combobox):
        # the 0th index is just 'Select'; work only if a non zero value selected
        if(itSelf.current() != 0):
            self.isChipSeleted = True

            if self.isPortSeleted:
                self.writeFileChooseBtn.config(
                    state = tk.NORMAL
                )
                self.readFileChooseBtn.config(
                    state = tk.NORMAL
                )

            selectedChip = itSelf.get()
            print("Selected Chip:", selectedChip)
            if selectedChip == CHIP_AT28C16:
                self.labelWriteFileSelect.config(
                    text = "Select a 2KB .bin file to flash to AT28C16"
                )
                self.finalChipType = CHIP_AT28C16
                self.finalChipSize = SIZE_AT28C16
            elif selectedChip == CHIP_AT28C256:
                self.labelWriteFileSelect.config(
                    text = "Select a 32KB .bin file to flash to AT28C256"
                )
                self.finalChipType = CHIP_AT28C256
                self.finalChipSize = SIZE_AT28C256
            else:
                pass
        else:
            self.isChipSeleted = False
            self.writeFileChooseBtn.config(
                state = tk.DISABLED
            )
            self.readFileChooseBtn.config(
                state = tk.DISABLED
            )
            self.labelWriteFileSelect.config(
                text = ""
            )
            self.finalChipType = None
            self.finalChipSize = 0


    def selectUsbPort(self, itSelf:ttk.Combobox):
        # the 0th index is just 'Select'; work only if a non zero value selected
        if(itSelf.current() != 0):
            self.isPortSeleted = True
            self.finalUsbPort = itSelf.get()
            print("Selected Port:", self.finalUsbPort)

            if self.isChipSeleted:
                self.writeFileChooseBtn.config(
                    state = tk.NORMAL
                )

                self.readFileChooseBtn.config(
                    state = tk.NORMAL
                )
        else:
            self.isPortSeleted = False
            self.writeFileChooseBtn.config(
                state = tk.DISABLED
            )

            self.readFileChooseBtn.config(
                state = tk.DISABLED
            )
            self.finalUsbPort = None


    def getSerialPorts(self):
        ports = serial.tools.list_ports.comports()
        portList = ["Select"]
        serialPorts = [port.device for port in ports]
        serialPorts.reverse()
        portList.extend(serialPorts)
        return portList


    def refreshPorts(self, combobox:ttk.Combobox):
        combobox['values'] = self.getSerialPorts()
        if combobox['values']:
            combobox.current(0)


    def chooseWriteFile(self):
        filePath = filedialog.askopenfilename(
            filetypes=[("Binary files", "*.bin")]
        )

        if filePath:
            self.finalWriteFile = filePath
            self.labelWriteSelectedFile.config(
                text = os.path.basename(filePath)
            )
            self.btnWriteStart.config(
                state = tk.NORMAL
            )
            self.labelWriteStatus.config(
                text = "File selected. Ready to flash."
            )
            print("Selected binary:", self.finalWriteFile)


    def setWriteAbort(self):
        self.writeAbort = True


    def chooseReadFilePath(self):
        filePath = filedialog.asksaveasfilename(
            filetypes=[("Binary files", "*.bin")]
        )

        if filePath:
            self.finalReadFile = filePath
            self.labelReadSelectedFile.config(
                text = os.path.basename(filePath)
            )
            self.btnReadStart.config(
                state = tk.NORMAL
            )
            self.labelReadStatus.config(
                text = "File selected. Ready to flash."
            )
            print("Selected binary:", self.finalReadFile)


    def setReadAbort(self):
        self.readAbort = True


    def guiSetupMain(self):
        self.root = tk.Tk()
        self.root.title("AT28C16/AT28C256 EEPROM Uploader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.guiHeaderSetup(self.root)
        self.guiBodySetup(self.root)

        self.root.mainloop()


    def guiHeaderSetup(self, parent:tk.Tk):
        header = tk.Frame(parent, bg = "#ececec", height = 40)
        header.pack(fill = tk.X)

        labelSerialPort = tk.Label(header,
                 text = "Select Chip:",
                 bg   = "#ececec"
        )
        labelSerialPort.pack(
            side = tk.LEFT,
            padx = 10
        )

        self.selectedChip = tk.StringVar()
        self.chipSelectCombobox = ttk.Combobox(
            header,
            textvariable = self.selectedChip,
            width        = 15,
            state        = "readonly"
        )

        self.chipSelectCombobox.pack(
            side = tk.LEFT,
            padx = 5
        )
        self.chipSelectCombobox["values"] = ["Select", CHIP_AT28C16, CHIP_AT28C256]
        self.chipSelectCombobox.current(0)
        self.chipSelectCombobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.selectChipType(self.chipSelectCombobox)
        )

        labelSerialPort = tk.Label(header,
                 text = "Select Serial Port:",
                 bg   = "#ececec"
        )
        labelSerialPort.pack(
            side = tk.LEFT,
            padx = 10
        )

        self.selectedPort = tk.StringVar()
        self.portSelectCombobox = ttk.Combobox(
            header,
            textvariable = self.selectedPort,
            width        = 15,
            state        = "readonly"
        )

        self.portSelectCombobox.pack(
            side = tk.LEFT,
            padx = 5
        )
        self.portSelectCombobox["values"] = self.getSerialPorts()
        self.portSelectCombobox.current(0)
        self.portSelectCombobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.selectUsbPort(self.portSelectCombobox)
        )

        self.portRefreshButton = tk.Button(
            header,
            text    = "↻",
            command = lambda: self.refreshPorts(self.portSelectCombobox)
        )
        self.portRefreshButton.pack(
            side = tk.LEFT
            )


    def guiBodySetup(self, parent:tk.Tk):
        self.notebook = ttk.Notebook(parent)
        self.writeTab = ttk.Frame(self.notebook)
        self.readTab  = ttk.Frame(self.notebook)

        self.notebook.add(
            self.writeTab,
            text = "Write to Chip"
        )
        self.notebook.add(
            self.readTab,
            text = "Read from Chip"
        )

        self.notebook.pack(
            padx   = 5,
            pady   = 5,
            fill   = "both",
            expand = True
        )

        self.guiWriteTabSetup(self.writeTab)
        self.guiReadTabSetup(self.readTab)


    def guiWriteTabSetup(self, parent:ttk.Frame):

        fileSelectFrame = tk.Frame(parent)
        fileSelectFrame.pack(pady = 5)

        self.labelWriteFileSelect = tk.Label(
            fileSelectFrame,
            text = "",
            pady = 10
        )
        self.labelWriteFileSelect.pack(
            side = tk.TOP
        )

        self.writeFileChooseBtn = tk.Button(
            fileSelectFrame,
            text    = "Choose File",
            command = self.chooseWriteFile,
            state = tk.DISABLED,
            width   = 15
            )
        self.writeFileChooseBtn.pack(
            side = tk.LEFT,
            padx = 5
        )

        self.labelWriteSelectedFile = tk.Label(
            fileSelectFrame,
            text   = "No file selected",
            width  = 25,
            anchor = "w"
        )
        self.labelWriteSelectedFile.pack(
            side = tk.LEFT
        )

        # === File Write Frame ===
        fileWriteFrame = tk.Frame(parent)
        fileWriteFrame.pack(pady = 5)

        # === Write Start Button ===
        self.btnWriteStart = tk.Button(
            fileWriteFrame,
            text    = "Start Writting",
            state   = tk.DISABLED,
            width   = 20
        )
        self.btnWriteStart.pack(
            pady = 10
        )

        # === Write Abort Button ===
        self.btnWriteAbort = tk.Button(
            fileWriteFrame,
            text    = "Abort Writting",
            state   = tk.DISABLED,
            width   = 20
        )
        self.btnWriteAbort.pack(
            pady = 10
        )

        # === Write Progress Bar ===
        writeProgressFrame = tk.Frame(fileWriteFrame)
        writeProgressFrame.pack(
            pady = 5
        )

        writeProgressValue = tk.DoubleVar()
        writeProgressbar = ttk.Progressbar(
            writeProgressFrame,
            length   = 250,
            variable = writeProgressValue,
            maximum  = 100
        )
        writeProgressbar.pack(
            side = tk.LEFT
        )

        writeProgressLabel = tk.Label(
            writeProgressFrame,
            text  = "0%",
            width = 7
        )
        writeProgressLabel.pack(
            side = tk.LEFT,
            padx = 5
        )

        # === Write Status Label ===
        self.labelWriteStatus = tk.Label(
            fileWriteFrame,
            text = "Waiting for file selection..."
        )
        self.labelWriteStatus.pack(
            pady = 10
        )

        self.btnWriteStart.config(
            command = lambda : self.sendBinToChip(
                writeProgressValue,
                writeProgressLabel,
                writeProgressbar
            )
        )

        self.btnWriteAbort.config(
            command = lambda: self.setWriteAbort()
        )


    def guiReadTabSetup(self, parent:ttk.Frame):
        # === Read File Selection Frame ===
        fileSelectFrame = tk.Frame(parent)
        fileSelectFrame.pack(pady = 5)

        labelFileSelect = tk.Label(
            fileSelectFrame,
            text = "Select a path to save the binary.",
            pady = 10
        )
        labelFileSelect.pack(
            side = tk.TOP
        )

        self.readFileChooseBtn = tk.Button(
            fileSelectFrame,
            text    = "Choose File",
            command = self.chooseReadFilePath,
            state = tk.DISABLED,
            width   = 15
            )
        self.readFileChooseBtn.pack(
            side = tk.LEFT,
            padx = 5
        )

        self.labelReadSelectedFile = tk.Label(
            fileSelectFrame,
            text   = "No path defined",
            width  = 25,
            anchor = "w"
        )
        self.labelReadSelectedFile.pack(
            side = tk.LEFT
        )

        # === File Read Frame ===
        fileReadFrame = tk.Frame(parent)
        fileReadFrame.pack(pady = 5)

        # === Read Start Button ===
        self.btnReadStart = tk.Button(
            fileReadFrame,
            text  = "Start Reading",
            state = tk.DISABLED,
            width = 20
        )
        self.btnReadStart.pack(
            pady = 10
        )

        # === Read Abort Button ===
        self.btnReadAbort = tk.Button(
            fileReadFrame,
            text    = "Abort Reading",
            state   = tk.DISABLED,
            width   = 20
        )
        self.btnReadAbort.pack(
            pady = 10
        )


        # === Read Progress Bar ===
        readProgressFrame = tk.Frame(fileReadFrame)
        readProgressFrame.pack(
            pady = 5
        )

        readProgressValue = tk.DoubleVar()
        readProgressbar = ttk.Progressbar(
            readProgressFrame,
            length   = 250,
            variable = readProgressValue,
            maximum  = 100
        )
        readProgressbar.pack(
            side = tk.LEFT
        )

        readProgressLabel = tk.Label(
            readProgressFrame,
            text  = "0%",
            width = 7
        )
        readProgressLabel.pack(
            side = tk.LEFT,
            padx = 5
        )

        # === Read Status Label ===
        self.labelReadStatus = tk.Label(
            fileReadFrame,
            text = "Waiting for path selection..."
        )
        self.labelReadStatus.pack(
            pady = 10
        )

        self.btnReadStart.config(
            command = lambda : self.readBinFromChip(
                readProgressValue,
                readProgressLabel,
                readProgressbar
            )
        )

        self.btnReadAbort.config(
            command = lambda: self.setReadAbort()
        )


    def updateGuiForStartWriting(self):
        # Enable Write Abort Btn
        self.btnWriteAbort.config(
            state = tk.NORMAL
        )

        # Disable Read Tab
        self.notebook.tab(
            self.readTab,
            state = tk.DISABLED
        )

        # Disable chip select combobox
        self.chipSelectCombobox.config(
            state = tk.DISABLED
        )

        # Disable port select combobox
        self.portSelectCombobox.config(
            state = tk.DISABLED
        )

        # Disable port refresh Btn
        self.portRefreshButton.config(
            state = tk.DISABLED
        )

        # Disable File Select Btn
        self.writeFileChooseBtn.config(
            state = tk.DISABLED
        )

        # Disable Write Start Btn
        self.btnWriteStart.config(
            state = tk.DISABLED
        )


    def updateGuiForAbortWriting(self):
        # Enable Write Abort Btn
        self.btnWriteAbort.config(
            state = tk.DISABLED
        )

        # Disable Read Tab
        self.notebook.tab(
            self.readTab,
            state = tk.NORMAL
        )

        # Disable chip select combobox
        self.chipSelectCombobox.config(
            state = "readonly"
        )

        # Disable port select combobox
        self.portSelectCombobox.config(
            state = "readonly"
        )

        # Disable port refresh Btn
        self.portRefreshButton.config(
            state = tk.NORMAL
        )

        # Disable File Select Btn
        self.writeFileChooseBtn.config(
            state = tk.NORMAL
        )

        # Disable Write Start Btn
        self.btnWriteStart.config(
            state = tk.NORMAL
        )


    def sendBinToChip(self, progressVal:tk.DoubleVar, progressLabel:tk.Label, progressBar:ttk.Progressbar):
        self.writeAbort = False
        self.updateGuiForStartWriting()

        try:
            if self.finalWriteFile:
                with open(self.finalWriteFile, "rb") as f:
                    data = f.read()
                    if len(data) != self.finalChipSize:
                        self.labelWriteStatus.config(
                            text = f"[ERROR] Expected {self.finalChipSize} bytes, got {len(data)} bytes."
                        )
                        self.updateGuiForAbortWriting()
                        return
            else:
                raise Exception("Write file path is not valid!!")
        except Exception as e:
            self.labelWriteStatus.config(
                text = f"[ERROR] File read error: {e}"
            )
            self.updateGuiForAbortWriting()
            return

        try:
            with serial.Serial(self.finalUsbPort, 115200, timeout = 1) as ser:
                time.sleep(2)  # Allow Arduino reset
                self.labelWriteStatus.config(text="[INFO] Flashing in progress...")
                self.root.update()

                # Send instruction commands
                print("Sending write instruction commands!!")
                ser.write(bytes([0xAA, 0x01])) # Instruction for Write
                ack = ser.read()
                if ack == b'\x55':
                    print("ACK_NO")
                    self.labelWriteStatus.config(text="[ERROR] Instruction failed!!")
                    self.updateGuiForAbortWriting()
                    return
                if ack == b'\xAA':
                    print("ACK_OK")

                # Send Actual data
                print("Sending data!!")
                for addr in range(self.finalChipSize):
                    addrHigh = (addr >> 8) & 0xFF
                    addrLow = addr & 0xFF
                    byte = data[addr]

                    ser.write(bytes([addrHigh, addrLow, byte]))
                    ack = ser.read()
                    # print(f"Write: 0x{addr:04X}: 0x{byte:02X}")
                    if ack != b'\xAA':
                        self.labelWriteStatus.config(
                            text = f"[ERROR] No ACK at 0x{addr:04X}"
                        )
                        self.updateGuiForAbortWriting()
                        return

                    percent = (addr + 1) * 100 / self.finalChipSize
                    progressVal.set(percent)
                    progressLabel.config(text = f"{percent:0.2f}%")
                    progressBar.update()

                    if self.writeAbort:
                        self.labelWriteStatus.config(
                            text = "[ERROR] Write Aborted manually."
                        )
                        self.updateGuiForAbortWriting()
                        return

                self.labelWriteStatus.config(
                    text = "[SUCCESS] EEPROM programming complete."
                )
                print("Done!")
        except serial.SerialException as e:
            self.labelWriteStatus.config(
                text = f"[ERROR] Serial error: {e}"
            )

        self.updateGuiForAbortWriting()


    def updateGuiForStartReading(self):
        # Enable Read Abort Btn
        self.btnReadAbort.config(
            state = tk.NORMAL
        )

        # Disable Read Tab
        self.notebook.tab(
            self.writeTab,
            state = tk.DISABLED
        )

        # Disable chip select combobox
        self.chipSelectCombobox.config(
            state = tk.DISABLED
        )

        # Disable port select combobox
        self.portSelectCombobox.config(
            state = tk.DISABLED
        )

        # Disable port refresh Btn
        self.portRefreshButton.config(
            state = tk.DISABLED
        )

        # Disable File Select Btn
        self.readFileChooseBtn.config(
            state = tk.DISABLED
        )

        # Disable Read Start Btn
        self.btnReadStart.config(
            state = tk.DISABLED
        )


    def updateGuiForAbortReading(self):
        # Enable Read Abort Btn
        self.btnReadAbort.config(
            state = tk.DISABLED
        )

        # Disable Read Tab
        self.notebook.tab(
            self.writeTab,
            state = tk.NORMAL
        )

        # Disable chip select combobox
        self.chipSelectCombobox.config(
            state = "readonly"
        )

        # Disable port select combobox
        self.portSelectCombobox.config(
            state = "readonly"
        )

        # Disable port refresh Btn
        self.portRefreshButton.config(
            state = tk.NORMAL
        )

        # Disable File Select Btn
        self.readFileChooseBtn.config(
            state = tk.NORMAL
        )

        # Disable Read Start Btn
        self.btnReadStart.config(
            state = tk.NORMAL
        )


    def readBinFromChip(self, progressVal:tk.DoubleVar, progressLabel:tk.Label, progressBar:ttk.Progressbar):
        self.readAbort = False
        self.updateGuiForStartReading()

        data = [0]*self.finalChipSize

        try:
            with serial.Serial(self.finalUsbPort, 115200, timeout = 1) as ser:
                time.sleep(2)  # Allow Arduino reset
                self.labelReadStatus.config(text="[INFO] Reading in progress...")
                self.root.update()

                # Send instruction commands
                print("Sending read instruction commands!!")
                ser.write(bytes([0xAA, 0x00])) # Instruction for Read
                ack = ser.read()
                if ack == b'\x55':
                    print("ACK_NO")
                    self.labelWriteStatus.config(text="[ERROR] Instruction failed!!")
                    self.updateGuiForAbortWriting()
                    return
                if ack == b'\xAA':
                    print("ACK_OK")

                print("Reading data!!")
                for addr in range(self.finalChipSize):
                    addrHigh = (addr >> 8) & 0xFF
                    addrLow = addr & 0xFF

                    ser.write(bytes([addrHigh, addrLow]))
                    dataByte = ser.read()
                    ack = ser.read()

                    data[addr] = dataByte[0]
                    # print(f"Read: 0x{addr:04X}: 0x{dataByte[0]:02X}")
                    if ack != b'\xAA':
                        self.labelReadStatus.config(
                            text = f"[ERROR] No ACK at 0x{addr:04X}"
                        )
                        self.updateGuiForAbortReading()
                        return

                    percent = (addr + 1) * 100 / self.finalChipSize
                    progressVal.set(percent)
                    progressLabel.config(text = f"{percent:0.2f}%")
                    progressBar.update()

                    if self.readAbort:
                        self.labelReadStatus.config(
                            text = "[ERROR] Read Aborted manually."
                        )
                        self.updateGuiForAbortReading()
                        return

                self.labelReadStatus.config(
                    text = "[SUCCESS] EEPROM reading complete."
                )
                print("Done!")
        except serial.SerialException as e:
            self.labelReadStatus.config(
                text = f"[ERROR] Serial error: {e}"
            )
            print(e)

        self.updateGuiForAbortReading()

        try:
            if self.finalReadFile:
                with open(self.finalReadFile, "wb") as f:
                    f.write(bytes(data))
            else:
                raise Exception("Read file path is not valid!!")
        except Exception as e:
            self.labelReadStatus.config(
                text = f"[ERROR] File write error: {e}"
            )
            return


if __name__ == "__main__":
    microcodeFlasherApp = MicrocodeFlasher()
