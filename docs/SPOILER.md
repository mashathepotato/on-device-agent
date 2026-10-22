# Get to the Point — local MVP

A dependency-free Python 3.9+ server, Chrome/Chromium Manifest V3 extension, and local Ollama inference. No cloud inference, CI, or deployment. The provisional original is **LiquidAI/LFM2.5-1.2B-Instruct**, official Q4_K_M GGUF. Confirm Instruct versus Base with organizers before training. A tuned checkpoint has not been trained.

## Run

Install [Ollama](https://ollama.com), start it, then:

```sh
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF:Q4_K_M
python3 -m spoiler.server
```

Open **http://127.0.0.1:8765** (use this exact host). Paste a headline and article, or prepare Webis below to unlock the first 30 frozen validation examples in the offline selector. Once model and examples are downloaded, both paths run without internet. The server keeps the model loaded for 30 minutes and caches up to 100 requests in memory. No app packages required.

The app accepts one article at a time; requests serialize through the model. It uses the first 16,000 characters and prominently marks partial articles. This character bound is conservative for ordinary English, not a tokenizer guarantee for arbitrary Unicode; investigate any runtime context limit errors. No whole-article claim is made for truncated input. Page extraction uses article/main visible text, then body as fallback; it can include navigation or miss content. Login-only, paywalled, script-heavy, and browser-internal pages may fail; paste article text instead.

The model emits JSON with an answer and source quote. Answers without a character-exact nonempty quote, valid strings, or at most 60 words are withheld. A matched quote **does not prove the answer follows from it**. Always inspect support and whether the headline's missing answer is actually resolved. Model-generated answers are fallible; the MVP does not promise semantic grounding.

## Extension

1. In `chrome://extensions`, enable Developer mode and **Load unpacked** → the repository's `extension/` directory.
2. Open its popup; expand Pair local server and copy its displayed `chrome-extension://…` origin.
3. Restart the server with that exact origin:

```sh
SPOILER_EXTENSION_ORIGIN=chrome-extension://YOUR_EXTENSION_ID python3 -m spoiler.server
```

4. Copy the newly printed pairing token (also in the demo's pairing details) into the popup and Save token. Tokens change on each server restart.
5. Visit an article and click **Spoil this article**. Choose Original or a configured Fine-tuned model.

Only explicit clicks read the active tab. The extension sends title and text to the loopback server, which calls fixed loopback Ollama. It never fetches supplied URLs. The API requires an allowed Origin, exact Host, and token; no permissive CORS. Source HTML and model text render as text. Pairing token is local capability data; do not publish it. The server provides no protection against other already-running local processes.

## Data and frozen evaluation

```sh
python3 -m tools.prepare_data
python3 -m tools.evaluate --limit 30 --out results/baseline.json
python3 -m unittest discover -s tests -v
```

[Original Webis release](https://zenodo.org/records/8136637), CC-BY-4.0: 3,200 train / 800 validation / 1,000 test. Downloaded data and raw reports are ignored. Manifest records archive/split hashes, labels retained, and cross-split duplicate IDs/articles. Raw official splits remain unchanged. SFT train excludes exact normalized article duplicates of validation/test. This detects exact-content leakage, not near-duplicate articles.

SFT includes single phrase/passage labels with a verbatim target present inside the inference input and at most 60 words. It preserves the human spoiler and original positions in raw adapted records; it never invents rewritten human labels. The JSON evidence target uses the same verified verbatim spoiler span. Multipart examples remain in evaluation but are excluded from initial SFT. Baseline inference receives no references/positions.

The evaluation uses the first N rows in the chosen split, with no filtering and no application response caching. It stores every output, rejected model output, model ID, settings, prompt fingerprint, input-file hash, timings, token overlap F1, exact match, and quote acceptance. Timings are wall-clock inference plus runtime load/prefill/decode measurements. First call is reported separately; it is not necessarily cold unless the model was explicitly unloaded. Request latency includes lock wait; inference excludes extraction/network article retrieval. Cache hits show both current request and historical model inference time.

Token F1 uses lowercase whitespace tokens and is a rough lexical proxy, not semantic quality or the official leaderboard metric. Quote acceptance checks source presence only. Review headline resolution, semantic support, and brevity manually. Validation is for prompt/checkpoint selection; final test must remain untouched until choices are frozen. Existing 30-row runs are diagnostic validation results, not final test performance.

## Fair comparison after actual training

Import the trained and merged checkpoint's GGUF into Ollama with the **same quantization and tokenizer/chat template** as original. Do not compare a LoRA adapter alone. Then:

```sh
SPOILER_TUNED_MODEL=spoiler-specialist python3 -m spoiler.server
SPOILER_TUNED_MODEL=spoiler-specialist python3 -m tools.evaluate --compare --limit 30 --out results/comparison.json
# After prompt/checkpoint selection is frozen, a single final test run:
SPOILER_TUNED_MODEL=spoiler-specialist python3 -m tools.evaluate --compare --data data/webis/test.jsonl --limit 1000 --out results/final-test.json
```

Identical input preparation, prompts, runtime, generation settings, and device are shared. Same-model comparison is rejected. Ensure the machine is otherwise idle and record runtime/model digest/quantization/hardware. Baseline runs first; the MVP does not randomize ordering or provide confidence intervals. Do not infer speed gains from tuning itself.

## Halo training handoff — GPU required, not executed

Inspected [Halo](https://github.com/whitecircle/halo) commit `41da0838499a2459b236252ba1200a31957d3606`: `examples/sft/qwen3/qwen3-4b-ultrachat.yaml`, `scripts/training/sft.py`, `src/data/sources/loading.py`, and LFM model notes. Halo supports local `save_to_disk` DatasetDict and preserves validation when `test_size` is null. Never pass the official final test into training. With Halo's documented GPU environment installed:

```sh
# From this repository, using Halo environment's Python/datasets:
python3 tools/export_halo.py /absolute/path/data/webis /data/spoiler-halo
# From Halo checkout (copy our training/halo.yaml there):
python scripts/training/sft.py /absolute/path/training/halo.yaml
```

`training/halo.yaml` is a proposed full SFT recipe, not GPU-validated. It uses native tokenizer template, full-sequence loss, no packing, SDPA, batch 1, 8K context. Full-sequence loss avoids an unverified completion-masking marker. Current Halo LFM notes primarily validate MoE, not this exact dense 1.2B checkpoint: first run a tiny subset for one step and verify model loading, short-convolution backward, tokenizer boundaries, pad tokens, loss, memory, and saved-checkpoint reload. Install requirements from Halo's own docs; no H100/H200 credentials were provided. Confirm the exact organizer-approved checkpoint and license. No training, tuned quality, export compatibility, or improvement is claimed.

After training, merge if needed, convert using current llama.cpp's HF-to-GGUF tools, quantize to the same Q4_K_M, import locally, and verify chat template and held-out behavior. These export steps remain to be tested with real trained weights.

## Measured diagnostic, 2026-10-22

Apple M4, 24 GiB RAM; Ollama 0.32.5; official 730 MB Q4_K_M model ID `5791ac70d52d`. First-ever baseline request: 8,628 ms including 7,422 ms loading. A prompt revision explicitly prohibited evidence ellipses, then the same 30 validation rows were rerun: median **1,076 ms**, p95 **2,210 ms**, mean whitespace token F1 **0.0487**, exact match **0/30**, exact-quote acceptance **10/30**. Manual review found **3/30** displayed answers resolving the hook (rows 12, 18, 30); several accepted quotes did not entail the answer. Rejected responses include format/quote failures even when the withheld answer was present, so this measures the delivered pipeline rather than pure model reasoning. This is poor pipeline quality and demonstrates why source-quote matching cannot substitute for evaluation. Some UI smoke inference ran concurrently, so timings are observational. The ~500-word under-2-second target is not established across articles. No tuned comparison exists. See `docs/notes/sol/baseline-summary.json` for durable hashes/settings/leakage metadata; ignored `results/` contains full local reports.
