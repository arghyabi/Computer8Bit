#ifndef EEPROM_FLASH_FIRMWARE_H
#define EEPROM_FLASH_FIRMWARE_H

#include <Arduino.h>

// Enumerations
typedef enum {
    OPERATION_READ,
    OPERATION_WRITE,
    OPERATION_UNKNOWN
} opMode_t;

typedef enum {
    CMD_MODE_SET  = 0xAA,
    CMD_DATA_SEND = 0x55
} cmd_t;

typedef enum {
    ACK_OK = 0xAA,
    ACK_NO = 0x55
} ack_t;

// Pin definitions
// Address shift register (74LS595)
extern const int addDataPin;
extern const int addClockPin;
extern const int addLatchPin;

// EEPROM control pins (active low)
extern const int writeEnbPin;
extern const int outputEnbPin;
extern const int chipEnbPin;

// Input/Output pins for EEPROM (8 bits)
extern const int inOut0;
extern const int inOut1;
extern const int inOut2;
extern const int inOut3;
extern const int inOut4;
extern const int inOut5;
extern const int inOut6;
extern const int inOut7;

// LED pins for status indication
extern const int greenLedPin;
extern const int redLedPin;
extern const int blueLedPin;

extern const int inOutPins[8];

// Global variables
extern uint16_t led_counter;
extern bool led_state;
extern opMode_t operationMode;

// Function declarations
void    setAddress(uint16_t address, bool reverse = true);
uint8_t readEEPROM(uint16_t address);
void    writeEEPROM(uint16_t address, uint8_t data);
void    initializeInputPort();
void    initializeOutputPort();

#endif // EEPROM_FLASH_FIRMWARE_H
