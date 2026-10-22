# LFM summary + click score — saved H200 run

- Owner: Codex. Reviewer/human lead: Masha.
- Branch: `agent/codex/lfm-score-training`.
- Status: actual Halo fine-tuning COMPLETE; user requested immediate save before comparison/ONNX.
- Data: 512 public Webis training examples + 100 validation examples, human spoiler selectors and Claude Haiku 5.5 synthetic utility scores. No overlength exclusions; exact train/heldout article duplicates excluded. Official test not labelled or evaluated.
- GPU/environment: organizer NVIDIA H200, Halo 1.1.0, PyTorch 2.11.0+cu130, Transformers 5.16.1. The supplied container needed CUDA include/tool paths set explicitly; use `training/click_model/h200_env.sh`.
- Training: full 1,170,340,608-parameter BF16 SFT, assistant-only loss, batch 2, accumulation 4, LR 2e-5, 2 epochs, 128 optimizer steps, seed 42. Two-step backward smoke passed. Full training runtime 104.8 seconds, training loss 0.3539.
- Best actual checkpoint: `/data/checkpoints/lfm-click-v2/checkpoint-128` (model.safetensors 2,340,697,936 bytes, config/tokenizer/chat template). Also retained checkpoint-64. Save-only-model means full optimizer state is not preserved; this is a usable inference checkpoint, not exact optimizer continuation.
- Validation loss: epoch 1 = 0.3236351907; epoch 2 = 0.3070726097, selected as best. Teacher-forced token accuracy 91.58% is not summary correctness or click accuracy.
- Persistent remote code: `/data/lfm-click-project`; labelled data: `/data/lfm-click-project/data/click-v2`; prepared DatasetDict: `/data/click-v2-halo512`; log `/data/lfm-training512.log`; code/data archive `/data/lfm-click-handoff-code-data.tgz`; Halo source snapshot `/data/halo-1.1.0-source.tgz`; HF cache `/data/hf`.
- A local backup is being copied to this checkout's ignored `models/lfm-click-tuned/`; verify completed transfer and model size before using it. Remote persistent checkpoint is complete and authoritative.
- Baseline generation pilot: only the earlier 30-row local Ollama experiment exists (675 ms median / 1578 ms p95; selector accuracy 10%; synthetic score MAE 29.67). NO matched baseline/tuned generation benchmark yet. NO demonstrated improvement claim.
- ONNX: exporter environment prepared at `/data/onnx-export-browser`, pinned browser-compatible revision `5ae758991464f2acd77c4ba5b654a9f32dbd60ea`. No ONNX graph exported yet. The new upstream GenAI-only layout is incompatible with Transformers.js.
- Checks: 21 tests pass, syntax/compile/diff checks pass; real training and checkpoint save confirmed in Halo logs. Model generation/ONNX/browser correctness and latency remain unverified.

## Resume after immediate save

```sh
cd /data/lfm-click-project
source training/click_model/h200_env.sh
python -m training.click_model.benchmark_hf --tuned /data/checkpoints/lfm-click-v2/checkpoint-128 --limit 100 --out /data/lfm-hf-comparison.json
/data/onnx-export-browser/.venv/bin/python -m training.click_model.export_onnx --checkpoint /data/checkpoints/lfm-click-v2/checkpoint-128 --exporter-dir /data/onnx-export-browser --out /data/browser-models
/data/onnx-export-browser/.venv/bin/python -m training.click_model.verify_onnx --checkpoint /data/checkpoints/lfm-click-v2/checkpoint-128 --package /data/browser-models/exports/lfm-click-tuned
```

Browser integration notes: `docs/notes/codex/lfm-onnx-extension-handoff.md`. No organizer contacts or teammate messages sent. SSH agent forwarding disabled. No restart. No CI added or main merge.
