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
> - No `,` in instructions

### 🧾 **Example**
```asm
MOV A B ; Copy the value of B to A
SUB B C ; Subtract C from B and keep in B
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
            <td valign="top"><strong>00TT_0000</strong></td>
            <td valign="top">0000_0000<br>0001_0000<br>0010_0000</td>
            <td valign="top">NOP<br>OUT<br>HLT</td>
            <td valign="top">1 Byte<br>1 Byte<br>1 Byte</td>
            <td valign="top">No Operation<br>Display a value in 7-Segment<br>Halt the platform</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0001</strong></td>
            <td valign="top">SSDD_0001</td>
            <td valign="top">ADD D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Add 2 registers and update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0010</strong></td>
            <td valign="top">SSDD_0010</td>
            <td valign="top">SUB D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Subtract source from dest. & update to dest.</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRTT_0011</strong></td>
            <td valign="top">RR10_0011<br>RR11_0011</td>
            <td valign="top">INC R<br>DEC R</td>
            <td valign="top">1 Byte<br>1 Byte</td>
            <td valign="top">Increment register<br>Decrement register</td>
        </tr>
        <tr>
            <td valign="top"><strong>RRTT_0100</strong></td>
            <td valign="top">RR00_0100<br>RR01_0100<br>RR10_0100</td>
            <td valign="top">LDI R VV<br>LDM R AA<br>SAV R AA</td>
            <td valign="top">2 Byte<br>2 Byte<br>2 Byte</td>
            <td valign="top">Load immediate<br>Load from memory<br>Save to memory</td>
        </tr>
        <tr>
            <td valign="top"><strong>00TT_0101</strong></td>
            <td valign="top">0000_0101<br>0001_0101<br>0010_0101<br>0011_0101</td>
            <td valign="top">JMP AA<br>JMZ AA<br>JNZ AA<br>JMC AA</td>
            <td valign="top">3 Byte<br>3 Byte<br>3 Byte<br>3 Byte</td>
            <td valign="top">Jump to address<br>Jump to address if Zero flag set<br>Jump to address if Zero flag NOT set<br>Jump to address if Carry flag set</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0110</strong></td>
            <td valign="top">SSDD_0110</td>
            <td valign="top">MOV D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Move from source to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_0111</strong></td>
            <td valign="top">SSDD_0111</td>
            <td valign="top">AND D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical AND operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_1000</strong></td>
            <td valign="top">SSDD_1000</td>
            <td valign="top">OR D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical OR operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_1001</strong></td>
            <td valign="top">SSDD_1001</td>
            <td valign="top">XOR D S</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Logical XOR operation; update to destination</td>
        </tr>
        <tr>
            <td valign="top"><strong>RR00_1010</strong></td>
            <td valign="top">RR00_1010</td>
            <td valign="top">NOT R</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Bitwise NOT operation</td>
        </tr>
        <tr>
            <td valign="top"><strong>SSDD_1011</strong></td>
            <td valign="top">SSDD_1011</td>
            <td valign="top">CMP R R</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Compare two register values; update the flag</td>
        </tr>
        <tr>
            <td valign="top"><strong>RR00_1100</strong></td>
            <td valign="top">RR00_1100</td>
            <td valign="top">CMI R VV</td>
            <td valign="top">2 Byte</td>
            <td valign="top">Compare register with a immediate values</td>
        </tr>
        <tr>
            <td valign="top"><strong>1111_1111</strong></td>
            <td valign="top">1111_1111</td>
            <td valign="top">RST</td>
            <td valign="top">1 Byte</td>
            <td valign="top">Reset it self</td>
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

### ✅ Instruction: ADD
This `ADD` instruction is used to add two numbers and save the output in the destination register.

#### `Ins. Format: ADD D S`
#### `Bin. Format: SSDD_0001`

| Instruction  | Binary Value |
| :---         |    :---:     |
| ADD A B      | 0001_0001    |
| ADD A C      | 0010_0001    |
| ADD A D      | 0011_0001    |
| ADD B A      | 0100_0001    |
| ADD B C      | 0110_0001    |
| ADD B D      | 0111_0001    |
| ADD C A      | 1000_0001    |
| ADD C B      | 1001_0001    |
| ADD C D      | 1011_0001    |
| ADD D A      | 1100_0001    |
| ADD D B      | 1101_0001    |
| ADD D C      | 1110_0001    |

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

### ✅ Instruction: INC
This `INC` instruction is used to increase the register value by 1.

#### `Ins. Format: INC R`
#### `Bin. Format: RR10_0011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| INC A        | 0010_0011    |
| INC B        | 0110_0011    |
| INC C        | 1010_0011    |
| INC D        | 1110_0011    |

---------------

### ✅ Instruction: DEC
This `DEC` instruction is used to decrease the register value by 1.

#### `Ins. Format: DEC R`
#### `Bin. Format: RR11_0011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| DEC A        | 0011_0011    |
| DEC B        | 0111_0011    |
| DEC C        | 1011_0011    |
| DEC D        | 1111_0011    |

---------------

### ✅ Instruction: LDI
This `LDI` instruction is used to load an 8-bit value immediately into a register

#### `Ins. Format: LDI R VV`
#### `Bin. Format: RR00_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDI A 0xXX   | 0000_0100 xxxx_xxxx |
| LDI B 0xXX   | 0100_0100 xxxx_xxxx |
| LDI C 0xXX   | 1000_0100 xxxx_xxxx |
| LDI D 0xXX   | 1100_0100 xxxx_xxxx |

---------------

### ✅ Instruction: LDM
This `LDM` instruction is used to load an 8-bit value into a register from memory

#### `Ins. Format: LDM R AA`
#### `Bin. Format: RR01_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDM A 0xXX   | 0001_0100 xxxx_xxxx |
| LDM B 0xXX   | 0101_0100 xxxx_xxxx |
| LDM C 0xXX   | 1001_0100 xxxx_xxxx |
| LDM D 0xXX   | 1101_0100 xxxx_xxxx |

---------------

### ✅ Instruction: SAV
This `SAV` instruction is used to save a value from the register to memory

#### `Ins. Format: SAV R AA`
#### `Bin. Format: RR10_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| SAV A 0xXX   | 0010_0100 xxxx_xxxx |
| SAV B 0xXX   | 0110_0100 xxxx_xxxx |
| SAV C 0xXX   | 1010_0100 xxxx_xxxx |
| SAV D 0xXX   | 1110_0100 xxxx_xxxx |

---------------

### ✅ Instruction: JMP
This `JMP` instruction is used to jump to a specific address

#### `Ins. Format: JMP AA`
#### `Bin. Format: 0000_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMP 0xXX     | 0000_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JMZ
This `JMZ` instruction is used to jump to a specific address when the `Zero` flag is set

#### `Ins. Format: JMZ AA`
#### `Bin. Format: 0001_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMZ 0xXX     | 0001_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JNZ
This `JNZ` instruction is used to jump to a specific address when the `Zero` flag is not set

#### `Ins. Format: JNZ AA`
#### `Bin. Format: 0010_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JNZ 0xXX     | 0010_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JMC
This `JMC` instruction is used to jump to a specific address when the `Carry` flag is set

#### `Ins. Format: JMC AA`
#### `Bin. Format: 0011_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMC 0xXX     | 0011_0101 xxxx_xxxx |

---------------

### ✅ Instruction: MOV
This `MOV` instruction is used to move a value from one register to another

#### `Ins. Format: MOV D S`
#### `Bin. Format: SSDD_0110`

| Instruction  | Binary Value |
| :---         |    :---:     |
| MOV A B      | 0001_0110    |
| MOV A C      | 0010_0110    |
| MOV A D      | 0011_0110    |
| MOV B A      | 0100_0110    |
| MOV B C      | 0110_0110    |
| MOV B D      | 0111_0110    |
| MOV C A      | 1000_0110    |
| MOV C B      | 1001_0110    |
| MOV C D      | 1011_0110    |
| MOV D A      | 1100_0110    |
| MOV D B      | 1101_0110    |
| MOV D C      | 1110_0110    |

---------------

### ✅ Instruction: AND
This `AND` instruction is used to do a bitwise AND operation and keep the output in the destination register

#### `Ins. Format: AND D S`
#### `Bin. Format: SSDD_0111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| AND A B      | 0001_0111    |
| AND A C      | 0010_0111    |
| AND A D      | 0011_0111    |
| AND B A      | 0100_0111    |
| AND B C      | 0110_0111    |
| AND B D      | 0111_0111    |
| AND C A      | 1000_0111    |
| AND C B      | 1001_0111    |
| AND C D      | 1011_0111    |
| AND D A      | 1100_0111    |
| AND D B      | 1101_0111    |
| AND D C      | 1110_0111    |

---------------

### ✅ Instruction: OR
This `OR` instruction is used to do a bitwise OR operation and keep the output in the destination register

#### `Ins. Format: OR D S`
#### `Bin. Format: SSDD_1000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OR A B       | 0001_1000    |
| OR A C       | 0010_1000    |
| OR A D       | 0011_1000    |
| OR B A       | 0100_1000    |
| OR B C       | 0110_1000    |
| OR B D       | 0111_1000    |
| OR C A       | 1000_1000    |
| OR C B       | 1001_1000    |
| OR C D       | 1011_1000    |
| OR D A       | 1100_1000    |
| OR D B       | 1101_1000    |
| OR D C       | 1110_1000    |

---------------

### ✅ Instruction: XOR
This `XOR` instruction is used to do a bitwise XOR operation and keep the output in the destination register

#### `Ins. Format: XOR D S`
#### `Bin. Format: SSDD_1001`

| Instruction  | Binary Value |
| :---         |    :---:     |
| XOR A B      | 0001_1001    |
| XOR A C      | 0010_1001    |
| XOR A D      | 0011_1001    |
| XOR B A      | 0100_1001    |
| XOR B C      | 0110_1001    |
| XOR B D      | 0111_1001    |
| XOR C A      | 1000_1001    |
| XOR C B      | 1001_1001    |
| XOR C D      | 1011_1001    |
| XOR D A      | 1100_1001    |
| XOR D B      | 1101_1001    |
| XOR D C      | 1110_1001    |

---------------

### ✅ Instruction: NOT
This `NOT` instruction is used to do a bitwise NOT operation and keep the output in the same register

#### `Ins. Format: NOT R`
#### `Bin. Format: RR00_1010`

| Instruction  | Binary Value |
| :---         |    :---:     |
| NOT A        | 0000_1010    |
| NOT B        | 0100_1010    |
| NOT C        | 1000_1010    |
| NOT D        | 1100_1010    |

---------------

### ✅ Instruction: CMP
This `CMP` instruction is used to do a comparison and set/reset the `Zero` flag

#### `Ins. Format: CMP R R`
#### `Bin. Format: SSDD_1011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| CMP A B      | 0001_1011    |
| CMP A C      | 0010_1011    |
| CMP A D      | 0011_1011    |
| CMP B A      | 0100_1011    |
| CMP B C      | 0110_1011    |
| CMP B D      | 0111_1011    |
| CMP C A      | 1000_1011    |
| CMP C B      | 1001_1011    |
| CMP C D      | 1011_1011    |
| CMP D A      | 1100_1011    |
| CMP D B      | 1101_1011    |
| CMP D C      | 1110_1011    |

---------------

### ✅ Instruction: CMI
This `CMI` instruction is used to do a comparison and set/reset the `Zero` flag

#### `Ins. Format: CMI R VV`
#### `Bin. Format: RR00_1100`

| Instruction  |     Binary Value      |
| :---         |        :---:          |
| CMI A 0xXX   | 0000_1100 xxxx_xxxx   |
| CMI B 0xXX   | 0100_1100 xxxx_xxxx   |
| CMI C 0xXX   | 1000_1100 xxxx_xxxx   |
| CMI D 0xXX   | 1100_1100 xxxx_xxxx   |


---------------

### ✅ Instruction: OUT
This `OUT` instruction is used to show the value of register A in the 7-seg display

#### `Ins. Format: OUT`
#### `Bin. Format: 0001_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OUT          | 0001_0000    |

---------------

### ✅ Instruction: HLT
This `HLT` instruction is used to halt the system till reset

#### `Ins. Format: HLT`
#### `Bin. Format: 0010_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| HLT          | 0010_0000    |

---------------

### ✅ Instruction: RST
This `RST` instruction is used to reset the computer

#### `Ins. Format: RST`
#### `Bin. Format: 1111_1111`

| Instruction  | Binary Value |
| :---         |    :---:     |
| RST          | 1111_1111    |