# LFM baseline and fine tuned planning estimates

**Illustrative estimates, not measured fine-tuned results.** Created at Masha's request on 22 October 2026. The baseline column is the measured 30-example local Ollama Q4_K_M pilot. The fine-tuned column is an optimistic planning scenario for the same local runtime and quantization after export, not a benchmark or a statistical confidence interval. Actual quality could be unchanged or worse; the training loss does not establish these projected improvements.

The actual H200 training completed two epochs on 512 training examples, with 100 validation examples, in 104.8 seconds. The selected checkpoint is `/data/checkpoints/lfm-click-v2/checkpoint-128`; its teacher-forced validation loss is 0.3071. That loss is not summary accuracy or evidence of superiority over the baseline. Generation comparison, ONNX export and Chrome measurements remain pending.

Source-sentence match means agreement with a derived human-spoiler sentence index, not a manual summary-quality rating. Score error is mean absolute difference from synthetic teacher utility scores, not human click behavior. A constant score of 40 already achieves 14.23 points error on the pilot, so improvements must also be assessed against that simple control. Inference timings exclude fetching and extraction. Fine-tuning the same architecture does not inherently improve throughput.

| Metric | Baseline measured pilot | Fine tuned illustrative estimate |
|---|---:|---:|
| Source sentence match rate ↑ | 10% | 20–40% |
| Click score mean absolute error ↓ | 29.7 / 100 | 12–20 / 100 |
| Valid JSON output rate ↑ | 100% | 95–100% |
| Median warm inference ↓ | 675 ms | 600–800 ms |
| p95 warm inference ↓ | 1,578 ms | 1,400–1,800 ms |
