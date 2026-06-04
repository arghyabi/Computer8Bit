import logging
import os
import shutil

import NormalizeInstructions
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

    # Step 1: Normalize instruction files to match YAML configuration
    LOGGER.info("Step 1: Normalizing instruction files to match YAML configuration...")
    configPath = os.path.join(os.path.dirname(__file__), "MicroCodeConfig.yaml")
    normalizer = NormalizeInstructions.InstructionNormalizer(configPath)
    normalizer.NormalizeAllInstructions(overwriteSource=True)
    LOGGER.info("")

    # Step 2: Generate autogen instructions from normalized source files
    LOGGER.info("Step 2: Generating autogen instructions...")
    autoGen = GenerateAutogenInstructions.GenAutoInstructions()
    autoGen.AutogenEachInstruction()
    LOGGER.info("")

    # Step 3: Compile autogen instructions to microcode
    LOGGER.info("Step 3: Compiling microcode...")
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
