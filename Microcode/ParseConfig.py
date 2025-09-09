import os
import yaml

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


if __name__ == "__main__":
    configPath = "MicroCodeConfig.yaml"
    try:
        config = parseConfig(configPath)
        print(config)
        print(getSignalIndex("PCHI", config))
        print(getAllInstructions(config))
        print(getAllVirtualPins(config))
        print(getAllSignalIndex("InputControl", config))
    except Exception as e:
        print(f"Error: {e}")
