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
|    17   |  PCLI  |
|    18   |  PCHI  |
|    19   |  PCL   |
|    20   |  PCC   |
|    21   |  RomO  |
|    22   |  MdI   |
|    23   |  MeO   |
|    24   |  MeI   |

| Pin Num | Signal |
|  :---:  |  :---: |
|    25   |  IRI   |
|    26   |  SqR   |
|    27   |  AdSuO |
|    28   |  AdSu  |
|    29   |  Cin   |
|    30   |  CmpO  |
|    31   |  T1I   |
|    32   |  T2I   |

| Pin Num | Signal |
|  :---:  |  :---: |
|    33   |  NtO   |
|    34   |  AndO  |
|    35   |  OrO   |
|    36   |  XorO  |
|    37   |  Seg7E |
|    38   |        |
|    39   |        |
|    40   | HLT    |

| Pin Num | Signal |
|  :---:  |  :---: |
|    41   |  ZeroF **\***|
|    42   |  Carry **\***|
|    43   |        |
|    44   |        |
|    45   |  CLK   |
|    46   |  CLK~  |
|    47   |  V+    |
|    48   |  GND   |


**\* Those are NOT output from Microcode IC; They are input to the uCode IC.**
