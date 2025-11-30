docker run --runtime nvidia --gpus all \
	-v /mnt/disk2/hiennm/hub:/workspace  \
	-w /workspace \
	-p 8000:8000 \
	--ipc=host \
	 vllm/vllm-openai:v0.8.5 \
        --model Qwen3-8B \
       	--max-model-len 8000 \
	--max-num-batched-tokens 4000 

# Setting up environment
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv
source .venv/bin/activate
uv pip install vllm==0.10.2 --torch-backend=auto

# Serving gpt-oss-20b on google cloud
vllm serve openai/gpt-oss-20b \
	--port 8881 \
	--gpu-memory-utilization 0.90 \
	--tensor-parallel-size 1 \
	--disable-log-requests \
	--max-model-len 32000 \
	--max-num-batched-tokens 16000 \
	--generation-config auto

# Serving gpt-oss-20b on google cloud
vllm serve unsloth/gemma-3-27b-it \
	--port 8881 \
	--gpu-memory-utilization 0.98 \
	--tensor-parallel-size 1 \
	--disable-log-requests \
	--max-model-len 32000 \
	--max-num-batched-tokens 16000 \
	--generation-config auto


# Simple test request
curl -X POST http://34.67.179.2:8881/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-oss-20b",
    "messages": [
      {"role": "user", "content": "What are the application of LLMs in biology research?"}
    ],
    "max_tokens": 1000,
    "temperature": 0.9,
    "reasoning_effort": "high"
  }'

curl -X POST http://35.188.36.133:8881/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "unsloth/gemma-3-27b-it",
    "messages": [
      {"role": "user", "content": "What are the application of LLMs in biology research?"}
    ],
    "max_tokens": 1000,
    "temperature": 0.9
  }'