# 8-Bit Signed / Unsigned Comparator

## Overview

This comparator supports both **signed** and **unsigned** comparison of two 8-bit values.

The design is based on two cascaded **74LS85** magnitude comparators and a single **74LS157** multiplexer.

A control signal named `Sgn` selects whether the comparison is interpreted as signed or unsigned.

```text
Sgn = 0  -> Unsigned Comparison
Sgn = 1  -> Signed Comparison
```

The comparator produces three output flags:

```text
GT = A > B
LT = A < B
EQ = A = B
```

---

# Theory of Operation

The 74LS85 naturally performs an unsigned comparison.

For signed two's complement numbers:

* If both operands have the same sign, the unsigned comparison result is already correct.
* If the operands have different signs:

  * Positive is always greater than negative.
  * Negative is always less than positive.

This observation allows the entire signed comparison logic to be implemented with a single multiplexer.

---

# Comparator Outputs

The cascaded 74LS85 comparators generate:

```text
G  = A > B (unsigned)
L  = A < B (unsigned)
EQ = A = B
```

Additional signals:

```text
A7 = Sign bit of A
B7 = Sign bit of B
```

Generated elsewhere in the ALU:

```text
DIFF = A7 XOR B7
nA7  = NOT(A7)
```

---

# Select Logic

The multiplexer select signal is:

```text
SEL = Sgn AND DIFF
```

Where:

```text
DIFF = A7 XOR B7
```

Meaning:

```text
Sgn=0
    SEL=0
    Always perform unsigned comparison.

Sgn=1 and A7=B7
    SEL=0
    Use 74LS85 outputs.

Sgn=1 and A7!=B7
    SEL=1
    Use sign bits only.
```

---

# 74LS157 Connections

## Control Pins

| Pin | Connection                |
| --- | ------------------------- |
| 1   | SEL = Sgn AND (A7 XOR B7) |
| 15  | GND                       |
| 16  | +5V                       |
| 8   | GND                       |

---

## GT Channel

| Pin     | Connection |
| ------- | ---------- |
| 2 (I0A) | G          |
| 3 (I1A) | nA7        |
| 4 (ZA)  | GT         |

---

## LT Channel

| Pin     | Connection |
| ------- | ---------- |
| 5 (I0B) | L          |
| 6 (I1B) | A7         |
| 7 (ZB)  | LT         |

---

## Unused Channels

| Pin      | Connection |
| -------- | ---------- |
| 14 (I0C) | GND        |
| 13 (I1C) | GND        |
| 12 (ZC)  | NC         |
| 11 (I0D) | GND        |
| 10 (I1D) | GND        |
| 9 (ZD)   | NC         |

---

# EQ Flag

No special logic is required.

```text
EQ = 74LS85_EQ
```

Connect the equality output of the upper 74LS85 directly to the flag register.

---

# Final Truth Table

## Inputs

```text
A7 = Sign bit of A
B7 = Sign bit of B

G = Unsigned Greater-Than output from 74LS85
L = Unsigned Less-Than output from 74LS85
```

## Outputs

```text
GT = Greater Than Flag
LT = Less Than Flag
```

| A7 | B7 | G | L | GT | LT |
| -- | -- | - | - | -- | -- |
| 0  | 0  | 0 | 0 | 0  | 0  |
| 0  | 0  | 0 | 1 | 0  | 1  |
| 0  | 0  | 1 | 0 | 1  | 0  |
| 0  | 1  | X | X | 1  | 0  |
| 1  | 0  | X | X | 0  | 1  |
| 1  | 1  | 0 | 0 | 0  | 0  |
| 1  | 1  | 0 | 1 | 0  | 1  |
| 1  | 1  | 1 | 0 | 1  | 0  |

Where:

```text
X = Don't Care
```

because when sign bits differ, the comparator outputs are ignored.

---

# Functional Behavior

## Unsigned Mode

```text
Sgn = 0
```

Results:

```text
GT = G
LT = L
EQ = EQ
```

The circuit behaves exactly like a standard 8-bit unsigned comparator.

---

## Signed Mode

```text
Sgn = 1
```

### Same Sign

```text
A7 = B7
```

Results:

```text
GT = G
LT = L
EQ = EQ
```

The 74LS85 outputs are used directly.

### Different Signs

```text
A7 != B7
```

Results:

```text
GT = !A7
LT = A7
EQ = 0
```

Meaning:

```text
Positive > Negative
Negative < Positive
```

---

# IC Usage

## Comparator Section

```text
2 × 74LS85
1 × 74LS157
```

## Reused ALU Signals

The following signals are assumed to already exist elsewhere in the ALU:

```text
A7 XOR B7
NOT(A7)
```

Therefore no additional XOR or inverter ICs are required for the comparator block itself.

---

# Advantages

* Supports both signed and unsigned comparison.
* Only three flags are required:

  * GT
  * LT
  * EQ
* Single control signal (`Sgn`) selects comparison mode.
* Very small hardware footprint.
* Uses only one multiplexer beyond the standard 74LS85 comparator chain.
* Integrates cleanly into a TTL-based 8-bit CPU.
