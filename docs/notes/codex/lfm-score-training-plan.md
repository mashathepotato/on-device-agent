# LFM joint spoiler and click-value experiment

Owner: Codex. Human lead/reviewer: Masha. Explicit assignment: train LFM, compare against original, optimize local latency, try organizer White Circle GPU. Worktree/branch: `agent/codex/lfm-score-training`. Scope: new `training/click_model/` experiment, focused tests, own notes. Existing app contract remains v1 until real checkpoint comparison and integration.

## Experiment

Use official Webis Clickbait Spoiling Corpus 2022: https://zenodo.org/records/8136637. Inputs are public headline/article text. Human single phrase/passage spoiler maps to the first source sentence containing that exact target. Exclude training articles duplicated in either held-out split. Keep official test out of labels, training and pilot evaluation. Candidate eligibility and short-article exclusions mean the pilot is not representative of all Webis types.

Joint JSON is `{"sentence": 12, "worth_clicking": 65}`. The displayed summary/spoiler is retrieved verbatim from source with the chosen index. This keeps generation short and evidence exact, but does not guarantee semantic relevance. Score means residual value of opening the full article after seeing the spoiler, for a general reader; it is subjective utility, not click probability or credibility. >=60 means worth clicking. Teacher only sees public text and the grounded human spoiler. Reasons and response IDs/usage are retained for audit. No online teacher call at product inference time.

Pilot: first 64 eligible train / 30 eligible validation rows. Teacher: `claude-haiku-5-5` confirmed via Anthropic Models API. Pilot validates tooling, not enough examples for a strong model. Label a larger training set after auditing examples and score distribution. Resumable JSONL labels include model/protocol/input provenance; all generated corpus and raw outputs are ignored by Git.

## Commands from this checkout

```sh
# Requires ANTHROPIC_API_KEY, never committed.
python3 -m training.click_model.label --model claude-haiku-5-5 --train-limit 64 --validation-limit 30
python3 -m training.click_model.benchmark
# After pilot audit, scale with e.g. --train-limit 2000 --validation-limit 200.
```

On organizer's single H100/H200 in its Halo Hopper image (https://github.com/whitecircle/halo):

```sh
# Transfer code plus data/click-v2; do not transfer API credentials.
python -m training.click_model.export --out /data/click-v2-halo
bash training/click_model/preflight.sh
halo launch sft training/click_model/halo.yaml --max_steps=2 --eval_strategy=no --save_strategy=no
halo launch sft training/click_model/halo.yaml
```

Config is a candidate, not GPU-verified. Dense 1.2B support must pass a real backward step; the Halo documented LFM MoE integration is a different architecture. Export rejects overlength conversations so labels cannot silently disappear under truncation. Full fine-tuning avoids an unverified hybrid-model LoRA module selection. Preflight checks nonempty assistant-only loss masks for every training row using Halo’s actual collator before training. Use an actual revision of Halo recorded on the remote host and record final model provenance and optimizer/train loss.

## Local deployment and comparison

Download trained HF checkpoint. Convert both original HF and trained weights using the SAME llama.cpp revision; quantize both to Q4_K_M and load each into Ollama. Follow official tooling docs for that installed revision; conversion/import is pending real weights. Preserve trained tokenizer/chat template. Use distinct model names.

```sh
python3 -m training.click_model.benchmark --baseline ORIGINAL_NAME --tuned TUNED_NAME --out results/click-v2-comparison.json
```

Same hardware/runtime/prompt/8192 context/48 output token cap/temperature 0/seed 42. Warm each model, then measure uncached inference; exclude warmup. Report p50/p95, under-2s rate, prefill/decode/load times, output validity, human-spoiler token overlap and teacher-score MAE/threshold agreement. Review hook resolution manually. Teacher agreement is not human preference validation. Validation used for iteration; test only once frozen. Do not use repeated-input cache times as model latency. Measure fetch/extract separately, and cold start separately after an actual unload. Keep the model resident and output only two integers to reduce overhead. Fine-tuning alone does not increase inference throughput.

## Access

No organizer SSH/portal/GPU credentials found in project, local SSH configuration or relevant event emails. This machine is Apple arm64, with no NVIDIA CUDA GPU. GPU allocation cannot be attempted until the endpoint is supplied. Prepared contact request: “Could you provide our team's White Circle H100/H200 SSH host/user/port or GPU portal, the Halo Hopper environment, persistent checkpoint storage, and any allocation expiry? We are fine-tuning LiquidAI/LFM2.5-1.2B-Instruct on public Webis examples and need one GPU.” No message sent.

## Measured pilot outcome

94 teacher-labelled rows completed (64 train, 30 validation). Training scores 8–72, mean 40.3; 11/64 >=60. Validation scores 22–74, mean 40.1; 4/30 >=60. Untuned local Q4_K_M joint output: 30/30 valid JSON; 3/30 reference sentence IDs; token F1 0.0689; teacher-score MAE 29.67/100; threshold accuracy 50%. Always skipping reaches 86.7% on this imbalanced subset and constant score 40 reaches MAE 14.23, so current model scoring is worse than trivial controls. Warm inference median 674.5 ms, p95 1578.2 ms, 30/30 <2 s; article network/extraction excluded. Summary in `lfm-score-baseline.json`; raw outputs in ignored `results/click-v2-baseline.json`. No fine-tuned checkpoint or improvement claim.
