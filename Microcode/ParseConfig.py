import os
import yaml

MAX_CONTROL_SIGNALS = 16

def parseConfig(configPath):
    if not os.path.exists(configPath):
        raise FileNotFoundError(f"Pin Configuration file not found: {configPath}")

    with open(configPath, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")


def getSignalIndex(signalName, config):
    pinConfig = config.get("PinConfig", {})
    sections = ["InputControl", "OutputControl", "Extra"]

    returnVal = -1
    sectionType = None

    for section in sections:
        controls = pinConfig.get(section, {})
        for signal, index in controls.items():
            if signal == signalName:
                returnVal   = index
                sectionType = section
                break
    return returnVal, sectionType


def getAllSignalIndex(sectionName, config):
    pinConfig = config.get("PinConfig", {})
    controls = pinConfig.get(sectionName, {})

    signalIndexDict = {}
    for signal, index in controls.items():
        signalIndexDict[signal] = index
    return signalIndexDict


def getAllSignalList(config):
    pinConfig = config.get("PinConfig", {})
    InputSignals = pinConfig.get("InputControl", {})
    OutputSignals = pinConfig.get("OutputControl", {})

    signalList = []
    for signal, index in InputSignals.items():
        if signal == "RESRV":
            continue
        signalList.append(signal)
    for signal, index in OutputSignals.items():
        if signal == "RESRV":
            continue
        signalList.append(signal)
    return signalList


def getAllVirtualPins(config):
    virtualPinConfig = {}
    virtualPins = config.get("VirtualPins", {})
    for section, pins in virtualPins.items():
        virtualPinConfig[section] = []
        for pin, states in pins.items():
            virtualPinConfig[section].append(pin)
    return virtualPinConfig


def getAllInstructions(config):
    InsConfig = config.get("InsConfig", {})
    instructions = InsConfig.get("Instructions", [])
    return instructions


def getCharValue(val):
    if val > ord('Z'):
        val = val - 26
    return chr(val)


def genHardwarePinMap(config):
    def check40PinLimit(signalCount, file, pinA, pinB):
        if signalCount == 40:
            for _ in range(4):
                pinA += 1
                pinB += 1
                file.write(f"| -- |  --  | ----- |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
        return pinA, pinB

    pinConfig     = config.get("PinConfig", {})
    InputSignals  = pinConfig.get("InputControl", {})
    OutputSignals = pinConfig.get("OutputControl", {})
    ExtraSignals  = pinConfig.get("Extra", {})

    OutputHardwarePinMap = []
    InputHardwarePinMap  = []
    ExtraHardwarePinMap  = []

    for signal, index in OutputSignals.items():
        if signal == "RESRV":
            continue
        OutputHardwarePinMap.append(signal)

    for signal, index in ExtraSignals.items():
        if signal == "RESRV":
            continue
        ExtraHardwarePinMap.append(signal)

    for signal, index in InputSignals.items():
        if signal == "RESRV":
            continue
        InputHardwarePinMap.append(signal)

    os.makedirs("out", exist_ok=True)
    with open("out/OutputHardwarePinMap.txt", 'w') as file:
        serialNo = 1
        pinA     = 65
        pinB     = 66
        slotLeft = MAX_CONTROL_SIGNALS

        file.write("===========================================================\n")
        file.write("|  X | Type | Name  | Pin A | Pin B | Comment             |\n")
        file.write("===========================================================\n")
        for busLine in range(8):
            file.write(f"| {serialNo:>2} |  Bu  | BL{busLine:<3} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            serialNo += 1
            pinA     += 1
            pinB     += 1
        file.write("|----|------|-------|-------|-------|---------------------|\n")
        for signal in InputHardwarePinMap:
            file.write(f"| {serialNo:>2} |  In  | {signal:<5} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            serialNo += 1
            pinA     += 1
            pinB     += 1
            slotLeft -= 1
            if slotLeft <= 0:
                break
        file.write("|----|------|-------|-------|-------|---------------------|\n")
        extraSigDone = 0
        for index in range(slotLeft):
            file.write(f"| {serialNo:>2} |  Ex  | {ExtraHardwarePinMap[index]:<5} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            serialNo += 1
            pinA     += 1
            pinB     += 1
            extraSigDone += 1

        file.write("|----|------|-------|-------|-------|---------------------|\n")
        print(f"Used Extra Signals: {extraSigDone}")

        slotLeft = MAX_CONTROL_SIGNALS
        for signal in OutputHardwarePinMap:
            file.write(f"| {serialNo:>2} |  Ou  | {signal:<5} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            pinA, pinB = check40PinLimit(serialNo, file, pinA, pinB)
            serialNo += 1
            pinA     += 1
            pinB     += 1
            slotLeft -= 1
            if slotLeft <= 0:
                break

        file.write("|----|------|-------|-------|-------|---------------------|\n")
        ExtraHardwarePinMap = ExtraHardwarePinMap[extraSigDone:]
        extraSigDone = 0
        print("Serial No before Extra Signals:", serialNo)
        for index in range(slotLeft):
            file.write(f"| {serialNo:>2} |  Ex  | {ExtraHardwarePinMap[index]:<5} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            pinA, pinB = check40PinLimit(serialNo, file, pinA, pinB)
            serialNo += 1
            pinA     += 1
            pinB     += 1
            extraSigDone += 1

        file.write("|----|------|-------|-------|-------|---------------------|\n")
        ExtraHardwarePinMap = ExtraHardwarePinMap[extraSigDone:]
        for signal in ExtraHardwarePinMap:
            file.write(f"| {serialNo:>2} |  Ex  | {signal:<5} |  {getCharValue(pinA):>3}  |  {getCharValue(pinB):>3}  |                     |\n")
            pinA, pinB = check40PinLimit(serialNo, file, pinA, pinB)
            serialNo += 1
            pinA     += 1
            pinB     += 1


        file.write("===========================================================\n")



if __name__ == "__main__":
    configPath = "MicroCodeConfig.yaml"
    try:
        config = parseConfig(configPath)
        print(config)
        print(getSignalIndex("PCHI", config))
        print(getAllInstructions(config))
        print(getAllVirtualPins(config))
        print(getAllSignalIndex("InputControl", config))
        print(getAllSignalList(config))

        genHardwarePinMap(config)
    except Exception as e:
        print(f"Error: {e}")
