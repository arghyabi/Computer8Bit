// Address shift register (74LS595)
const int addDataPin  = 2;
const int addClockPin = 3;
const int addLatchPin = 4;

// EEPROM control pins (active low)
const int writeEnbPin = A1;
const int readEnbPin  = A2;
const int chipEnbPin  = A3;

const int inOut0      = 5;
const int inOut1      = 6;
const int inOut2      = 7;
const int inOut3      = 8;
const int inOut4      = 9;
const int inOut5      = 10;
const int inOut6      = 11;
const int inOut7      = 12;

const int ledPin      = 13;

const int inOutPins[] = {inOut0, inOut1, inOut2, inOut3, inOut4, inOut5, inOut6, inOut7};

uint16_t led_counter = 0;
bool led_state = false;


void    setAddress(uint16_t address);
uint8_t readEEPROM(uint16_t address);
void    writeEEPROM(uint16_t address, uint8_t data);
void    dumpEEPROM(int startAddress = 0, int endAddress = 255);
void    writeMicrocodeToEEPROM(const uint8_t* microcode, size_t size);
void    initializeInputPort();
void    initializeOutputPort();


void setup() {
  // Address shift register pins
  pinMode(addDataPin, OUTPUT);
  pinMode(addClockPin, OUTPUT);
  pinMode(addLatchPin, OUTPUT);

  // EEPROM control signals
  pinMode(writeEnbPin, OUTPUT);
  pinMode(readEnbPin, OUTPUT);
  pinMode(chipEnbPin, OUTPUT);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  digitalWrite(writeEnbPin, HIGH);  // Disable write
  digitalWrite(readEnbPin, HIGH);   // Disable read
  digitalWrite(chipEnbPin, LOW);   // Disable read

  Serial.begin(9600);
}


void loop() {
  if (Serial.available() >= 3) {
    uint16_t addr = Serial.read() << 8;
    addr |= Serial.read();
    uint8_t data = Serial.read();

    writeEEPROM(addr, data);
    Serial.write(0xAA);  // ACK

    // Toggle LED every 256 bytes
    led_counter++;
    if (led_counter >= 2) {
      led_state = !led_state;
      digitalWrite(ledPin, led_state ? HIGH : LOW);
      led_counter = 0;
    }
  }
}


void writeMicrocodeToEEPROM(const uint8_t* microcode, size_t size) {
  Serial.println("Writing microcode to EEPROM...");

  // Initialize output port
  initializeOutputPort();

  // Write microcode to EEPROM
  for (uint16_t address = 0; address < size; address++) {
    writeEEPROM(address, microcode[address]);
    // delay(1); // Small delay to allow EEPROM write
  }

  Serial.println("Microcode write complete.");
}


void dumpEEPROM(int startAddress, int endAddress) {
  Serial.print("EEPROM Dump:");
  Serial.print("\nStart Address: 0x");
  if (startAddress < 0x10) Serial.print("0");
  Serial.print(startAddress, HEX);
  Serial.print("\nEnd Address: 0x");
  if (endAddress < 0x10) Serial.print("0");
  Serial.print(endAddress, HEX);
  Serial.print("\n\n");

  for (int addr = startAddress; addr < endAddress; addr++) {
    uint8_t val = readEEPROM(addr);
    if (addr % 16 == 0) {
      Serial.print("\n0x");
      if (addr < 0x10) Serial.print("0");
      Serial.print(addr, HEX);
      Serial.print(": ");
    }
    if (val < 0x10) Serial.print("0");
    Serial.print(val, HEX);
    Serial.print(" ");
  }

  Serial.println("\n\nDump Complete.");
}


void initializeInputPort() {
  // Set all inOut pins to INPUT
  for (int i = 0; i < 8; i++) {
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
void setAddress(uint16_t address) {
  digitalWrite(addLatchPin, LOW);
  for (int i = 15; i >= 0; i--) {
    digitalWrite(addClockPin, LOW);
    digitalWrite(addDataPin, (address & (1 << i)) ? HIGH : LOW);
    digitalWrite(addClockPin, HIGH);
  }
  digitalWrite(addLatchPin, HIGH);
}


// ========== Read 8-bit data from EEPROM ==========
uint8_t readEEPROM(uint16_t address) {
  setAddress(address);

  // Enable EEPROM output by setting readEnbPin LOW
  digitalWrite(readEnbPin, LOW);
  digitalWrite(writeEnbPin, HIGH); // Ensure write is disabled

  uint8_t value = 0;
  for (int i = 0; i < 8; i++) {
    if (digitalRead(inOutPins[i]) == HIGH) {
      value |= (1 << i);
    }
  }

  // Disable EEPROM output by setting readEnbPin HIGH
  digitalWrite(readEnbPin, HIGH);

  return value;
}


// ========== Function to write to EEPROM ==========
void writeEEPROM(uint16_t address, uint8_t data) {
  setAddress(address);

  // Set data bus pins as OUTPUT
  for (int i = 0; i < 8; i++) {
    digitalWrite(inOutPins[i], (data & (1 << i)) ? HIGH : LOW);
  }

  // Enable write operation
  digitalWrite(readEnbPin, HIGH);   // Disable read
  digitalWrite(writeEnbPin, LOW);   // Enable write
  delay(5);                         // Short pulse for write operation
  digitalWrite(writeEnbPin, HIGH);  // Disable write
  delay(1);
}
