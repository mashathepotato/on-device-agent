"""Matched real HF baseline/tuned generation on the training GPU, without a JSON grammar."""
import argparse
import gc
import json
import math
from pathlib import Path
import statistics
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tools.evaluate import f1
from .protocol import VERSION, digest, prompt, validate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', default='LiquidAI/LFM2.5-1.2B-Instruct')
    p.add_argument('--tuned')
    p.add_argument('--labels', default='data/click-v2/validation.labels.jsonl')
    p.add_argument('--data', default='data/webis/validation.jsonl')
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--out', default='results/hf-comparison.json')
    a = p.parse_args()
    if a.tuned == a.baseline: p.error('Identical model references')
    labels = {r['id']:r for r in [json.loads(s) for s in Path(a.labels).read_text().split('\n') if s.strip()]}
    rows = [json.loads(s) for s in Path(a.data).read_text().split('\n') if s.strip()]
    rows = [r for r in rows if r['id'] in labels][:a.limit]
    if not rows: p.error('No evaluation rows')
    models = {'baseline':a.baseline}
    if a.tuned: models['tuned'] = a.tuned
    report = {'status':'running','protocol':VERSION,'models':models,'settings':{'max_new_tokens':48,'do_sample':False,'dtype':'bfloat16','attention':'sdpa'},
              'hardware':torch.cuda.get_device_name(),'labels_sha256':digest(labels),'records':[], 'warmup':{},'load_seconds':{},'summary':{}}
    path = Path(a.out); path.parent.mkdir(parents=True,exist_ok=True)
    for mode, identifier in models.items():
        started = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(identifier)
        model = AutoModelForCausalLM.from_pretrained(identifier,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
        report['load_seconds'][mode] = time.perf_counter()-started
        def infer(row):
            messages, choices, truncated = prompt(row)
            encoded = tokenizer.apply_chat_template(messages, tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt').to('cuda')
            input_tokens = encoded['input_ids'].shape[-1]
            if input_tokens+48>8192: raise ValueError('Input exceeds benchmark token budget')
            torch.cuda.synchronize(); start=time.perf_counter()
            with torch.inference_mode(): generated=model.generate(**encoded,max_new_tokens=48,do_sample=False,pad_token_id=tokenizer.eos_token_id)
            torch.cuda.synchronize(); elapsed=(time.perf_counter()-start)*1000
            output_ids=generated[0,input_tokens:]
            text=tokenizer.decode(output_ids,skip_special_tokens=True).strip()
            try: output=validate(json.loads(text),len(choices)); error=None
            except ValueError as exc: output=None; error=str(exc)
            selected=output['sentence'] if output else 0
            return {'output':output,'raw_text':text,'error':error,'spoiler':choices[selected-1] if selected else '',
                    'request_ms':elapsed,'input_tokens':input_tokens,'output_tokens':len(output_ids),'truncated':truncated,'prompt_sha256':digest(messages)}
        report['warmup'][mode]=infer(rows[-1])
        for row in rows:
            result=infer(row); target=labels[row['id']]['target']; output=result['output']
            result.update({'mode':mode,'id':row['id'],'target':target,
                           'token_f1':max(f1(result['spoiler'],r) for r in row['references']),
                           'sentence_correct':output is not None and output['sentence']==target['sentence'],
                           'score_absolute_error':abs(output['worth_clicking']-target['worth_clicking']) if output else None,
                           'click_correct':output is not None and (output['worth_clicking']>=60)==(target['worth_clicking']>=60)})
            report['records'].append(result)
            path.write_text(json.dumps(report,indent=2))
            print(mode,row['id'],round(result['request_ms']),output,flush=True)
        preds=[r for r in report['records'] if r['mode']==mode]
        times=sorted(r['request_ms'] for r in preds); errors=[r['score_absolute_error'] for r in preds if r['score_absolute_error'] is not None]
        report['summary'][mode]={'n':len(preds),'valid_json_rate':statistics.mean(r['output'] is not None for r in preds),
            'sentence_label_accuracy':statistics.mean(r['sentence_correct'] for r in preds), 'token_f1':statistics.mean(r['token_f1'] for r in preds),
            'teacher_score_mae_valid_only':statistics.mean(errors) if errors else None,'click_accuracy':statistics.mean(r['click_correct'] for r in preds),
            'always_skip_accuracy':statistics.mean(r['target']['worth_clicking']<60 for r in preds),
            'median_ms':statistics.median(times),'p95_ms':times[math.ceil(.95*len(times))-1]}
        del model; gc.collect(); torch.cuda.empty_cache()
    report['status']='complete'
    report['limitations']='Synthetic teacher agreement and reference-sentence matching are proxies. Warm CUDA timings exclude tokenization and article fetching. No browser latency claim; no JSON grammar unlike Ollama pilot. Official test unused.'
    path.write_text(json.dumps(report,indent=2)); print(json.dumps(report['summary'],indent=2),flush=True)

if __name__=='__main__': main()
