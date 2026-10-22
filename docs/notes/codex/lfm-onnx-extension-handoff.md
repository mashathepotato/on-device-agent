# Chrome extension model handoff

User requested ONNX after fine-tuning. No trained checkpoint or ONNX artifact exists yet: White Circle GPU endpoint is still missing. Owner Codex handles training/export; teammate owns extension integration. No teammate messages sent.

## Export path

Use saved **Hugging Face safetensors weights**, not the Ollama GGUF. After training, use Python >=3.12, uv, and a separate exporter environment:

```sh
git clone https://github.com/Liquid4All/onnx-export.git /data/onnx-export-browser
git -C /data/onnx-export-browser checkout 5ae758991464f2acd77c4ba5b654a9f32dbd60ea
python3 -m training.click_model.export_onnx \
  --checkpoint /data/checkpoints/lfm-click-v2 \
  --exporter-dir /data/onnx-export-browser --out /data/browser-models
```

The pinned revision supports local LFM2 checkpoints and Transformers.js v4 format. Current exporter main has migrated to ONNX Runtime GenAI and explicitly says those exports are not loadable by Transformers.js. Do not upgrade this export pin without redoing the browser integration. Sources: [pinned exporter](https://github.com/Liquid4All/onnx-export/tree/5ae758991464f2acd77c4ba5b654a9f32dbd60ea), [current exporter](https://github.com/Liquid4All/onnx-export), [official baseline ONNX](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX).

The wrapper uses symmetric Q4 and splits external data to <=1 GiB chunks. It preserves tokenizer assets, checks ONNX structure, lists actual graph inputs/outputs, and writes `browser-manifest.json` with hashes. Ship exactly the files listed there plus the manifest; the export directory also contains larger FP32 development files that are unnecessary for browser Q4. Never rename the graph's external weight files. Export has not been executed yet; structural validity does not verify numerical parity or browser support.

## Integration contract

Use Transformers.js with LFM2 support and ONNX Runtime Web WebGPU. Bundle runtime code locally within the extension. Load a model once in a persistent extension document/worker with an available WebGPU adapter and reuse it. Check the actual target Chrome environment rather than assuming a service worker can own WebGPU. Cache weights; show first download/loading separately from article inference. Q4 baseline model is approximately 1.2 GB according to Liquid's model card; actual tuned package size will be in manifest.

Inputs: actual headline + actual article text, trimmed, maximum 16,000 characters (flag truncation). Reproduce `training/click_model/protocol.py` exactly: source candidates, 1-based candidate IDs, and prompt. Source-sentence splitting and indexing must match Python; compare golden fixtures before running. Apply the **exported checkpoint's** chat template/tokenizer. Use greedy decoding, <=48 new tokens, <=8192 total context, one article at a time. Browser runtime must detect invalid/truncated JSON, because the Ollama JSON grammar used by the pilot benchmark is not automatically present in Transformers.js.

Output: `{"sentence": INTEGER, "worth_clicking": INTEGER}`. Validate strict integers, sentence 0..candidate_count and score 0..100. Sentence 0 means no supported answer. Display source candidate at index `sentence-1` as short summary/spoiler, with its original evidence paragraph. >=60 means worth opening; 40..59 intermediate; below40 skip. Score describes the additional value of full article after seeing the spoiler; it is a synthetic subjective rating, not credibility/confidence or click probability. Reject invalid output and show unavailable instead of heuristic values labelled as model predictions.

LFM has both attention KV state and convolution state. Transformers.js handles this for compatible graphs. For direct ONNX Runtime Web, wire the actual names/types/shapes from the manifest/session metadata; carry both cache types across token generation and reset all article state between requests. Do not assume a Llama-only KV layout.

## Acceptance before shipping weights

1. Compare unquantized PyTorch and ONNX logits/greedy outputs on the same short and long public fixtures; record quantization differences separately.
2. Run the same validation articles through baseline and tuned ONNX Q4 in Chrome, with the identical browser protocol and decoding settings. Ollama timings/grammar results cannot serve as browser results.
3. Verify source support, hook resolution, JSON validity, click-score errors and threshold balance. Preserve official final test for frozen evaluation.
4. Measure cold load/download, warm uncached prefill+decode, p50/p95, peak memory, and offline cached reload. Keep <2s as a measured target, not a promise.

References: [browser large-model/external-data constraints](https://onnxruntime.ai/docs/tutorials/web/large-models.html), [WebGPU execution](https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html), [Transformers.js LFM2 implementation](https://github.com/huggingface/transformers.js/blob/main/packages/transformers/src/models/lfm2/modeling_lfm2.js).
