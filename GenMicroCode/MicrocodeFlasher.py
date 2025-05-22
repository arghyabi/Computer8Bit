import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import filedialog, ttk
import time
import os

# Constants
EEPROM_SIZE = 2048  # for AT28C16
selected_file = None
selected_port = None

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def refresh_ports():
    port_menu['values'] = list_serial_ports()
    if port_menu['values']:
        port_menu.current(0)

def choose_file():
    global selected_file
    file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if file_path:
        selected_file = file_path
        file_label.config(text=os.path.basename(file_path))
        start_button.config(state=tk.NORMAL)
        status_label.config(text="File selected. Ready to flash.")

def send_bin_to_eeprom():
    global selected_file, selected_port
    if not selected_file:
        status_label.config(text="[ERROR] No file selected.")
        return
    if not selected_port.get():
        status_label.config(text="[ERROR] No serial port selected.")
        return

    try:
        with open(selected_file, "rb") as f:
            data = f.read()
            if len(data) != EEPROM_SIZE:
                status_label.config(text=f"[ERROR] Expected 2048 bytes, got {len(data)} bytes.")
                return
    except Exception as e:
        status_label.config(text=f"[ERROR] File read error: {e}")
        return

    try:
        with serial.Serial(selected_port.get(), 9600, timeout=1) as ser:
            time.sleep(2)  # Allow Arduino reset
            status_label.config(text="[INFO] Flashing in progress...")
            root.update()

            for addr in range(EEPROM_SIZE):
                addr_high = (addr >> 8) & 0xFF
                addr_low = addr & 0xFF
                byte = data[addr]

                ser.write(bytes([addr_high, addr_low, byte]))
                ack = ser.read()
                if ack != b'\xAA':
                    status_label.config(text=f"[ERROR] No ACK at 0x{addr:04X}")
                    return

                percent = (addr + 1) * 100 // EEPROM_SIZE
                progress_var.set(percent)
                percent_label.config(text=f"{percent}%")
                progress_bar.update()

            status_label.config(text="[SUCCESS] EEPROM programming complete.")
    except serial.SerialException as e:
        status_label.config(text=f"[ERROR] Serial error: {e}")

# GUI setup
root = tk.Tk()
root.title("AT28C16 EEPROM Uploader")
root.geometry("400x270")
root.resizable(False, False)

# === Header/Nav Bar ===
header = tk.Frame(root, bg="#ececec", height=40)
header.pack(fill=tk.X)

tk.Label(header, text="Select Serial Port:", bg="#ececec").pack(side=tk.LEFT, padx=10)

selected_port = tk.StringVar()
port_menu = ttk.Combobox(header, textvariable=selected_port, width=20, state="readonly")
port_menu.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(header, text="↻", command=refresh_ports)
refresh_button.pack(side=tk.LEFT)

# === File Selection ===
tk.Label(root, text="Select a 2KB .bin file to flash to AT28C16", pady=10).pack()

file_frame = tk.Frame(root)
file_frame.pack(pady=5)

choose_button = tk.Button(file_frame, text="Choose File", command=choose_file, width=15)
choose_button.pack(side=tk.LEFT, padx=5)

file_label = tk.Label(file_frame, text="No file selected", width=25, anchor="w")
file_label.pack(side=tk.LEFT)

# === Start Flashing Button ===
start_button = tk.Button(root, text="Start Flashing", command=send_bin_to_eeprom, state=tk.DISABLED, width=20)
start_button.pack(pady=10)

# === Progress Bar ===
progress_frame = tk.Frame(root)
progress_frame.pack(pady=5)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(progress_frame, length=250, variable=progress_var, maximum=100)
progress_bar.pack(side=tk.LEFT)

percent_label = tk.Label(progress_frame, text="0%", width=5)
percent_label.pack(side=tk.LEFT, padx=5)

# === Status Label ===
status_label = tk.Label(root, text="Waiting for file selection...")
status_label.pack(pady=10)

# Load serial ports on startup
refresh_ports()

root.mainloop()
