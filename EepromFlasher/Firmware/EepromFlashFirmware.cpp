#include "EepromFlashFirmware.h"
#include "communication.h"

// Pin definitions
// Address shift register (74LS595)
const int addDataPin   = 2;
const int addClockPin  = 3;
const int addLatchPin  = 4;

// EEPROM control pins (active low)
const int writeEnbPin  = A0;
const int outputEnbPin = A1;
const int chipEnbPin   = A2;

// Input/Output pins for EEPROM (8 bits)
const int inOut0       = 5;
const int inOut1       = 6;
const int inOut2       = 7;
const int inOut3       = 8;
const int inOut4       = 9;
const int inOut5       = 10;
const int inOut6       = 11;
const int inOut7       = 12;

// LED pins for status indication
const int greenLedPin  = A3;
const int redLedPin    = A4;
const int blueLedPin   = A5;

// Buzzer pin
const int buzzerPin    = 13;

const int inOutPins[8] = {inOut0, inOut1, inOut2, inOut3, inOut4, inOut5, inOut6, inOut7};

// Global variables
uint16_t led_counter   = 0;
bool red_led_state     = false;
bool green_led_state   = false;
bool blue_led_state    = false;
opMode_t operationMode = OPERATION_UNKNOWN;

uint8_t writeBuffer[DEFAULT_CHUNK_SIZE] = {0};
uint8_t payloadBytes[PAYLOAD_SIZE_MAX]  = {0};

#define SERIAL_BAUD_RATE     250000


void setup() {
    // Address shift register pins
    pinMode(addDataPin,  OUTPUT);
    pinMode(addClockPin, OUTPUT);
    pinMode(addLatchPin, OUTPUT);

    // EEPROM control signals
    pinMode(writeEnbPin,  OUTPUT);
    pinMode(outputEnbPin, OUTPUT);
    pinMode(chipEnbPin,   OUTPUT);

    pinMode(redLedPin,   OUTPUT);
    pinMode(greenLedPin, OUTPUT);
    pinMode(blueLedPin,  OUTPUT);

    digitalWrite(redLedPin,   LOW);
    digitalWrite(greenLedPin, LOW);
    digitalWrite(blueLedPin,  LOW);

    digitalWrite(writeEnbPin,  HIGH);  // Disable write
    digitalWrite(outputEnbPin, LOW);   // Disable read
    digitalWrite(chipEnbPin,   LOW);   // Enable chip

    //buzzerPin
    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW); // Ensure buzzer is off

    Serial.begin(SERIAL_BAUD_RATE);
}

returnCode_t readPayloadBytes(payloadSize_t payloadSize) {
    unsigned long startTime = millis();
    const unsigned long timeout = 100; // 100ms timeout for reading payload

    for (int i = 0; i < payloadSize; i++) {
        while (Serial.available() == 0) {
            if (millis() - startTime > timeout) {
                return RET_PAYLOAD_TOO_SHORT; // Timeout
            }
        }
        payloadBytes[i] = Serial.read();
    }

    return RET_OK;
}

// Read exactly N bytes with timeout; returns RET_OK or RET_PAYLOAD_TOO_SHORT
returnCode_t readExact(uint8_t* buf, size_t len, unsigned long timeoutMs = 200) {
    unsigned long start = millis();
    size_t got = 0;
    while (got < len) {
        if (Serial.available()) {
            buf[got++] = (uint8_t)Serial.read();
            start = millis();
        } else if (millis() - start > timeoutMs) {
            return RET_PAYLOAD_TOO_SHORT;
        }
    }
    return RET_OK;
}

void loop() {
    uint8_t  data    = 0;
    uint16_t address = 0;
    uint8_t  dataLen = 0;

    // Check for incoming serial data
    if (Serial.available() > 0) {
        switch (operationMode) {
            // OPERATION_UNKNOWN: Default case, wait for operation type
            case OPERATION_UNKNOWN:
                operationMode = (opMode_t)Serial.read();
                break;

            // OPERATION_WRITE: Handle write operation
            case OPERATION_WRITE:
                initializeOutputPort();
                if (readPayloadBytes(PAYLOAD_SIZE_OP_WRITE) == RET_OK) {
                    address = (payloadBytes[IDX_H_ADDRESS] << 8) | payloadBytes[IDX_L_ADDRESS]; // High byte + Low byte
                    data    = payloadBytes[IDX_DATA]; // Data byte
                    writeEEPROM(address, data);
                    Serial.write(ACK_WRITE_OK);
                    digitalWrite(blueLedPin, blue_led_state ? HIGH : LOW);
                    blue_led_state = !blue_led_state;
                } else {
                    Serial.write(ACK_WRITE_NO); // Payload too short
                }
                operationMode = OPERATION_UNKNOWN;
                break;

            // OPERATION_READ: Handle read operation
            case OPERATION_READ:
                initializeInputPort();
                if (readPayloadBytes(PAYLOAD_SIZE_OP_READ) == RET_OK) {
                    address = (payloadBytes[IDX_H_ADDRESS] << 8) | payloadBytes[IDX_L_ADDRESS]; // High byte + Low byte
                    data    = readEEPROM(address);
                    Serial.write(data);
                    Serial.write(ACK_READ_OK);
                    digitalWrite(greenLedPin, green_led_state ? HIGH : LOW);
                    green_led_state = !green_led_state;
                } else {
                    Serial.write(0xFF); // Send 0xFF if no data read
                    Serial.write(ACK_READ_NO); // Payload too short
                }
                operationMode = OPERATION_UNKNOWN;
                break;

            // OPERATION_WRITE_BLOCK: Handle block write
            case OPERATION_WRITE_BLOCK:
                initializeOutputPort();
                digitalWrite(outputEnbPin, HIGH);
                if (readPayloadBytes(PAYLOAD_SIZE_OP_BLOCK_HDR) == RET_OK) {
                    address = (payloadBytes[IDX_H_ADDRESS] << 8) | payloadBytes[IDX_L_ADDRESS];
                    dataLen = payloadBytes[IDX_LEN];
                    if (dataLen == 0 || dataLen > DEFAULT_CHUNK_SIZE) {
                        Serial.write(ACK_WRITE_NO);
                        operationMode = OPERATION_UNKNOWN;
                        break;
                    }
                    if (readExact(writeBuffer, dataLen) != RET_OK) {
                        Serial.write(ACK_WRITE_NO);
                        operationMode = OPERATION_UNKNOWN;
                        break;
                    }
                    // Reliable per-byte path for small page size (AT28C16) to avoid boundary issues
                    // Per-byte writes using internal polling; optional end verification
                    initializeOutputPort();
                    for (uint8_t index = 0; index < dataLen; index++) {
                        writeEEPROM(address + index, writeBuffer[index]);
                    }
                    digitalWrite(blueLedPin, blue_led_state ? HIGH : LOW);
                    blue_led_state = !blue_led_state;
                    Serial.write(ACK_WRITE_OK);
                    operationMode = OPERATION_UNKNOWN;
                    break;
                } else {
                    Serial.write(ACK_WRITE_NO);
                }
                operationMode = OPERATION_UNKNOWN;
                break;

            // OPERATION_READ_BLOCK: Handle block read
            case OPERATION_READ_BLOCK:
                initializeInputPort();
                if (readPayloadBytes(PAYLOAD_SIZE_OP_BLOCK_HDR) == RET_OK) {
                    address = (payloadBytes[IDX_H_ADDRESS] << 8) | payloadBytes[IDX_L_ADDRESS];
                    dataLen = payloadBytes[IDX_LEN];
                    if (dataLen == 0) {
                        Serial.write(ACK_READ_NO);
                        operationMode = OPERATION_UNKNOWN;
                        break;
                    }
                    for (uint8_t index = 0; index < dataLen; index++) {
                        Serial.write(readEEPROM(address + index));
                    }
                    digitalWrite(greenLedPin, green_led_state ? HIGH : LOW);
                    green_led_state = !green_led_state;
                    Serial.write(ACK_READ_OK);
                } else {
                    Serial.write(ACK_READ_NO);
                }
                operationMode = OPERATION_UNKNOWN;
                break;

            // OPERATION_INS_DONE: Handle instruction done
            case OPERATION_INS_DONE:
                if (readPayloadBytes(PAYLOAD_SIZE_OP_INS_DONE) == RET_OK) {
                    // Dummy byte received and ignored (payloadBytes[0])
                    Serial.write(ACK_INS_DONE_OK);
                    digitalWrite(redLedPin, LOW);
                    digitalWrite(greenLedPin, LOW);
                    digitalWrite(blueLedPin, LOW);
                    // Play buzzer for 1000ms
                    digitalWrite(buzzerPin, HIGH);
                    delay(1000);
                    digitalWrite(buzzerPin, LOW);
                } else {
                    Serial.write(ACK_INS_DONE_NO); // Payload too short
                }
                operationMode = OPERATION_UNKNOWN;
                break;

            // Default case: Unknown operation
            default:
                operationMode = OPERATION_UNKNOWN;
                Serial.write(ACK_OTHER_NO); // Default to other no
                break;
        }
    }
}

void initializeInputPort() {
    // Set all inOut pins to INPUT
    for (int i = 0; i < 8; i++) {
        digitalWrite(inOutPins[i], LOW);  // Optional: disable pull-ups
        pinMode(inOutPins[i], INPUT);
    }
}

void initializeOutputPort() {
    // Set all inOut pins to OUTPUT
    for (int i = 0; i < 8; i++) {
        pinMode(inOutPins[i], OUTPUT);
    }
}

// ========== Set 16-bit address via 2x 74LS595 ==========
void setAddress(uint16_t address, bool reverse) {
    for (int i = 1; i <= 16; i++) {
        digitalWrite(addLatchPin, LOW);
        digitalWrite(addClockPin, LOW);
        if(reverse)
            digitalWrite(addDataPin, (address & (1 << (15 - i))) ? HIGH : LOW);
        else
            digitalWrite(addDataPin, (address & (1 << i)) ? HIGH : LOW);
        digitalWrite(addClockPin, HIGH);
        digitalWrite(addLatchPin, HIGH);
    }
}

// ========== Read 8-bit data from EEPROM ==========
uint8_t readEEPROM(uint16_t address) {
    setAddress(address);

    digitalWrite(writeEnbPin, HIGH);   // Ensure write is disabled
    digitalWrite(outputEnbPin, LOW);   // EEPROM drives the data bus
    delayMicroseconds(1);              // Allow bus to settle

    uint8_t value = 0;
    for (int i = 0; i < 8; i++) {
        if (digitalRead(inOutPins[i]) == HIGH) {
            value |= (1 << i);
        }
    }

    digitalWrite(outputEnbPin, HIGH);  // Stop EEPROM driving the bus

    return value;
}

// ========== Write 8-bit data to EEPROM ==========
void writeEEPROM(uint16_t address, uint8_t data) {
    setAddress(address);

    digitalWrite(outputEnbPin, HIGH);  // Ensure EEPROM is not driving the bus

    // Drive data onto the bus (pinMode already OUTPUT)
    for (int i = 0; i < 8; i++) {
        digitalWrite(inOutPins[i], (data & (1 << i)) ? HIGH : LOW);
    }

    delayMicroseconds(1);              // Setup time before WE

    digitalWrite(writeEnbPin, LOW);    // Begin write
    delayMicroseconds(2);              // Pulse width (>=200ns)
    digitalWrite(writeEnbPin, HIGH);   // End write

    // Data polling (DQ7) + full byte match, timeout ~12ms
    unsigned long start = millis();
    while (millis() - start < 12) {
        // Switch to input to read
        initializeInputPort();
        uint8_t v = readEEPROM(address); // readEEPROM toggles OE appropriately
        if ((v & 0x80) == (data & 0x80) && v == data) {
            initializeOutputPort();
            return;
        }
        initializeOutputPort();
    }
}
