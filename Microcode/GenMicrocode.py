import logging
import os
import shutil
from dataclasses import dataclass
from hashlib import md5
from typing import Dict, Optional

import NormalizeInstructions
import GenerateAutogenInstructions
import CompileAutogenInstructions

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"

MICROCODE_CHIP_NAMES = [
    CompileAutogenInstructions.UCODE_0,
    CompileAutogenInstructions.UCODE_1,
    CompileAutogenInstructions.UCODE_2,
]


@dataclass
class MicrocodeBuildStatus:
    ChipName: str
    HasPreviousVersion: bool
    Changed: bool
    PreviousMd5: Optional[str]
    CurrentMd5: str


def CalculateMd5(data: bytes) -> str:
    return md5(data).hexdigest()


def LoadPreviousMicrocodeSnapshots() -> Dict[str, bytes]:
    previousSnapshots: Dict[str, bytes] = {}
    outDir = os.path.join(os.path.dirname(__file__), "out")
    for chipName in MICROCODE_CHIP_NAMES:
        filePath = os.path.join(outDir, f"{chipName}.bin")
        if not os.path.exists(filePath):
            continue
        with open(filePath, "rb") as filePointer:
            previousSnapshots[chipName] = filePointer.read()
    return previousSnapshots


def BuildMicrocodeStatus(chipName: str, data: bytes, previousSnapshots: Dict[str, bytes]) -> MicrocodeBuildStatus:
    previousData = previousSnapshots.get(chipName)
    currentMd5 = CalculateMd5(data)

    if previousData is None:
        return MicrocodeBuildStatus(
            ChipName=chipName,
            HasPreviousVersion=False,
            Changed=True,
            PreviousMd5=None,
            CurrentMd5=currentMd5,
        )

    previousMd5 = CalculateMd5(previousData)
    return MicrocodeBuildStatus(
        ChipName=chipName,
        HasPreviousVersion=True,
        Changed=previousData != data,
        PreviousMd5=previousMd5,
        CurrentMd5=currentMd5,
    )


def Colorize(text: str, color: str) -> str:
    if not os.isatty(1) or os.environ.get("TERM") == "dumb":
        return text
    return f"{color}{text}{ANSI_RESET}"


def LogMicrocodeStatus(statusList):
    LOGGER.info("")
    LOGGER.info(Colorize("Microcode change summary:", ANSI_BOLD + ANSI_CYAN))
    for status in statusList:
        chipLabel = Colorize(status.ChipName, ANSI_BOLD + ANSI_CYAN)
        if not status.HasPreviousVersion:
            LOGGER.info(
                f"  {chipLabel}: "
                f"{Colorize('no previous binary found', ANSI_YELLOW)} -> "
                f"{Colorize('flash required', ANSI_RED)} "
                f"(md5={status.CurrentMd5})"
            )
            continue

        if status.Changed:
            LOGGER.info(
                f"  {chipLabel}: {Colorize('changed', ANSI_YELLOW)} -> "
                f"{Colorize('flash required', ANSI_RED)} "
                f"(old={status.PreviousMd5}, new={status.CurrentMd5})"
            )
        else:
            LOGGER.info(
                f"  {chipLabel}: {Colorize('unchanged', ANSI_GREEN)} -> "
                f"{Colorize('flashing can be skipped', ANSI_GREEN)} "
                f"(md5={status.CurrentMd5})"
            )


def GenMicrocode(chipName, data):
    """Write one generated microcode image to its chip-specific binary file."""
    with open(os.path.join("out", f"{chipName}.bin"), "wb") as filePointer:
        filePointer.write(bytes(data))


def Main():
    """Run the full microcode generation pipeline from instruction sources to ROM images."""
    previousSnapshots = LoadPreviousMicrocodeSnapshots()

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
    buildStatuses = []
    for chipName, eachChipMicrocode in generationResult.MicrocodeByChip.items():
        LOGGER.info(f"Creating Microcode for Chip: {chipName}")
        if generationResult.LastMicroInstructionMatrix:
            chipData = bytes(eachChipMicrocode)
            GenMicrocode(chipName, chipData)
            buildStatuses.append(BuildMicrocodeStatus(chipName, chipData, previousSnapshots))
        else:
            LOGGER.warning("Microcode index is null!!")

    LogMicrocodeStatus(buildStatuses)
    LOGGER.info("Microcode generation completed successfully.")


if __name__ == "__main__":
    Main()
