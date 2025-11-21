"""
Usage:
python -m src.benchmark.extract_p2 \
    --input-folder "./data/casestudies/markdown" \
    --output-folder "./data/casestudies/problem02" \
    --config-path "./configs/gpt-oss-20b.yaml"
"""

from .templates import TEMPLATE_SUBPROBLEM_2, TEMPLATE_SUBPROBLEM_2b
from ..utils.inference import run_inference
from ..utils.common import read_jsonl, parse_json_from_text
from pathlib import Path
import pandas as pd
import re
import json
import argparse

def cut_paper(text):
    SEP = r"\n## discussion\n"
    main_text = re.split(SEP, text, flags=re.IGNORECASE)[0]
    main_text = re.sub(r"## article", "", main_text, flags=re.IGNORECASE)
    return main_text

def extract_subsections(text):
    # \n##          -> A newline, two hashes, and a space.
    # (?!Figure)    -> A "negative lookahead". Asserts that the following text is NOT "Figure".
    #                This is the key part for the exclusion.
    # [^\n]+        -> Matches one or more characters that are NOT a newline (the header text).
    # \n            -> The final newline ending the header line.
    # wrapping the whole pattern in a capturing group (...)
    SEP = r"(## (?!Figure)[^\n]+\n)"
    parts = re.split(SEP, text, flags=re.IGNORECASE)
    subsections = []
    # import pdb; pdb.set_trace()
    for i in range(1, len(parts), 2): # deliberately omit the first, empty element
        subtitle = parts[i]
        content = parts[i+1]
        subsections.append({
            "subtitle": subtitle.strip(),
            "content": content.strip()
        })
    
    return subsections

def build_prompts(input_folder: Path, output_folder: Path):
    """
    Finds all .md files in a folder, creates a prompt for each, and saves them
    to a 'tmp.jsonl' file in the same folder.
    
    Args:
        input_folder: The path to the folder containing the .md files.
    """
    template = TEMPLATE_SUBPROBLEM_2b
    prompts = []
    for md_file in input_folder.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        main_text = cut_paper(text)
        subsections = extract_subsections(main_text)
        intro = subsections[0]
        intro_text = intro["subtitle"] + "\n\n" + intro["content"]
        for subsection in subsections[1:]:
            subtext = subsection["subtitle"] + "\n\n" + subsection["content"]
            prompt_body = (
                f"--- INTRODUCTION ---\n\n{intro_text}\n\n"
                f"--- RESULTS ---\n\n{subtext}"
            )
            prompt = template.replace("{{paper}}", prompt_body)
            prompts.append({
                "prompt": prompt, 
                "text": subtext,
                "from": str(md_file)
            })
    # import pdb; pdb.set_trace()

    output_path = output_folder / "prompts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in prompts[:]:
            f.write(json.dumps(p) + "\n")

    return output_path

def aggregate_results(output_folder: Path):
    def contains_ref(row):
        cp = row["connecting_principle"]
        return "(Ref:" in cp
    
    responses_file = output_folder / "responses.jsonl"
    results_jsonl = output_folder / "results.jsonl"
    results_csv = output_folder / "results.csv"

    results = []
    for row in read_jsonl(responses_file):
        response = str(row["response"])
        parsed = parse_json_from_text(response)
        if parsed is None:
            print(f"Error parsing json object")
            parsed = []
        for new_result in parsed:
            filestem = Path(row["from"]).stem
            new_row = {
                "from": filestem, 
                # "text": row["text"],
                **new_result
            }
            # if contains_ref(new_row): 
            results.append(new_row)

    results = sorted(results, key=lambda x: x["from"])

    # Write the results to .jsonl format
    with open(results_jsonl, "w", encoding="utf-8") as f:
        for line in results[:]:
            f.write(json.dumps(line) + "\n")

    # Write the results to .csv format
    pd.DataFrame(results).to_csv(results_csv, index=False)

    return results_jsonl, results_csv



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", type=Path, required=True)
    parser.add_argument("-c", "--config-path", type=Path, required=True)
    parser.add_argument("-o", "--output-folder", type=Path, required=True)
    args = parser.parse_args()

    input_folder = args.input_folder.resolve()
    output_folder = args.output_folder.resolve()
    config_path = args.config_path.resolve()

    responses_file = output_folder / "responses.jsonl"
    responses_file.parent.mkdir(parents=True, exist_ok=True)
    
    # # 1. Build the prompts from the markdown files
    # print("--- Step 1: Building Prompts ---")
    # prompts_file = build_prompts(input_folder, output_folder)

    # # 2. Run the inference using the generated prompts
    # print("\n--- Step 2: Running Inference ---")
    # print(f"Using config: {config_path}")
    # print(f"Input prompts: {prompts_file}")
    # print(f"Saving responses to: {responses_file}")
    
    # run_inference(
    #     str(config_path),
    #     str(prompts_file),
    #     str(responses_file)
    # )

    # 3. Parse results
    print("\n--- Step 3: Parsing Results ---")
    results_jsonl, results_csv = aggregate_results(output_folder)
    print(f"Saving results to jsonl at: {results_jsonl}")
    print(f"Saving results to csv at: {results_csv}")

    print("\nPipeline finished successfully.")

if __name__ == "__main__":
    main()