# Architecture Documentation

## Executive Summary

local-text2image follows a **modular layered architecture** designed for CLI applications. The system separates concerns into distinct modules: validation, configuration, model management, generation, and output. Each module has a clear responsibility and communicates through well-defined interfaces.

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime language |
| Click | 8.0+ | CLI framework |
| PyTorch | 2.0+ | Deep learning backend |
| Diffusers | 0.20+ | Model pipeline management |
| HuggingFace Hub | 0.20+ | Model distribution |
| Rich | 13.0+ | Terminal UI and progress bars |
| PyYAML | 6.0+ | Configuration parsing |
| Pillow | 10.0+ | Image I/O |

### Dependencies (pyproject.toml)

```toml
click>=8.0.0          # CLI framework
torch>=2.0.0,<3.0.0   # Deep learning
torchvision>=0.15.0   # Computer vision utilities
rich>=13.0.0          # Terminal formatting
pyyaml>=6.0           # YAML parsing
huggingface_hub>=0.20.0  # Model hub client
transformers>=4.30.0  # Transformer models
diffusers>=0.20.0     # Diffusion pipelines
accelerate>=0.20.0    # Hardware acceleration
pillow>=10.0.0        # Image processing
pytest>=7.0.0         # Testing framework
```

## Architecture Pattern

### Layered CLI Architecture

The application follows a **layered architecture** with clear separation between:

1. **Interface Layer** - CLI commands and user interaction
2. **Validation Layer** - Pre-flight checks and input validation
3. **Business Logic Layer** - Configuration, model management, generation
4. **Infrastructure Layer** - File I/O, model storage, output management

```
┌─────────────────────────────────────────┐
│           CLI Interface Layer           │
│              (src/cli.py)               │
│  - generate command                     │
│  - download command                     │
│  - list-models command                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Validation Layer                │
│        (src/validation/)                │
│  - GPU availability check               │
│  - Model validation                     │
│  - Config validation                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Business Logic Layer               │
│  ┌────────────┐  ┌────────────┐         │
│  │  Config    │  │   Models   │         │
│  │  (config/) │  │ (models/)  │         │
│  └────────────┘  └────────────┘         │
│  ┌────────────┐  ┌────────────┐         │
│  │ Generation │  │   Output   │         │
│  │(generation/)│ │ (output/)  │         │
│  └────────────┘  └────────────┘         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Infrastructure Layer               │
│  - File system I/O                      │
│  - Model storage (models/)              │
│  - Image output (output/)               │
│  - Error handling (errors/)             │
└─────────────────────────────────────────┘
```

## Data Architecture

### Configuration Data Flow

```
config/config.yaml ──► load_config() ──► validate_against_model_constraints()
                            │
                            ▼
                  DEFAULT_CONFIG + user_config
                            │
                            ▼
                  Model-specific constraints
                  (config/models/*.yaml)
```

### Model Constraint Schema

```yaml
# config/models/flux-schnell.yaml
min_vram_gb: 4
recommended_vram_gb: 8
model_size_gb: 4

constraints:
  width:
    min: 256
    max: 2048
  height:
    min: 256
    max: 2048
  num_inference_steps:
    min: 1
    max: 50
  guidance_scale:
    min: 1.0
    max: 10.0
```

### Generation Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `prompt` | string | required | - | Text description |
| `negative_prompt` | string | optional | "" | Elements to avoid |
| `width` | int | 256-2048 (÷8) | 1024 | Image width |
| `height` | int | 256-2048 (÷8) | 1024 | Image height |
| `num_inference_steps` | int | 1-50 (schnell), 1-100 (dev) | 28 | Denoising steps |
| `guidance_scale` | float | 1.0-10.0 (schnell), 1.0-20.0 (dev) | 3.5 | Prompt adherence |
| `seed` | int | 0-2³²-1 | null | Random seed |
| `batch_size` | int | ≥1 | 1 | Images per generation |

## Component Overview

### Core Modules

#### 1. CLI Module (`src/cli.py`)

**Responsibility:** Command-line interface using Click

**Key Functions:**
- `main()` - Entry point
- `generate()` - Image generation command
- `download()` - Model download command
- `list_models()` - Model listing command
- `create_progress_manager()` - Multi-tiered progress callback

**Design Pattern:** Command pattern with Click decorators

#### 2. Configuration Module (`src/config/`)

**Responsibility:** Load and validate user configuration

**Key Components:**
- `load_config()` - Load YAML config with defaults
- `load_model_config()` - Load model-specific constraints
- `_validate_against_model_constraints()` - Range validation
- `_validate_config()` - General validation

**Error Handling:** Raises `ConfigError` with guidance messages

#### 3. Models Module (`src/models/`)

**Responsibility:** Model download, validation, and factory pattern

**Key Components:**
- `downloader.py` - HuggingFace model downloads
- `validator.py` - Model integrity validation
- `factory.py` - Create model loader instances
- `get_models_dir()` - Model storage management

**Design Pattern:** Factory pattern for model loaders

#### 4. Generation Module (`src/generation/flux.py`)

**Responsibility:** Load FLUX models and run inference

**Key Components:**
- `BaseModelLoader` - Abstract base class
- `FluxModelLoader` - FLUX-specific implementation
- `SuppressProgress` - Context manager for progress suppression

**Memory Optimization:**
- Sequential CPU offload
- Model CPU offload
- FP16 precision on CUDA

#### 5. Output Module (`src/output/`)

**Responsibility:** Save generated images

**Key Functions:**
- `save_image()` - Save PIL Image to file
- `generate_filename()` - Timestamp-based filenames
- `ensure_output_dir()` - Create output directory

**Filename Format:** `{timestamp}_{prompt_hash}.png`

#### 6. Validation Module (`src/validation/`)

**Responsibility:** Pre-flight validation checks

**Key Functions:**
- `validate_gpu()` - GPU availability and VRAM check
- `validate_all_components()` - Full validation suite
- `check_gpu_availability()` - nvidia-smi integration

#### 7. Errors Module (`src/errors/`)

**Responsibility:** Custom exception hierarchy

**Error Types:**
- `ModelDownloadError` - Download failures
- `ModelLoadError` - Loading failures
- `ModelNotFoundError` - Model not found
- `ModelValidationError` - Validation failures
- `ConfigError` - Configuration errors
- `ImageSaveError` - Output failures
- `CudaNotAvailableError` - GPU unavailable
- `InsufficientMemoryError` - VRAM insufficient

**Base Class:** `Text2ImageError` with guidance messages

## Source Tree Analysis

```
src/
├── cli.py                    # Main CLI entry point (275 LOC)
├── __init__.py               # Package init
│
├── config/                   # Configuration management
│   ├── __init__.py           # Exports: load_config, load_model_config
│   └── loader.py             # Config loading & validation (358 LOC)
│
├── models/                   # Model management
│   ├── __init__.py           # Package exports
│   ├── downloader.py         # HuggingFace downloads (81 LOC)
│   ├── validator.py          # Model validation (204 LOC)
│   └── factory.py            # Model loader factory (not shown)
│
├── generation/               # Image generation
│   ├── __init__.py           # Package exports
│   └── flux.py               # FLUX model loader (262 LOC)
│
├── output/                   # Image output
│   ├── __init__.py           # Save functions (101 LOC)
│   └── ...
│
├── validation/               # Pre-flight checks
│   ├── __init__.py           # Validation functions (175 LOC)
│   └── ...
│
├── errors/                   # Error hierarchy
│   ├── __init__.py           # Error exports
│   ├── base.py               # Base exception class
│   ├── config_errors.py      # Config-related errors
│   ├── model_errors.py       # Model-related errors
│   ├── output_errors.py      # Output-related errors
│   └── hardware_errors.py    # Hardware-related errors
│
└── utils/                    # Utilities
    ├── __init__.py
    ├── console.py            # Rich console output
    └── progress.py           # Progress bar management
```

## Development Workflow

### Project Flow

```
1. Validation (src/validation/)
   ↓
2. Model Loading (src/generation/flux.py)
   ↓
3. Image Generation (FluxModelLoader.generate())
   ↓
4. Output (src/output/)
```

### Key Commands

| Command | Description |
|---------|-------------|
| `pip install -e .` | Install in development mode |
| `text2image generate` | Generate image from config |
| `text2image download <model>` | Download a model |
| `text2image list-models` | List downloaded models |
| `pytest tests/` | Run unit tests |

### Testing Strategy

**Unit Tests Location:** `tests/unit/`

**Test Files:**
- `test_cli_generate.py` - CLI generate command tests
- `test_config_loader.py` - Configuration loading tests
- `test_flux_loader.py` - FLUX loader tests
- `test_model_validator.py` - Model validation tests
- `test_output.py` - Output management tests
- `test_validation.py` - Pre-flight validation tests

**Run Tests:**
```bash
pytest tests/
```

## Deployment Architecture

### Local Deployment

**Prerequisites:**
- Python 3.10+
- CUDA-capable GPU (recommended)
- 4GB+ VRAM (8GB for FLUX.1-dev)

**Installation:**
```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Install project
pip install -e .

# Download model
text2image download flux-schnell
```

### Memory Management

**VRAM Requirements:**
- FLUX.1-schnell: 4GB minimum, 8GB recommended
- FLUX.1-dev: 8GB minimum

**Optimization Techniques:**
- FP16 precision on CUDA
- Sequential CPU offload
- Model CPU offload
- Progress bar suppression

## Integration Points

### External Services

| Service | Purpose | Integration |
|---------|---------|-------------|
| HuggingFace Hub | Model distribution | `huggingface_hub.snapshot_download()` |
| CUDA | GPU acceleration | PyTorch CUDA backend |
| nvidia-smi | VRAM monitoring | subprocess call |

### File System

| Directory | Purpose | Gitignored |
|-----------|---------|------------|
| `models/` | Downloaded models | Yes |
| `output/` | Generated images | Yes |
| `config/` | User configuration | No |
| `venv/` | Virtual environment | Yes |

---

**Architecture Document Version:** 1.0  
**Last Updated:** 2026-04-30  
