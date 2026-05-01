# Source Tree Analysis

## Annotated Directory Structure

```
local-text2image/
│
├── src/                          # Core application source code
│   ├── cli.py                    # ★ ENTRY POINT - Click CLI commands
│   │                            # - generate, download, list-models commands
│   │                            # - Progress manager creation
│   │                            # - Error handling and user feedback
│   │
│   ├── __init__.py               # Package initialization
│   │
│   ├── config/                   # ★ CONFIGURATION LAYER
│   │   ├── __init__.py           # Exports: load_config, load_model_config
│   │   └── loader.py             # Config loading & validation logic
│   │                            # - load_config() - Main config loader
│   │                            # - _validate_against_model_constraints()
│   │                            # - _validate_config() - Range checks
│   │
│   ├── models/                   # ★ MODEL MANAGEMENT
│   │   ├── __init__.py           # Package exports
│   │   ├── downloader.py         # HuggingFace model downloads
│   │   ├── validator.py          # Model integrity validation
│   │   └── factory.py            # Model loader factory pattern
│   │
│   ├── generation/               # ★ IMAGE GENERATION
│   │   ├── __init__.py           # Package exports
│   │   └── flux.py               # FLUX model loader implementation
│   │                            # - BaseModelLoader (ABC)
│   │                            # - FluxModelLoader
│   │                            # - Memory optimization techniques
│   │
│   ├── output/                   # ★ OUTPUT MANAGEMENT
│   │   └── __init__.py           # Image saving functions
│   │                            # - save_image()
│   │                            # - generate_filename()
│   │                            # - ensure_output_dir()
│   │
│   ├── validation/               # ★ PRE-FLIGHT CHECKS
│   │   └── __init__.py           # Validation functions
│   │                            # - validate_gpu()
│   │                            # - validate_all_components()
│   │                            # - check_gpu_availability()
│   │
│   ├── errors/                   # ★ ERROR HIERARCHY
│   │   ├── __init__.py           # Error class exports
│   │   ├── base.py               # Text2ImageError base class
│   │   ├── config_errors.py      # ConfigError
│   │   ├── model_errors.py       # ModelDownloadError, ModelLoadError, etc.
│   │   ├── output_errors.py      # ImageSaveError
│   │   └── hardware_errors.py    # CudaNotAvailableError, InsufficientMemoryError
│   │
│   └── utils/                    # ★ UTILITIES
│       ├── __init__.py
│       ├── console.py            # Rich console output functions
│       └── progress.py           # Progress bar management
│
├── config/                       # ★ USER CONFIGURATION
│   ├── config.example.yaml       # Example user configuration file
│   ├── config.yaml               # Local user configuration file (gitignored)
│   │                            # - model, prompt, parameters
│   │                            # - MUST exist before 'generate' works
│   │
│   └── models/                   # Model-specific constraints
│       ├── flux-schnell.yaml     # Constraints for FLUX.1-schnell
│       └── flux-dev.yaml         # Constraints for FLUX.1-dev
│
├── tests/                        # ★ UNIT TESTS
│   ├── __init__.py
│   └── unit/                     # Unit test modules
│       ├── test_cli_generate.py  # CLI generate command tests
│       ├── test_config_loader.py # Configuration loading tests
│       ├── test_flux_loader.py   # FLUX loader tests
│       ├── test_model_validator.py # Model validation tests
│       ├── test_output.py        # Output management tests
│       └── test_validation.py    # Pre-flight validation tests
│
├── docs/                         # ★ DOCUMENTATION
│   ├── index.md                  # Documentation index (this file)
│   ├── project-overview.md       # Project overview and tech stack
│   ├── architecture.md           # Architecture documentation
│   ├── user-guide.md             # User guide
│   ├── technical.md              # Technical details
│   └── manual-download.md        # Manual model download guide
│
├── models/                       # ★ DOWNLOADED MODELS (Gitignored)
│   ├── flux-schnell/             # FLUX.1-schnell model files
│   └── flux-dev/                 # FLUX.1-dev model files
│
├── output/                       # ★ GENERATED IMAGES (Gitignored)
│   └── *.png                     # Generated image files
│
├── pyproject.toml                # ★ PROJECT METADATA & DEPENDENCIES
├── README.md                     # Project overview and quick start
├── AGENTS.md                     # AI agent instructions
├── .gitignore                    # Git ignore rules
└── venv/                         # Python virtual environment (Gitignored)
```

## Critical Folders Explained

### Core Application Folders

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| `src/` | Main application code | `cli.py` (entry point) |
| `src/config/` | Configuration loading | `loader.py` (358 LOC) |
| `src/models/` | Model management | `downloader.py`, `validator.py`, `factory.py` |
| `src/generation/` | Image generation | `flux.py` (262 LOC) |
| `src/output/` | Image output | `__init__.py` (101 LOC) |
| `src/validation/` | Pre-flight checks | `__init__.py` (175 LOC) |
| `src/errors/` | Error hierarchy | Multiple error type files |

### Configuration Folders

| Folder | Purpose | Gitignored |
|--------|---------|------------|
| `config/` | User configuration | No - **Must be committed** |
| `config/models/` | Model constraints | No - **Must be committed** |
| `models/` | Downloaded model weights | **Yes** - Large binary files |

### Output Folders

| Folder | Purpose | Gitignored |
|--------|---------|------------|
| `output/` | Generated images | **Yes** - User-generated content |

### Test Folders

| Folder | Purpose | Coverage |
|--------|---------|----------|
| `tests/unit/` | Unit tests | 6 test modules covering all core functionality |

## Entry Points

### Primary Entry Point

**File:** `src/cli.py:main()`  
**Command:** `text2image` (installed via `project.scripts` in pyproject.toml)

```python
# pyproject.toml
[project.scripts]
text2image = "src.cli:main"
```

### CLI Commands

1. **`text2image generate`** - Generate image from config
2. **`text2image download <model>`** - Download a model
3. **`text2image list-models`** - List downloaded models

## Key File Locations

| Purpose | File Path |
|---------|-----------|
| CLI entry point | `src/cli.py` |
| User config | `config/config.yaml` |
| Model constraints | `config/models/*.yaml` |
| Config loader | `src/config/loader.py` |
| Model downloader | `src/models/downloader.py` |
| Model validator | `src/models/validator.py` |
| Model factory | `src/models/factory.py` |
| FLUX loader | `src/generation/flux.py` |
| Image saver | `src/output/__init__.py` |
| Validation | `src/validation/__init__.py` |
| Error classes | `src/errors/` |

## Integration Points

### External Service Integration

- **HuggingFace Hub:** `src/models/downloader.py:download_model()` uses `snapshot_download()`
- **CUDA/nvidia-smi:** `src/validation/__init__.py:check_gpu_availability()` uses subprocess

### Internal Module Dependencies

```
cli.py
├── imports config.load_config
├── imports models.downloader
├── imports models.factory.create_model_loader
├── imports models.validator
├── imports generation.flux (via factory)
├── imports output.save_image
├── imports validation.validate_all_components
└── imports errors.* (custom exceptions)
```

## Multi-Part Structure

**This is a single-part CLI application** - no client/server separation or monorepo structure.

All code resides in a single cohesive package under `src/`.

---

**Source Tree Generated:** 2026-04-30  
**Scan Level:** Deep Scan  
