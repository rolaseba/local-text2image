# local-text2image Project Overview

**Project Type:** CLI Application (Python)  
**Primary Language:** Python 3.10+  
**Architecture:** Modular CLI with separation of concerns  

## Executive Summary

local-text2image is a command-line application for local text-to-image generation using FLUX.1 models. It provides a user-friendly interface for running AI image generation locally without cloud dependencies, with strict validation, progress feedback, and error handling.

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.10+ | Core language |
| CLI Framework | Click | 8.0+ | Command-line interface |
| Deep Learning | PyTorch | 2.0+ | Tensor operations |
| Model Loading | Diffusers | 0.20+ | FLUX pipeline |
| Model Hub | HuggingFace Hub | 0.20+ | Model downloads |
| Configuration | PyYAML | 6.0+ | YAML config parsing |
| UI/Feedback | Rich | 13.0+ | Console output, progress bars |
| Image Processing | Pillow | 10.0+ | Image saving |

## Architecture Pattern

**Layered CLI Architecture:**
- **Entry Point:** `src/cli.py` - Click-based CLI commands
- **Validation Layer:** `src/validation/` - Pre-flight checks
- **Configuration Layer:** `src/config/` - YAML loading and validation
- **Model Layer:** `src/models/` - Download, validation, factory pattern
- **Generation Layer:** `src/generation/` - FLUX model loader and inference
- **Output Layer:** `src/output/` - Image saving with timestamp filenames
- **Error Handling:** `src/errors/` - Custom exception hierarchy

## Repository Structure

```
local-text2image/
├── src/                      # Core application code
│   ├── cli.py               # CLI entry point (Click)
│   ├── config/              # Configuration loading & validation
│   ├── models/              # Model download, validation, factory
│   ├── generation/          # FLUX model loader & inference
│   ├── output/              # Image output management
│   ├── validation/          # Pre-flight validation checks
│   ├── errors/              # Custom error hierarchy
│   └── utils/               # Console output, progress bars
├── config/                   # User configuration
│   ├── config.example.yaml  # Example user config
│   ├── config.yaml          # Local user config (gitignored)
│   └── models/              # Model-specific constraints
│       ├── flux-schnell.yaml
│       └── flux-dev.yaml
├── tests/                    # Unit tests
│   └── unit/                # Unit tests per module
├── docs/                     # Documentation
├── models/                   # Downloaded models (gitignored)
└── output/                   # Generated images (gitignored)
```

## Quick Reference

- **Entry Point:** `src/cli.py:main()` → `text2image` command
- **Config Location:** `config/config.yaml` (or root `config.yaml`)
- **Model Storage:** `models/` directory (auto-created)
- **Output Location:** `output/` directory (auto-created)
- **Supported Models:** `flux-schnell`, `flux-dev`

## Generated Documentation

- [Architecture](./architecture.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Component Inventory](./component-inventory.md)
- [Development Guide](./development-guide.md)

*Note: No API Contracts or Data Models — this is a CLI application without web APIs or database components.*

## Existing Documentation

- [README.md](../README.md) - Project overview and quick start
- [user-guide.md](./user-guide.md) - Complete user guide
- [technical.md](./technical.md) - Technical architecture details
- [manual-download.md](./manual-download.md) - Manual model download guide

## Getting Started

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Install PyTorch with CUDA (Recommended)
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

### 3. Download a Model
```bash
text2image download flux-schnell
```

### 4. Configure and Generate
Edit `config/config.yaml`, then run:
```bash
text2image generate
```

---

**Documentation Generated:** 2026-04-30  
**Scan Level:** Deep Scan  
