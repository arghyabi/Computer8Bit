# GitHub Actions Workflows

This directory contains all CI/CD workflows for the Computer8Bit project, organized into logical folders.

## 📁 Structure

```
.github/
├── scripts/
│   └── validate_version.py          # Shared version validation logic
│
└── workflows/
    ├── ci.yaml                       # ⭐ SINGLE ENTRY POINT
    │
    ├── versionChecks/               # Version validation workflows
    │   ├── check-main-version.yaml
    │   ├── check-compiler-version.yaml
    │   ├── check-emulator-version.yaml
    │   ├── check-flasher-version.yaml
    │   ├── check-isa-version.yaml
    │   ├── check-inspector-version.yaml
    │   ├── check-sevensegment-version.yaml
    │   ├── check-document-version.yaml
    │   ├── validate-format.yaml
    │   └── version-summary.yaml
    │
    └── buildsChecks/                       # Build workflows
        ├── build-microcode.yaml
        ├── build-7segment-driver.yaml
        └── build-eeprom-firmware.yaml
```

## 🚀 Main Entry Point

### ci.yaml ⭐
**THE ONLY ENTRY POINT** - Main CI pipeline that orchestrates everything.

**Triggers:**
- Pull requests to `master` → Runs version checks + builds
- Pushes to `master` → Runs builds only

**What it does:**

#### On Pull Request:
1. **Setup & Analysis** - Analyzes which files changed
2. **Version Checks** (parallel):
   - Config.yaml modification check
   - MainVersion validation
   - All component version validations
   - Format validation
   - Version summary
3. **Builds** (parallel):
   - Microcode generation
   - 7-segment driver generation
   - EEPROM firmware build
4. **Status Checks** - Verifies all passed

#### On Push to Master:
1. **Builds** (parallel):
   - Microcode generation
   - 7-segment driver generation
   - EEPROM firmware build
2. **Status Check** - Verifies all passed

## 📋 Version Check Workflows

Located in `versionChecks/` folder. These are called by `ci.yaml`:

| Workflow                          | Purpose                                |
|-----------------------------------|----------------------------------------|
| `check-main-version.yaml`         | Validates MainVersion updates          |
| `check-compiler-version.yaml`     | Validates Compiler version             |
| `check-emulator-version.yaml`     | Validates Emulator version             |
| `check-flasher-version.yaml`      | Validates Flasher version              |
| `check-isa-version.yaml`          | Validates ISA version                  |
| `check-inspector-version.yaml`    | Validates Inspector version            |
| `check-sevensegment-version.yaml` | Validates 7Segment version             |
| `check-document-version.yaml`     | Validates Document version             |
| `validate-format.yaml`            | Validates version format (X.Y.Z.BUILD) |
| `version-summary.yaml`            | Displays version summary               |

### Version Validation Rules

All version checks enforce:
- ✅ Build number must always be updated
- ✅ At least one of major/minor/patch must change
- ✅ Major change → minor and patch reset to 0
- ✅ Minor change → patch resets to 0
- ✅ Patch change → no reset needed

## 🔨 Build Workflows

Located in `buildsChecks/` folder. These can be called by `ci.yaml` or triggered independently:

### build-microcode.yaml
Generates microcode for the CPU.

**Triggers:**
- Called by `ci.yaml`
- Push/PR to `master` with changes in `Microcode/**`

**Steps:**
1. Generate autogen instructions
2. Compile autogen instructions
3. Normalize instructions
4. Generate microcode

### build-7segment-driver.yaml
Generates 7-segment display driver.

**Triggers:**
- Called by `ci.yaml`
- Push/PR to `master` with changes in `Gen7segDriver/**`

**Steps:**
1. Run 7-segment driver generator
2. Verify output

### build-eeprom-firmware.yaml
Builds EEPROM flasher firmware for AVR.

**Triggers:**
- Called by `ci.yaml`
- Push/PR to `master` with changes in `EepromFlasher/Firmware/**`

**Steps:**
1. Install Arduino-mk toolchain
2. Build firmware
3. Upload hex file as artifact

## 🔧 Adding New Components

### Adding a New Version Check

1. Copy an existing `check-*-version.yaml` file in `versionChecks/`
2. Update the component name in 3 places:
   - Workflow name
   - Job name
   - Component parameter in validation script call
3. Add the workflow call in `ci.yaml` under version checks section

### Adding a New Build

1. Create `build-<name>.yaml` in `buildsChecks/` folder
2. Define build steps
3. Add workflow call in `ci.yaml` under builds section

## 📊 Workflow Execution Flow

### On Pull Request:
```
ci.yaml (SINGLE ENTRY POINT)
│
├── Setup & Analysis
│   └── Detect which files changed
│
├── Version Checks (parallel) ⚡
│   ├── Config.yaml check
│   ├── MainVersion
│   ├── Compiler
│   ├── Emulator
│   ├── Flasher
│   ├── ISA
│   ├── Inspector
│   ├── 7Segment
│   ├── Document
│   ├── Format validation
│   └── Summary
│
├── Builds (parallel) ⚡
│   ├── Microcode
│   ├── 7-Segment Driver
│   └── EEPROM Firmware
│
└── Status Checks
    ├── Version check status
    └── Build status
```

### On Push to Master:
```
ci.yaml (SINGLE ENTRY POINT)
│
├── Builds (parallel) ⚡
│   ├── Microcode
│   ├── 7-Segment Driver
│   └── EEPROM Firmware
│
└── Build Status Check
```

⚡ = Runs in parallel

## 🎯 Key Benefits

### Single Entry Point
- ✅ Only ONE workflow file to trigger: `ci.yaml`
- ✅ No confusion about which workflow to use
- ✅ Clear, centralized orchestration

### Organized Structure
- ✅ Version checks in `versionChecks/` folder
- ✅ Builds in `buildsChecks/` folder
- ✅ Easy to navigate and find specific workflows

### Modular & Maintainable
- ✅ Small, focused workflow files
- ✅ Shared validation logic in Python script
- ✅ Easy to update and extend

### Fast Execution
- ✅ All version checks run in parallel
- ✅ All builds run in parallel
- ✅ Efficient CI pipeline

## 📝 Notes

- All version checks use the shared `validate_version.py` script
- Build workflows can be triggered independently by file changes
- Artifacts are retained for 30 days
- Version checks only run on pull requests
- Builds run on both pull requests and pushes to master