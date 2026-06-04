# Reset Architecture

## Goal

Implement a safe hardware reset mechanism without electrical contention between:

* EEPROM control outputs
* External reset circuitry

---

# Existing Architecture

## Input Control Path

```text id="2s4q3m"
EEPROM
   ↓
74LS154
   ↓
74F640
   ↓
CPU Input Control Signals
```

---

# Important IC Behavior

## 74F640 Output Enable

| G    | Operation                     |
| ---- | ----------------------------- |
| LOW  | Outputs Enabled               |
| HIGH | Outputs High-Z (Disconnected) |

When `G = HIGH`, the EEPROM-generated control signals become electrically isolated.

---

# Proposed Reset Mechanism

## During Normal Execution

```text id="1j5c8n"
G = LOW
```

EEPROM controls all input control signals normally.

---

# During RESET

## Step 1

Disable the `74F640` outputs:

```text id="d4m1rq"
G = HIGH
```

This disconnects the EEPROM control path.

---

## Step 2

Drive required reset signals using external reset buffer.

Example:

```text id="93s1ow"
RESET BUFFER
   ├── rAI
   ├── rBI
   ├── rCI
   ├── rDI
   ├── T1I
   ├── PCL
   └── other required reset signals
```

---

# Sequencer Reset

The sequencer uses:

* `SN74LS191`

The signal:

```text id="w63x0m"
sqncr_rst
```

is connected to:

```text id="g7u6rk"
PL#
```

of the LS191.

Since the parallel inputs are hardwired to:

```text id="8l7kz0"
0000
```

asserting `sqncr_rst` loads the sequencer to state:

```text id="kw3v8g"
0000
```

---

# Recommended Reset Flow

```text id="8j29sl"
RESET Button
    ├── Disable 74F640 outputs (G = HIGH)
    ├── Reset Sequencer
    ├── Clear HALT state
    └── Drive required reset control signals
```

---

# Notes

* Reset buffer must actively drive the signals.
* Floating TTL inputs must be avoided.
* EEPROM outputs must never directly fight external reset drivers.

---

# Future Scope

Possible future additions:

* Power-On Reset
* Watchdog Timer
* Front Panel Reset
* Single Step Execution
* Debug Override Logic

---
