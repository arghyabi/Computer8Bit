# Generate AT28C16 binary image for displaying decimal digits on 7-segment displays

def getNegetiveNum(num):
    return (num ^ 0xFF) + 1



    # ' aaaa '
    # 'f    b'
    # 'f    b'
    # ' gggg '
    # 'e    c'
    # 'e    c'
    # ' dddd '

segment_map = [
                 #      g f e d  c b a -
    0b0111_1110, # 0 => 0 1 1 1  1 1 1 0 // 0x7E
    0b0000_1100, # 1 => 0 0 0 0  1 1 0 0 // 0x0C
    0b1011_1010, # 2 => 1 0 1 1  1 0 1 0 // 0xBA
    0b1001_1110, # 3 => 1 0 0 1  1 1 1 0 // 0x9E
    0b1100_1100, # 4 => 1 1 0 0  1 1 0 0 // 0xCC
    0b1101_1010, # 5 => 1 1 0 1  1 0 1 0 // 0xDA
    0b1111_1010, # 6 => 1 1 1 1  1 0 1 0 // 0xFA
    0b0000_1110, # 7 => 0 0 0 0  1 1 1 0 // 0x0E
    0b1111_1110, # 8 => 1 1 1 1  1 1 1 0 // 0xFE
    0b1101_1110, # 9 => 1 1 0 1  1 1 1 0 // 0xDE
    0b1000_0000  # - => 1 0 0 0  0 0 0 0 // 0x80

]

eeprom = [0]*2048  # 2 KB for AT28C16

# For positive numbers
for index in range(256):  # All 8-bit switch combinations
    num = index
    unit = num % 10
    ten = (num // 10) % 10
    hundred = (num // 100) % 10

    eeprom[0b000_0000_0000 + index] = 0x00                 # MSB
    eeprom[0b001_0000_0000 + index] = segment_map[hundred] # Hundreds digit
    eeprom[0b010_0000_0000 + index] = segment_map[ten]     # Tens digit
    eeprom[0b011_0000_0000 + index] = segment_map[unit]    # Units digit

# For negative numbers
for index in range(256):  # All 8-bit switch combinations
    num = getNegetiveNum(index)
    unit = num % 10
    ten = (num // 10) % 10
    hundred = (num // 100) % 10

    eeprom[0b100_0000_0000 + index] = segment_map[-1]       # MSB
    eeprom[0b101_0000_0000 + index] = segment_map[hundred]  # Hundreds digit
    eeprom[0b110_0000_0000 + index] = segment_map[ten]      # Tens digit
    eeprom[0b111_0000_0000 + index] = segment_map[unit]     # Units digit

with open("decimal_display_segments.bin", "wb") as f:
    f.write(bytes(eeprom))

print("EEPROM image created: decimal_display_segments.bin")
