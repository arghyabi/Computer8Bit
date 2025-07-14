# Signal Informations
Our 8-bit computer has 30 control signals. All these signals are controlled by the Control Unit with the help of microcode.


## General Purpose Register Signals
* `rAI`: The rAI signal is used for Register A Input. When this signal is high, the value on the bus is copied into the A register.

* `rAO`: The rAO signal is used for Register A Output. When this signal is high, the value in the A register is copied onto the bus.

* `rBI`: The rBI signal is used for Register B Input. When this signal is high, the value on the bus is copied into the B register.

* `rBO`: The rBO signal is used for Register B Output. When this signal is high, the value in the B register is copied onto the bus.

* `rCI`: The rCI signal is used for Register C Input. When this signal is high, the value on the bus is copied into the C register.

* `rCO`: The rCO signal is used for Register C Output. When this signal is high, the value in the C register is copied onto the bus.

* `rDI`: The rDI signal is used for Register D Input. When this signal is high, the value on the bus is copied into the D register.

* `rDO`: The rDO signal is used for Register D Output. When this signal is high, the value in the D register is copied onto the bus.

## ALU Side Signals
* `T1I`: The T1I signal is used for Temp-Register 1 Input. When this signal is high, the value on the bus is copied into Temp-Register 1.

* `T2I`: The T2I signal is used for Temp-Register 2 Input. When this signal is high, the value on the bus is copied into Temp-Register 2.

* `AdSu`: The AdSu signal is used to select the operation between addition and subtraction in the Adder/Subtractor module.

* `Cin`: The Cin signal is a multipurpose signal. It is used to provide a carry bit to the Adder/Subtractor module and also helps execute the `INC` and `DEC` instructions.

* `AdSuO`: The AdSuO signal is used to copy the result of the addition or subtraction operation onto the bus.

* `AndO`: The AndO signal is used to copy the logical AND result of Temp-Register 1 and Temp-Register 2 onto the bus.

* `OrO`: The OrO signal is used to copy the logical OR result of Temp-Register 1 and Temp-Register 2 onto the bus.

* `XorO`: The XorO signal is used to copy the logical XOR result of Temp-Register 1 and Temp-Register 2 onto the bus.

* `NtO`: The NtO signal is used to copy the logical NOT result of Temp-Register 1 onto the bus.

* `FlgU`: The FlgU signal updates the flag register with the values from the Comparator and Adder/Subtractor modules.

## 7-Seg Control Signal
* `Seg7E`: The Seg7E signal is used to display the value of Register A on the 7-segment display in decimal format.

## Memory Related Signals
* `PCC`: The PCC signal enables the Program Counter to count. If PCC is high, the counter increments on each clock cycle.

* `PCI`: The PCI signal (Program Counter Register Input) is used to load a specific value into the Program Counter Register.
This signal is typically used for executing branch instructions.
The value will not loaded in the counter until the PCL is high.

* `PCL`: The PCL signal is used to load the value from program counter register to the program counter.

* `RomO`: The RomO signal loads the current instruction from ROM onto the bus.

* `MdI`: The MdI signal stands for Memory Decoder Input. It is used to activate the memory decoder when accessing the RAM module.

* `MeI`: The MeI (Memory Input) signal is used to copy the value from the bus into a specific memory location.

* `MeO`: The MeO (Memory Output) signal is used to copy the value from memory onto the bus.

## Control Unit Signals
* `IRI`: The IRI (Instruction Register Input) signal is used to load the instruction from the Program ROM into the Instruction Register.

* `SqR`: The SqR (Sequencer Reset) signal is used to reset the Sequencer, causing it to restart its count from 0.

## flag Signals
* `Carry`: The Carry signal is used to track the generation of a carry during addition or subtraction operations.

* `Zero`: The Zero flag signal indicates the output of the comparator—typically showing whether the result is zero.
