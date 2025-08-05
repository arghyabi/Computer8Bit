import tkinter as tk

from Common import *
from HardwareSelection import HardwareSelect
from BodySetup         import BodySetup
from Console           import Console
from Footer            import Footer

class GuiMain:
    def __init__(self):
        self.writePortSelectCallback   = None
        self.writeChipSelectCallback   = None

        self.readPortSelectCallback    = None
        self.readChipSelectCallback    = None

        self.footerPortSelectCallback  = None
        self.footerChipSelectCallback  = None

        self.consoleInfo               = None
        self.consoleWarning            = None
        self.consoleError              = None

        self.readTabGuiDisableHook     = None
        self.readTabGuiEnableHook      = None
        
        self.writeTabGuiDisableHook    = None
        self.writeTabGuiEnableHook     = None

        self.setupMainGui()


    def setupMainGui(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry(APP_SIZE)
        self.root.resizable(False, False)

        hardwareSelect       = HardwareSelect(self.root, self)
        bodySetup            = BodySetup(self.root, self)
        console              = Console(self.root)
        footer               = Footer(self.root, self)

        self.consoleInfo     = console.info
        self.consoleWarning  = console.warning
        self.consoleError    = console.error
        self.consoleSuccess  = console.success

        self.consoleInfo(f"{APP_NAME} {APP_VERSION}")
        self.consoleInfo(APP_DESCRIPTION)

        self.root.mainloop()
