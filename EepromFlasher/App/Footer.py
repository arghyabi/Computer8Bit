import tkinter as tk
from tkinter import ttk

from Common import *

class Footer:
    def __init__(self, parent: tk.Tk, main):
        self.main = main
        self.footerSetup(parent)


    def footerSetup(self, parent):
        footer = tk.Frame(parent, bg = COLOR_LIGHT_GRAY, height = 25)
        footer.pack(side = tk.BOTTOM, fill = tk.X)

        label = tk.Label(
            footer,
            text = f"{APP_NAME} v{APP_VERSION}",
            bg   = COLOR_LIGHT_GRAY
        )
        label.pack(side = tk.LEFT, padx = 10)

        self.connectionStatusLabel = tk.Label(
            footer,
            text = "Disconnected",
            fg   = COLOR_RED,
            bg   = COLOR_LIGHT_GRAY
        )
        self.connectionStatusLabel.pack(side = tk.LEFT, padx = 10)

        self.chipSelectLabel = tk.Label(
            footer,
            text = "No Chip Selected",
            bg   = COLOR_LIGHT_GRAY
        )
        self.chipSelectLabel.pack(side = tk.LEFT, padx = 10)

        authorLabel = tk.Label(
            footer,
            text = "Created by Arghya Biswas",
            bg   = COLOR_LIGHT_GRAY
        )
        authorLabel.pack(side = tk.RIGHT, padx = 10)

        self.main.footerPortSelectCallback = self.onUsbPortSelect
        self.main.footerChipSelectCallback = self.onChipSelect


    def onUsbPortSelect(self, isUsbSelected: bool, selectedUsbPort: str):
        if isUsbSelected:
            self.connectionStatusLabel.config(
                text = f"Connected: {selectedUsbPort}",
                fg   = COLOR_GREEN
            )
        else:
            self.connectionStatusLabel.config(
                text = "Disconnected",
                fg   = COLOR_RED
            )

    def onChipSelect(self, isChipSelected: bool, selectedChip: str):
        if isChipSelected:
            self.chipSelectLabel.config(
                text = f"Chip: {selectedChip}"
            )
        else:
            self.chipSelectLabel.config(
                text = "No Chip Selected"
            )
