class ALU:
    def __init__(self):
        self.reset()


    def reset(self):
        self.flags = {
            'zero'    : False,   # Z flag - result is zero
            'carry'   : False,   # C flag - carry out from MSB
            'negative': False    # N flag - result is negative (bit 7 set)
        }
        self.temp1 = 0  # Temporary register 1
        self.temp2 = 0  # Temporary register 2


    def setTemps(self, val1, val2):
        self.temp1 = val1 & 0xFF
        self.temp2 = val2 & 0xFF


    def add(self, a, b, carryIn = 0):
        result   = (a + b + carryIn) & 0x1FF  # 9-bit result
        carryOut = (result > 0xFF)
        result   = result & 0xFF

        self._updateFlags(result, carryOut)
        return result, carryOut


    def subtract(self, a, b, borrowIn = 0):
        result    = a - b - borrowIn
        borrowOut = (result < 0)

        if result < 0:
            result = (result + 256) & 0xFF  # Two's complement
        else:
            result = result & 0xFF

        self._updateFlags(result, borrowOut)
        return result, borrowOut


    def increment(self, value):
        result, carry = self.add(value, 1)
        return result


    def decrement(self, value):
        result, borrow = self.subtract(value, 1)
        return result


    def logicalAnd(self, a, b):
        result = (a & b) & 0xFF
        self._updateFlags(result, False)
        return result


    def logicalOr(self, a, b):
        result = (a | b) & 0xFF
        self._updateFlags(result, False)
        return result


    def logicalXor(self, a, b):
        result = (a ^ b) & 0xFF
        self._updateFlags(result, False)
        return result


    def logicalNot(self, value):
        result = (~value) & 0xFF
        self._updateFlags(result, False)
        return result


    def compare(self, a, b):
        self.subtract(a, b)
        # Flags are updated by subtract operation


    def _updateFlags(self, result, carry):
        self.flags['zero']     = (result == 0)
        self.flags['carry']    = carry
        self.flags['negative'] = (result & 0x80) != 0  # Bit 7 set


    def getFlags(self):
        return self.flags.copy()


    def setFlag(self, flagName, value):
        if flagName in self.flags:
            self.flags[flagName] = bool(value)


    def __str__(self):
        flagsStr = ""
        flagsStr += "Z" if self.flags['zero'] else "-"
        flagsStr += "C" if self.flags['carry'] else "-"
        flagsStr += "N" if self.flags['negative'] else "-"
        return f"ALU Flags: {flagsStr}"
