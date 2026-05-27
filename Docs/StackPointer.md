# Stack Pointer
Stack pointer is a 4 bit counter, and it able to point 16 differnt location in RAM.
it have 4 signal: SpC, SpUd, SpO and SpI.

By default the stack pointer should point to 0000.
Push operation will put some value on 0000 location and increase the pointer to 0001.
Pop operation will descrese the pointer and then fetch the data.
