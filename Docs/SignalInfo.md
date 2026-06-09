# Signal Informations
Our 8-bit computer has 32 control signals. All these signals are controlled by the Control Unit with the help of
microcode.

## Clock Signal
* <a id="signal-clk"></a>`CLK`: The main clock signal of the system.
* <a id="signal-clk!"></a>`CLK~`: The inverted clock signal of the system.
* <a id="signal-htl"></a>`HLT`: Halt signal is basically disable the clock signal.

## General Purpose Register Signals
* <a id="signal-rai"></a>`rAI`: The rAI signal is used for Register A Input. When this signal is high, the value on the bus is copied into the
A register.

* <a id="signal-rao"></a>`rAO`: The rAO signal is used for Register A Output. When this signal is high, the value in the A register is copied
onto the bus.

* <a id="signal-rbi"></a>`rBI`: The rBI signal is used for Register B Input. When this signal is high, the value on the bus is copied into the
B register.

* <a id="signal-rbo"></a>`rBO`: The rBO signal is used for Register B Output. When this signal is high, the value in the B register is copied
onto the bus.

* <a id="signal-rci"></a>`rCI`: The rCI signal is used for Register C Input. When this signal is high, the value on the bus is copied into the
C register.

* <a id="signal-rco"></a>`rCO`: The rCO signal is used for Register C Output. When this signal is high, the value in the C register is copied
onto the bus.

* <a id="signal-rdi"></a>`rDI`: The rDI signal is used for Register D Input. When this signal is high, the value on the bus is copied into the
D register.

* <a id="signal-rdo"></a>`rDO`: The rDO signal is used for Register D Output. When this signal is high, the value in the D register is copied
onto the bus.

## ALU Side Signals
* <a id="signal-t1i"></a>`T1I`: The T1I signal is used for Temp-Register 1 Input. When this signal is high, the value on the bus is copied into
Temp-Register 1.

* <a id="signal-t2is0"></a>`T2IS0`: Shift-register control signal bit 0.

* <a id="signal-t2is1"></a>`T2IS1`: Shift-register control signal bit 1.

`T2IS0` and `T2IS1` control the shared shift-register path in the ALU section. This shift register is reused both as
the Temp-Register 2 data path and for shifting operations such as left-shift and right-shift. Together, these two
signals replace the older single `T2I` control signal with a more flexible 2-bit control scheme.

In handwritten instruction tables, the legacy `T2I` row is no longer used. The corresponding behavior is now expressed
through the `T2IS0` and `T2IS1` rows while preserving the physical microcode bit positions allocated on `uCode0`.

* <a id="signal-adsu"></a>`AdSu`: The AdSu signal is used to select the operation between addition and subtraction in the Adder/Subtractor
module.

* <a id="signal-cin"></a>`Cin`: The Cin signal is a multipurpose signal. It is used to provide a carry bit to the Adder/Subtractor module and
also helps execute the `INC` and `DEC` instructions.

* <a id="signal-adsuo"></a>`AdSuO`: The AdSuO signal is used to copy the result of the addition or subtraction operation onto the bus.

* <a id="signal-ando"></a>`AndO`: The AndO signal is used to copy the logical AND result of Temp-Register 1 and Temp-Register 2 onto the bus.

* <a id="signal-oro"></a>`OrO`: The OrO signal is used to copy the logical OR result of Temp-Register 1 and Temp-Register 2 onto the bus.

* <a id="signal-xoro"></a>`XorO`: The XorO signal is used to copy the logical XOR result of Temp-Register 1 and Temp-Register 2 onto the bus.

* <a id="signal-nto"></a>`NtO`: The NtO signal is used to copy the logical NOT result of Temp-Register 1 onto the bus.

* <a id="signal-flgu"></a>`FlgU`: The FlgU signal updates the flag register with the values from the Comparator and Adder/Subtractor modules.

## 7-Seg Control Signal
* <a id="signal-seg7e"></a>`Seg7E`: The Seg7E signal is used to display the value of Register A on the 7-segment display in decimal format.

## Memory Related Signals
* <a id="signal-pcli"></a>`PCLI`: The PCLI signal (Program Counter Register Low Input) is used to load the **lower 8 bits** of a 11-bit address
into the Program Counter Low Register. This signal is typically used for executing branch instructions. The value will
not loaded in the counter until the PCL is high.

* <a id="signal-pchi"></a>`PCHI`: The PCHI signal (Program Counter Register High Input) is used to load the **upper 3 bits** of a 11-bit into
the Program Counter High Register. This signal is typically used for executing branch instructions. The value will not
loaded in the counter until the PCL is high.

* <a id="signal-pcl"></a>`PCL`: The PCL signal is used to load the value from program counter register to the program counter.

* <a id="signal-pcc"></a>`PCC`: The PCC signal enables the Program Counter to count. If PCC is high, the counter increments on each clock cycle.

* <a id="signal-pco"></a>`PCO`: The PCO signal load the value from the PC register to the bus.

* <a id="signal-romo"></a>`RomO`: The RomO signal loads the current instruction from ROM onto the bus.

* <a id="signal-mdi"></a>`MdI`: The MdI signal stands for Memory Decoder Input. It is used to activate the memory decoder when accessing the
RAM module.

* <a id="signal-mei"></a>`MeI`: The MeI (Memory Input) signal is used to copy the value from the bus into a specific memory location.

* <a id="signal-meo"></a>`MeO`: The MeO (Memory Output) signal is used to copy the value from memory onto the bus.

## Control Unit Signals
* <a id="signal-iri"></a>`IRI`: The IRI (Instruction Register Input) signal is used to load the instruction from the Program ROM into the
Instruction Register.

* <a id="signal-sqr"></a>`SqR`: The SqR (Sequencer Reset) signal is used to reset the Sequencer, causing it to restart its count from 0.

## Stack Pointer Signals
* <a id="signal-spc"></a>`SpC`: Clear the Stack Pointer.
* <a id="signal-spud"></a>`SpUd`: Move the pointer up or down. 0 is for up and 1 is for down. Up is for push and down is for pop.
* <a id="signal-spo"></a>`SpO`: Bring the data to the bus from the ram address where Stack Pointer pointing.
* <a id="signal-spi"></a>`SpI`: Push the data to the ram in the SP address.


## Flag Select Signals
* <a id="signal-flse0"></a>`FlSe0`: Flag Select Signal 0
* <a id="signal-flse1"></a>`FlSe1`: Flag Select Signal 1
* <a id="signal-flse2"></a>`FlSe2`: Flag Select Signal 2; FlSe0, FlSe1, and FlSe2 combined point to a maximum of 8 flag bits.

## Flag Signal
* <a id="signal-flg"></a>`Flg`: This is the common output to the flag register. Based on the combination of FlSe0, FlSe1, and FlSe2, one flag 
will be selected and sent to the Flag signal.

## Sign Signals
* <a id="signal-sgn"></a>`Sgn`: This is the sign signal. It is used to indicate the sign of the result of an operation. 0 for positive and 1 for negative. Mainly, it is used for comparison and to show the output on a 7-segment display.

| FlSe2 | FlSe1 | FlSe0 | Flag | Meaning       | Description              |
| :---: | :---: | :---: | :----| :-------------| :------------------------|
|   0   |   0   |   0   | Z    | Zero Flag     | Final Output is Zero     |
|   0   |   0   |   1   | C    | Carry Flag    | Add/Sub have carryout    |
|   0   |   1   |   0   | N    | Negative Flag | BUS[7]                   |
|   0   |   1   |   1   | EQ   | Equal Compare | Temp1 and Temp2 Equal    |
|   1   |   0   |   0   | GT   | Greater Than  | Temp1 > Temp2            |
|   1   |   0   |   1   | LT   | Less Than     | Temp1 < Temp2            |
|   1   |   1   |   0   | RSV  | Reserved      | -                        |
|   1   |   1   |   1   | RSV  | Reserved      | -                        |
