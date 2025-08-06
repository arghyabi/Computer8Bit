# Arduino Makefile

# Target board and port
BOARD_TAG = uno
OBJDIR  = build-EepromFlashFirmware

# Arduino installation path
ARDUINO_DIR = /usr/share/arduino
ARDUINO_TOOLS = $(ARDUINO_DIR)/hardware/tools/avr

# Compiler and flags
CC = $(ARDUINO_TOOLS)/bin/avr-g++
CFLAGS = -mmcu=atmega328p -DF_CPU=16000000L -Os -Wall
CFLAGS += -I$(ARDUINO_DIR)/hardware/arduino/avr/cores/arduino
CFLAGS += -I$(ARDUINO_DIR)/hardware/arduino/avr/variants/eightanaloginputs

# Source files
LOCAL_INO_SRCS =
LOCAL_CPP_SRCS = EepromFlashFirmware.cpp

# Output file
TARGET = EepromFlashFirmware.hex


include /usr/share/arduino/Arduino.mk
