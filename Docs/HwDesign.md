# Component blocks

* [`General Purpose Registers`](Registers.md)
* [`Program Counter`](ProgramCounter.md)


# BUS pin configuration

| Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
|  :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
|    80    |     1    |  [Flg](SignalInfo.md#signal-flg)     | \| |  BUS0                                |    80    |     1    |
|    79    |     2    |   -                                  | \| |  BUS1                                |    79    |     2    |
|    78    |     3    |   -                                  | \| |  BUS2                                |    78    |     3    |
|    77    |     4    |   -                                  | \| |  BUS3                                |    77    |     4    |
|    76    |     5    |   -                                  | \| |  BUS4                                |    76    |     5    |
|    75    |     6    |   -                                  | \| |  BUS5                                |    75    |     6    |
|    74    |     7    |   -                                  | \| |  BUS6                                |    74    |     7    |
|    73    |     8    |   -                                  | \| |  BUS7                                |    73    |     8    |


| Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
|  :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
|    72    |     9    |  [rAI](SignalInfo.md#signal-rai)     | \| |  [IRI](SignalInfo.md#signal-iri)     |    72    |     9    |
|    71    |    10    |  [rBI](SignalInfo.md#signal-rbi)     | \| |  [T1I](SignalInfo.md#signal-t1i)     |    71    |    10    |
|    70    |    11    |  [rCI](SignalInfo.md#signal-rci)     | \| |  [T2I](SignalInfo.md#signal-t2i)     |    70    |    11    |
|    69    |    12    |  [rDI](SignalInfo.md#signal-rdi)     | \| |  [Seg7E](SignalInfo.md#signal-seg7e) |    69    |    12    |
|    68    |    13    |  [PCLI](SignalInfo.md#signal-pcli)   | \| |  [SpI](SignalInfo.md#signal-spi)     |    68    |    13    |
|    67    |    14    |  [PCHI](SignalInfo.md#signal-pchi)   | \| |   -                                  |    67    |    14    |
|    66    |    15    |  [MdI](SignalInfo.md#signal-mdi)     | \| |   -                                  |    66    |    15    |
|    65    |    16    |  [MeI](SignalInfo.md#signal-mei)     | \| |   -                                  |    65    |    16    |


 |Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
 | :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
 |   64    |    17    |  [PCL](SignalInfo.md#signal-pcl)     | \| |  [FlSe0](SignalInfo.md#signal-flse0) |    64    |    17    |
 |   63    |    18    |  [PCC](SignalInfo.md#signal-pcc)     | \| |  [FlSe1](SignalInfo.md#signal-flse1) |    63    |    18    |
 |   62    |    19    |  [AdSu](SignalInfo.md#signal-adsu)   | \| |  [FlSe2](SignalInfo.md#signal-flse2) |    62    |    19    |
 |   61    |    20    |  [Cin](SignalInfo.md#signal-cin)     | \| |   -                                  |    61    |    20    |
 |   60    |    21    |  [SpC](SignalInfo.md#signal-spc)     | \| |   -                                  |    60    |    21    |
 |   59    |    22    |  [SpUd](SignalInfo.md#signal-spud)   | \| |   -                                  |    59    |    22    |
 |   58    |    23    |  [HLT](SignalInfo.md#signal-hlt)     | \| |   -                                  |    58    |    23    |
 |   57    |    24    |  [Sgn](SignalInfo.md#signal-sgn)    | \| |   -                                  |    57    |    24    |


| Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
|  :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
|    56    |    25    |  [rAO](SignalInfo.md#signal-rao)     | \| |  [OrO](SignalInfo.md#signal-oro)     |    56    |    25    |
|    55    |    26    |  [rBO](SignalInfo.md#signal-rbo)     | \| |  [AndO](SignalInfo.md#signal-ando)   |    55    |    26    |
|    54    |    27    |  [rCO](SignalInfo.md#signal-rco)     | \| |  [XorO](SignalInfo.md#signal-xoro)   |    54    |    27    |
|    53    |    28    |  [rDO](SignalInfo.md#signal-rdo)     | \| |  [FlgU](SignalInfo.md#signal-flgu)   |    53    |    28    |
|    52    |    29    |  [RomO](SignalInfo.md#signal-romo)   | \| |  [PCO](SignalInfo.md#signal-pco)     |    52    |    29    |
|    51    |    30    |  [SpO](SignalInfo.md#signal-spo)     | \| |  [SqR](SignalInfo.md#signal-sqr)     |    51    |    30    |
|    50    |    31    |  [MeO](SignalInfo.md#signal-meo)     | \| |   -                                  |    50    |    31    |
|    49    |    32    |  [AdSuO](SignalInfo.md#signal-adsuo) | \| |   -                                  |    49    |    32    |


| Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
|  :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
|    48    |    33    |   -                                  | \| |   -                                  |    48    |    33    |
|    47    |    34    |   -                                  | \| |   -                                  |    47    |    34    |
|    46    |    35    |   -                                  | \| |   -                                  |    46    |    35    |
|    45    |    36    |   -                                  | \| |   -                                  |    45    |    36    |
|    44    |    37    |   -                                  | \| |   -                                  |    44    |    37    |
|    43    |    38    |   -                                  | \| |   -                                  |    43    |    38    |
|    42    |    39    |   -                                  | \| |   -                                  |    42    |    39    |
|    41    |    40    |   -                                  | \| |   -                                  |    41    |    40    |


| Card Pin | Base Pin |  Signal                              | \| |  Signal                              | Base Pin | Card Pin |
|  :----:  |  :----:  |  :--------------------------------:  |:--:|  :--------------------------------:  |  :----:  |  :----:  |
|    88    |    81    |  [CLK~](SignalInfo.md#signal-clk!)   | \| |  [CLK](SignalInfo.md#signal-clk)     |    88    |    81    |
|    87    |    82    |  VCC                                 | \| |  VCC                                 |    87    |    82    |
|    86    |    83    |   -                                  | \| |   -                                  |    86    |    83    |
|    85    |    84    |  GND                                 | \| |  GND                                 |    85    |    84    |
