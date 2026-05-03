# TODO

Project-level ideas, improvements, and follow-up work live here. Use inline
`# TODO:` comments only when the note belongs next to a specific line of code.

## Bugs

- [x] **BaseModelLoader.is_loaded() references wrong attribute** — `flux.py:64` checks `self._pipeline` but base only initializes `self._model`. Hard crash on polymorphic calls.
- [x] **load() method signature mismatch** — `FluxModelLoader.load(device)` vs abstract `BaseModelLoader.load()`. Violates Liskov substitution.
- [x] **SuppressProgress not thread-safe** — `flux.py:33` redirects `sys.stderr` globally. Concurrent threads interfere.
- [x] **Global mutable state in factory** — `factory.py:9-10` global `MODEL_REGISTRY` / `_registered`. Reimport can leave inconsistent state.
- [x] **VRAM check hardcodes device index 0** — `loader.py:363` always checks GPU 0. Wrong/missing on multi-GPU.
- [ ] **Duplicated model lists** — `["flux-schnell", "flux-dev"]` hardcoded in `cli.py:235` and `loader.py:210`.
- [ ] **Duplicate validation runs on every config load** — `_validate_required_fields()` and `_validate_config()` both validate model/prompt.
- [ ] **Bare `except Exception` in save_image** — `output/__init__.py:87` catches everything, masks disk full / permissions errors.
- [ ] **Prompt hash collision risk** — `output/__init__.py:45`: `hash(prompt) % 10000` uses only 4 digits. Collisions overwrite files.
- [ ] **Module-level env vars set at import time** — `flux.py:5-8` side-effects when module imports, not at generation time.

## Improvements

- _No items for now._

## Ideas

_No items yet._

## Later

- _No items for now._
