import tkinter as tk
from tkinter import filedialog, ttk
import os
import time

from Common  import *
from Utility import *

class WriteTab:
    def __init__(self, parent:ttk.Frame, main):
        self.parent            = parent
        self.main              = main
        self.isUsbPortSelected = False
        self.isChipSelected    = False
        self.selectedUsbPort   = ""
        self.selectedChip      = ""
        self.finalChipType     = None
        self.finalChipSize     = 0
        self.writeAbort        = False
        self.writeTimeStart    = 0

        self.main.writeTabGuiDisableHook = self.disableWriteTabGui
        self.main.writeTabGuiEnableHook  = self.enableWriteTabGui
        self.writeTabSetup(self.parent)


    def onUsbPortSelect(self, isUsbSelected:bool, selectedUsbPort:str):
        self.isUsbPortSelected = isUsbSelected
        self.selectedUsbPort   = selectedUsbPort

        if self.isUsbPortSelected and self.isChipSelected:
            self.writeFileChooseBtn.config(state=tk.NORMAL)
            self.verifyAfterWriteCheck.config(state=tk.NORMAL)
        else:
            self.writeFileChooseBtn.config(state=tk.DISABLED)
            self.verifyAfterWriteCheck.config(state=tk.DISABLED)


    def onChipSelect(self, isChipSelected:bool, selectedChip:str):
        self.isChipSelected = isChipSelected
        self.selectedChip   = selectedChip

        if self.isUsbPortSelected and self.isChipSelected:
            self.writeFileChooseBtn.config(state=tk.NORMAL)
            self.verifyAfterWriteCheck.config(state=tk.NORMAL)
        else:
            self.writeFileChooseBtn.config(state=tk.DISABLED)
            self.verifyAfterWriteCheck.config(state=tk.DISABLED)

        if self.selectedChip == CHIP_AT28C16:
            self.labelWriteFileSelect.config(
                text = "Select a 2KB .bin file to flash to AT28C16"
            )
            self.finalChipType = CHIP_AT28C16
            self.finalChipSize = SIZE_AT28C16
        elif self.selectedChip == CHIP_AT28C256:
            self.labelWriteFileSelect.config(
                text = "Select a 32KB .bin file to flash to AT28C256"
            )
            self.finalChipType = CHIP_AT28C256
            self.finalChipSize = SIZE_AT28C256
        else:
            self.labelWriteFileSelect.config(
                text = ""
            )
            self.finalChipType = None
            self.finalChipSize = 0


    def chooseWriteFile(self):
        filePath = filedialog.askopenfilename(
            filetypes = [("Binary files", "*.bin")]
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
            self.main.consoleInfo(f"Selected binary: {self.finalWriteFile}")


    def setWriteAbort(self):
        self.writeAbort = True


    def writeTabSetup(self, parent):
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
            state   = tk.DISABLED,
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
            text    = "Start Writing",
            state   = tk.DISABLED,
            width   = 20
        )
        self.btnWriteStart.pack(
            pady = 10
        )

        # === Write Abort Button ===
        self.btnWriteAbort = tk.Button(
            fileWriteFrame,
            text    = "Abort Writing",
            state   = tk.DISABLED,
            width   = 20
        )
        self.btnWriteAbort.pack(
            pady = 10
        )

        # checkbox for verify each byte after writing
        self.verifyAfterWriteVar = tk.BooleanVar(value = True)
        self.verifyAfterWriteCheck = tk.Checkbutton(
            fileWriteFrame,
            text     = "Verify after write",
            variable = self.verifyAfterWriteVar,
            state    = tk.DISABLED,
            # by default the checkbox is checked
            onvalue  = True,
            offvalue = False,
            width    = 20
        )
        self.verifyAfterWriteCheck.pack(
            pady = 5
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


    def disableWriteTabGui(self, disableAbort:bool = False):
        self.btnWriteStart.config(state = tk.DISABLED)
        self.btnWriteAbort.config(state = tk.DISABLED if disableAbort else tk.NORMAL)
        self.writeFileChooseBtn.config(state = tk.DISABLED)
        self.verifyAfterWriteCheck.config(state = tk.DISABLED)


    def enableWriteTabGui(self):
        self.btnWriteStart.config(state = tk.NORMAL)
        self.btnWriteAbort.config(state = tk.DISABLED)
        self.writeFileChooseBtn.config(state = tk.NORMAL)
        self.verifyAfterWriteCheck.config(state = tk.NORMAL)


    def updateGuiForStartWriting(self):
        self.disableWriteTabGui()
        self.main.readTabGuiDisableHook(disableAbort = True)


    def updateGuiForAbortWriting(self):
        self.enableWriteTabGui()
        self.main.readTabGuiEnableHook()
        self.writeAbort = False


    def sendBinToChip(self, progressVal:tk.DoubleVar, progressLabel:tk.Label, progressBar:ttk.Progressbar):
        self.writeAbort = False
        self.updateGuiForStartWriting()

        # Read the bin file and prepare for writing
        self.main.consoleInfo("Reading bin file for writing...", end = "")
        data, error = readBinFile(self.finalWriteFile)
        if error or data is None:
            self.labelWriteStatus.config(
                text = f"[ERROR] Failed to read bin file: {error}"
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"Failed to read bin file: {error}")
            self.updateGuiForAbortWriting()
            return
        self.main.consoleSuccess(f" Success.", append = True)
        self.parent.update()

        # Check if the data length matches the expected chip size
        self.main.consoleInfo("Validating the bin file...", end = "")
        if data and (len(data) != self.finalChipSize):
            self.labelWriteStatus.config(
                text = f"[ERROR] Expected {self.finalChipSize} bytes, got {len(data)} bytes."
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"Expected {self.finalChipSize} bytes, got {len(data)} bytes.")
            self.updateGuiForAbortWriting()
            return
        self.main.consoleSuccess(f" Success.", append = True)
        self.parent.update()

        # Initialize Serial Port
        self.main.consoleInfo(f"Initializing serial port: {self.selectedUsbPort}...", end = "")
        self.parent.update()
        serial, error = serialPortInitialization(self.selectedUsbPort)
        time.sleep(2)  # Allow Arduino reset
        if error or not serial:
            self.labelWriteStatus.config(
                text = f"[ERROR] Serial port initialization failed: {error}"
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"Serial port initialization failed: {error}")
            self.updateGuiForAbortWriting()
            return
        self.main.consoleSuccess(f" Success.", append = True)
        self.parent.update()

        # Flush any stale bytes after reset
        try:
            serial.reset_input_buffer()
            serial.reset_output_buffer()
        except Exception:
            pass

        # verify after write
        self.main.consoleInfo("Verify after write ", end = "")
        if self.verifyAfterWriteVar.get():
            self.main.consoleSuccess("Enabled", append = True)
        else:
            self.main.consoleWarning("Disabled", append = True)

        self.writeTimeStart = time.time()
        try:
            # Start writing data to chip using block transfers
            self.main.consoleInfo("Starting data write to chip (block mode)...")
            self.parent.update()
            total = self.finalChipSize
            addr = 0
            while addr < total:
                length = min(DEFAULT_CHUNK_SIZE, total - addr)
                addrHigh = (addr >> 8) & 0xFF
                addrLow  = addr & 0xFF
                payload = bytes([OPERATION_WRITE_BLOCK, addrHigh, addrLow, length]) + bytes(data[addr:addr+length])
                # Ensure output buffer clear before sending block
                try:
                    serial.reset_input_buffer()
                except Exception as e:
                    self.main.consoleWarning(f"Exception while resetting input buffer: {e}")

                serial.write(payload)
                ack = serial.read()  # expect ACK_WRITE_OK
                if ack != ACK_WRITE_OK:
                    self.labelWriteStatus.config(text = f"[ERROR] Write block failed at 0x{addr:04X}")
                    self.main.consoleError(" Failed.", append = True)
                    self.main.consoleError(f"Write block failed at 0x{addr:04X}; ack: {ack}")
                    serial.close()
                    self.updateGuiForAbortWriting()
                    return

                if self.verifyAfterWriteVar.get():
                    serial.write(bytes([OPERATION_READ_BLOCK, addrHigh, addrLow, length]))
                    readBlock = serial.read(length)
                    ack2 = serial.read()
                    if (not readBlock) or (len(readBlock) != length) or (ack2 != ACK_READ_OK):
                        self.labelWriteStatus.config(text = f"[ERROR] Verify read block failed at 0x{addr:04X}")
                        self.main.consoleError(" Failed.", append = True)
                        self.main.consoleError(f"Verify read block failed at 0x{addr:04X}; got {len(readBlock) if readBlock else 0} bytes, ack={ack2}")
                        serial.close()
                        self.updateGuiForAbortWriting()
                        return
                    if readBlock != bytes(data[addr:addr+length]):
                        self.labelWriteStatus.config(text = f"[ERROR] Verification mismatch at 0x{addr:04X}")
                        self.main.consoleError(" Failed.", append = True)
                        self.main.consoleError(f"Verification mismatch at 0x{addr:04X}")
                        serial.close()
                        self.updateGuiForAbortWriting()
                        return

                addr += length
                percent = addr * 100 / total
                progressVal.set(percent)
                progressLabel.config(text = f"{percent:0.2f}%")
                progressBar.update()

                self.main.consoleInfo(".", end = "", append = True)

                if self.writeAbort:
                    self.labelWriteStatus.config(text = "[ERROR] Write Aborted manually.")
                    self.main.consoleWarning(" Aborted.", append = True)
                    self.main.consoleWarning("Write Aborted manually.")
                    serial.close()
                    self.updateGuiForAbortWriting()
                    return

            # Final done command to finalize the write operation
            serial.write(bytes([OPERATION_INS_DONE, 0x00]))  # Send dummy byte 0x00
            readByte = serial.read()
            if readByte != ACK_INS_DONE_OK:
                self.labelWriteStatus.config(
                    text = "[ERROR] Failed to finalize write operation."
                )
                self.main.consoleError(" Failed.", append = True)
                self.main.consoleError("Failed to finalize write operation.")
                serial.close()
                self.updateGuiForAbortWriting()
                return

            self.main.consoleSuccess(" Success.", append = True)
            self.main.consoleInfo("Data write complete.")
            self.labelWriteStatus.config(
                text = "[INFO] Data write complete."
            )
            self.parent.update()
            serial.close()
            self.updateGuiForAbortWriting()
        except Exception as e:
            self.labelWriteStatus.config(
                text = f"[ERROR] Exception during writing: {e}"
            )
            self.main.consoleError(" Failed.", append = True)
            self.main.consoleError(f"Exception during writing: {e}")
            self.updateGuiForAbortWriting()
        finally:
            if serial and serial.is_open:
                serial.close()
            self.enableWriteTabGui()
            self.main.readTabGuiEnableHook()
            self.parent.update()
            currentTime = time.time()
            elapsedTime = currentTime - self.writeTimeStart
            self.main.consoleInfo(f"Total write time: {elapsedTime:.2f} seconds")
