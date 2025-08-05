import serial
import serial.tools.list_ports

from Common import *

def getSerialPorts():
    ports = serial.tools.list_ports.comports()
    portList = ["Select"]
    serialPorts = [port.device for port in ports]
    serialPorts.reverse()
    portList.extend(serialPorts)
    return portList


def serialPortInitialization(serialPort):
    error     = None
    serialObj = None
    try:
        serialObj = serial.Serial(serialPort, SERIAL_BAUD_RATE, timeout = 1)
    except Exception as e:
        error = e

    return serialObj, error


def readBinFile(filePath):
    data  = None
    error = None
    try:
        with open(filePath, "rb") as file:
            data = file.read()
    except Exception as e:
        error = e

    return data, error


def writeBinFile(filePath, data):
    error = None
    try:
        with open(filePath, "wb") as file:
            file.write(data)
    except Exception as e:
        error = e

    return error
