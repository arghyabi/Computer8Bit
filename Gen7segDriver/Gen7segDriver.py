# Generate AT28C16 binary image for displaying decimal digits on 7-segment displays

def getNegetiveNum(num):
    return (num ^ 0xFF) + 1


segment_map = [
                #      a b c d e f g
    0b111_1110, # 0 => 1 1 1 1 1 1 0 // 0x7E
    0b011_0000, # 1 => 0 1 1 0 0 0 0 // 0x30
    0b110_1101, # 2 => 1 1 0 1 1 0 1 // 0x6D
    0b111_1001, # 3 => 1 1 1 1 0 0 1 // 0x79
    0b011_0011, # 4 => 0 1 1 0 0 1 1 // 0x33
    0b101_1011, # 5 => 1 0 1 1 0 1 1 // 0x5B
    0b101_1111, # 6 => 1 0 1 1 1 1 1 // 0x5F
    0b111_0000, # 7 => 1 1 1 0 0 0 0 // 0x70
    0b111_1111, # 8 => 1 1 1 1 1 1 1 // 0x7F
    0b111_1011, # 9 => 1 1 1 1 0 1 1 // 0x7B
    0b000_0001  # - => 0 0 0 0 0 0 1 // 0x01
]

eeprom = [0]*2048  # 2 KB for AT28C16

# For positive numbers
for i in range(256):  # All 8-bit switch combinations
    num = i
    u = num % 10
    t = (num // 10) % 10
    h = (num // 100) % 10

    eeprom[0b000_0000_0000 + i] = segment_map[u]  # Units digit
    eeprom[0b001_0000_0000 + i] = segment_map[t]  # Tens digit
    eeprom[0b010_0000_0000 + i] = segment_map[h]  # Hundreds digit

# # For negative numbers
for i in range(256):  # All 8-bit switch combinations
    num = getNegetiveNum(i)
    u = num % 10
    t = (num // 10) % 10
    h = (num // 100) % 10

    eeprom[0b100_0000_0000 + i] = segment_map[u]  # Units digit
    eeprom[0b101_0000_0000 + i] = segment_map[t]  # Tens digit
    eeprom[0b110_0000_0000 + i] = segment_map[h]  # Hundreds digit

with open("decimal_display_segments.bin", "wb") as f:
    f.write(bytes(eeprom))

print("EEPROM image created: decimal_display_segments.bin")
