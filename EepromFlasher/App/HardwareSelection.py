import tkinter as tk
from tkinter import ttk

from Common  import *
from Utility import *

class HardwareSelect:
    def __init__(self, parent:tk.Tk, main):
        self.main = main
        self.guiHeaderSetup(parent)


    def usbPortSelectCallbacks(self, isUsbSelected: bool, selectedUsbPort: str):
        if not (self.main.writePortSelectCallback and
                self.main.readPortSelectCallback and
                self.main.footerPortSelectCallback):
            self.main.consoleError("Port select callbacks not set in main")
            raise ValueError("Port select callbacks not set in main")

        self.main.writePortSelectCallback(isUsbSelected, selectedUsbPort)
        self.main.readPortSelectCallback(isUsbSelected, selectedUsbPort)
        self.main.footerPortSelectCallback(isUsbSelected, selectedUsbPort)


    def chipSelectCallbacks(self, isChipSelected: bool, selectedChip: str):
        if not (self.main.writeChipSelectCallback and
                self.main.readChipSelectCallback and
                self.main.footerChipSelectCallback):
            self.main.consoleError("Chip select callback not set in main")
            raise ValueError("Chip select callback not set in main")

        self.main.writeChipSelectCallback(isChipSelected, selectedChip)
        self.main.readChipSelectCallback(isChipSelected, selectedChip)
        self.main.footerChipSelectCallback(isChipSelected, selectedChip)


    def refreshPorts(self, combobox:ttk.Combobox):
        combobox['values'] = getSerialPorts()
        if combobox['values']:
            combobox.current(0)


    def selectUsbPort(self, itSelf:ttk.Combobox):
        # the 0th index is just 'Select'; work only if a non zero value selected
        if(itSelf.current() != 0):
            isUsbSelected = True
            selectedUsbPort = itSelf.get()
            self.main.consoleInfo(f"Selected Port: {selectedUsbPort}")
        else:
            isUsbSelected = False
            selectedUsbPort = ""
            self.main.consoleWarning("No Port Selected")

        self.usbPortSelectCallbacks(isUsbSelected, selectedUsbPort)


    def selectChipType(self, itSelf:ttk.Combobox):
        # the 0th index is just 'Select'; work only if a non zero value selected
        if(itSelf.current() != 0):
            isChipSelected = True
            selectedChip = itSelf.get()
            self.main.consoleInfo(f"Selected Chip: {selectedChip}")
        else:
            isChipSelected = False
            selectedChip = ""
            self.main.consoleWarning("No Chip Selected")

        self.chipSelectCallbacks(isChipSelected, selectedChip)


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
        self.portSelectCombobox["values"] = getSerialPorts()
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
