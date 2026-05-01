# Documentation Index

## Project Overview

- **Type:** CLI Application (Python)
- **Primary Language:** Python 3.10+
- **Architecture:** Modular CLI with separation of concerns

### Quick Reference

- **Entry Point:** `src/cli.py:main()` → `text2image` command
- **Config Location:** `config/config.yaml` (or root `config.yaml`)
- **Model Storage:** `models/` directory (auto-created, gitignored)
- **Output Location:** `output/` directory (auto-created, gitignored)
- **Supported Models:** `flux-schnell`, `flux-dev`

### Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.10+ |
| CLI Framework | Click 8.0+ |
| Deep Learning | PyTorch 2.0+ |
| Model Pipeline | Diffusers 0.20+ |
| Model Hub | HuggingFace Hub 0.20+ |
| UI/Feedback | Rich 13.0+ |
| Config | PyYAML 6.0+ |

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md) - Executive summary and tech stack
- [Architecture](./architecture.md) - Detailed architecture and design patterns
- [Source Tree Analysis](./source-tree-analysis.md) - Annotated directory structure

### Component Documentation

- [Component Inventory](./component-inventory.md) - All modules and their responsibilities

### Development Documentation

- [Development Guide](./development-guide.md) - Setup, testing, debugging

### Technical Documentation

*No additional technical docs needed — CLI application without APIs or data models. See [technical.md](technical.md) for legacy module reference.*

## User Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and quick start |
| [user-guide.md](user-guide.md) | Complete user guide with commands and configuration |
| [manual-download.md](manual-download.md) | Manual model download guide (alternative to CLI) |

## Quick Links

- **Quick Start**: See [README.md](../README.md)
- **User Guide**: [user-guide.md](user-guide.md)
- **Technical Docs**: [architecture.md](architecture.md)
- **Development**: [development-guide.md](development-guide.md)

---

**Documentation Index Version:** 2.0  
**Generated:** 2026-04-30  
**Scan Level:** Deep Scan  
