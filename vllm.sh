# CUDA_VISIBLE_DEVICES=1 
vllm serve /home/user/models/Qwen3-32B \
    --host 0.0.0.0 \
    --port 30000 \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.95 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes