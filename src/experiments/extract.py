"""
Usage:

python -m src.experiments.extract \
    --input-folder ./data/gemini/conversion/formatted/ \
    --config-path ./configs/gemini-3-pro.yaml \
    --response-folder ./data/gemini/extraction/raw \
    --output-folder ./data/gemini/extraction/formatted \
    --aggregate-only
"""

from .templates import EXTRACTION_TEMPLATE
from ..utils.inference_gemini import run_inference
from ..utils.common import read_jsonl, read_json, parse_json
from ..utils.document_builder import generate_document
from pathlib import Path
import pandas as pd
import os
import json
import argparse


def build_prompts(input_folder: Path, output_folder: Path):
    """
    Finds all .md files in a folder, creates a prompt for each, and saves them
    to a 'tmp.jsonl' file in the same folder.
    
    Args:
        input_folder: The path to the folder containing the .md files.
    """
    template = EXTRACTION_TEMPLATE
    prompts = []
    for json_file in input_folder.glob("*.json"):
        data = read_json(json_file.resolve())
        title = data.get("article_title", "Untitled Article")
        documents = generate_document(
            data,
            include_intro=True,
            include_result=True,
            include_discussion=False,
            include_figures=True,
            chunk_subsections=False
        )
        for doc in documents:
            prompt = template.replace("{{paper}}", doc)
            prompts.append({
                "prompt": prompt,
                "title": title,
                "from": str(json_file)
            })

    output_path = output_folder / "prompts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in prompts[:]:
            f.write(json.dumps(p) + "\n")

    return output_path

def aggregate_results(response_folder: Path, output_folder: Path):
    
    responses_file = response_folder / "responses.jsonl"
    results_csv = output_folder / "results.csv"

    for row in read_jsonl(responses_file):
        response = str(row["response"])
        title = row["title"]
        filestem = Path(row["from"]).stem
        parsed_json = parse_json(response)[0]
        extractions = parsed_json["extractions"]

        results = []
        for subsection in extractions:
            subtitle = subsection["subsection"]
            triplets = subsection["triplets"]
            new_rows = [{
                "title": title,
                "subsection": subtitle,
                **triplet
            } for triplet in triplets]
            results += new_rows
        
        results_csv = output_folder / f"{filestem}.csv"
        pd.DataFrame(results).to_csv(results_csv, index=False)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", type=Path, required=True)
    parser.add_argument("-c", "--config-path", type=Path, required=True)
    parser.add_argument("-r", "--response-folder", type=Path, required=True)
    parser.add_argument("-o", "--output-folder", type=Path, required=True)
    parser.add_argument("--aggregate-only", action='store_true')
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    input_folder = args.input_folder.resolve()
    response_folder = args.response_folder.resolve()
    output_folder = args.output_folder.resolve()
    config_path = args.config_path.resolve()

    responses_file = response_folder / "responses.jsonl"
    responses_file.parent.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)

    if not args.aggregate_only:
        # 1. Build the prompts from the markdown files
        print("--- Step 1: Building Prompts ---")
        prompts_file = build_prompts(input_folder, response_folder)

        # 2. Run the inference using the generated prompts
        print("\n--- Step 2: Running Inference ---")
        print(f"Using config: {config_path}")
        print(f"Input prompts: {prompts_file}")
        print(f"Saving responses to: {responses_file}")
        
        run_inference(
            str(config_path),
            str(prompts_file),
            str(responses_file),
            api_key=api_key
        )

    # 3. Parse results
    print("\n--- Step 3: Parsing Results ---")
    aggregate_results(response_folder, output_folder)

    print("\nPipeline finished successfully.")

if __name__ == "__main__":
    main()