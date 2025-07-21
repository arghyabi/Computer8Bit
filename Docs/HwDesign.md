# Component blocks

* [`General Purpose Registers`](Registers.md)
* [`Program Counter`](ProgramCounter.md)


# BUS pin configuration

| Pin Num | Signal |
|  :---:  |  :---: |
|    1    |  BUS7  |
|    2    |  BUS6  |
|    3    |  BUS5  |
|    4    |  BUS4  |
|    5    |  BUS3  |
|    6    |  BUS2  |
|    7    |  BUS1  |
|    8    |  BUS0  |

| Pin Num | Signal |
|  :---:  |  :---: |
|    9    |  rAI   |
|    10   |  rBI   |
|    11   |  rCI   |
|    12   |  rDI   |
|    13   |  rAO   |
|    14   |  rBO   |
|    15   |  rCO   |
|    16   |  rDO   |

| Pin Num | Signal |
|  :---:  |  :---: |
|    17   |  PCI   |
|    18   |  PCL   |
|    19   |  PCC   |
|    20   |  RomO  |
|    21   |  MdI   |
|    22   |  MeO   |
|    23   |  MeI   |
|    24   |  IRI   |

| Pin Num | Signal |
|  :---:  |  :---: |
|    25   |  SqR   |
|    26   |  AdSuO |
|    27   |  AdSu  |
|    28   |  Cin   |
|    29   |  CmpO  |
|    30   |  T1I   |
|    31   |  T2I   |
|    32   |  NtO   |

| Pin Num | Signal |
|  :---:  |  :---: |
|    33   | AndO   |
|    34   | OrO    |
|    35   | XorO   |
|    36   | Seg7E  |
|    37   | ZeroF **\***|
|    38   | Carry **\***|
|    39   |        |
|    40   | HLT    |

| Pin Num | Signal |
|  :---:  |  :---: |
|    41   |        |
|    42   |        |
|    43   |        |
|    44   |        |
|    45   |  CLK   |
|    46   |  CLK~  |
|    47   |  V+    |
|    48   |  GND   |


**\* Those are NOT output from Microcode IC; They are input to the uCode IC.**
