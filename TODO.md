# TODO

Project-level ideas, improvements, and follow-up work live here. Use inline
`# TODO:` comments only when the note belongs next to a specific line of code.

## Bugs

- [x] **BaseModelLoader.is_loaded() references wrong attribute** — `flux.py:64` checks `self._pipeline` but base only initializes `self._model`. Hard crash on polymorphic calls.
- [x] **load() method signature mismatch** — `FluxModelLoader.load(device)` vs abstract `BaseModelLoader.load()`. Violates Liskov substitution.
- [x] **SuppressProgress not thread-safe** — `flux.py:33` redirects `sys.stderr` globally. Concurrent threads interfere.
- [x] **Global mutable state in factory** — `factory.py:9-10` global `MODEL_REGISTRY` / `_registered`. Reimport can leave inconsistent state.
- [x] **VRAM check hardcodes device index 0** — `loader.py:363` always checks GPU 0. Wrong/missing on multi-GPU.
- [x] **Duplicated model lists** — `["flux-schnell", "flux-dev"]` hardcoded in `cli.py:235` and `loader.py:210`.
- [x] **Duplicate validation runs on every config load** — `_validate_required_fields()` and `_validate_config()` both validate model/prompt.
- [x] **Bare `except Exception` in save_image** — `output/__init__.py:87` catches everything, masks disk full / permissions errors.
- [x] **Prompt hash collision risk** — `output/__init__.py:45`: `hash(prompt) % 10000` uses only 4 digits. Collisions overwrite files.
- [x] **Module-level env vars set at import time** — `flux.py:5-8` side-effects when module imports, not at generation time.
- [ ] **Magic number file size thresholds** — `validator.py:135` uses 0 bytes, `validator.py:141` uses 1000 bytes. No explanation.
- [ ] **Torch not installed check is shallow** — `device.py:45-46` catches ImportError but not when torch is installed but CUDA fails.
- [ ] **import random inside function** — `cli.py:160`. Works but indicates the 20-line import block at top missed something.
- [ ] **No-op when progress_callback is None** — `flux.py:268-270` silently skips without any indicator.
- [ ] **model_path.iterdir() not guarded** — `validator.py:118` raises OSError if directory permissions prevent reading.
- [ ] **Model type detection is fragile** — `factory.py:84-90` uses `"flux" in name_lower`. Both `"flux-schnell"` and `"my-flux-model"` return `"flux"`.
- [ ] **Memory requirement is hardcoded static dict** — `flux.py:220-224` returns fixed values rather than querying actual hardware.
- [ ] **ValidationResult not frozen** — `validator.py:25` `@dataclass` without `frozen=True`. Instances are mutable.
- [ ] **No __repr__ on model classes** — Hard to debug when you can't inspect loader state.
- [ ] **Hardcoded assumption of single GPU** — `device.py:65` only checks device 0 for VRAM validation.

## Improvements

- _No items for now._

## Ideas

_No items yet._

## Later

- _No items for now._