"""Real local inference only; writes per-row predictions for manual hook/support review."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import time
from spoiler.core import Engine


def words(text): return text.lower().split()

def f1(prediction, reference):
    p,r = words(prediction),words(reference)
    common = sum((Counter(p)&Counter(r)).values())
    return 2*common/(len(p)+len(r)) if p or r else 1.0


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data', default='data/webis/validation.jsonl')
    parser.add_argument('--limit',type=int,default=30)
    parser.add_argument('--out',default='results/baseline.json')
    parser.add_argument('--compare',action='store_true')
    args=parser.parse_args()
    engine=Engine()
    if args.compare and (not engine.models['tuned'] or engine.models['tuned']==engine.models['original']):
        parser.error('Comparison needs a distinct actual tuned checkpoint')
    source=Path(args.data).read_bytes()
    rows=[json.loads(line) for line in source.splitlines()][:args.limit]
    records=[]
    for i,row in enumerate(rows):
        record={'id':row['id'],'headline':row['headline'],'references':row['references'],'type':row['type'],'predictions':{}}
        for mode in (['original','tuned'] if args.compare else ['original']):
            prediction=engine.generate(row['headline'],row['article'],mode,use_cache=False)
            prediction['token_f1']=max(f1(prediction['spoiler'],r) for r in row['references'])
            prediction['exact_match']=prediction['spoiler'].strip().lower() in [r.strip().lower() for r in row['references']]
            record['predictions'][mode]=prediction
        records.append(record)
        print(f'{i+1}/{len(rows)} {row["id"]}',flush=True)
    summary={}
    for mode in records[0]['predictions'] if records else []:
        preds=[r['predictions'][mode] for r in records]
        times=sorted(p['inference_ms'] for p in preds)
        summary[mode]={'n':len(preds),'mean_token_f1':statistics.mean(p['token_f1'] for p in preds),
                       'exact_match':statistics.mean(p['exact_match'] for p in preds),
                       'quote_verified_rate':statistics.mean(p['evidence_verified'] for p in preds),
                       'median_ms':statistics.median(times),'p95_ms':times[min(len(times)-1,int(len(times)*.95))],
                       'first_request_ms':times[0] if len(times)==1 else preds[0]['inference_ms']}
    output={'data_sha256':hashlib.sha256(source).hexdigest(),'selection':'first N official split rows, no filtering',
            'created_unix':time.time(),'summary':summary,'records':records,
            'limitations':'Token overlap is a proxy, not hook resolution. Verified quote presence is not semantic entailment. Manually judge both.'}
    path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(output,indent=2,ensure_ascii=False))
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
