# Signed Mode Default - Implementation Summary

## ✅ Changes Made to Match Assembler Behavior

### **Assembler Analysis**
The assembler (`Compiler/Assembler.py`) has:
- **Default: Signed mode** (treats numbers as signed by default)
- **Flag: `-u` or `--unsigned`** to switch to unsigned mode
- **Two's complement handling** for negative values in signed mode

### **Emulator Updates**

#### **1. Command Line Interface**
**Before:**
```bash
python main.py program.bin --signed    # Explicit signed mode
python main.py program.bin --unsigned  # Explicit unsigned mode  
# Default was unsigned
```

**After (matches assembler):**
```bash
python main.py program.bin             # Signed mode (default)
python main.py program.bin -u          # Unsigned mode (explicit)
python main.py program.bin --unsigned  # Unsigned mode (explicit)
```

#### **2. Default Behavior Changes**
- **CPU**: `self.signed_mode = True` (was `False`)
- **7-Segment Display**: Default to "Signed" mode (was "Unsigned")
- **Main.py**: `initial_signed_mode = not args.unsigned` (was complex logic)

#### **3. Help Text Updates**
```bash
usage: main.py [-h] [--no-gui] [--debug] [-u] [program]

options:
  -h, --help      show this help message and exit
  --no-gui        Run without GUI (command line only)  
  --debug         Enable debug output
  -u, --unsigned  Start in unsigned mode (0 to 255)

Note: Signed mode (-128 to +127) is the default.
```

### **4. Documentation Updates**
- **README.md**: Updated usage examples and defaults
- **DISPLAY_IMPLEMENTATION.md**: Updated to reflect signed-first approach
- **Docstrings**: Updated to show signed as default

## 🧪 Verification Test

### **Test Program with Negative Values**
```assembly
LDI A -1     ; Assembler compiles as 0xFF
LDI A -10    ; Assembler compiles as 0xF6  
LDI A -56    ; Assembler compiles as 0xC8
LDI A -128   ; Assembler compiles as 0x80
```

### **Assembler Output** (signed mode default):
- `-1` → `0xFF` (255 in two's complement)
- `-10` → `0xF6` (246 in two's complement)
- `-56` → `0xC8` (200 in two's complement)  
- `-128` → `0x80` (128 in two's complement)

### **Emulator Display** (signed mode default):
- `0xFF` displays as **-1**
- `0xF6` displays as **-10**
- `0xC8` displays as **-56**
- `0x80` displays as **-128**

## 🔄 Consistency Achieved

Now both assembler and emulator:
1. **Default to signed mode** (-128 to +127)
2. **Use `-u/--unsigned` flag** for unsigned mode (0-255)
3. **Handle two's complement correctly** for negative values
4. **Match hardware jumper behavior** (signed default)

## 📝 Usage Examples

### **Complete Workflow - Signed (Default)**
```bash
# Compile in signed mode (default)
python Compiler/Assembler.py program.s -o program.bin

# Run in emulator signed mode (default)  
python Emulator/main.py program.bin
```

### **Complete Workflow - Unsigned (Explicit)**
```bash
# Compile in unsigned mode
python Compiler/Assembler.py program.s -o program.bin --unsigned

# Run in emulator unsigned mode
python Emulator/main.py program.bin --unsigned
```

## 🎯 Benefits

1. **Consistent behavior** between assembler and emulator
2. **Matches hardware design** (signed default with jumper override)
3. **Intuitive workflow** (same flags for both tools)
4. **Educational clarity** (shows proper two's complement handling)
5. **Professional consistency** (tools work together seamlessly)

The emulator now perfectly matches the assembler's behavior and provides a consistent development experience! 🎉