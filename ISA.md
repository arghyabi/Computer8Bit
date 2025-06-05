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

```
--------------------------------------------------------------------------------------------------------
| Instruction Format | Binary Opcode | Instruction | Ins Size | Operation Description                  |
|--------------------|---------------|-------------|----------|----------------------------------------|
| 00TT_0000          | 0000_0000     | NOP         | 1 Byte   | No Operation                           |
| T: Type            | 0001_0000     | OUT         | 1 Byte   | Display a value in 7-Segment           |
|                    | 0010_0000     | HLT         | 1 Byte   | Halt the platform                      |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_0001          | SSDD_0001     | ADD S D     | 1 Byte   | Add 2 register and update to source    |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_0010          | SSDD_0010     | SUB S D     | 1 Byte   | Substract 2 regs. & update to source   |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| RRTT_0011          | RR10_0011     | INC R       | 1 Byte   | Increment register                     |
| R: Register        | RR11_0011     | DEC R       | 1 Byte   | Decrement register                     |
| T: Type            |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| RRTT_0100          | RR00_0100     | LDI R VV    | 2 Byte   | Load immediate                         |
| T: Type            | RR01_0100     | LDM R AA    | 2 Byte   | Load from memory                       |
| R: Register        | RR10_0100     | SAV R AA    | 2 Byte   | Save to memory                         |
|--------------------|---------------|-------------|----------|----------------------------------------|
| 00TT_0101          | 0000_0101     | JMP AA      | 2 Byte   | Jump to a specific address             |
| T: Type            | 0001_0101     | JMZ AA      | 2 Byte   | Jump to address when Zero flag set     |
|                    | 0010_0101     | JNZ AA      | 2 Byte   | Jump to address when Zero flag not set |
|                    | 0011_0101     | JMC AA      | 2 Byte   | Jump to address when Carry flag set    |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_0110          | SSDD_0110     | MOV S D     | 1 Byte   | Register-to-register move              |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_0111          | SSDD_0111     | AND S D     | 1 Byte   | Logical AND operation                  |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_1000          | SSDD_1000     | OR S D      | 1 Byte   | Logical OR operation                   |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_1001          | SSDD_1001     | XOR S D     | 1 Byte   | Logical XOR operation                  |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| RR00_1010          | RR00_1010     | NOT R       | 1 Byte   | Logical XOR operation                  |
| R: Register        |               |             |          |                                        |
|--------------------|---------------|-------------|----------|----------------------------------------|
| SSDD_1011          | SSDD_1011     | CMP S D     | 1 Byte   | Compare two register value             |
| S: Source Register |               |             |          |                                        |
| D: Dest. Register  |               |             |          |                                        |
--------------------------------------------------------------------------------------------------------
```


## Instructions set


### ✅ Instruction: NOP
This `NOP` instruction does nothing. It's kind of a blank instruction.

#### `Format: 0000_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| NOP          | 0000_0000    |

---------------

### ✅ Instruction: ADD
This `ADD` instruction is used to add two numbers and save the output in the source register.

#### `Format: SSDD_0001`

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
This `SUB` instruction is used to subtract one number from another and save the output in the source register.

#### `Format: SSDD_0010`

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

#### `Format: RR10_0011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| INC A        | 0010_0011    |
| INC B        | 0110_0011    |
| INC C        | 1010_0011    |
| INC D        | 1110_0011    |

---------------

### ✅ Instruction: DEC
This `DEC` instruction is used to decrease the register value by 1.

#### `Format: RR11_0011`

| Instruction  | Binary Value |
| :---         |    :---:     |
| DEC A        | 0011_0011    |
| DEC B        | 0111_0011    |
| DEC C        | 1011_0011    |
| DEC D        | 1111_0011    |

---------------

### ✅ Instruction: LDI
This `LDI` instruction is used to load an 8-bit value immediately into a register

#### `Format: RR00_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDI A 0xXX   | 0000_0100 xxxx_xxxx |
| LDI B 0xXX   | 0100_0100 xxxx_xxxx |
| LDI C 0xXX   | 1000_0100 xxxx_xxxx |
| LDI D 0xXX   | 1100_0100 xxxx_xxxx |

---------------

### ✅ Instruction: LDM
This `LDM` instruction is used to load an 8-bit value into a register from memory

#### `Format: RR01_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| LDM A 0xXX   | 0001_0100 xxxx_xxxx |
| LDM B 0xXX   | 0101_0100 xxxx_xxxx |
| LDM C 0xXX   | 1001_0100 xxxx_xxxx |
| LDM D 0xXX   | 1101_0100 xxxx_xxxx |

---------------

### ✅ Instruction: SAV
This `SAV` instruction is used to save a value from the register to memory

#### `Format: RR10_0100`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| SAV A 0xXX   | 0010_0100 xxxx_xxxx |
| SAV B 0xXX   | 0110_0100 xxxx_xxxx |
| SAV C 0xXX   | 1010_0100 xxxx_xxxx |
| SAV D 0xXX   | 1110_0100 xxxx_xxxx |

---------------

### ✅ Instruction: JMP
This `JMP` instruction is used to jump to a specific address

#### `Format: 0000_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMP 0xXX     | 0000_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JMZ
This `JMZ` instruction is used to jump to a specific address when the `Zero` flag is set

#### `Format: 0001_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMZ 0xXX     | 0001_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JNZ
This `JNZ` instruction is used to jump to a specific address when the `Zero` flag is not set

#### `Format: 0010_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JNZ 0xXX     | 0010_0101 xxxx_xxxx |

---------------

### ✅ Instruction: JMC
This `JMC` instruction is used to jump to a specific address when the `Carry` flag is set

#### `Format: 0011_0101`

| Instruction  |     Binary Value    |
| :---         |        :---:        |
| JMC 0xXX     | 0011_0101 xxxx_xxxx |

---------------

### ✅ Instruction: MOV
This `MOV` instruction is used to move a value from one register to another

#### `Format: SSDD_0110`

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
This `AND` instruction is used to do a bitwise AND operation and keep the output in the source register

#### `Format: SSDD_0111`

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
This `OR` instruction is used to do a bitwise OR operation and keep the output in the source register

#### `Format: SSDD_1000`

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
This `XOR` instruction is used to do a bitwise XOR operation and keep the output in the source register

#### `Format: SSDD_1001`

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
This `NOT` instruction is used to do a bitwise NOT operation and keep the output in the source register

#### `Format: RR00_1010`

| Instruction  | Binary Value |
| :---         |    :---:     |
| NOT A        | 0000_1010    |
| NOT B        | 0100_1010    |
| NOT C        | 1000_1010    |
| NOT D        | 1100_1010    |

---------------

### ✅ Instruction: CMP
This `CMP` instruction is used to do a comparison and set/reset the `Zero` flag

#### `Format: SSDD_1011`

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

### ✅ Instruction: OUT
This `OUT` instruction is used to show the value of register A in the 7-seg display

#### `Format: 0001_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| OUT          | 0001_0000    |

---------------

### ✅ Instruction: HLT
This `HLT` instruction is used to halt the system till reset

#### `Format: 0010_0000`

| Instruction  | Binary Value |
| :---         |    :---:     |
| HLT          | 0010_0000    |
