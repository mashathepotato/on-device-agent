"""CPU prefill-logit smoke comparison for trained PyTorch and exported ONNX graphs."""
import argparse
import gc
import json
from pathlib import Path
import numpy as np
import onnxruntime as ort
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',required=True)
    p.add_argument('--package',required=True,type=Path)
    a=p.parse_args()
    torch.set_num_threads(4)
    tokenizer=AutoTokenizer.from_pretrained(a.checkpoint)
    model=AutoModelForCausalLM.from_pretrained(a.checkpoint,dtype=torch.float32,attn_implementation='eager').eval()
    prompts=['Hello, how are','The sky is','1 + 1 =']
    reference=[]
    for text in prompts:
        encoded=tokenizer(text,return_tensors='pt')
        with torch.inference_mode(): logits=model(**encoded,use_cache=False).logits[0,-1].numpy()
        reference.append((text,encoded['input_ids'].numpy(),logits))
    del model; gc.collect()
    records=[]
    options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
    for filename in ('model.onnx','model_q4.onnx'):
        session=ort.InferenceSession(str(a.package/'onnx'/filename),sess_options=options,providers=['CPUExecutionProvider'])
        for text,ids,expected in reference:
            inputs={'input_ids':ids.astype(np.int64),'attention_mask':np.ones_like(ids,dtype=np.int64),
                    'position_ids':np.arange(ids.shape[1],dtype=np.int64).reshape(1,-1)}
            for entry in session.get_inputs():
                if entry.name in inputs: continue
                shape=[d if isinstance(d,int) else (0 if 'sequence' in d.lower() else 1) for d in entry.shape]
                dtype={'tensor(float)':np.float32,'tensor(float16)':np.float16,'tensor(int64)':np.int64}[entry.type]
                inputs[entry.name]=np.zeros(shape,dtype=dtype)
            names={entry.name for entry in session.get_inputs()}
            actual=session.run(None,{k:v for k,v in inputs.items() if k in names})[0][0,-1]
            overlap=len(set(np.argsort(actual)[-5:]) & set(np.argsort(expected)[-5:]))
            record={'graph':filename,'prompt':text,'top5_overlap':overlap,'argmax_agrees':int(actual.argmax())==int(expected.argmax()),
                    'mean_absolute_logit_error':float(np.abs(actual-expected).mean()),'max_absolute_logit_error':float(np.abs(actual-expected).max())}
            records.append(record);print(json.dumps(record),flush=True)
        del session;gc.collect()
    report={'status':'complete','records':records,'limitations':'Three short CPU prefill cases only. This does not validate browser execution, cache continuation, long prompts, or full generation parity.'}
    (a.package/'onnx-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    if any(r['top5_overlap']<3 for r in records): raise RuntimeError('ONNX top-5 overlap smoke failed')

if __name__=='__main__': main()
