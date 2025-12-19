# Scientific Reasoning Extraction Pipeline

A pipeline for extracting logical reasoning structures from scientific research papers using Large Language Models (LLMs). The system identifies how authors connect empirical findings to established knowledge to form new hypotheses and conclusions.

## Overview
This project implements a multi-stage pipeline to analyze scientific papers:

1. **PDF to JSON Conversion**: Extract structured text from scientific papers
2. **Triplet Extraction**: Identify reasoning patterns (Q1: Inquiry Logic, Q2: Discovery Logic)
3. **Triplet Prediction**: Generate missing components of reasoning structures

See `documentation/experiment_overview.md` for detailed explanation of the experimental reasoning framework.

## Project Structure

```
.
├── configs/                    # Model configuration files
│   ├── gemini-2.5-flash.yaml
│   ├── gemini-3-flash.yaml
│   └── gemini-3-pro.yaml
├── src/
│   ├── experiments/           # Main experiment scripts
│   │   ├── convert.py        # PDF → JSON conversion
│   │   ├── extract.py        # Triplet extraction
│   │   ├── predict.py        # Triplet prediction
│   │   └── templates.py      # Prompt templates
│   └── utils/
│       ├── inference_gemini.py
│       ├── document_builder.py
│       └── common.py
└── data/
    └── gemini/
        ├── pdf/              # Input PDFs
        ├── conversion/       # Conversion outputs
        ├── extraction/       # Extraction outputs
        └── prediction/       # Prediction outputs
```

## Installation

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (for local inference)
- Docker (optional, for vLLM deployment)

### Setup

```bash
# Clone the repository
git clone https://github.com/dourofficer/biology-reasoning-tool.git
cd biology-reasoning-tool

# Install dependencies (using uv recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv
source .venv/bin/activate
uv pip install vllm==0.10.2 --torch-backend=auto
uv pip install docling==2.55.1
```

## Experiments
As all experiments are run with GEMINI models, please (create and) obtain your api key and save it as follows:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Experiment 1: PDF to JSON Conversion
Convert scientific papers from PDF format to structured JSON.

**Input**: PDF files containing scientific papers  
**Output**: JSON files with extracted sections (abstract, introduction, results, discussion)

```bash
python -m src.experiments.convert \
    --input-folder ./data/gemini/pdf/ \
    --config-path ./configs/gemini-3-pro.yaml \
    --response-folder ./data/gemini/conversion/raw \
    --output-folder ./data/gemini/conversion/formatted
```

**Options**:
- `--input-folder`: Directory containing PDF files
- `--config-path`: Model configuration file (choose from `configs/`)
- `--response-folder`: Raw API responses
- `--output-folder`: Formatted JSON outputs
- `--aggregate-only`: Skip inference, only process existing responses

**Output Format**:
```json
{
  "article_title": "Paper Title",
  "metadata": {
    "doi": "10.xxxx/xxxxx",
    "authors": ["Author 1", "Author 2"]
  },
  "abstract": "...",
  "introduction": "...",
  "results": {
    "subsections": [
      {
        "title": "Subsection Title",
        "content": "...",
        "figures": ["Figure caption 1", "..."]
      }
    ]
  },
  "discussion": "..."
}
```

### Experiment 2: Triplet Extraction

Extract reasoning triplets (Q1 and Q2) from structured papers.

**Q1 (Inquiry Logic)**: Research Question → Justification → Method  
**Q2 (Discovery Logic)**: Observation → Theory → Interpretation

**Input**: JSON files from Experiment 1  
**Output**: CSV files with extracted triplets

```bash
python -m src.experiments.extract \
    --input-folder ./data/gemini/conversion/formatted/ \
    --config-path ./configs/gemini-3-pro.yaml \
    --response-folder ./data/gemini/extraction/raw \
    --output-folder ./data/gemini/extraction/formatted
```

**Options**:
- `--input-folder`: Directory with JSON papers from Experiment 1
- `--config-path`: Model configuration file
- `--response-folder`: Raw extraction responses
- `--output-folder`: Formatted CSV outputs (one per paper)
- `--aggregate-only`: Skip inference, only aggregate results

**Output Format**:
Each paper generates a CSV with columns:
- `title`: Paper title
- `subsection`: Results subsection name
- `type`: Q1 or Q2
- `main_content`: Primary component (question/observation)
- `context`: Background/justification
- `outcome`: Method/interpretation

### Experiment 3: Triplet Prediction

Generate missing components of reasoning triplets.

**Input**: 
- JSON paper (from Experiment 1)
- CSV/TSV file with partial triplets

**Output**: Predictions for missing `context` and `outcome` components

```bash
python -m src.experiments.predict \
    --paper-path ./data/gemini/conversion/formatted/mechanical.json \
    --triplets-file ./data/gemini/triplets.mechanical.csv \
    --output-folder ./data/gemini/prediction/ \
    --config-path ./configs/gemini-3-pro.yaml
```

**Options**:
- `--paper-path`: Path to specific JSON paper
- `--triplets-file`: CSV/TSV with triplets to complete (must include `type`, `main_content`, `context`, `outcome` columns)
- `--output-folder`: Output directory for predictions
- `--config-path`: Model configuration file
- `--aggregate-only`: Skip inference, only aggregate results

**Input CSV Format**:
```csv
title,type,subsection,main_content,context,outcome
Paper Title,Q1,Section 1,"To determine...",Original context,Original outcome
```

**Output CSV Format**:
```csv
title,type,subsection,main_content,context,outcome,predicted_context,predicted_outcome
Paper Title,Q1,Section 1,"To determine...",Original,Original,Generated context,Generated outcome
```

## Model Configuration

Configuration files in `configs/` specify model parameters:

```yaml
model_name: gemini-3-pro-preview  # Model identifier
temperature: 1.0                   # Sampling temperature
topP: 0.95                        # Nucleus sampling (optional)
topK: 40                          # Top-K sampling (optional)
thinkingConfig:                   # Extended thinking (Gemini 2+)
  thinkingBudget: 64000
concurrent_requests: 5            # Parallel API calls
```

**Available Gemini Configurations**:
- `gemini-2.5-flash.yaml`: Fast, lower cost
- `gemini-3-flash.yaml`: Balanced performance
- `gemini-3-pro.yaml`: Highest quality (recommended for experiments)

## Other Usages

### 1. PDF to Text Conversion

Convert scientific PDFs to structured markdown:

```bash
# Single file
python -m src.pdf2text.pdf2text input.pdf output_dir/

# Batch processing
cd src/pdf2text
bash run_batch.sh
```

### 2. VLLM Server Setup

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
model_name: gemini-2.5-flash
temperature: 1.0
topP: 0.8
thinkingConfig:
  thinkingBudget: 1000
concurrent_requests: 5
```

## Technical Concerns

### Inference throughput
For more optimized batch processing, you may want to adopt the official script: https://github.com/vllm-project/vllm/blob/main/examples/offline_inference/batch_llm_inference.py

Instead, in this repo, I opted for building a minimal yet more configurable script for handling input-output and steaming. Throughput varies by model, context length, and hardware. In your config file, be aware of `concurrent_requests` in configs to optimize for your setup. The higher `concurent_requests`, the larger the throughput, as well as the higher chance of timeout.

### PDF2Text
My current pipeline does not process PDF directly because open models cannot work with PDF natively. Instead it first OCR the PDF to text before using LLM.
1. The quality of OCR-ed text may affect the quality of extraction and 
2. open-source solutions are not reliable as proprietary models (Gemini/GPT/etc). Rough observation: gpt-oss-20b can extract 20 triples with OCR-ed text from the best opensource solution I found, meanwhile it can extract 25 triples with clean OCR-text from Gemini.
Currently I use Gemini to do the OCR. I made this decision because: (1) I want to focus on the capability of LLM at extracting first, having noisy input data would make my judgement not clear, and (2) I suppose that when we scale up our experiment with thousands of papers, they will all be open-access paper with clean text version, hence no need for pre-processing PDF->text.
