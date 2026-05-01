# Component Inventory

## CLI Components

### Click Commands (`src/cli.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `main()` | Function | CLI entry point |
| `cli` | Click.Group | Command group |
| `generate` | Click.Command | Image generation command |
| `download` | Click.Command | Model download command |
| `list_models` | Click.Command | Model listing command |
| `create_progress_manager()` | Function | Multi-tiered progress callback factory |

## Configuration Components

### Config Loader (`src/config/loader.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `DEFAULT_CONFIG` | Dict | Default configuration values |
| `get_config_path()` | Function | Resolve config file path |
| `load_config()` | Function | Load and validate user config |
| `load_model_config()` | Function | Load model-specific constraints |
| `_validate_against_model_constraints()` | Function | Validate params against model ranges |
| `_validate_config()` | Function | General config validation |
| `_validate_output_settings()` | Function | Validate output settings |
| `_validate_seed()` | Function | Validate seed value |
| `_validate_vram_requirements()` | Function | Check VRAM requirements |

## Model Management Components

### Downloader (`src/models/downloader.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `MODEL_SHORTCUTS` | Dict | HuggingFace model ID mappings |
| `get_model_id()` | Function | Resolve short name to HF ID |
| `get_models_dir()` | Function | Get/create models directory |
| `download_model()` | Function | Download model from HuggingFace |
| `is_model_downloaded()` | Function | Check if model exists |
| `get_model_path()` | Function | Get path to downloaded model |

### Validator (`src/models/validator.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `FLUX_REQUIRED_FILES` | List | Required model files |
| `FLUX_OPTIONAL_FILES` | List | Optional model files |
| `ValidationResult` | Dataclass | Validation result container |
| `get_model_config()` | Function | Get file requirements for model |
| `_find_file_in_model()` | Function | Search for file in model dir |
| `validate_model()` | Function | Full model validation |
| `validate_model_or_raise()` | Function | Validate with exception |
| `is_model_valid()` | Quick | Boolean validation check |

### Factory (`src/models/factory.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `create_model_loader()` | Function | Factory function for model loaders |

## Generation Components

### FLUX Loader (`src/generation/flux.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `SuppressProgress` | Class | Context manager to suppress output |
| `BaseModelLoader` | ABC | Abstract base for model loaders |
| `FluxModelLoader` | Class | FLUX-specific implementation |
| `load()` | Method | Load model into memory |
| `generate()` | Method | Run inference |
| `unload()` | Method | Release model from memory |
| `get_memory_requirement()` | Method | Get VRAM requirements |
| `get_memory_usage()` | Method | Get current memory usage |
| `_get_device()` | Method | Determine CUDA/CPU device |
| `_report_progress()` | Method | Report progress via callback |

## Output Components

### Image Saver (`src/output/__init__.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `ensure_output_dir()` | Function | Create output directory |
| `generate_filename()` | Function | Generate timestamp-based filename |
| `save_image()` | Function | Save PIL Image to file |
| `get_output_path()` | Function | Resolve full output path |

## Validation Components

### Pre-flight Checks (`src/validation/__init__.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `ValidationResult` | Dataclass | Validation result container |
| `check_gpu_availability()` | Function | Check GPU and VRAM via nvidia-smi |
| `validate_gpu()` | Function | Validate and raise on failure |
| `validate_all_components()` | Function | Full system validation |
| `get_validation_summary()` | Function | Format validation results |

## Error Handling Components

### Error Hierarchy (`src/errors/`)

| Component | Type | Purpose |
|-----------|------|---------|
| `Text2ImageError` | Base | Base exception with guidance |
| `ModelDownloadError` | Exception | Download failures |
| `ModelLoadError` | Exception | Loading failures |
| `ModelNotFoundError` | Exception | Model not found |
| `ModelValidationError` | Exception | Validation failures |
| `ConfigError` | Exception | Configuration errors |
| `ImageSaveError` | Exception | Output failures |
| `CudaNotAvailableError` | Exception | GPU unavailable |
| `InsufficientMemoryError` | Exception | VRAM insufficient |

## Utility Components

### Console (`src/utils/console.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `console` | Rich.Console | Main console instance |
| `print_info()` | Function | Print info message |
| `print_success()` | Function | Print success message |
| `print_error()` | Function | Print error message |
| `print_header()` | Function | Print section header |

### Progress (`src/utils/progress.py`)

| Component | Type | Purpose |
|-----------|------|---------|
| `progress` | Rich.Progress | Progress bar instance |

## Test Components

### Unit Tests (`tests/unit/`)

| Test File | Coverage |
|-----------|----------|
| `test_cli_generate.py` | CLI generate command |
| `test_config_loader.py` | Configuration loading and validation |
| `test_flux_loader.py` | FLUX model loader |
| `test_model_validator.py` | Model validation |
| `test_output.py` | Image output |
| `test_validation.py` | Pre-flight validation |

## Component Dependencies

```
cli.py (main entry)
├── src.config (load_config)
├── src.models.downloader (get_models_dir)
├── src.models.factory (create_model_loader)
├── src.models.validator (is_model_valid)
├── src.generation.flux (FluxModelLoader)
├── src.output (save_image)
├── src.validation (validate_all_components, validate_gpu)
└── src.errors (all exceptions)

config/loader.py
├── src.errors (ConfigError)
├── src.config (load_model_config)

models/downloader.py
├── src.errors (ModelDownloadError)

models/validator.py
├── src.errors (ModelValidationError, ModelNotFoundError)

generation/flux.py
├── src.errors (ModelLoadError)

output/__init__.py
├── src.errors (ImageSaveError)

validation/__init__.py
├── src.config (load_config)
├── src.models.validator (is_model_valid)
├── src.models.downloader (get_models_dir)
└── src.errors (CudaNotAvailableError, InsufficientMemoryError)
```

---

**Component Inventory Generated:** 2026-04-30  
**Scan Level:** Deep Scan  
