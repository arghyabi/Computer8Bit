; ================================================================
; Simple Increment Program
; ================================================================

_main:

    ; Start from 0
    LDI A, 0

_loop:

    ; Display current value
    OUT

    ; Increment A
    INC A

    ; Compare A with 10
    CMI A, 10

    ; If A < 10, continue the loop
    JML _loop

    ; Stop the computer
    HLT
