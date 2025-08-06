APP_VERSION      = "1.2.0.1002"
FIRMWARE_VERSION = "1.0.0.1000"

CHIP_AT28C16     = "AT28C16"
CHIP_AT28C256    = "AT28C256"
SIZE_AT28C16     = 2048
SIZE_AT28C256    = 32768

SERIAL_BAUD_RATE = 115200

# Application Constants
APP_NAME         = "EEPROM Flasher"
APP_DESCRIPTION  = "A tool for flashing EEPROM chips."
APP_SIZE         = "800x600"

# Colors
COLOR_WHITE       = "#FFFFFF"
COLOR_BLACK       = "#000000"
COLOR_RED         = "#FF0000"
COLOR_GREEN       = "#0A630A"
COLOR_LIGHT_GREEN = "#00FF00"
COLOR_YELLOW      = "#FFFF00"
COLOR_LIGHT_GRAY  = "#ECECEC"



# +-----------+------------------+--------------+-------------+----------+
# | Operation | Byte 1 (OpType)  | Byte 2       | Byte 3      | Byte 4   |
# +-----------+------------------+--------------+-------------+----------+
# | WRITE     | Command for Write| Address High | Address Low | Data     |
# | READ      | Command for Read | Address High | Address Low | Not Used |
# | RESET     | Command for Reset| Not Used     | Not Used    | Not Used |
# +-----------+------------------+--------------+-------------+----------+
OPERATION_WRITE       = 0x10
OPERATION_READ        = 0x20
OPERATION_INS_FW      = 0x30
OPERATION_INS_DONE    = 0x40
OPERATION_UNKNOWN     = 0xFF

ACK_WRITE_OK          = bytes([0x1A])
ACK_READ_OK           = bytes([0x2A])
ACK_INS_FW_OK         = bytes([0x3A])
ACK_INS_DONE_OK       = bytes([0x4A])

ACK_WRITE_NO          = bytes([0x15])
ACK_READ_NO           = bytes([0x25])
ACK_INS_FW_NO         = bytes([0x35])
ACK_INS_DONE_NO       = bytes([0x45])

ACK_OTHER_NO          = bytes([0xF5])
