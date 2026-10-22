"""Export trained HF LFM weights using the pinned Transformers.js-compatible exporter."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

EXPORTER_REVISION = '5ae758991464f2acd77c4ba5b654a9f32dbd60ea'
EXPORTER_REPO = 'https://github.com/Liquid4All/onnx-export.git'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', required=True, type=Path)
    p.add_argument('--exporter-dir', required=True, type=Path)
    p.add_argument('--out', default='models/onnx', type=Path)
    p.add_argument('--name', default='lfm-click-tuned')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if not a.name or Path(a.name).name != a.name or a.name in ('.','..'):
        p.error('--name must be one folder name')
    checkpoint = a.checkpoint.resolve(); exporter = a.exporter_dir.resolve(); out = a.out.resolve()
    command = ['uv', 'run', '--frozen', 'lfm2-export', str(checkpoint), '--output-dir', str(out),
               '--output-name', a.name, '--precision', 'q4', '--split-data', '1.0']
    if a.dry_run:
        print(json.dumps({'cwd':str(exporter),'command':command,'required_exporter_revision':EXPORTER_REVISION},indent=2));return
    config_path = checkpoint/'config.json'
    if not config_path.exists(): p.error('Missing trained HF checkpoint config.json')
    config = json.loads(config_path.read_text())
    if config.get('model_type') != 'lfm2': p.error('Expected dense LFM2 checkpoint')
    if not list(checkpoint.glob('*.safetensors')): p.error('Missing HF safetensors weights')
    revision = subprocess.check_output(['git','-C',str(exporter),'rev-parse','HEAD'],text=True).strip()
    if revision != EXPORTER_REVISION:
        p.error('Exporter revision mismatch: newer GenAI exports are not Transformers.js packages')
    if subprocess.check_output(['git','-C',str(exporter),'status','--porcelain'],text=True).strip():
        p.error('Exporter checkout must be clean for reproducible export')
    target = out/'exports'/a.name
    if target.exists(): p.error('Output exists; use a fresh --name to preserve previous weights')
    subprocess.run(command,cwd=exporter,check=True)
    import onnx
    graph_path = target/'onnx/model_q4.onnx'
    onnx.checker.check_model(str(graph_path))
    graph = onnx.load(str(graph_path),load_external_data=False)
    assets = {graph_path}
    for tensor in graph.graph.initializer:
        for item in tensor.external_data:
            if item.key == 'location':
                asset = (graph_path.parent/item.value).resolve()
                if not asset.is_relative_to(target.resolve()): raise ValueError('External data escapes package')
                if not asset.is_file(): raise ValueError('Missing external weights '+str(asset))
                assets.add(asset)
    for name in ('config.json','tokenizer.json','tokenizer_config.json','chat_template.jinja','generation_config.json'):
        file = target/name
        if file.exists(): assets.add(file)
    for required in ('config.json','tokenizer.json','tokenizer_config.json'):
        if target/required not in assets: raise ValueError('Missing browser asset '+required)
    files = []
    for file in sorted(assets):
        h = hashlib.sha256()
        with file.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024), b''): h.update(block)
        files.append({'path':str(file.relative_to(target)), 'bytes':file.stat().st_size,'sha256':h.hexdigest()})
    manifest = {'source_checkpoint':str(checkpoint),'exporter_revision':revision,'precision':'q4',
                'target_runtime':'Transformers.js / ONNX Runtime Web WebGPU',
                'validation':'ONNX structural check only; browser generation parity and latency still required',
                'graph_inputs':[x.name for x in graph.graph.input],
                'graph_outputs':[x.name for x in graph.graph.output], 'browser_files':files}
    (target/'browser-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(target/'browser-manifest.json')

if __name__ == '__main__': main()
