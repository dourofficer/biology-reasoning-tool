docker run --runtime nvidia --gpus all \
	-v /mnt/disk2/hiennm/hub:/workspace  \
	-w /workspace \
	-p 8000:8000 \
	--ipc=host \
	 vllm/vllm-openai:v0.8.5 \
        --model Qwen3-8B \
       	--max-model-len 8000 \
	--max-num-batched-tokens 4000 
