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

## More Documentation

This README covers the essentials. For more in-depth guides, see the full documentation:

- [docs/index.md](docs/index.md) - Documentation index with all available guides
- [docs/user-guide.md](docs/user-guide.md) - Complete user guide
- [docs/architecture.md](docs/architecture.md) - Technical architecture
- [docs/development-guide.md](docs/development-guide.md) - Development setup and testing

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

### 2. Configure Hugging Face Access

FLUX model repositories on Hugging Face can require authentication and accepted
model terms before the first download. Put your token in a local `.env` file so
`text2image download` can authenticate without storing secrets in Git:

```bash
printf 'HF_TOKEN=hf_your_token_here\n' > .env
```

To get the token the first time:

1. Create or log in to your Hugging Face account.
2. Open the FLUX model page, such as <https://huggingface.co/black-forest-labs/FLUX.1-schnell>, and accept the model terms.
3. Go to <https://huggingface.co/settings/tokens>.
4. Create a token with `read` access, then copy it into `.env` as `HF_TOKEN=...`.

The `.env` file is ignored by Git. Keep the token private; it allows downloads
for repositories your Hugging Face account can read. Hugging Face documents user
access tokens and token roles in its [User access tokens guide](https://huggingface.co/docs/hub/en/security-tokens).

### 3. Download a Model

Models are downloaded from Hugging Face into the local `models/` directory. For example, `text2image download flux-schnell` saves files to `models/flux-schnell/`.

The `text2image download <model>` command accepts two types of names:

- **Built-in shortcuts**: `flux-schnell`, `flux-dev` (pre-configured, recommended for most users)
- **Full Hugging Face repository IDs**: e.g., `black-forest-labs/FLUX.1-schnell`

**Where the shortcut names come from:**

The built-in shortcuts map to these Hugging Face repositories:

| `text2image` shortcut | Hugging Face repository |
|----------------------|-------------------------|
| `flux-schnell` | `black-forest-labs/FLUX.1-schnell` |
| `flux-dev` | `black-forest-labs/FLUX.1-dev` |

**How to find and compare models on Hugging Face:**

When searching for models on <https://huggingface.co/models>, look for:

1. **Repository ID format** - Shown as `owner/model-name` (e.g., `black-forest-labs/FLUX.1-schnell`). Use this full ID directly with `text2image download <owner>/<model-name>`.

2. **Diffusers support** - This app uses Diffusers pipelines, so look for models that provide a Diffusers format.

3. **License and access** - Check if you need to accept model terms on the page before downloading.

4. **Hardware requirements** - Larger models (like FLUX.1-dev) need more VRAM (~8GB) compared to smaller variants.

5. **Model cards** - The model page contains hardware recommendations and usage details.

If you use a full Hugging Face repository ID, files are saved under `models/<model_name>/` using the exact value you passed.

```bash
# Using built-in shortcut (recommended)
text2image download flux-schnell

# Using full Hugging Face repository ID
text2image download black-forest-labs/FLUX.1-schnell
```

### 4. Configure Your Prompt
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

### 5. Generate an Image
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

Download a model before generating images. For details on model sources, naming, and how to find models on Hugging Face, see [### 3. Download a Model](#3-download-a-model).

If the repository requires authentication, configure `HF_TOKEN` in `.env` first (see [### 2. Configure Hugging Face Access](#2-configure-hugging-face-access)).

Examples:

```bash
# Download FLUX.1-schnell (using shortcut)
text2image download flux-schnell

# Download FLUX.1-dev (using shortcut)
text2image download flux-dev

# Download using full Hugging Face repository ID
text2image download black-forest-labs/FLUX.1-schnell
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
