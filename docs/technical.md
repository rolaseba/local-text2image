# local-text2image - Technical Documentation

## Architecture Overview

```
local-text2image/
├── src/
│   ├── cli.py                 # CLI entry point
│   ├── config/                # Configuration system
│   ├── models/                # Model management
│   ├── generation/            # FLUX model loader
│   ├── output/               # Image output
│   ├── validation/           # Pre-flight validation
│   ├── errors/               # Error hierarchy
│   └── utils/                # Utilities (console, progress)
├── config/                    # User configuration
│   ├── config.yaml           # Main config
│   └── models/               # Model-specific configs
├── tests/                      # Unit tests
└── docs/                       # Documentation
```

---

## Module: CLI (`src/cli.py`)

Entry point for the application. Uses Click framework.

### Commands

| Command | Function |
|---------|-----------|
| `generate` | Main generation workflow |
| `download` | Download model from HuggingFace |
| `list-models` | List downloaded models |

### Workflow (generate command)

1. Load configuration (`load_config`)
2. Validate model exists (`is_model_valid`)
3. Create model loader (`create_model_loader`)
4. Run inference (`loader.generate`)
5. Save image (`save_image`)

---

## Module: Configuration (`src/config/`)

### `loader.py`

| Function | Description |
|----------|-------------|
| `load_config()` | Load and validate user config |
| `load_model_config()` | Load model-specific config |
| `get_config_path()` | Find config.yaml location |
| `get_default_config()` | Get default values |

**Validation:**
- Required fields: model, prompt
- Range validation: width, height, steps, guidance_scale
- Output directory validation
- VRAM requirements check

---

## Module: Models (`src/models/`)

### `factory.py`

Model loader factory with auto-registration.

| Function | Description |
|----------|-------------|
| `create_model_loader()` | Create model loader instance |
| `register_model()` | Register a model type |
| `list_supported_models()` | List available models |

### `downloader.py`

| Function | Description |
|----------|-------------|
| `download_model()` | Download model from HuggingFace |
| `get_models_dir()` | Get models directory path |
| `get_model_id()` | Resolve model ID |

### `validator.py`

| Function | Description |
|----------|-------------|
| `validate_model()` | Validate model files |
| `is_model_valid()` | Quick validity check |
| `validate_model_or_raise()` | Validate with exception |

---

## Module: Generation (`src/generation/`)

### `flux.py`

FLUX model loader implementing `BaseModelLoader`.

| Method | Description |
|--------|-------------|
| `load()` | Load model into memory |
| `generate()` | Generate image from prompt |
| `unload()` | Unload model from memory |
| `get_memory_requirement()` | Get VRAM requirement |
| `get_memory_usage()` | Get current memory usage |

**Features:**
- Progress callbacks
- Memory tracking
- Support for custom parameters

---

## Module: Output (`src/output/`)

### Functions

| Function | Description |
|----------|-------------|
| `save_image()` | Save PIL Image to output directory |
| `ensure_output_dir()` | Create output directory |
| `generate_filename()` | Generate timestamp-based filename |
| `get_output_path()` | Get full output path |

**Filename Format:**
```
{YYYYMMDD}_{HHMMSS}_{prompt_hash:04d}.{format}
Example: 20260406_164408_1234.png
```

---

## Module: Validation (`src/validation/`)

### Functions

| Function | Description |
|----------|-------------|
| `validate_all_components()` | Pre-flight validation |
| `get_validation_summary()` | Human-readable summary |

**ValidationResult Dataclass:**
- `is_valid`: Boolean status
- `errors`: List of error messages
- `warnings`: List of warnings

---

## Module: Errors (`src/errors/`)

### Error Hierarchy

```
Text2ImageError (base)
├── ModelError
│   ├── ModelNotFoundError
│   ├── ModelDownloadError
│   ├── ModelLoadError
│   └── ModelValidationError
├── ConfigError
│   ├── ConfigNotFoundError
│   ├── ConfigValidationError
│   └── ConfigCompatibilityError
├── HardwareError
│   ├── InsufficientMemoryError
│   └── CudaNotAvailableError
└── ImageSaveError
```

**Error Format:**
Each error has:
- `message`: Plain English description
- `guidance`: Actionable suggestion

---

## Module: Utils (`src/utils/`)

### `console.py`
Rich console utilities for formatted output.

### `progress.py`
Rich progress bar utilities for generation feedback.

---

## Configuration Files

### `config/config.yaml`
Main user configuration file.

### `config/models/flux-schnell.yaml`
Model-specific settings for FLUX.1-schnell.

### `config/models/flux-dev.yaml`
Model-specific settings for FLUX.1-dev.

---

## Test Coverage

Tests are organized in `tests/unit/`:

| Test File | Coverage |
|-----------|----------|
| `test_config_loader.py` | Configuration loading & validation |
| `test_model_validator.py` | Model validation |
| `test_flux_loader.py` | FLUX model loader |
| `test_cli_generate.py` | CLI generate command |
| `test_output.py` | Image output |
| `test_validation.py` | Pre-flight validation |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| click | CLI framework |
| torch | ML framework |
| rich | Terminal formatting |
| pyyaml | Config parsing |
| huggingface_hub | Model download |
| diffusers | FLUX pipeline |
| pillow | Image handling |
| pytest | Testing |

---

## Data Flow

```
User Command (CLI)
    ↓
load_config() → Validates config
    ↓
validate_all_components() → Pre-flight checks
    ↓
create_model_loader() → Creates FLUX loader
    ↓
loader.generate() → Runs inference
    ↓
save_image() → Saves to output/
    ↓
Display success message
```

---

## Epic Structure

| Epic | Stories | Description |
|------|---------|--------------|
| 1 | 5 | Project Foundation (CLI, error hierarchy) |
| 2 | 4 | Model Management (download, store, validate) |
| 3 | 4 | Configuration (YAML config, validation) |
| 4 | 3 | Image Generation (load model, inference, progress) |
| 5 | 2 | Output Management (save, timestamps) |
| 6 | 6 | Validation & Error Handling |
