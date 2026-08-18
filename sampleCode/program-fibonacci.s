; ================================================================
; Fibonacci Sequence
; ================================================================

_main:

    ; Initialize the first two values
    LDI A, 0
    LDI B, 1

_loop:

    ; Display current Fibonacci number
    OUT

    ; Calculate next number
    MOV C, A
    ADD C, B

    ; Shift the values
    MOV A, B
    MOV B, C

    ; Continue while the result is below 255
    CMI B, 255
    JML _loop

    HLT
