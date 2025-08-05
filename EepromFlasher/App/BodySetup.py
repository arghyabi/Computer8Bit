import tkinter as tk
from tkinter import ttk

from Common import *

from WriteTab import WriteTab
from ReadTab  import ReadTab


class BodySetup:
    def __init__(self, parent:tk.Tk, main):
        self.main = main
        self.notebookSetup(parent)


    def notebookSetup(self, parent):
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
            padx   = 0,
            pady   = 0,
            fill   = "both",
            expand = True
        )

        writeTab = WriteTab(self.writeTab, self.main)
        readTab  = ReadTab(self.readTab, self.main)

        self.main.writePortSelectCallback = writeTab.onUsbPortSelect
        self.main.writeChipSelectCallback = writeTab.onChipSelect

        self.main.readPortSelectCallback  = readTab.onUsbPortSelect
        self.main.readChipSelectCallback  = readTab.onChipSelect
