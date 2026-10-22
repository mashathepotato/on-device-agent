#!/usr/bin/env bash
# Source in the supplied Halo 1.1.0 H200 container; keep artifacts persistent.
export HF_HOME=/data/hf
export HF_DATASETS_CACHE=/data/hf/datasets
export HALO_DATA_ROOT=/data
export TMPDIR=/data/tmp
export TRITON_CACHE_DIR=/data/triton-cache
export TORCH_HOME=/data/torch-cache
export XDG_CACHE_HOME=/data/cache
export CUDA_CACHE_PATH=/data/cuda-cache
export PYTHONPATH=/workspace${PYTHONPATH:+:$PYTHONPATH}
export CUDA_HOME=/usr/local/cuda-13.2
export CPATH="$CUDA_HOME/targets/x86_64-linux/include${CPATH:+:$CPATH}"
export TRITON_PTXAS_PATH="$CUDA_HOME/bin/ptxas"
export TRITON_CUOBJDUMP_PATH="$CUDA_HOME/bin/cuobjdump"
export TRITON_NVDISASM_PATH="$CUDA_HOME/bin/nvdisasm"
mkdir -p "$TMPDIR" "$TRITON_CACHE_DIR"
