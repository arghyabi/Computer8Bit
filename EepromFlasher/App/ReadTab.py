import tkinter as tk
from tkinter import filedialog, ttk
import os
import time

from Common  import *
from Utility import *

class ReadTab:
    def __init__(self, parent:ttk.Frame, main):
        self.parent            = parent
        self.main              = main
        self.isUsbPortSelected = False
        self.isChipSelected    = False
        self.selectedUsbPort   = ""
        self.selectedChip      = ""
        self.finalChipType     = None
        self.finalChipSize     = 0
        self.readAbort         = False

        self.main.readTabGuiDisableHook  = self.disableReadTabGui
        self.main.readTabGuiEnableHook   = self.enableReadTabGui
        self.readTabSetup(self.parent)


    def onUsbPortSelect(self, isUsbSelected:bool, selectedUsbPort:str):
        self.isUsbPortSelected = isUsbSelected
        self.selectedUsbPort   = selectedUsbPort

        if self.isUsbPortSelected and self.isChipSelected:
            self.readFileChooseBtn.config(state = tk.NORMAL)
        else:
            self.readFileChooseBtn.config(state = tk.DISABLED)


    def onChipSelect(self, isChipSelected:bool, selectedChip:str):
        self.isChipSelected = isChipSelected
        self.selectedChip   = selectedChip

        if self.isUsbPortSelected and self.isChipSelected:
            self.readFileChooseBtn.config(state = tk.NORMAL)
        else:
            self.readFileChooseBtn.config(state = tk.DISABLED)

        if self.selectedChip == CHIP_AT28C16:
            self.finalChipType = CHIP_AT28C16
            self.finalChipSize = SIZE_AT28C16
            self.labelReadFileSelect.config(
                text = "Specify a 2KB .bin file to save data read from AT28C16"
            )
        elif self.selectedChip == CHIP_AT28C256:
            self.finalChipType = CHIP_AT28C256
            self.finalChipSize = SIZE_AT28C256
            self.labelReadFileSelect.config(
                text = "Specify a 32KB .bin file to save data read from AT28C256"
            )
        else:
            self.finalChipType = None
            self.finalChipSize = 0
            self.labelReadFileSelect.config(
                text = ""
            )


    def chooseReadFilePath(self):
        filePath = filedialog.asksaveasfilename(
            filetypes = [("Binary files", "*.bin")]
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
                text = "File selected. Ready to Read."
            )
            self.main.consoleInfo(f"Selected binary: {self.finalReadFile}")


    def setReadAbort(self):
        self.readAbort = True


    def readTabSetup(self, parent):
        # === Read File Selection Frame ===
        fileSelectFrame = tk.Frame(parent)
        fileSelectFrame.pack(pady = 5)

        self.labelReadFileSelect = tk.Label(
            fileSelectFrame,
            text = "Select a path to save the binary.",
            pady = 10
        )
        self.labelReadFileSelect.pack(
            side = tk.TOP
        )

        self.readFileChooseBtn = tk.Button(
            fileSelectFrame,
            text    = "Choose File",
            command = self.chooseReadFilePath,
            state   = tk.DISABLED,
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


    def disableReadTabGui(self, disableAbort:bool = False):
        self.btnReadStart.config(state = tk.DISABLED)
        self.btnReadAbort.config(state = tk.DISABLED if disableAbort else tk.NORMAL)
        self.readFileChooseBtn.config(state = tk.DISABLED)


    def enableReadTabGui(self):
        self.btnReadStart.config(state = tk.NORMAL)
        self.btnReadAbort.config(state = tk.DISABLED)
        self.readFileChooseBtn.config(state = tk.NORMAL)


    def updateGuiForStartReading(self):
        self.disableReadTabGui()
        self.main.writeTabGuiDisableHook(disableAbort = True)


    def updateGuiForAbortReading(self):
        self.enableReadTabGui()
        self.main.writeTabGuiEnableHook()
        self.readAbort = False


    def readBinFromChip(self, progressVal:tk.DoubleVar, progressLabel:tk.Label, progressBar:ttk.Progressbar):
        self.readAbort = False
        self.updateGuiForStartReading()

        data = [0]*self.finalChipSize

        # Initialize Serial Port
        self.main.consoleInfo(f"Initializing serial port: {self.selectedUsbPort}...", end = "")
        self.parent.update()
        serial, error = serialPortInitialization(self.selectedUsbPort)
        time.sleep(2)  # Allow Arduino reset
        if error or not serial:
            self.labelReadStatus.config(
                text = f"[ERROR] Serial port initialization failed: {error}"
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"Serial port initialization failed: {error}")
            self.updateGuiForAbortReading()
            return
        self.main.consoleSuccess(f" Success.", append = True)
        self.parent.update()

        try:
            # Send Read commands to chip
            self.labelReadStatus.config(text="[INFO] Reading in progress...")
            self.main.consoleInfo("Sending Read command to chip...", end = "")
            self.parent.update()
            serial.write(bytes([0xAA, 0x00]))  # Instruction for Read
            ack = serial.read()
            if ack == b'\x55':
                self.labelReadStatus.config(text="[ERROR] Instruction failed!!")
                self.main.consoleError(" Failed.", append = True)
                serial.close()
                self.updateGuiForAbortReading()
                return
            elif ack == b'\xAA':
                self.main.consoleSuccess(f" Success.", append = True)
            else:
                self.labelReadStatus.config(
                    text = "[ERROR] Unexpected response from chip!"
                )
                self.main.consoleError(" Failed.", append = True)
                self.main.consoleError(f"Unexpected response from chip! Received: {ack}")
                serial.close()
                self.updateGuiForAbortReading()
                return
            self.parent.update()

            # Start Reading data from chip
            self.main.consoleInfo("Starting data read from chip...")
            self.parent.update()
            for addr in range(self.finalChipSize):
                addrHigh = (addr >> 8) & 0xFF
                addrLow = addr & 0xFF

                serial.write(bytes([addrHigh, addrLow]))
                dataByte = serial.read()
                ack = serial.read()

                data[addr] = dataByte[0]
                if ack != b'\xAA':
                    self.labelReadStatus.config(
                        text = f"[ERROR] No ACK at address 0x{addr:04X}"
                    )
                    self.main.consoleError(" Failed.", append = True)
                    self.main.consoleError(f"No ACK at address 0x{addr:04X}")
                    serial.close()
                    self.updateGuiForAbortReading()
                    return

                percent = (addr + 1) * 100 / self.finalChipSize
                progressVal.set(percent)
                progressLabel.config(text = f"{percent:0.2f}%")
                progressBar.update()

                self.main.consoleInfo(".", end = "", append = True)

                if self.readAbort:
                    self.labelReadStatus.config(
                        text = "[ERROR] Read Aborted manually."
                    )
                    self.main.consoleWarning(" Aborted.", append = True)
                    self.main.consoleWarning("Read Aborted manually.")
                    serial.close()
                    self.updateGuiForAbortReading()
                    return

            self.labelReadStatus.config(
                text = "[SUCCESS] EEPROM reading complete."
            )
            self.main.consoleSuccess(" Success.", append = True)
            self.main.consoleInfo("Data read complete.")
            self.main.consoleInfo("Saving data to file...", end = "")
            self.parent.update()
            serial.close()

            # Save data to file
            with open(self.finalReadFile, "wb") as f:
                f.write(bytes(data))
            self.main.consoleSuccess(" Success.", append = True)
            self.labelReadStatus.config(
                text = f"[SUCCESS] Data saved to {self.finalReadFile}"
            )
            self.main.consoleInfo(f"Data saved to {self.finalReadFile}")
            self.updateGuiForAbortReading()
        except Exception as e:
            self.labelReadStatus.config(
                text = f"[ERROR] Serial error: {e}"
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"{e}")
        finally:
            if serial and serial.is_open:
                serial.close()
            self.enableReadTabGui()
            self.main.writeTabGuiEnableHook()
            self.parent.update()
