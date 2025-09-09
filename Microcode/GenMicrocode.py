import os
import shutil

import CreateAutogenIns
import ParseInstruction


def genMicrocode(chipNumer, data):
    with open(os.path.join("out", f"Microcode_{chipNumer}.bin"), "wb") as f:
        # write the binary data to a file
        f.write(bytes(data))


def main():
    if os.path.exists("out"):
        shutil.rmtree("out")

    autoGen = CreateAutogenIns.GenAutoInstructions()
    autoGen.autogenEachInstruction()

    insParser = ParseInstruction.ParseInstructions()
    insParser.parseEachInstruction()
    microcodeBank, microInsMatrix = insParser.generateAddressDataMap()
    for chipNumber in microcodeBank:
        print(f"Creating Microcode for Chip: {chipNumber}")
        eachChipMicrocode = microcodeBank[chipNumber]
        if microInsMatrix:
            genMicrocode(int(chipNumber), eachChipMicrocode)
        else:
            print("Microcode index is null!!")
    print("Done!")


if __name__ == "__main__":
    main()
