__bl_start:
    ; Reset all the registers
    LDI A, 0
    LDI B, 0
    LDI C, 0
    LDI D, 0

    ; Reset the 7 segment display
    OUT

    ; Reset all temp registers and flags
    ADD A, B

    ; Reset the stack pointer
    LDSR SP, 0

    ; Jump to the main program
    JMP __app_main
