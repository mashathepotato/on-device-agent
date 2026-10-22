#!/usr/bin/env bash
set -euo pipefail
# Run INSIDE the organizer-provided Halo Hopper environment.
nvidia-smi
command -v halo
python - <<'PY'
import torch
from transformers import AutoConfig, AutoTokenizer
from src.data.collators.completions_only import DataCollatorForCompletionOnlyLM
from datasets import load_from_disk
assert torch.cuda.is_available(), 'CUDA unavailable'
c = AutoConfig.from_pretrained('LiquidAI/LFM2.5-1.2B-Instruct')
print('model_type:', c.model_type, 'GPU:', torch.cuda.get_device_name())
tokenizer = AutoTokenizer.from_pretrained('LiquidAI/LFM2.5-1.2B-Instruct')
if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
collator = DataCollatorForCompletionOnlyLM('<|im_start|>assistant\n', tokenizer=tokenizer)
for row in load_from_disk('/data/click-v2-halo')['train']:
    encoded = tokenizer.apply_chat_template(row['messages'], tokenize=True)
    labels = collator([{'input_ids':encoded}])['labels'][0]
    supervised = labels[labels != -100]
    assert 0 < len(supervised) < len(encoded), 'Empty or unmasked assistant target'
    decoded = tokenizer.decode(supervised.tolist())
    assert 'worth_clicking' in decoded and 'sentence' in decoded, 'Missing supervised target'
print('All training assistant masks checked')
PY
halo launch sft training/click_model/halo.yaml --dry-run
# First do a 2-step backward/checkpoint smoke before committing to the full run:
# halo launch sft training/click_model/halo.yaml --max_steps=2 --eval_strategy=no --save_strategy=no
# halo launch sft training/click_model/halo.yaml
