# Scientific Reasoning Extraction Pipeline

A pipeline for extracting logical reasoning structures from scientific research papers using Large Language Models (LLMs). The system identifies how authors connect empirical findings to established knowledge to form new hypotheses and conclusions.

## Overview

This repository provides tools to:

1. **Convert PDFs to structured text** using document layout analysis and OCR
2. **Extract logical triplets** from research papers that capture scientific reasoning:
   - **Premise**: Novel findings from the current study
   - **Connecting Principle**: Established biological knowledge from literature
   - **Interpretation**: New hypotheses or conclusions
3. **Run batch inference** across multiple LLM backends (vLLM, Google Gemini)
4. **Analyze results** and generate structured outputs

## Project Structure

```
.
├── configs/                    # Model configuration files
│   ├── gpt-oss-20b.yaml
│   ├── gpt-oss-120b.yaml
│   ├── gemma-3-27b-it.yaml
│   └── gemini-2.5-flash.yaml
├── src/
│   ├── pdf2text/              # PDF processing utilities
│   │   ├── pdf2text.py        # Document conversion with layout analysis
│   │   ├── vlm.py             # Vision-language model pipeline
│   │   ├── annotate_pdf.py    # Layout visualization tools
│   │   └── run_batch.sh       # Batch PDF processing
│   ├── benchmark/             # Extraction pipelines
│   │   ├── extract.py         # Unified extraction pipeline (md & json)
│   │   └── templates.py       # Prompt templates for extraction
│   ├── prediction/            # Experimental design prediction
│   │   ├── predict.py
│   │   └── templates.py       # Prompt templates for prediction
│   └── utils/                 # Shared utilities
│       ├── inference.py       # vLLM inference client
│       ├── inference_gemini.py # Gemini API client
│       ├── document_builder.py # Document generation
│       └── common.py          # Data I/O utilities
├── scripts/
│   ├── vllm.sh               # vLLM server setup examples
│   └── test_inference.sh     # Testing script
├── data/
│   └── inference_samples/    # Example prompts and results
│   └── casestudies/          # Representative papers
└── documentation/
    └── experiment_overview.md # Scientific framework explanation
```

## Installation

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (for local inference)
- Docker (optional, for vLLM deployment)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies (using uv recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv
source .venv/bin/activate
uv pip install vllm==0.10.2 --torch-backend=auto
uv pip install docling==2.55.1
```

## Usage

### 1. PDF to Text Conversion

Convert scientific PDFs to structured markdown:

```bash
# Single file
python -m src.pdf2text.pdf2text input.pdf output_dir/

# Batch processing
cd src/pdf2text
bash run_batch.sh
```

### 2. Model Server Setup

**Option A: vLLM (Local)**

```bash
# Start vLLM server (see scripts/vllm.sh for examples)
# Serving gpt-oss-20b on 1x A100 40GB
vllm serve openai/gpt-oss-20b \
	--port 8881 \
	--gpu-memory-utilization 0.90 \
	--tensor-parallel-size 1 \
	--disable-log-requests \
	--max-model-len 32000 \
	--max-num-batched-tokens 16000 \
	--generation-config auto
```

**Option B: Google Gemini API**

Configure your API key in `configs/gemini-*.yaml`:
```yaml
api_key: YOUR_API_KEY_HERE
model_name: gemini-2.5-flash
```

### 3. Extract Reasoning Structures

**From JSON (structured papers):**

```bash
python -m src.benchmark.extract \
  --input-folder ./data/casestudies/json \
  --output-folder ./data/output/gpt-oss-120b \
  --config-path ./configs/gpt-oss-120b.yaml \
  --input-format json
```

**From Markdown:**

```bash
python -m src.benchmark.extract \
  --input-folder ./data/casestudies/markdown \
  --output-folder ./data/output/markdown-results \
  --config-path ./configs/gemini-2.5-flash.yaml \
  --input-format markdown
```

### 4. Batch Inference

Test inference on sample prompts:

```bash
# Using vLLM
python -m src.utils.inference \
  --config configs/gpt-oss-20b.yaml \
  --input-file data/inference_samples/prompts.jsonl \
  --results-file data/inference_samples/results.jsonl

# Using Gemini
python -m src.utils.inference_gemini \
  --config configs/gemini-2.5-flash.yaml \
  --input-file data/inference_samples/prompts.jsonl \
  --results-file data/inference_samples/results_gemini.jsonl
```

## Configuration

Model configs support the following parameters:

**vLLM configs:**
```yaml
model: openai/gpt-oss-120b
temperature: 0.9
max_tokens: 48000
reasoning_effort: high  # For reasoning models
hostname: 34.12.60.86
port: 8881
concurrent_requests: 2
```

**Gemini configs:**
```yaml
api_key: YOUR_KEY
model_name: gemini-2.5-flash
temperature: 1.0
topP: 0.8
thinkingConfig:
  thinkingBudget: 1000
concurrent_requests: 5
```

## Output Format

Extracted triplets are saved in both JSONL and CSV formats:

```json
{
  "title": "Paper Title",
  "subsection": "Results subsection name",
  "premise_finding": "We observed increased OXPHOS activity (Fig. 3a)",
  "connecting_principle": "OXPHOS is known to regulate stem cell function (Ref: 12, 15)",
  "interpretation": "These findings suggest OXPHOS mediates the mutation's effect"
}
```

## Scientific Framework

The extraction pipeline identifies logical argument structures where authors:

1. Present a **novel finding** from their current study
2. Connect it to **established biological knowledge**
3. Derive a **new hypothesis or conclusion**

See `documentation/experiment_overview.md` for detailed explanation of the experimental reasoning framework.

## Performance

Throughput varies by model, context length, and hardware. In your config file, be aware of `concurrent_requests` in configs to optimize for your setup. The higher `concurent_requests`, the larger the throughput, as well as the higher chance of timeout.