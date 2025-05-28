CUDA_VISIBLE_DEVICES=1 vllm serve /raid2/model/Qwen3-8B \
    --host 0.0.0.0 \
    --port 30000 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilizatio 0.8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes