# How to Download FLUX Models

This guide covers the recommended methods for downloading FLUX models from HuggingFace.

---

## Prerequisites

### 1. Accept Terms on HuggingFace

Before downloading FLUX.1-schnell, you must accept the terms:

1. Go to: https://huggingface.co/black-forest-labs/FLUX.1-schnell
2. Log in to your HuggingFace account
3. Click **"Accept"** on the terms and conditions

### 2. Get Your API Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"Create new token"**
3. Copy the token (you'll need it for authentication)

---

## Method 1: Using HF CLI (Recommended)

This is the **best practice** - uses the official HuggingFace CLI with resumable downloads.

### Step 1: Install HF CLI

```bash
# Option A: Standalone installer (recommended)
curl -LsSf https://hf.co/cli/install.sh | bash

# Option B: Using pip
pip install -U huggingface_hub
```

### Step 2: Login

```bash
# Login interactively
hf auth login

# Or with token
hf auth login --token YOUR_HF_TOKEN
```

### Step 3: Download the Model

```bash
# Download entire repository to specific folder
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```

**Options:**
```bash
# Download specific revision
hf download black-forest-labs/FLUX.1-schnell --revision main --local-dir models/flux-schnell

# Dry run (see what would be downloaded)
hf download black-forest-labs/FLUX.1-schnell --dry-run

# Download with quiet mode
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell --quiet
```

---

## Method 2: Using Environment Variable

If you don't want to login interactively, set the token as an environment variable:

```bash
# Set token (add to ~/.bashrc for permanent)
export HF_TOKEN="your_token_here"

# Download
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```

For slower connections, increase timeout:
```bash
export HF_HUB_DOWNLOAD_TIMEOUT=60
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```

---

## Method 3: Using Python

```python
from huggingface_hub import snapshot_download

# Download entire repository
snapshot_download(
    repo_id="black-forest-labs/FLUX.1-schnell",
    local_dir="models/flux-schnell",
)
```

**With authentication:**
```python
from huggingface_hub import HfApi

api = HfApi(token="your_token_here")
api.snapshot_download(
    repo_id="black-forest-labs/FLUX.1-schnell",
    local_dir="models/flux-schnell",
)
```

---

## Method 4: Using Git LFS (Not Recommended)

This method is slower and less reliable for large models:

```bash
# Install git-lfs
apt install git-lfs

# Clone repository
git clone https://huggingface.co/black-forest-labs/FLUX.1-schnell models/flux-schnell
```

---

## Troubleshooting

### "Gated Model" Error

```
Cannot access gated repo for url... Access to model is restricted.
```

**Solution:** You must accept the terms on HuggingFace first:
- Go to: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- Click "Accept"

### "Authentication Failed"

```
401 Client Error
```

**Solution:** 
```bash
# Re-login
hf auth login --force
```

### "Connection Timeout"

```
httpx.TimeoutException: Read timed out
```

**Solution:**
```bash
# Increase timeout
export HF_HUB_DOWNLOAD_TIMEOUT=60

# Retry download
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```

### "Insufficient Disk Space"

FLUX.1-schnell requires ~24GB. Make sure you have enough space:

```bash
df -h
```

---

## Verifying the Download

After downloading, verify the files:

```bash
ls -la models/flux-schnell/
```

You should see:
```
flux1-schnell.safetensors  (or model.safetensors)
ae.safetensors
model_index.json
scheduler/
text_encoder/
text_encoder_2/
tokenizer/
tokenizer_2/
transformer/
vae/
```

---

## Testing the Download

Once downloaded, test with text2image:

```bash
text2image generate
```

If you get validation errors, the model files may be incomplete. Try re-downloading:

```bash
rm -rf models/flux-schnell
hf download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```
