"""
ALU Implementation
Handles arithmetic and logic operations for the 8-bit computer
"""

class ALU:
    """Arithmetic Logic Unit for 8-bit operations"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset ALU state"""
        self.flags = {
            'zero'    : False,   # Z flag - result is zero
            'carry'   : False,   # C flag - carry out from MSB
            'negative': False    # N flag - result is negative (bit 7 set)
        }
        self.temp1 = 0  # Temporary register 1
        self.temp2 = 0  # Temporary register 2

    def set_temps(self, val1, val2):
        """Set temporary registers for operations"""
        self.temp1 = val1 & 0xFF
        self.temp2 = val2 & 0xFF

    def add(self, a, b, carry_in=0):
        """
        8-bit addition with carry
        Returns: (result, carry_out)
        """
        result = (a + b + carry_in) & 0x1FF  # 9-bit result
        carry_out = (result > 0xFF)
        result = result & 0xFF

        self._updateFlags(result, carry_out)
        return result, carry_out

    def subtract(self, a, b, borrow_in=0):
        """
        8-bit subtraction with borrow (a - b)
        Returns: (result, borrow_out)
        """
        result = a - b - borrow_in
        borrow_out = (result < 0)

        if result < 0:
            result = (result + 256) & 0xFF  # Two's complement
        else:
            result = result & 0xFF

        self._updateFlags(result, borrow_out)
        return result, borrow_out

    def increment(self, value):
        """Increment 8-bit value"""
        result, carry = self.add(value, 1)
        return result

    def decrement(self, value):
        """Decrement 8-bit value"""
        result, borrow = self.subtract(value, 1)
        return result

    def logicalAnd(self, a, b):
        """Bitwise AND operation"""
        result = (a & b) & 0xFF
        self._updateFlags(result, False)
        return result

    def logicalOr(self, a, b):
        """Bitwise OR operation"""
        result = (a | b) & 0xFF
        self._updateFlags(result, False)
        return result

    def logicalXor(self, a, b):
        """Bitwise XOR operation"""
        result = (a ^ b) & 0xFF
        self._updateFlags(result, False)
        return result

    def logicalNot(self, value):
        """Bitwise NOT operation (complement)"""
        result = (~value) & 0xFF
        self._updateFlags(result, False)
        return result

    def compare(self, a, b):
        """
        Compare two values (a - b)
        Updates flags but doesn't return result
        """
        self.subtract(a, b)
        # Flags are updated by subtract operation

    def _updateFlags(self, result, carry):
        """Update ALU flags based on result"""
        self.flags['zero'] = (result == 0)
        self.flags['carry'] = carry
        self.flags['negative'] = (result & 0x80) != 0  # Bit 7 set

    def getFlags(self):
        """Get current flag state"""
        return self.flags.copy()

    def setFlag(self, flag_name, value):
        """Set specific flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = bool(value)

    def __str__(self):
        """String representation for debugging"""
        flags_str = ""
        flags_str += "Z" if self.flags['zero'] else "-"
        flags_str += "C" if self.flags['carry'] else "-"
        flags_str += "N" if self.flags['negative'] else "-"
        return f"ALU Flags: {flags_str}"