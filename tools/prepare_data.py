"""Download original Webis release, freeze splits, export inference + SFT JSONL."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
from spoiler.core import MAX_CHARS, messages, candidates

URL = 'https://zenodo.org/api/records/8136637/files/webis-clickbait-22.zip/content'


def adapt(row):
    article = '\n\n'.join(row['targetParagraphs'])
    headline = ' '.join(row['postText'])
    return {'id': row['uuid'], 'headline': headline, 'article': article,
            'references': row['spoiler'], 'positions': row['spoilerPositions'], 'type': row['tags'][0]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='data/webis')
    parser.add_argument('--zip', default='data/webis-clickbait-22.zip')
    args = parser.parse_args()
    archive = Path(args.zip); archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    if checksum != '30acf935efc82e4f99d45943827c4e14551d1554bc43514c90e4948c1514586b':
        raise ValueError('Archive checksum differs from inspected original Webis release')
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    all_rows = {}; manifest = {'source':URL,'license':'CC-BY-4.0','zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'splits':{}}
    with zipfile.ZipFile(archive) as zipped:
        heldout_articles = {hashlib.sha256(' '.join(adapt(json.loads(line))['article'].lower().split()).encode()).hexdigest()
                            for split in ('validation','test') for line in zipped.read(split+'.jsonl').splitlines() if line.strip()}
        for split, expected in [('train',3200),('validation',800),('test',1000)]:
            raw = [json.loads(line) for line in zipped.read(split+'.jsonl').splitlines() if line.strip()]
            if len(raw) != expected: raise ValueError('Unexpected official split size')
            rows = [adapt(row) for row in raw]; all_rows[split] = rows
            path = out/(split+'.jsonl')
            path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
            sft = []
            for row in rows:
                # Deterministic weak label: first displayed candidate containing the exact human spoiler.
                # The sentence ID is derived, not a human evidence annotation.
                if row['type'] not in ('phrase','passage') or len(row['references']) != 1: continue
                if split == 'train' and hashlib.sha256(' '.join(row['article'].lower().split()).encode()).hexdigest() in heldout_articles: continue
                target = row['references'][0]
                if target not in row['article'][:MAX_CHARS]: continue
                if len(target.split()) > 60: continue
                choices = candidates(row['article'][:MAX_CHARS])
                selected = next((i+1 for i, sentence in enumerate(choices) if target in sentence), None)
                if selected is None: continue
                sft.append({'messages':messages(row['headline'],row['article'][:MAX_CHARS])+[
                    {'role':'assistant','content':json.dumps({'sentence':selected})}]})
            (out/(split+'.sft.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sft))
            manifest['splits'][split] = {'count':len(rows),'sft_count':len(sft),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    seen_ids = {}; seen_content = {}; leaks = []
    for split,rows in all_rows.items():
        for row in rows:
            signature = hashlib.sha256(' '.join(row['article'].lower().split()).encode()).hexdigest()
            for seen,key,kind in [(seen_ids,row['id'],'id'),(seen_content,signature,'article')]:
                if key in seen and seen[key] != split: leaks.append({'kind':kind,'id':row['id'],'splits':[seen[key],split]})
                seen[key] = split
    manifest['cross_split_duplicates'] = leaks
    manifest['training_policy'] = 'Official raw splits unchanged; SFT train excludes exact normalized article duplicates of either held-out split. Validation/test remain frozen.'
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__': main()
