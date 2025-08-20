# Generate AT28C16 binary image for displaying decimal digits on 7-segment displays

def genReverseNegativeNum(num):
    return (num - 1) ^ 0xFF


eeprom             = [0]*2048  # 2 KB for AT28C16
dataSize           = 8

# Thus(00)  Hund(10)  Tens(01)  Unit(11)
#
# ' aaaa '  ' aaaa '  ' aaaa '  ' aaaa '
# 'f    b'  'f    b'  'f    b'  'f    b'
# 'f    b'  'f    b'  'f    b'  'f    b'
# ' gggg '  ' gggg '  ' gggg '  ' gggg '
# 'e    c'  'e    c'  'e    c'  'e    c'
# 'e    c'  'e    c'  'e    c'  'e    c'
# ' dddd '  ' dddd '  ' dddd '  ' dddd '

segment_map = [
                 #      g f e d  c b a -
    0b0111_1110, # 0 => 0 1 1 1  1 1 1 0 // 0x7E
    0b0000_1100, # 1 => 0 0 0 0  1 1 0 0 // 0x0C
    0b1011_0110, # 2 => 1 0 1 1  0 1 1 0 // 0xB6
    0b1001_1110, # 3 => 1 0 0 1  1 1 1 0 // 0x9E
    0b1100_1100, # 4 => 1 1 0 0  1 1 0 0 // 0xCC
    0b1101_1010, # 5 => 1 1 0 1  1 0 1 0 // 0xDA
    0b1111_1010, # 6 => 1 1 1 1  1 0 1 0 // 0xFA
    0b0000_1110, # 7 => 0 0 0 0  1 1 1 0 // 0x0E
    0b1111_1110, # 8 => 1 1 1 1  1 1 1 0 // 0xFE
    0b1101_1110, # 9 => 1 1 0 1  1 1 1 0 // 0xDE

    0b1000_0000, # - => 1 0 0 0  0 0 0 0 // 0x80
    0b0000_0000  #   => 0 0 0 0  0 0 0 0 // 0x00
]


NO_SEGMENT_INDEX   = 11  # No segment lit
SIGN_SEGMENT_INDEX = 10  # Sign segment lit

THOUSAND_ADD       = 0b000 << dataSize
HUNDRED_ADD        = 0b010 << dataSize
TEN_ADD            = 0b001 << dataSize
UNIT_ADD           = 0b011 << dataSize

SIGN               = 0b100 << dataSize


# For positive numbers
for index in range(256):
    num = index
    unit = num % 10
    ten = (num // 10) % 10
    hundred = (num // 100) % 10

    eeprom[UNIT_ADD + index] = segment_map[unit]

    if hundred: # If there is a hundreds digit
        eeprom[HUNDRED_ADD + index] = segment_map[hundred]
    else:
        eeprom[HUNDRED_ADD + index] = segment_map[NO_SEGMENT_INDEX]

    if ten or hundred: # If there is a tens digit or hundreds digit (ex 102)
        eeprom[TEN_ADD + index] = segment_map[ten]          # Tens digit
    else:
        eeprom[TEN_ADD + index] = segment_map[NO_SEGMENT_INDEX]

    # No Sign
    eeprom[THOUSAND_ADD + index] = segment_map[NO_SEGMENT_INDEX]


# For negative numbers
for index in range(256):
    num = genReverseNegativeNum(index)
    unit = num % 10
    ten = (num // 10) % 10
    hundred = (num // 100) % 10

    # Initialization
    eeprom[SIGN + THOUSAND_ADD     + index] = segment_map[NO_SEGMENT_INDEX]
    eeprom[SIGN + TEN_ADD          + index] = segment_map[NO_SEGMENT_INDEX]
    eeprom[SIGN + HUNDRED_ADD      + index] = segment_map[NO_SEGMENT_INDEX]
    eeprom[SIGN + UNIT_ADD         + index] = segment_map[unit]

    if ten:
        eeprom[SIGN + TEN_ADD      + index] = segment_map[ten]
        eeprom[SIGN + HUNDRED_ADD  + index] = segment_map[SIGN_SEGMENT_INDEX]
    else:
        eeprom[SIGN + TEN_ADD      + index] = segment_map[SIGN_SEGMENT_INDEX]

    if hundred:
        eeprom[SIGN + HUNDRED_ADD  + index] = segment_map[hundred]
        eeprom[SIGN + THOUSAND_ADD + index] = segment_map[SIGN_SEGMENT_INDEX]


with open("decimal_display_segments.bin", "wb") as f:
    f.write(bytes(eeprom))

print("EEPROM image created: decimal_display_segments.bin")
