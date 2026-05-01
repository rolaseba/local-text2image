# Development Guide

## Prerequisites

### Required Software

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime language |
| pip | Latest | Package manager |
| CUDA Toolkit | 12.1+ | NVIDIA GPU acceleration (recommended) |
| nvidia-smi | Compatible | NVIDIA GPU memory monitoring |

### Hardware Requirements

| Model | Minimum VRAM | Recommended VRAM |
|-------|-------------|-----------------|
| FLUX.1-schnell | 4 GB | 8 GB |
| FLUX.1-dev | 8 GB | 16 GB |

## Environment Setup

### 1. Clone and Setup

```bash
# Navigate to project directory
cd /path/to/local-text2image

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
# Install project in development mode
pip install -e .
```

### 3. Install PyTorch

**For NVIDIA CUDA 12.4 (Recommended):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**For CUDA 12.1:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**For CPU fallback:**
```bash
pip install torch torchvision
```

Other PyTorch GPU backends such as Apple MPS and Intel XPU are experimental for
this project. Use `device: auto` to prefer CUDA, then MPS, XPU, and CPU.

### 4. Verify Installation

```bash
# Check Python version
python --version

# Check PyTorch and common device backends
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'MPS: {hasattr(torch.backends, \"mps\") and torch.backends.mps.is_available()}'); print(f'XPU: {hasattr(torch, \"xpu\") and torch.xpu.is_available()}')"

# Check CLI is installed
text2image --version
```

## Project Structure

```
local-text2image/
├── src/                    # Source code
│   ├── cli.py            # CLI entry point
│   ├── config/           # Configuration
│   ├── models/           # Model management
│   ├── generation/       # FLUX loader
│   ├── output/          # Image output
│   ├── validation/      # Pre-flight checks
│   ├── errors/          # Error classes
│   └── utils/           # Utilities
├── config/                # User config
│   ├── config.yaml      # Main config
│   └── models/          # Model constraints
├── tests/                 # Unit tests
├── models/               # Downloaded models (auto-created)
└── output/               # Generated images (auto-created)
```

## Common Development Tasks

### Download a Model

```bash
text2image download flux-schnell
# or
text2image download flux-dev
```

### Generate an Image

```bash
# Ensure config/config.yaml has your prompt
text2image generate
```

### Generate Multiple Images

```bash
# Using CLI option
text2image generate --batch 4

# Or using config
# Set batch_size: 4 in config.yaml
text2image generate
```

### List Downloaded Models

```bash
text2image list-models
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_config_loader.py

# Run with verbose output
pytest tests/ -v
```

### Edit Configuration

```yaml
# config/config.yaml
model: flux-schnell
prompt: "Your prompt here"
negative_prompt: "Elements to avoid"
width: 1024
height: 1024
num_inference_steps: 28
guidance_scale: 3.5
seed: null  # Remove for random
batch_size: 1
```

## Testing

### Run All Tests

```bash
pytest tests/
```

### Test Coverage

| Test File | Description |
|-----------|-------------|
| `test_cli_generate.py` | Tests for CLI generate command |
| `test_config_loader.py` | Configuration loading and validation tests |
| `test_flux_loader.py` | FLUX model loader tests |
| `test_model_validator.py` | Model validation tests |
| `test_output.py` | Image output tests |
| `test_validation.py` | Pre-flight validation tests |

### Writing Tests

```python
# Example test structure
import pytest
from src.config import load_config

def test_load_config_with_valid_file():
    # Arrange
    config_path = Path("config/config.yaml")
    
    # Act
    config = load_config(config_path)
    
    # Assert
    assert config["model"] == "flux-schnell"
    assert config["prompt"] is not None
```

## Debugging

### Enable Verbose Output

The application uses Rich for console output. No special verbose flag needed.

### Check Device Availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print(f"MPS available: {hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()}")
print(f"XPU available: {hasattr(torch, 'xpu') and torch.xpu.is_available()}")
```

### Check Model Files

```bash
ls -la models/flux-schnell/
```

### Check Configuration

```python
from src.config import load_config
config = load_config()
print(config)
```

## Common Issues

### CUDA Not Available

**Error:** `CudaNotAvailableError`

**Solution:**
1. Verify CUDA is installed: `nvidia-smi`
2. Reinstall PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124`
3. Check Python environment has CUDA access
4. Use `device: auto` or `device: cpu` if you want to run without CUDA

### Model Not Found

**Error:** `ModelNotFoundError`

**Solution:**
```bash
text2image download flux-schnell
```

### VRAM Insufficient

**Error:** `InsufficientMemoryError`

**Solution:**
- Close other GPU applications
- Use smaller image dimensions (e.g., 512x512)
- Use FLUX.1-schnell instead of FLUX.1-dev

### Config Error

**Error:** `ConfigError`

**Solution:**
- Check `config/config.yaml` exists
- Verify required fields: `model`, `prompt`
- Check value ranges are valid for selected model

## Code Style

### Python Conventions

- Follow PEP 8
- Use type hints where appropriate
- Docstrings for public functions
- Use Rich for console output

### Example Function

```python
from pathlib import Path
from typing import Optional

def load_config(config_path: Optional[Path] = None) -> dict:
    """Load user configuration from YAML file.

    Args:
        config_path: Path to config file. If None, searches for config.yaml

    Returns:
        Configuration dictionary with defaults applied

    Raises:
        ConfigError: If config file is invalid or missing required fields
    """
    # Implementation...
```

## Contributing

### Code Review Process

1. Write tests for new functionality
2. Ensure all tests pass: `pytest tests/`
3. Check code style (if linting configured)
4. Update documentation if needed

### Project Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ...

# Run tests
pytest tests/

# Commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/my-feature
```

---

**Development Guide Version:** 1.0  
**Last Updated:** 2026-04-30  
