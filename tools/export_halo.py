"""Run in Halo's GPU environment (requires datasets). Keep test out of training."""
import argparse
from datasets import DatasetDict, load_dataset
parser=argparse.ArgumentParser()
parser.add_argument('prepared_dir');parser.add_argument('output_dir')
args=parser.parse_args()
DatasetDict({'train':load_dataset('json',data_files=args.prepared_dir+'/train.sft.jsonl',split='train'),
             'validation':load_dataset('json',data_files=args.prepared_dir+'/validation.sft.jsonl',split='train')}).save_to_disk(args.output_dir)
