"""
Unified extraction pipeline for problem 2 that supports both JSON and markdown inputs.

Usage:
# For JSON input:
python -m src.benchmark.extract \
    --input-folder "./data/casestudies/json" \
    --output-folder "./data/casestudies/benchmark/gpt-oss-20b" \
    --config-path "./configs/gpt-oss-20b.yaml" \
    --input-format json

# For markdown input:
python -m src.benchmark.extract \
    --input-folder "./data/casestudies/markdown" \
    --output-folder "./data/casestudies/benchmark-md/gpt-oss-20b" \
    --config-path "./configs/gpt-oss-20b.yaml" \
    --input-format markdown
"""

from .templates import TEMPLATE_SUBPROBLEM_2b, TEMPLATE_SUBPROBLEM_2c
from ..utils.inference import run_inference
from ..utils.common import read_jsonl, read_json, parse_json, parse_json_from_text
from ..utils.document_builder import generate_document
from pathlib import Path
import pandas as pd
import re
import json
import argparse


# ============================================================================
# Markdown Processing Functions
# ============================================================================

def cut_paper(text):
    """Remove discussion section and article header from markdown text."""
    SEP = r"\n## discussion\n"
    main_text = re.split(SEP, text, flags=re.IGNORECASE)[0]
    main_text = re.sub(r"## article", "", main_text, flags=re.IGNORECASE)
    return main_text


def extract_subsections(text):
    """Extract subsections from markdown text, excluding Figure sections."""
    # \n##          -> A newline, two hashes, and a space.
    # (?!Figure)    -> A "negative lookahead". Asserts that the following text is NOT "Figure".
    #                This is the key part for the exclusion.
    # [^\n]+        -> Matches one or more characters that are NOT a newline (the header text).
    # \n            -> The final newline ending the header line.
    # wrapping the whole pattern in a capturing group (...)
    SEP = r"(## (?!Figure)[^\n]+\n)"
    parts = re.split(SEP, text, flags=re.IGNORECASE)
    subsections = []
    
    for i in range(1, len(parts), 2):  # deliberately omit the first, empty element
        subtitle = parts[i]
        content = parts[i + 1]
        subsections.append({
            "subtitle": subtitle.strip(),
            "content": content.strip()
        })
    
    return subsections


# ============================================================================
# Prompt Building Functions
# ============================================================================

def build_prompts_from_json(input_folder: Path, output_folder: Path):
    """Build prompts from JSON files."""
    template = TEMPLATE_SUBPROBLEM_2c
    prompts = []
    
    for json_file in input_folder.glob("*.json"):
        data = read_json(json_file.resolve())
        title = data.get("article_title", "Untitled Article")
        documents = generate_document(
            data,
            include_abstract=True,
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
        for p in prompts:
            f.write(json.dumps(p) + "\n")

    return output_path


def build_prompts_from_markdown(input_folder: Path, output_folder: Path):
    """Build prompts from markdown files."""
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

    output_path = output_folder / "prompts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(p) + "\n")

    return output_path


def build_prompts(input_folder: Path, output_folder: Path, input_format: str):
    """Build prompts based on input format."""
    if input_format == "json":
        return build_prompts_from_json(input_folder, output_folder)
    elif input_format == "markdown":
        return build_prompts_from_markdown(input_folder, output_folder)
    else:
        raise ValueError(f"Unsupported input format: {input_format}")


# ============================================================================
# Results Aggregation Functions
# ============================================================================

def aggregate_results_json(output_folder: Path):
    """Aggregate results from JSON-based processing."""
    def contains_ref(row):
        cp = row["connecting_principle"]
        return "(Ref:" in cp
    
    responses_file = output_folder / "responses.jsonl"
    results_jsonl = output_folder / "results.jsonl"
    results_csv = output_folder / "results.csv"

    results = []
    for row in read_jsonl(responses_file):
        response = str(row["response"])
        filestem = Path(row["from"]).stem
        title = row["title"]
        parsed_json = parse_json(response)

        for parsed in parsed_json:
            for section_data in parsed:
                subsection = section_data.get("subsection")
                triplets = section_data.get("triplets", [])
                for triplet in triplets:
                    new_row = {
                        "title": title,
                        "subsection": subsection,
                        **triplet
                    }
                    if not contains_ref(new_row):
                        continue
                    results.append(new_row)

    results = sorted(results, key=lambda x: x["title"])

    # Write the results to .jsonl format
    with open(results_jsonl, "w", encoding="utf-8") as f:
        for line in results:
            f.write(json.dumps(line) + "\n")

    # Write the results to .csv format
    pd.DataFrame(results).to_csv(results_csv, index=False)

    return results_jsonl, results_csv


def aggregate_results_markdown(output_folder: Path):
    """Aggregate results from markdown-based processing."""
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
                **new_result
            }
            results.append(new_row)

    results = sorted(results, key=lambda x: x["from"])

    # Write the results to .jsonl format
    with open(results_jsonl, "w", encoding="utf-8") as f:
        for line in results:
            f.write(json.dumps(line) + "\n")

    # Write the results to .csv format
    pd.DataFrame(results).to_csv(results_csv, index=False)

    return results_jsonl, results_csv


def aggregate_results(output_folder: Path, input_format: str):
    """Aggregate results based on input format."""
    if input_format == "json":
        return aggregate_results_json(output_folder)
    elif input_format == "markdown":
        return aggregate_results_markdown(output_folder)
    else:
        raise ValueError(f"Unsupported input format: {input_format}")


# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified extraction pipeline for problem 2"
    )
    parser.add_argument(
        "-i", "--input-folder",
        type=Path,
        required=True,
        help="Path to input folder containing JSON or markdown files"
    )
    parser.add_argument(
        "-c", "--config-path",
        type=Path,
        required=True,
        help="Path to model configuration file"
    )
    parser.add_argument(
        "-o", "--output-folder",
        type=Path,
        required=True,
        help="Path to output folder"
    )
    parser.add_argument(
        "-f", "--input-format",
        type=str,
        choices=["json", "markdown"],
        required=True,
        help="Input file format (json or markdown)"
    )
    parser.add_argument(
        "--aggregate-only",
        action="store_true",
        help="Skip inference and only aggregate existing results"
    )
    args = parser.parse_args()

    input_folder = args.input_folder.resolve()
    output_folder = args.output_folder.resolve()
    config_path = args.config_path.resolve()

    responses_file = output_folder / "responses.jsonl"
    responses_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not args.aggregate_only:
        # 1. Build the prompts from the input files
        print("--- Step 1: Building Prompts ---")
        print(f"Input format: {args.input_format}")
        prompts_file = build_prompts(input_folder, output_folder, args.input_format)

        # 2. Run the inference using the generated prompts
        print("\n--- Step 2: Running Inference ---")
        print(f"Using config: {config_path}")
        print(f"Input prompts: {prompts_file}")
        print(f"Saving responses to: {responses_file}")
        
        run_inference(
            str(config_path),
            str(prompts_file),
            str(responses_file)
        )

    # 3. Parse results
    print("\n--- Step 3: Parsing Results ---")
    results_jsonl, results_csv = aggregate_results(output_folder, args.input_format)
    print(f"Saving results to jsonl at: {results_jsonl}")
    print(f"Saving results to csv at: {results_csv}")

    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()