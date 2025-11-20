docker run --runtime nvidia --gpus all \
	-v /mnt/disk2/hiennm/hub:/workspace  \
	-w /workspace \
	-p 8000:8000 \
	--ipc=host \
	 vllm/vllm-openai:v0.8.5 \
        --model Qwen3-8B \
       	--max-model-len 8000 \
	--max-num-batched-tokens 4000 

# Serving gpt-oss-20b on google cloud
vllm serve openai/gpt-oss-20b \
	--port 8881 \
	--gpu-memory-utilization 0.90 \
	--tensor-parallel-size 1 \
	--disable-log-requests \
	--max-model-len 8000 \
	--max-num-batched-tokens 4000 \
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