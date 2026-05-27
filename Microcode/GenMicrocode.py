import logging
import os
import shutil

import GenerateAutogenInstructions
import CompileAutogenInstructions

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)


def GenMicrocode(chipName, data):
    """Write one generated microcode image to its chip-specific binary file."""
    with open(os.path.join("out", f"{chipName}.bin"), "wb") as filePointer:
        filePointer.write(bytes(data))


def Main():
    """Run the full microcode generation pipeline from instruction sources to ROM images."""
    if os.path.exists("out"):
        shutil.rmtree("out")

    autoGen = GenerateAutogenInstructions.GenAutoInstructions()
    autoGen.AutogenEachInstruction()

    insParser = CompileAutogenInstructions.ParseInstructions()
    insParser.ParseEachInstruction()
    generationResult = insParser.GenerateAddressDataMap()
    for chipName, eachChipMicrocode in generationResult.MicrocodeByChip.items():
        LOGGER.info(f"Creating Microcode for Chip: {chipName}")
        if generationResult.LastMicroInstructionMatrix:
            GenMicrocode(chipName, eachChipMicrocode)
        else:
            LOGGER.warning("Microcode index is null!!")

    LOGGER.info("Microcode generation completed successfully.")


if __name__ == "__main__":
    Main()
