# local-text2image

`local-text2image` is a Python project for generating images locally from a YAML
prompt configuration through the `text2image` CLI. It can download supported
FLUX models into a local `models/` directory, validate that model weights and
model config files are present, and save generated images with timestamped
filenames.

After a model is downloaded, image generation runs on your own machine. No cloud
API or web connection is needed to generate images locally, although the first
model download requires internet access.

## Open Source Note

This project is shared in the spirit of [OpenSource.Win](https://opensource.win/):
open tools, local ownership, and practical collaboration for our shared future.
It is a humble project, but it aims to move in that direction by making local
image generation easier to inspect, run, modify, and improve.

## Features

- **Local Generation** - No cloud dependencies or API costs
- **Multiple Models** - Download and switch between supported models such as FLUX.1-schnell and FLUX.1-dev
- **Model Integrity Checks** - Inspect downloaded model weights and required model config files
- **Configuration** - User-defined YAML config with strict model-specific range validation
- **Progress Feedback** - Real-time two-tiered Rich progress bars (Overall & Denoising)
- **Error Handling** - Clear error messages with actionable guidance
- **Pre-flight Validation** - Validates model, config, and resources before generation
- **Timestamp Filenames** - Automatic filename generation to prevent overwrites

## Example Output

Generated images are saved in `output/` with timestamped filenames, such as
`output/20260501_144113_2923.png`.

![Example generated image](docs/assets/pic-example.png)

## Installation

```bash
pip install -e .
```

### torch and torchvision

For NVIDIA CUDA support (recommended):
```bash
# Install with CUDA 12.4 (compatible with most GPUs)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Or for CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

For CPU fallback:
```bash
pip install torch torchvision
```

Other PyTorch GPU backends such as Apple MPS or Intel XPU are best-effort and
depend on the PyTorch build installed in your environment.

### Quick Start

### 1. Check Available Models

```bash
text2image list-models
```

Example output:

```text
Model Integrity Report
 - flux-schnell OK (Weights: ✅ Config: ✅)
 - flux-dev NOT DOWNLOADED (Weights: ❌ Config: ✅)
```

### 2. Download a Model
```bash
text2image download flux-schnell
```

### 3. Configure Your Prompt
Copy the example config, then edit `config/config.yaml`:
```bash
cp config/config.example.yaml config/config.yaml
```

Example:
```yaml
model: flux-schnell
prompt: "A beautiful sunset over mountains"
negative_prompt: "blurry, low quality"
width: 1024
height: 1024
num_inference_steps: 28
guidance_scale: 3.5
```

### 4. Generate an Image
```bash
text2image generate
```

## Commands

| Command | Description |
|---------|-------------|
| `text2image generate` | Generate image(s) from `config/config.yaml` |
| `text2image download <model>` | Download a model into `models/` |
| `text2image list-models` | Show supported models, local weights, and config status |
| `text2image --help` | Show the main CLI help |
| `text2image --version` | Show the installed app version |

### `text2image generate`

Generate image(s) using the local config file.

```bash
text2image generate
```

Options:

| Flag | Description | Example |
|------|-------------|---------|
| `--batch <number>` | Number of images to generate for this run | `text2image generate --batch 4` |
| `-b <number>` | Short form of `--batch` | `text2image generate -b 4` |

Examples:

```bash
# Generate one image using config/config.yaml
text2image generate

# Generate four images for the current prompt
text2image generate --batch 4

# Same as above, using the short flag
text2image generate -b 4
```

If `--batch` is not provided, the app uses `batch_size` from `config/config.yaml`.

### `text2image download <model>`

Download a model before generating images. Built-in shortcuts are available for `flux-schnell` and `flux-dev`.

```bash
text2image download flux-schnell
```

Examples:

```bash
# Download FLUX.1-schnell
text2image download flux-schnell

# Download FLUX.1-dev
text2image download flux-dev
```

### `text2image list-models`

Check whether each supported model has local weight files and a matching config file.

```bash
text2image list-models
```

Example output:

```text
Model Integrity Report
 - flux-schnell OK (Weights: ✅ Config: ✅)
 - flux-dev NOT DOWNLOADED (Weights: ❌ Config: ✅)
```

### Help and Version

```bash
# Show main CLI help
text2image --help

# Show help for a specific command
text2image generate --help

# Show installed version
text2image --version
```

## Requirements

- Python 3.10+
- NVIDIA CUDA-capable GPU recommended
- CPU fallback supported, but generation will be very slow
- 4GB+ VRAM recommended (8GB recommended for FLUX.1-dev)

## Configuration
Copy `config/config.example.yaml` to `config/config.yaml`, then edit your prompt and parameters. The local `config/config.yaml` file is ignored by Git so your personal prompts and runtime settings stay out of the repository.

**The application validates your settings against the selected model's constraints.** If a value is outside the allowed range for that model, the app will stop and provide guidance on the correct range. 

*Note: Model constraints are defined in `config/models/*.yaml` and are provided by the developer to ensure stability and image quality.*

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model name (flux-schnell, flux-dev) |
| `prompt` | string | required | Text prompt |
| `negative_prompt` | string | "" | Negative prompt |
| `output_dir` | string | "output" | Output directory |
| `width` | int | 1024 | Image width (Model specific range) |
| `height` | int | 1024 | Image height (Model specific range) |
| `num_inference_steps` | int | 28 | Generation steps (Model specific range) |
| `guidance_scale` | float | 3.5 | Prompt adherence (Model specific range) |
| `seed` | int | null | Random seed |
| `device` | string | "auto" | Compute device: auto, cuda, mps, xpu, or cpu |


## Project Structure

```
local-text2image/
├── src/
│   ├── cli.py              # CLI entry point
│   ├── config/            # Configuration
│   ├── models/            # Model management
│   ├── generation/        # FLUX loader
│   ├── output/            # Image output
│   ├── validation/        # Pre-flight checks
│   ├── errors/            # Error handling
│   └── utils/             # Utilities
├── config/                 # User config
│   ├── config.example.yaml # Example config
│   ├── config.yaml         # Local config (gitignored)
│   └── models/
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## Development

### Run Tests
```bash
pytest tests/
```

## License

This project's source code is licensed under the [MIT License](LICENSE).
Copyright (c) 2026 Sebastian Rolando.

Downloaded models are not included in this repository and are governed by their
own licenses. For example, FLUX.1-schnell is Apache-2.0, while FLUX.1-dev uses
the FLUX.1 dev non-commercial license. Review each model license before use.
