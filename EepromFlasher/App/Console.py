import tkinter as tk

from Common import *

class Console:
    def __init__(self, parent: tk.Tk):
        self.consoleSetup(parent)


    def consoleSetup(self, parent):
        frame = tk.Frame(parent)
        frame.pack(
            padx    = 0,
            pady    = 0,
            fill    = "x",
            expand  = False
        )

        self.console = tk.Text(
            frame,
            height  = 10,
            bg      = COLOR_BLACK,
            fg      = COLOR_WHITE,
            wrap    = tk.WORD,
            state   = tk.DISABLED
        )
        self.console.pack(
            side    = tk.LEFT,
            fill    = "x",
            expand  = True
        )

        scrollbar = tk.Scrollbar(frame, command = self.console.yview)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        self.console.config(yscrollcommand = scrollbar.set)

        self.console.tag_configure("info",    foreground = COLOR_WHITE)
        self.console.tag_configure("warning", foreground = COLOR_YELLOW)
        self.console.tag_configure("error",   foreground = COLOR_RED)
        self.console.tag_configure("success", foreground = COLOR_LIGHT_GREEN)


    def info(self, message, end ="\n", append = False):
        if append:
            self.log(f"{message}", "info", end)
        else:
            self.log(f"[INFO] {message}", "info", end)


    def warning(self, message, end ="\n", append = False):
        if append:
            self.log(f"{message}", "warning", end)
        else:
            self.log(f"[WARNING] {message}", "warning", end)


    def error(self, message, end ="\n", append = False):
        if append:
            self.log(f"{message}", "error", end)
        else:
            self.log(f"[ERROR] {message}", "error", end)


    def success(self, message, end ="\n", append = False):
        if append:
            self.log(f"{message}", "success", end)
        else:
            self.log(f"[SUCCESS] {message}", "success", end)


    def log(self, message, level, end ="\n"):
        self.console.config(state = tk.NORMAL)
        self.console.insert(tk.END, message + end, level)
        self.console.config(state = tk.DISABLED)
        self.console.see(tk.END)
