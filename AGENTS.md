# AGENTS.md - text-2-image

## Developer Commands
- **Install**: `pip install -e .`
- **Generate Image**: `text2image generate`
- **Download Model**: `text2image download <model>` (e.g., `flux-schnell`)
- **List Models**: `text2image list-models`
- **Test**: `pytest tests/`

## Architecture & Configuration
- **Entrypoint**: `src/cli.py:main`
- **User Config**: `config/config.yaml` (required for `generate`)
- **Model Storage**: Handled by `src/models/` and stored in a local `models/` directory.
- **Project Flow**: `Validation (src/validation/)` $\rightarrow$ `Model Loading (src/generation/)` $\rightarrow$ `Image Generation` $\rightarrow$ `Output (src/output/)`.

## Constraints & Quirks
- **Hardware**: Requires Python 3.10+ and CUDA-capable GPU (recommended).
- **VRAM**: Minimum 4GB (FLUX.1-dev requires 8GB+).
- **PyTorch**: Install CUDA wheels manually: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124`
- **Prerequisites**: Run `text2image download <model>` before `generate`; `config/config.yaml` must exist.
- **Files**: Images saved with timestamps to prevent overwrites; `output/` and `models/` are gitignored.
