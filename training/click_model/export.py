"""Export official train/validation subsets to Halo, rejecting overlong targets."""
import argparse
import json
from pathlib import Path
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', default='data/click-v2')
    p.add_argument('--out', default='/data/click-v2-halo')
    p.add_argument('--max-length', type=int, default=8192)
    args = p.parse_args()
    tokenizer = AutoTokenizer.from_pretrained('LiquidAI/LFM2.5-1.2B-Instruct')
    splits = {}; dropped = {}; seen = set()
    for split in ('train','validation'):
        records = [json.loads(s) for s in (Path(args.data)/(split+'.labels.jsonl')).read_text().split('\n') if s.strip()]
        kept = []; dropped[split] = []
        for row in records:
            if row['id'] in seen: raise ValueError('Duplicate training/evaluation ID')
            seen.add(row['id'])
            tokens = tokenizer.apply_chat_template(row['messages'], tokenize=True)
            if len(tokens) > args.max_length:
                dropped[split].append(row['id']); continue
            kept.append({'messages':row['messages']})
        if not kept: raise ValueError('Empty split ' + split)
        splits[split] = Dataset.from_list(kept)
    DatasetDict(splits).save_to_disk(args.out)
    print(json.dumps({'counts':{s:len(d) for s,d in splits.items()},'overlength_excluded':dropped},indent=2))

if __name__=='__main__': main()
