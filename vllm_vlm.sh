CUDA_VISIBLE_DEVICES=7 vllm serve /raid2/model/Qwen2.5-VL-7B-Instruct \
    --host 0.0.0.0 \
    --port 30000 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilizatio 0.6 \