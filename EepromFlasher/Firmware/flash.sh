avrdude -C/usr/share/arduino/hardware/tools/avrdude.conf -v -patmega328p -carduino -P "/dev/ttyUSB0" -b115200 -D -Uflash:w:"build-EepromFlash/EepromFlashFirmware.hex.hex":i
