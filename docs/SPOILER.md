# Get to the Point — browser headline spoilers

Click **Spoil beside a headline link** on a feed or search page. The linked public article is fetched without navigating away, extracted, read by local LFM2.5, and its selected answer appears inline with the surrounding source passage and real timings. No article copying is required.

## Run the local service

Python 3.9+, [Ollama](https://ollama.com), and the article extraction dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF:Q4_K_M
.venv/bin/python -m spoiler.server
```

Open **http://127.0.0.1:8765**. This is a real headline-link feed: **Spoil** fetches each external article and displays the result in the card, while clicking the title opens the publisher normally. Add another public article URL at the bottom; its actual publisher title is extracted automatically. The included NASA and BBC links were fetched live during development. The demo works independently of extension installation.

The provisional model is official **LiquidAI/LFM2.5-1.2B-Instruct Q4_K_M**, not a substitute model. Confirm Instruct versus Base with organizers before training. No tuned checkpoint has been trained.

## Install the browser extension

1. In Chrome/Chromium's `chrome://extensions`, enable Developer mode and **Load unpacked** → this repository's `extension/` directory. For updates, click Reload there and refresh the feed/search tab.
2. Open a feed or search page. A **Spoil** button appears beside eligible headline links automatically, including dynamically added links. For a page already open at installation, refresh it or click the extension popup's **Add buttons to this page**.
3. Click a headline's **Spoil**. It retrieves that link's article, runs local inference, and renders the answer inline. The feed stays open. No navigation, article paste, or current-article extraction is required.

The bundled public manifest key fixes the development ID to `phcphbfclmddibnfjpablbbeagdfdfie`. The server trusts only this exact extension origin by default, so pairing is automatic. There is no token-copy step. A different build can explicitly set `SPOILER_EXTENSION_ORIGIN=chrome-extension://YOUR_ID` before starting the service. The key is public identity material, not a private signing credential.

The popup shows connection status and selects Original or an actually configured Fine-tuned model. It does not start bulk fetching. Reading/fetching begins only on a Spoil click. Browser-internal pages cannot run content scripts. Detection is heuristic: heading links and long article links are supported, Google organic results mount controls outside citation wrappers, and Google Top stories cards have a dedicated placement. Some layouts will need adaptation.

## What the model actually does

Runtime protocol **`source-sentence-selector-v1`**: deterministic source sentences are numbered; the local model selects one integer through a constrained JSON schema. The displayed answer and context are copied from the actual article, not generated quotes. Candidate sentences contain 20+ characters and at most 60 words; extremely short/long sentences are excluded. Only the first 16,000 article characters are considered, with partial input visibly marked. Character bounds are conservative for ordinary English, not a tokenizer guarantee for arbitrary Unicode.

This is **model-selected source extraction**, not semantic verification. A selected sentence can be true to the source and still fail to resolve the headline. UI labels say this explicitly. Zero, out-of-range IDs, nonintegers, or malformed outputs produce a visible fallback. Informative headlines may yield a useful extra detail rather than a withheld answer. No cloud model, fabricated fallback, or cached mock prediction is used.

Earlier generative JSON/quote experiments frequently invented ellipses or repeated headlines; even plain-text answers hallucinated causes. Sentence selection addresses fabricated output text and reduces decoding, but **does not establish higher semantic quality**. Historical diagnostics are retained separately.

## Retrieval, privacy, and timing

The backend makes one public HTML request at a time per clicked link, with at most four concurrent fetches. It validates every redirect, rejects credentials/nonstandard ports/non-HTTP schemes, rejects all private/local/reserved or mixed DNS destinations, and pins the connection to a validated public IP while preserving TLS hostname validation. It ignores proxy environment variables, executes no source scripts, loads no subresources, and sends no browser cookies. Downloads are limited to 2 MB, three redirects, and a 20-second network deadline. Trafilatura extracts readable article text.

Publisher requests need internet and disclose the local service's ordinary network IP to the publisher. Inference stays on-device. Paywalls, bot blocks, JS-only pages, PDFs, and cookie-dependent pages can fail; the inline card reports failure. Neither publisher restrictions nor login walls are bypassed. Source HTML/model content render only as text. Google snippet text is not substituted for the article.

The API binds loopback and requires exact Host, permitted Origin, and per-start session token. Automatic pairing returns the token only to the configured extension origin. No permissive CORS or arbitrary local fixture exemption exists. This is not isolation from other already-running local processes.

The service caches up to 50 fetched URL records for 30 minutes and 100 model responses in memory; it keeps weights loaded for 30 minutes. Repeating an already-fetched exact URL can work offline with no DNS lookup. A fresh URL still needs internet. Nothing is persisted by the app. Timing separates fetch/extraction, local model request, runtime load/prefill/decode, and total wall time. Cached results are labelled; current request time is distinct from historical uncached inference time. Requests serialize through the local model; lock wait is included in model request time.

## Data, evaluation, and Halo handoff

```sh
.venv/bin/python -m tools.prepare_data
.venv/bin/python -m tools.evaluate --limit 30 --out results/selector-baseline.json
.venv/bin/python -m unittest discover -s tests -v
node --check extension/background.js
node --check extension/content.js
node --check extension/popup.js
node --check web/app.js
```

[Original Webis release](https://zenodo.org/records/8136637), CC-BY-4.0: 3,200 train / 800 validation / 1,000 test. The downloaded archive is checksum verified. Raw adapted records retain human spoilers and original positions. Manifest records hashes, retained labels, and exact normalized article leakage. Raw official splits stay unchanged; SFT train removes exact article duplicates of validation/test. This detects exact duplicates, not near duplicates.

Training matches the runtime contract: for single phrase/passage targets, find the first displayed candidate sentence containing the **exact human spoiler**, and derive its integer ID. These are deterministic weak labels, not new human annotations; targets absent from a single candidate sentence are excluded. Current eligible counts: **2,250 train / 562 validation / 707 test**. Test JSONL is for later evaluation only and is never included in Halo export. No rewritten answers or invented evidence labels are added.

The evaluation runs first N frozen split rows without filtering or application response caching. Reports contain model/settings/protocol/prompt hash, source-file hash, selected spans, latency, exact match and whitespace token F1. Token overlap is a rough proxy, not official leaderboard scoring or hook resolution. Quote presence is guaranteed by valid source selection and must not be interpreted as 100% semantic accuracy. Manually review whether the selected sentence answers the headline.

Validation is for prompt/checkpoint selection. The first 30 validation rows have been inspected during development; they are diagnostic, not untouched final-test results. The official test remains unused for inference. Legacy generative diagnostics and current selector diagnostics use different protocols and are **not a fine-tuning comparison**. See `docs/notes/sol/baseline-summary.json` (legacy) and `docs/notes/sol/selector-summary.json` (current).

### Train only when GPU access is supplied

Inspected [Halo](https://github.com/whitecircle/halo) commit `41da0838499a2459b236252ba1200a31957d3606`: SFT example, `scripts/training/sft.py`, local DatasetDict loader, and LFM model notes. In Halo's documented GPU environment:

```sh
# From this repository with Halo environment's Python/datasets:
python3 tools/export_halo.py /absolute/path/data/webis /data/spoiler-halo
# From Halo checkout:
python scripts/training/sft.py /absolute/path/training/halo.yaml
```

`training/halo.yaml` is proposed, not GPU validated: full SFT, native tokenizer template, full-sequence loss, no packing, SDPA, batch 1, 8K context. Full-sequence loss avoids an unverified completion-mask marker. Halo's published LFM examples primarily validate MoE, not this exact dense 1.2B checkpoint. First smoke-test loading, short-convolution backward, token boundaries/padding, loss, memory, checkpoint save/reload. Confirm the organizer-approved exact checkpoint and model license. No GPU credentials, training, tuned weights, or export validation were provided.

After training, export/merge using the appropriate tools, convert to GGUF using current llama.cpp, quantize to the **same Q4_K_M**, import into Ollama with the **same tokenizer/chat template**, and verify real local behavior. Then:

```sh
SPOILER_TUNED_MODEL=spoiler-specialist .venv/bin/python -m spoiler.server
SPOILER_TUNED_MODEL=spoiler-specialist .venv/bin/python -m tools.evaluate --compare --limit 30 --out results/comparison.json
# Only after choices are frozen:
SPOILER_TUNED_MODEL=spoiler-specialist .venv/bin/python -m tools.evaluate --compare --data data/webis/test.jsonl --limit 1000 --out results/final-test.json
```

Both checkpoints use the same candidate generation, prompt, integer schema, decoding settings, input, runtime, and hardware. Comparing identical model IDs is rejected. Record model digest, quantization, runtime, and idle hardware. Baseline runs first; ordering is not randomized and confidence intervals are not implemented. No trained-versus-original improvement has been measured. No CI or deployment is included.

## Current measured smoke results (2026-10-22)

Actual local HTTP API, live publisher retrieval, Apple M4 / 24 GiB / Ollama 0.32.5, already-warm original weights:

- NASA Moon Illusion: **453 ms total** (258 ms fetch/extract, 194 ms model); selects “Brace yourself: we don't really know.” The displayed surrounding paragraph explicitly says there is no rock-solid scientific explanation.
- NASA Moon Batteries: **466 ms total** (275 ms fetch/extract, 190 ms model); selects the source sentence explaining replacement of liquid electrolyte with solid ceramic- or polymer-based material.
- Identical repeat requests: **0.9–1.1 ms**, explicitly labelled article and response cache hits. These are not inference timings.

The current selector's first 30 validation rows: median **597 ms** uncached model request, p95 **1,437 ms**, token F1 **.0848**, exact match **1/30**, valid source selection **30/30**. Single-reviewer strict hook resolution was only **3/30**, with one additional partial answer. Source copying is reliable by construction; relevant sentence selection remains weak. These two live successes are smoke tests, not a representative quality claim. Historic first-ever original-model loading took 7.4 seconds; current warm timings exclude that cold start. No tuned model or fine-tuning improvement exists. Full live smoke output and settings: `docs/notes/sol/live-smoke.json`.
