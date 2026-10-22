# Local fine tuned inference deployment

The actual Halo checkpoint `checkpoint-128` is imported into Ollama as `lfm-click-tuned:checkpoint128`, dense LFM2 1.2B, Q4_K_M, 731,153,133 bytes. No remote inference is used. Model digest: `5de3d7d5e1f60458e1b26cee0f15073f0f5ae2171ef3c624ca86b4a6c6e7244d`. Hugging Face weights are backed up in this checkout's ignored `models/lfm-click-tuned/`, in addition to the organizer's persistent `/data` checkpoint.

## Run and import

```sh
# Only needed to recreate the already-imported local Ollama model:
ollama create lfm-click-tuned:checkpoint128 -f training/click_model/Modelfile -q Q4_K_M
# Start the service when port 8765 is free:
bash scripts/run-tuned.sh
```

The service is currently running at http://127.0.0.1:8765 from this checkout. `/api/status` reports the two distinct model names and `default_mode: tuned`. The local demo defaults to Fine-tuned. Fine-tuned was selected in the installed Chrome extension's actual model selector; existing extension code continues to work with the API, including pairing-token refresh after server restart. Current development extension changes preserve explicit model preferences and follow the server default for new users.

Full articles use the exact `sentence-click-score-v2` training prompt and source-sentence candidates. All 512 saved training prompts were compared against production after extracting the shared protocol and match exactly. Both original and tuned use that same prompt, strict JSON schema and 48-token cap when the specialist is configured. Selected source text becomes the summary; the model's `worth_clicking` integer becomes the displayed score. Invalid scores are errors, never replaced by a heuristic under a fine-tuned label. Scores >=60 are green for this protocol.

Metadata-only publisher fallback remains on the original model. The specialist was not trained to produce a topic summary from URL/title/snippet and gave an unhelpful summary in its deployment smoke. API fields report `mode: original`, actual model name and `requested_mode: tuned` when that fallback occurs. This preserves the previous preview behavior without claiming it is a full-article fine-tuned result.

## Rollback

Before deployment: `3d506a7` (checkpoint commit). The running publisher-preview changes were preserved in dependency merge `ead8da8`, leaving their source branch untouched. The following runtime switch restores original-only inference without changing Git history or deleting trained weights:

```sh
# Stop the current API service on its known port:
kill "$(lsof -tiTCP:8765 -sTCP:LISTEN)"
bash scripts/run-original.sh
```

Select Original in the extension when using original-only mode. If the local demo is open, refresh it. For a code rollback on the task branch, revert the deployment commit using `git revert <deployment-commit>`; this preserves the earlier checkpoint, training history and publisher changes. No reset or force push is required. The post-deployment commit is recorded by the handoff and chat.

## Verification and remaining work

32 Python tests pass, including distinct model routing, identical baseline/tuned prompts/settings, malformed-score rejection and metadata fallback routing. Extension publisher/transport tests, JavaScript syntax, shell syntax and diff checks pass. Actual model import, full-article local API requests, explicit original-mode request, preview fallback and Chrome's Fine-tuned selection were verified. Three uncached validation article smoke requests took 973, 1207 and 981 ms; these are individual smoke timings, not a representative benchmark. Source selection can still be irrelevant; no quality improvement is established.

The saved illustrative estimate table is still only an estimate. A matched held-out quality comparison and browser ONNX conversion remain pending. This deployment uses the installed extension's existing loopback API integration; it is not ONNX inference inside Chrome.
