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

const int inOutPins[]  = {inOut0, inOut1, inOut2, inOut3, inOut4, inOut5, inOut6, inOut7};

uint16_t led_counter   = 0;
bool led_state         = false;
opMode_t operationMode = OPERATION_UNKNOWN;


void    setAddress(uint16_t address, bool reverse = true);
uint8_t readEEPROM(uint16_t address);
void    writeEEPROM(uint16_t address, uint8_t data);
void    initializeInputPort();
void    initializeOutputPort();


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

    Serial.begin(115200);
}


void loop() {
    // Read operation instructions
    if (operationMode == OPERATION_UNKNOWN) {
        if (Serial.available() >= 2) {
            if ((cmd_t)Serial.read() != CMD_MODE_SET)
                return;
            opMode_t tmp = (opMode_t)Serial.read();
            if(tmp == OPERATION_READ) {
                operationMode = tmp;
                initializeInputPort();
                Serial.write(ACK_OK);
            }
            else if (tmp == OPERATION_WRITE) {
                operationMode = tmp;
                initializeOutputPort();
                Serial.write(ACK_OK);
            }
            else {
                Serial.write(ACK_NO);
            }
        }
        return;
    }

    // Write data to eeprom
    else if (operationMode == OPERATION_WRITE) {
        if (Serial.available() >= 3) {
            uint16_t addr = Serial.read() << 8;
            addr |= Serial.read();
            uint8_t data = Serial.read();

            writeEEPROM(addr, data);
            Serial.write(ACK_OK);  // ACK

            // Toggle LED every 256 bytes
            led_counter++;
            if (led_counter >= 2) {
                led_state = !led_state;
                digitalWrite(redLedPin, led_state ? HIGH : LOW);
                led_counter = 0;
            }
        }
    }

    // Read data from eeprom
    else if (operationMode == OPERATION_READ) {
        if (Serial.available() >= 2) {
            uint16_t addr = Serial.read() << 8;
            addr |= Serial.read();
            uint8_t data = readEEPROM(addr);
            Serial.write(data);

            Serial.write(ACK_OK);  // ACK

            // Toggle LED every 256 bytes
            led_counter++;
            if (led_counter >= 2) {
                led_state = !led_state;
                digitalWrite(redLedPin, led_state ? HIGH : LOW);
                led_counter = 0;
            }
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
    for (int i = 0; i <= 16; i++) {
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
    delay(1);                          // tWP (write pulse ≥ 200 ns)
    digitalWrite(writeEnbPin, HIGH);   // End write

    delay(10);                         // Wait for write cycle to finish (tWC ≤ 10 ms)
}
