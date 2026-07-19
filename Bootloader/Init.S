; ================================================================
; 8-Bit Computer Bootloader
; ================================================================
; This routine executes immediately after a hardware reset.
;
; On entry to __app_main, the following conditions are guaranteed:
;
;   -> SP = 0x7F
;   -> A  = 0
;   -> B  = 0
;   -> C  = 0
;   -> D  = 0
;   -> ALU flags are initialized.
;   -> 7-Segment display shows 0.
;
; ================================================================

__bl_start:

    ; ------------------------------------------------------------
    ; Initialize the Stack Pointer.
    ; RAM address range : 0x00 - 0x7F
    ; Initial SP value  : 0x7F
    ; The stack grows toward lower addresses.
    ; Each PUSH stores data at the current SP, then decrements SP.
    ; ------------------------------------------------------------
    LDI A, 0x7F
    WTSR SP

    ; ------------------------------------------------------------
    ; Clear all General Purpose Registers.
    ; ------------------------------------------------------------
    LDI A, 0
    LDI B, 0
    LDI C, 0
    LDI D, 0

    ; ------------------------------------------------------------
    ; Clear the 7-Segment Display.
    ; OUT displays the value of register A.
    ; ------------------------------------------------------------
    OUT

    ; ------------------------------------------------------------
    ; Initialize the ALU flags.
    ; A = 0 and B = 0, therefore:
    ;
    ;   Zero    = Set
    ;   Equal   = Set
    ;   Carry   = Cleared
    ;   Greater = Cleared
    ;   Less    = Cleared
    ; ------------------------------------------------------------
    ADD A, B

    ; ------------------------------------------------------------
    ; Transfer control to the user application.
    ; ------------------------------------------------------------
    JMP __app_main

    ; ------------------------------------------------------------
    ; This instruction should never be reached.
    ; Halt the CPU if control unexpectedly falls through.
    ; ------------------------------------------------------------
    HLT
