"""Real uncached Ollama inference with one matched joint protocol for both models."""
import argparse
import json
from pathlib import Path
import statistics
import time
import urllib.request
from spoiler.core import MODEL
from tools.evaluate import f1
from .protocol import VERSION, digest, prompt, schema, validate

OPTIONS = {'temperature':0, 'seed':42, 'num_predict':48, 'num_ctx':8192}

def infer(model, row):
    messages, choices, truncated = prompt(row)
    payload = {'model':model, 'messages':messages, 'format':schema(len(choices)),
               'stream':False, 'keep_alive':'30m', 'options':OPTIONS}
    request = urllib.request.Request('http://127.0.0.1:11434/api/chat', json.dumps(payload).encode(),
                                     {'Content-Type':'application/json'})
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response: raw = json.load(response)
    elapsed = (time.perf_counter()-start)*1000
    try:
        output = validate(json.loads(raw['message']['content']), len(choices))
        error = None
    except (ValueError, KeyError) as exc:
        output = None; error = str(exc)
    sentence = output['sentence'] if output else 0
    return {'output':output, 'error':error, 'spoiler':choices[sentence-1] if sentence else '',
            'truncated':truncated, 'request_ms':elapsed,
            **{k:raw.get(k,0)/1e6 for k in ('load_duration','prompt_eval_duration','eval_duration')},
            'output_tokens':raw.get('eval_count'), 'input_tokens':raw.get('prompt_eval_count'),
            'prompt_sha256':digest(messages)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', default='data/webis/validation.jsonl')
    p.add_argument('--labels', default='data/click-v2/validation.labels.jsonl')
    p.add_argument('--baseline', default=MODEL)
    p.add_argument('--tuned')
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--out', default='results/click-v2-baseline.json')
    a = p.parse_args()
    if a.tuned == a.baseline: p.error('Tuned model must be distinct')
    source = Path(a.data).read_bytes()
    rows = [json.loads(x) for x in source.decode().split('\n') if x.strip()]
    labels = {x['id']:x for x in [json.loads(s) for s in Path(a.labels).read_text().split('\n') if s.strip()]}
    rows = [r for r in rows if r['id'] in labels][:a.limit]
    if not rows: p.error('No labelled evaluation rows')
    models = {'baseline':a.baseline}
    if a.tuned: models['tuned'] = a.tuned
    records = []; warmup = {}
    path = Path(a.out); path.parent.mkdir(parents=True, exist_ok=True)
    for mode, model in models.items():
        warmup[mode] = infer(model, rows[-1])
        for row in rows:
            result = infer(model, row)
            target = labels[row['id']]['target']; output = result['output']
            result.update({'mode':mode, 'id':row['id'], 'target':target,
                'token_f1':max(f1(result['spoiler'], ref) for ref in row['references']),
                'score_absolute_error':abs(output['worth_clicking']-target['worth_clicking']) if output else None,
                'click_correct':(output['worth_clicking']>=60)==(target['worth_clicking']>=60) if output else False})
            records.append(result)
            path.write_text(json.dumps({'status':'running','records':records}, indent=2))
            print(mode,len(records),round(result['request_ms']),flush=True)
    summary = {}
    for mode in models:
        preds = [r for r in records if r['mode']==mode]
        times = sorted(r['request_ms'] for r in preds)
        errors = [r['score_absolute_error'] for r in preds if r['score_absolute_error'] is not None]
        summary[mode] = {'n':len(preds),'valid_json_rate':statistics.mean(r['output'] is not None for r in preds),
            'token_f1':statistics.mean(r['token_f1'] for r in preds),
            'teacher_score_mae_valid_only':statistics.mean(errors) if errors else None,
            'click_accuracy':statistics.mean(r['click_correct'] for r in preds),
            'sentence_label_accuracy':statistics.mean(r['output'] is not None and r['output']['sentence']==r['target']['sentence'] for r in preds),
            'always_skip_accuracy':statistics.mean(r['target']['worth_clicking']<60 for r in preds),
            'constant_40_score_mae':statistics.mean(abs(40-r['target']['worth_clicking']) for r in preds),
            'median_ms':statistics.median(times), 'p95_ms':times[max(0,__import__('math').ceil(.95*len(times))-1)],
            'under_2s_rate':statistics.mean(t<2000 for t in times)}
    report = {'status':'complete','protocol':VERSION,'models':models,'settings':OPTIONS,
              'data_sha256':digest(source.decode()),'label_sha256':digest(labels),
              'warmup':warmup,'summary':summary,'records':records,
              'limitations':'Eligible phrase/passage validation subset; synthetic score agreement is not human utility. '
              'Exact source presence does not prove hook resolution. Warm uncached timings exclude fetch/extract. '
              'Cold timing not measured unless model was actually unloaded. Final test remains unused.'}
    path.write_text(json.dumps(report,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
