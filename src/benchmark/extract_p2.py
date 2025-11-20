"""
Usage:
python -m src.benchmark.extract_p2 \
    --input-folder "./data/casestudies/markdown" \
    --config-path "./configs/gpt-oss-20b.yaml"
"""

from .templates import TEMPLATE_SUBPROBLEM_2
from ..utils.inference import run_inference
from ..utils.common import read_jsonl
from pathlib import Path
import re
import json
import argparse

def cut_paper(text):
    SEP = r"\n## discussion\n"
    main_text = re.split(SEP, text, flags=re.IGNORECASE)[0]
    return main_text

def build_prompts(input_folder: Path):
    """
    Finds all .md files in a folder, creates a prompt for each, and saves them
    to a 'tmp.jsonl' file in the same folder.
    
    Args:
        input_folder: The path to the folder containing the .md files.
    """
    prompts = []
    for md_file in input_folder.glob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            main_text = cut_paper(text)
            if not main_text.strip():
                continue
            prompt = TEMPLATE_SUBPROBLEM_2.replace("{{paper}}", main_text)
            prompts.append(prompt)
        except Exception as e:
            print(f"Error processing file {md_file.name}: {e}")

    output_path = input_folder / "tmp.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in prompts:
            json_line = {"prompt": p}
            f.write(json.dumps(json_line) + "\n")

    return output_path

def aggregate_results():
    pass

def main():
    """
    Main function to parse arguments and run the prompt building and inference pipeline.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", type=Path, required=True)
    parser.add_argument("-c", "--config-path", type=Path, required=True)
    parser.add_argument("-o", "--output-file", type=Path, default=None)
    args = parser.parse_args()

    input_folder = args.input_folder.resolve()
    config_path = args.config_path.resolve()

    if args.output_file is None:
        results_file = input_folder / "results.jsonl"
    else:
        results_file = args.output_file.resolve()
        results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Build the prompts from the markdown files
    print("--- Step 1: Building Prompts ---")
    prompts_file = build_prompts(input_folder)

    # 2. Run the inference using the generated prompts
    print("\n--- Step 2: Running Inference ---")
    print(f"Using config: {config_path}")
    print(f"Input prompts: {prompts_file}")
    print(f"Saving results to: {results_file}")
    
    run_inference(
        str(config_path),
        str(prompts_file),
        str(results_file)
    )

    data = read_jsonl(results_file)
    import pdb; pdb.set_trace()
    
    print("\nPipeline finished successfully.")

if __name__ == "__main__":
    main()