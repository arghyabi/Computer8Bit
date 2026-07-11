# 💻 8-bit Computer ISA

> **Available Registers:** `A`, `B`, `C`, `D`
>
> The corresponding value for each register is as follows.

| Register | Binary |
|   :---:  | :---:  |
| 🅰       | `00`   |
| 🅱       | `01`   |
| 🅲       | `10`   |
| 🅳       | `11`   |

---

> 💡 **Note**
> - Use `;` for comments
> - Both space and , separated instruction are valid like

### 🧾 **Example**
```asm
MOV A B ; Copy the value of B to A
SUB B C ; Subtract C from B and keep in B
ADD A, B ; Add B and A and keep in A
XOR B, C ; Logical XOR in B and C and keep in B
```


## 🧾 Instruction Format

*(Please refer to the full documentation below for all supported opcodes and binary formats)*

> ⬇️ *The full ISA instruction set follows below. It includes*:
> - Opcode formats
> - Register mappings
> - Full binary encodings
> - Descriptions for each instruction

### Abbreviation Table

| Abbreviation | Meaning            |
| :----------: | :------------------|
| **R**        | Any Register       |
| **S**        | Source Register    |
| **D**        | Dest. Register     |
| **T**        | Instruction Type   |
| **V**        | Value              |
| **A**        | Address            |
| **SR**       | Special Register   |


### Instruction Table
<table>
    <thead>
        <tr>
            <th>Instruction Format</th>
            <th>Binary Opcode</th>
            <th>Instruction</th>
            <th>Size</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td valign="top"><strong>0000_0000</strong></td>
            <td valign="top">0000_0000</td>
            <td valign="top">
                <a href="#-instruction-nop">NOP</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">No Operation</td>
        </tr>
        <tr>
            <td valign="top"><strong>SR01_0000</strong></td>
            <td valign="top">SR01_0000</td>
            <td valign="top">
                <a href="#-instruction-nop">LDSR SR VV</a>
            </td>
            <td valign="top">2 Byte</td>
            <td valign="top">Load value immediately to Special Register</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0001</strong></td>
            <td valign="top">SSDD_0001</td>
            <td valign="top">
                <a href="#-instruction-add">ADD D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Add 2 registers and update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0010</strong></td>
            <td valign="top">SSDD_0010</td>
            <td valign="top">
                <a href="#-instruction-sub">SUB D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Subtract source from dest. & update to dest.</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0011</strong></td>
            <td valign="top">SSDD_0011</td>
            <td valign="top">
                <a href="#-instruction-mov">MOV D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Move from source to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0100</strong></td>
            <td valign="top">SSDD_0100</td>
            <td valign="top">
                <a href="#-instruction-and">AND D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical AND operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0101</strong></td>
            <td valign="top">SSDD_0101</td>
            <td valign="top">
                <a href="#-instruction-or">OR D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical OR operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0110</strong></td>
            <td valign="top">SSDD_0110</td>
            <td valign="top">
                <a href="#-instruction-xor">XOR D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical XOR operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0111</strong></td>
            <td valign="top">SSDD_0111</td>
            <td valign="top">
                <a href="#-instruction-ldr">LDR D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Load destination from memory address in source</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_1000</strong></td>
            <td valign="top">SSDD_1000</td>
            <td valign="top">
                <a href="#-instruction-str">STR D S</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Save register value to memory address in source</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRRR_1001</strong></td>
            <td valign="top">RRRR_1001</td>
            <td valign="top">
                <a href="#-instruction-cmp">CMP R R</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Compare two register values (unsigned); update the flag</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRRR_1010</strong></td>
            <td valign="top">RRRR_1010</td>
            <td valign="top">
                <a href="#-instruction-cmps">CMPS R R</a>
            </td>
            <td valign="top">1 Byte</td>
            <td valign="top">Compare two register values (signed); update the flag</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRTT_1011</strong></td>
            <td valign="top">RR00_1011<br>RR01_1011<br>RR10_1011<br>RR11_1011</td>
            <td valign="top">
                <a href="#-instruction-shl">SHL R</a><br>
                <a href="#-instruction-shr">SHR R</a><br>
                <a href="#-instruction-inc">INC R</a><br>
                <a href="#-instruction-dec">DEC R</a>
            </td>
            <td valign="top">1 Byte<br>1 Byte<br>1 Byte<br>1 Byte</td>
            <td valign="top">Shift register left by 1 bit<br>Shift register right by 1 bit<br>Increment register<br>Decrement register</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRTT_1100</strong></td>
            <td valign="top">RR00_1100<br>RR01_1100<br>RR10_1100<br>RR11_1100</td>
            <td valign="top">
                <a href="#-instruction-ldi">LDI R VV</a><br>
                <a href="#-instruction-ldm">LDM R AA</a><br>
                <a href="#-instruction-sav">SAV R AA</a><br>
                <a href="#-instruction-not">NOT R</a>
            </td>
            <td valign="top">2 Byte<br>2 Byte<br>2 Byte<br>1 Byte</td>
            <td valign="top">Load the value to register immediately<br>Load from value to register from memory<br>Save the register value to memory<br>Bitwise NOT operation; update same register</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRTT_1101</strong></td>
            <td valign="top">RR00_1101<br>RR01_1101<br>RR10_1101<br>RR11_1101</td>
            <td valign="top">
                <a href="#-instruction-cmi">CMI R VV</a><br>
                <a href="#-instruction-cmis">CMIS R VV</a><br>
                <a href="#-instruction-push">PUSH R</a><br>
                <a href="#-instruction-pop">POP R</a>
            </td>
            <td valign="top">2 Byte<br>2 Byte<br>1 Byte<br>1 Byte</td>
            <td valign="top">Compare register with immediate value (unsigned)<br>Compare register with immediate value (signed)<br>Push register value to stack<br>Pop from stack and load to register</td>
        </tr>
        <tr>
            <td valign="top"><strong>0TTT_1110</strong></td>
            <td valign="top">0000_1110<br>0001_1110<br>0010_1110<br>0011_1110<br>0100_1110<br>0101_1110<br>0110_1110</td>
            <td valign="top">
                <a href="#-instruction-jmp">JMP AA</a><br>
                <a href="#-instruction-jmz">JMZ AA</a><br>
                <a href="#-instruction-jnz">JNZ AA</a><br>
                <a href="#-instruction-jmc">JMC AA</a><br>
                <a href="#-instruction-jme">JME AA</a><br>
                <a href="#-instruction-jmg">JMG AA</a><br>
                <a href="#-instruction-jml">JML AA</a>
            </td>
            <td valign="top">3 Byte<br>3 Byte<br>3 Byte<br>3 Byte<br>3 Byte<br>3 Byte<br>3 Byte</td>
            <td valign="top">Jump to address<br>Jump to address if Zero flag set<br>Jump to address if Zero flag NOT set<br>Jump to address if Carry flag set<br>Jump to address if Eql flag is set<br>Jump to address if Grt flag is set<br>Jump to address if Lst flag is set</td>
        </tr>
        <tr>
            <td valign="top"><strong>TTTT_1111</strong></td>
            <td valign="top">0000_1111<br>0001_1111<br>0010_1111<br>0011_1111<br>0100_1111<br>0101_1111<br>1111_1111</td>
            <td valign="top">
                <a href="#-instruction-pshv">PSHV VV</a><br>
                <a href="#-instruction-call">CALL AA</a><br>
                <a href="#-instruction-rtn">RTN</a><br>
                <a href="#-instruction-out">OUT</a><br>
                <a href="#-instruction-outs">OUTS</a><br>
                <a href="#-instruction-hlt">HLT</a><br>
                <a href="#-instruction-rst">RST</a>
            </td>
            <td valign="top">2 Byte<br>3 Byte<br>1 Byte<br>1 Byte<br>1 Byte<br>1 Byte<br>1 Byte</td>
            <td valign="top">Push immediate value to stack<br>Push the PC to Stack (PC high & low) & load new address<br>Pop the PC address and restore<br>Display unsigned value in 7-Segment<br>Display signed value in 7-Segment<br>Halt the platform<br>Reset it self</td>
        </tr>
    </tbody>
</table>

## Instructions set


### ✅ Instruction: NOP
This `NOP` instruction does nothing. It's kind of a blank instruction.

#### `Ins. Format: NOP`
#### `Bin. Format: 0000_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| NOP          | 0000_0000    |

---------------

### ✅ Instruction: LDSR
This `LDSR` instruction load the value imediatly to the Spacial Register.

#### `Ins. Format: LDSR SR VV`
#### `Bin. Format: SR01_0000`

| Instruction  | Binary Value          |
| :---         |    :---:              |
| LDSR SP 0xXX | 0001_0000 xxxx_xxxx   |

* 0101_0000, 1001_0000, 1101_0000, are Reserved for future use

---------------

### ✅ Instruction: ADD
This `ADD` instruction is used to add two numbers and save the output in the destination register.

#### `Ins. Format: ADD D S`
#### `Bin. Format: SSDD_0001`

| Instruction  | Binary Value |
| :---         |    :---:     |
| ADD A A      | 0000_0001    |
| ADD A B      | 0001_0001    |
| ADD A C      | 0010_0001    |
| ADD A D      | 0011_0001    |
| ADD B A      | 0100_0001    |
| ADD B B      | 0101_0001    |
| ADD B C      | 0110_0001    |
| ADD B D      | 0111_0001    |
| ADD C A      | 1000_0001    |
| ADD C B      | 1001_0001    |
| ADD C C      | 1010_0001    |
| ADD C D      | 1011_0001    |
| ADD D A      | 1100_0001    |
| ADD D B      | 1101_0001    |
| ADD D C      | 1110_0001    |
| ADD D D      | 1111_0001    |

---------------

### ✅ Instruction: SUB
This `SUB` instruction is used to subtract one number from another and save the output in the destination register.

#### `Ins. Format: SUB D S`
#### `Bin. Format: SSDD_0010`

| Instruction  | Binary Value |
| :---         |    :---:     |
| SUB A B      | 0001_0010    |
| SUB A C      | 0010_0010    |
| SUB A D      | 0011_0010    |
| SUB B A      | 0100_0010    |
| SUB B C      | 0110_0010    |
| SUB B D      | 0111_0010    |
| SUB C A      | 1000_0010    |
| SUB C B      | 1001_0010    |
| SUB C D      | 1011_0010    |
| SUB D A      | 1100_0010    |
| SUB D B      | 1101_0010    |
| SUB D C      | 1110_0010    |

---------------

### ✅ Instruction: MOV
This `MOV` instruction is used to move a value from one register to another

#### `Ins. Format: MOV D S`
#### `Bin. Format: SSDD_0011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| MOV A B      | 0001_0011    |
| MOV A C      | 0010_0011    |
| MOV A D      | 0011_0011    |
| MOV B A      | 0100_0011    |
| MOV B C      | 0110_0011    |
| MOV B D      | 0111_0011    |
| MOV C A      | 1000_0011    |
| MOV C B      | 1001_0011    |
| MOV C D      | 1011_0011    |
| MOV D A      | 1100_0011    |
| MOV D B      | 1101_0011    |
| MOV D C      | 1110_0011    |

---------------

### ✅ Instruction: AND
This `AND` instruction is used to do a bitwise AND operation and keep the output in the destination register

#### `Ins. Format: AND D S`
#### `Bin. Format: SSDD_0100`

| Instruction  | Binary Value |
| :---         |    :---:     |
| AND A B      | 0001_0100    |
| AND A C      | 0010_0100    |
| AND A D      | 0011_0100    |
| AND B A      | 0100_0100    |
| AND B C      | 0110_0100    |
| AND B D      | 0111_0100    |
| AND C A      | 1000_0100    |
| AND C B      | 1001_0100    |
| AND C D      | 1011_0100    |
| AND D A      | 1100_0100    |
| AND D B      | 1101_0100    |
| AND D C      | 1110_0100    |

---------------

### ✅ Instruction: OR
This `OR` instruction is used to do a bitwise OR operation and keep the output in the destination register

#### `Ins. Format: OR D S`
#### `Bin. Format: SSDD_0101`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OR A B       | 0001_0101    |
| OR A C       | 0010_0101    |
| OR A D       | 0011_0101    |
| OR B A       | 0100_0101    |
| OR B C       | 0110_0101    |
| OR B D       | 0111_0101    |
| OR C A       | 1000_0101    |
| OR C B       | 1001_0101    |
| OR C D       | 1011_0101    |
| OR D A       | 1100_0101    |
| OR D B       | 1101_0101    |
| OR D C       | 1110_0101    |

---------------

### ✅ Instruction: XOR
This `XOR` instruction is used to do a bitwise XOR operation and keep the output in the destination register

#### `Ins. Format: XOR D S`
#### `Bin. Format: SSDD_0110`

| Instruction  | Binary Value |
| :---         |    :---:     |
| XOR A B      | 0001_0110    |
| XOR A C      | 0010_0110    |
| XOR A D      | 0011_0110    |
| XOR B A      | 0100_0110    |
| XOR B C      | 0110_0110    |
| XOR B D      | 0111_0110    |
| XOR C A      | 1000_0110    |
| XOR C B      | 1001_0110    |
| XOR C D      | 1011_0110    |
| XOR D A      | 1100_0110    |
| XOR D B      | 1101_0110    |
| XOR D C      | 1110_0110    |

---------------

### ✅ Instruction: LDR
This `LDR` instruction is used to get the value from RAM of address, that hold in source register and load the value to destination register

#### `Ins. Format: LDR D S`
#### `Bin. Format: SSDD_0111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| LDR A B      | 0001_0111    |
| LDR A C      | 0010_0111    |
| LDR A D      | 0011_0111    |
| LDR B A      | 0100_0111    |
| LDR B C      | 0110_0111    |
| LDR B D      | 0111_0111    |
| LDR C A      | 1000_0111    |
| LDR C B      | 1001_0111    |
| LDR C D      | 1011_0111    |
| LDR D A      | 1100_0111    |
| LDR D B      | 1101_0111    |
| LDR D C      | 1110_0111    |

---------------

### ✅ Instruction: STR
This `STR` instruction is used to save the value of destination register to RAM of address, hold in the source register.

#### `Ins. Format: STR D S`
#### `Bin. Format: SSDD_1000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| STR A B      | 0001_1000    |
| STR A C      | 0010_1000    |
| STR A D      | 0011_1000    |
| STR B A      | 0100_1000    |
| STR B C      | 0110_1000    |
| STR B D      | 0111_1000    |
| STR C A      | 1000_1000    |
| STR C B      | 1001_1000    |
| STR C D      | 1011_1000    |
| STR D A      | 1100_1000    |
| STR D B      | 1101_1000    |
| STR D C      | 1110_1000    |

---------------

### ✅ Instruction: CMP
This `CMP` instruction is used to do an unsigned comparison and set/reset the comparison flags (Eql, Grt, Lst)

#### `Ins. Format: CMP R R`
#### `Bin. Format: RRRR_1001`

| Instruction  | Binary Value |
| :---         |    :---:     |
| CMP A B      | 0001_1001    |
| CMP A C      | 0010_1001    |
| CMP A D      | 0011_1001    |
| CMP B A      | 0100_1001    |
| CMP B C      | 0110_1001    |
| CMP B D      | 0111_1001    |
| CMP C A      | 1000_1001    |
| CMP C B      | 1001_1001    |
| CMP C D      | 1011_1001    |
| CMP D A      | 1100_1001    |
| CMP D B      | 1101_1001    |
| CMP D C      | 1110_1001    |

---------------

### ✅ Instruction: CMPS
This `CMPS` instruction is used to do a signed comparison and set/reset the comparison flags (Eql, Grt, Lst)

#### `Ins. Format: CMPS R R`
#### `Bin. Format: RRRR_1010`

| Instruction  | Binary Value |
| :---         |    :---:     |
| CMPS A B     | 0001_1010    |
| CMPS A C     | 0010_1010    |
| CMPS A D     | 0011_1010    |
| CMPS B A     | 0100_1010    |
| CMPS B C     | 0110_1010    |
| CMPS B D     | 0111_1010    |
| CMPS C A     | 1000_1010    |
| CMPS C B     | 1001_1010    |
| CMPS C D     | 1011_1010    |
| CMPS D A     | 1100_1010    |
| CMPS D B     | 1101_1010    |
| CMPS D C     | 1110_1010    |

---------------

### ✅ Instruction: SHL
This `SHL` instruction shifts the register value left by 1 bit.

#### `Ins. Format: SHL R`
#### `Bin. Format: RR00_1011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| SHL A        | 0000_1011    |
| SHL B        | 0100_1011    |
| SHL C        | 1000_1011    |
| SHL D        | 1100_1011    |

---------------

### ✅ Instruction: SHR
This `SHR` instruction shifts the register value right by 1 bit.

#### `Ins. Format: SHR R`
#### `Bin. Format: RR01_1011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| SHR A        | 0001_1011    |
| SHR B        | 0101_1011    |
| SHR C        | 1001_1011    |
| SHR D        | 1101_1011    |

---------------

### ✅ Instruction: INC
This `INC` instruction is used to increase the register value by 1.

#### `Ins. Format: INC R`
#### `Bin. Format: RR10_1011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| INC A        | 0010_1011    |
| INC B        | 0110_1011    |
| INC C        | 1010_1011    |
| INC D        | 1110_1011    |

---------------

### ✅ Instruction: DEC
This `DEC` instruction is used to decrease the register value by 1.

#### `Ins. Format: DEC R`
#### `Bin. Format: RR11_1011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| DEC A        | 0011_1011    |
| DEC B        | 0111_1011    |
| DEC C        | 1011_1011    |
| DEC D        | 1111_1011    |

---------------

### ✅ Instruction: LDI
This `LDI` instruction is used to load an 8-bit value immediately into a register

#### `Ins. Format: LDI R VV`
#### `Bin. Format: RR00_1100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDI A 0xXX   | 0000_1100 xxxx_xxxx |
| LDI B 0xXX   | 0100_1100 xxxx_xxxx |
| LDI C 0xXX   | 1000_1100 xxxx_xxxx |
| LDI D 0xXX   | 1100_1100 xxxx_xxxx |

---------------

### ✅ Instruction: LDM
This `LDM` instruction is used to load an 8-bit value into a register from memory

#### `Ins. Format: LDM R AA`
#### `Bin. Format: RR01_1100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDM A 0xXX   | 0001_1100 xxxx_xxxx |
| LDM B 0xXX   | 0101_1100 xxxx_xxxx |
| LDM C 0xXX   | 1001_1100 xxxx_xxxx |
| LDM D 0xXX   | 1101_1100 xxxx_xxxx |

---------------

### ✅ Instruction: SAV
This `SAV` instruction is used to save a value from the register to memory

#### `Ins. Format: SAV R AA`
#### `Bin. Format: RR10_1100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| SAV A 0xXX   | 0010_1100 xxxx_xxxx |
| SAV B 0xXX   | 0110_1100 xxxx_xxxx |
| SAV C 0xXX   | 1010_1100 xxxx_xxxx |
| SAV D 0xXX   | 1110_1100 xxxx_xxxx |

---------------

### ✅ Instruction: NOT
This `NOT` instruction is used to do a bitwise NOT operation and keep the output in the same register

#### `Ins. Format: NOT R`
#### `Bin. Format: RR11_1100`

| Instruction  | Binary Value |
| :---         |    :---:     |
| NOT A        | 0011_1100    |
| NOT B        | 0111_1100    |
| NOT C        | 1011_1100    |
| NOT D        | 1111_1100    |

---------------

### ✅ Instruction: CMI
This `CMI` instruction is used to do an unsigned comparison with an immediate value and set/reset the comparison flags (Eql, Grt, Lst)

#### `Ins. Format: CMI R VV`
#### `Bin. Format: RR00_1101`

| Instruction  |     Binary Value      |
| :---         |        :---:          |
| CMI A 0xXX   | 0000_1101 xxxx_xxxx   |
| CMI B 0xXX   | 0100_1101 xxxx_xxxx   |
| CMI C 0xXX   | 1000_1101 xxxx_xxxx   |
| CMI D 0xXX   | 1100_1101 xxxx_xxxx   |

---------------

### ✅ Instruction: CMIS
This `CMIS` instruction is used to do a signed comparison with an immediate value and set/reset the comparison flags (Eql, Grt, Lst)

#### `Ins. Format: CMIS R VV`
#### `Bin. Format: RR01_1101`

| Instruction  |     Binary Value      |
| :---         |        :---:          |
| CMIS A 0xXX  | 0001_1101 xxxx_xxxx   |
| CMIS B 0xXX  | 0101_1101 xxxx_xxxx   |
| CMIS C 0xXX  | 1001_1101 xxxx_xxxx   |
| CMIS D 0xXX  | 1101_1101 xxxx_xxxx   |

---------------

### ✅ Instruction: PUSH
This `PUSH` instruction is used to push a register value onto the stack

#### `Ins. Format: PUSH R`
#### `Bin. Format: RR10_1101`

| Instruction  | Binary Value |
| :---         |    :---:     |
| PUSH A       | 0010_1101    |
| PUSH B       | 0110_1101    |
| PUSH C       | 1010_1101    |
| PUSH D       | 1110_1101    |

---------------

### ✅ Instruction: POP
This `POP` instruction is used to pop a value from the stack and load it into a register

#### `Ins. Format: POP R`
#### `Bin. Format: RR11_1101`

| Instruction  | Binary Value |
| :---         |    :---:     |
| POP A        | 0011_1101    |
| POP B        | 0111_1101    |
| POP C        | 1011_1101    |
| POP D        | 1111_1101    |

---------------

### ✅ Instruction: JMP
This `JMP` instruction is used to jump to a specific address

#### `Ins. Format: JMP AA`
#### `Bin. Format: 0000_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JMP 0xXX     | 0000_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JMZ
This `JMZ` instruction is used to jump to a specific address when the `Zero` flag is set

#### `Ins. Format: JMZ AA`
#### `Bin. Format: 0001_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JMZ 0xXX     | 0001_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JNZ
This `JNZ` instruction is used to jump to a specific address when the `Zero` flag is not set

#### `Ins. Format: JNZ AA`
#### `Bin. Format: 0010_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JNZ 0xXX     | 0010_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JMC
This `JMC` instruction is used to jump to a specific address when the `Carry` flag is set

#### `Ins. Format: JMC AA`
#### `Bin. Format: 0011_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JMC 0xXX     | 0011_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JME
This `JME` instruction is used to jump to a specific address when the `Eql` flag is set

#### `Ins. Format: JME AA`
#### `Bin. Format: 0100_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JME 0xXX     | 0100_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JMG
This `JMG` instruction is used to jump to a specific address when the `Grt` flag is set

#### `Ins. Format: JMG AA`
#### `Bin. Format: 0101_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JMG 0xXX     | 0101_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: JML
This `JML` instruction is used to jump to a specific address when the `Lst` flag is set

#### `Ins. Format: JML AA`
#### `Bin. Format: 0110_1110`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| JML 0xXX     | 0110_1110 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: PSHV
This `PSHV` instruction is used to push an immediate value onto the stack

#### `Ins. Format: PSHV VV`
#### `Bin. Format: 0000_1111`

| Instruction  |     Binary Value      |
| :---         |        :---:          |
| PSHV 0xXX    | 0000_1111 xxxx_xxxx   |

---------------

### ✅ Instruction: CALL
This `CALL` instruction is used to call a subroutine by pushing the current PC to the stack and jumping to a new address

#### `Ins. Format: CALL AA`
#### `Bin. Format: 0001_1111`

| Instruction  |           Binary Value        |
| :---         |              :---:            |
| CALL 0xXX    | 0001_1111 xxxx_xxxx xxxx_xxxx |

---------------

### ✅ Instruction: RTN
This `RTN` instruction is used to return from a subroutine by popping the PC address from the stack

#### `Ins. Format: RTN`
#### `Bin. Format: 0010_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| RTN          | 0010_1111    |

---------------

### ✅ Instruction: OUT
This `OUT` instruction is used to show the unsigned value of register A in the 7-seg display

#### `Ins. Format: OUT`
#### `Bin. Format: 0011_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OUT          | 0011_1111    |

---------------

### ✅ Instruction: OUTS
This `OUTS` instruction is used to show the signed value of register A in the 7-seg display

#### `Ins. Format: OUTS`
#### `Bin. Format: 0100_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OUTS         | 0100_1111    |

---------------

### ✅ Instruction: HLT
This `HLT` instruction is used to halt the system till reset

#### `Ins. Format: HLT`
#### `Bin. Format: 0101_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| HLT          | 0101_1111    |

---------------

### ✅ Instruction: RST
This `RST` instruction is used to reset the computer

#### `Ins. Format: RST`
#### `Bin. Format: 1111_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| RST          | 1111_1111    |