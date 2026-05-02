# text2image - User Guide

**text2image** is a CLI application for local text-to-image generation using FLUX.1-schnell.

---

## Quick Start

### 1. Configure Hugging Face Access

Create a local `.env` file with your Hugging Face access token:

```bash
printf 'HF_TOKEN=hf_your_token_here\n' > .env
```

`HF_TOKEN` is needed when Hugging Face requires authentication for model
downloads. FLUX models can be gated, so your account must be allowed to read the
model repository before `text2image download` can fetch the files.

First-time setup:

1. Create or log in to a Hugging Face account.
2. Visit the model page, for example <https://huggingface.co/black-forest-labs/FLUX.1-schnell>, and accept the terms.
3. Open <https://huggingface.co/settings/tokens>.
4. Create a token with `read` access.
5. Copy the token into `.env`:

```text
HF_TOKEN=hf_your_token_here
```

The `.env` file is ignored by Git, so it can hold local secrets. Keep the token
private and rotate it from Hugging Face settings if it is ever exposed. See the
official Hugging Face [User access tokens guide](https://huggingface.co/docs/hub/en/security-tokens)
for token roles and management.

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
```

### 4. Generate an Image
```bash
text2image generate
```

---

## Commands

### `text2image generate`
Generate an image from your configured prompt.

- Validates model is downloaded
- Validates configuration
- Loads the model
- Generates the image
- Saves to output directory

### `text2image download <model-name>`
Download a model from HuggingFace.

Examples:
```bash
text2image download flux-schnell
text2image download flux-dev
```

### `text2image list-models`
List downloaded models.

---

## Configuration

### User Config (`config/config.yaml`)
This is the local runtime configuration file. Create it from `config/config.example.yaml`, then edit your prompt and parameters. The application will use these values and validate them against the selected model's constraints.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model name (flux-schnell, flux-dev) |
| `prompt` | string | required | Your text prompt |
| `negative_prompt` | string | "" | Things to avoid |
| `output_dir` | string | "output" | Output directory |
| `width` | int | 1024 | Image width (Validated against model constraints) |
| `height` | int | 1024 | Image height (Validated against model constraints) |
| `num_inference_steps` | int | 28 | Denoising steps (Validated against model constraints) |
| `guidance_scale` | float | 3.5 | Prompt adherence (Validated against model constraints) |
| `seed` | int/null | null | Random seed for reproducibility |

### Model Constraints (`config/models/*.yaml`)
These files define the allowed ranges and requirements for each model. They are used for validation and are not intended to be edited by the user.

| Parameter | Description |
|-----------|-------------|
| `min_vram_gb` | Minimum VRAM required to load the model |
| `constraints` | A mapping of parameters to their minimum and maximum allowed values |

---

## Output

Generated images are saved to the `output/` directory with timestamp-based filenames:

```
output/
└── 20260406_164408_1234.png
```

Filename format: `{timestamp}_{prompt_hash}.{format}`

---

## Error Messages

The app provides clear error messages with guidance:

| Error | Message |
|-------|---------|
| Model not found | "Model 'flux-schnell' not found. Run 'text2image download flux-schnell' first." |
| Config missing | "Config is missing required field 'model'. Add `model: flux-schnell` to your config.yaml" |
| Invalid width | "Width must be 256-2048 and divisible by 8." |
| VRAM insufficient | "Your GPU has 4GB VRAM but flux-dev requires 8GB. Use flux-schnell instead." |

---

## Troubleshooting

### Out of Memory
- Use FLUX.1-schnell instead of FLUX.1-dev (requires less VRAM)
- Reduce image size (width/height)
- Reduce num_inference_steps

### Model Not Found
Run `text2image download flux-schnell` to download the model.

### Permission Errors
Ensure the `output/` directory is writable.

---

## Requirements

- Python 3.10+
- NVIDIA CUDA-capable GPU recommended
- CPU fallback supported, but generation will be very slow
- 4GB+ VRAM recommended (8GB recommended)
- torchvision (optional, eliminates warnings)

### Installing torch and torchvision

For NVIDIA CUDA support (recommended):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

For CPU fallback:
```bash
pip install torch torchvision
```

Set `device: auto` in `config/config.yaml` to prefer CUDA, then MPS, XPU, and
finally CPU. Use `device: cuda`, `device: mps`, `device: xpu`, or `device: cpu`
to require a specific backend. MPS and XPU are experimental and depend on your
PyTorch build.
