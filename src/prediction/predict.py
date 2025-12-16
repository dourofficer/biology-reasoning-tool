from .templates import TEMPLATE_PREDICTION_1, TEMPLATE_PREDICTION_2
from ..utils.inference import run_inference
from ..utils.common import read_jsonl, read_json, parse_json, read_tsv
from ..utils.document_builder import generate_document
from pathlib import Path
import pandas as pd
import re
import json
import argparse

def build_prompt(prefix, input):
    content_type = input["type"]
    query = input["main"]
    template = TEMPLATE_PREDICTION_1 if ("Q1" in content_type) else TEMPLATE_PREDICTION_2

    content = f"{prefix}\n\nQUERY: {query}"
    prompt = template.replace("{{main_content}}", content)
    return prompt

def build_prompts(paper_path: Path, triplets_file: Path, output_folder: Path):
    """
    Finds all .md files in a folder, creates a prompt for each, and saves them
    to a 'tmp.jsonl' file in the same folder.
    
    Args:
        input_folder: The path to the folder containing the .md files.
    """
    triplets = read_tsv(triplets_file)
    paper = read_json(paper_path)
    prefix = generate_document(
        paper,
        include_intro=True,
        include_result=False,
        chunk_subsections=False,
        include_figures=False,
        include_discussion=False
    )[0].strip()
    prompts = []
    for triplet in triplets:
        prompt = build_prompt(prefix, triplet)
        prompts.append({
            "prompt": prompt,
            **triplet
        })

    output_path = output_folder / "prompts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in prompts[:]:
            f.write(json.dumps(p) + "\n")

    return output_path

def aggregate_results(output_folder: Path):
    
    responses_file = output_folder / "responses.jsonl"
    results_jsonl = output_folder / "results.jsonl"
    results_csv = output_folder / "results.csv"

    results = []
    for row in read_jsonl(responses_file):
        response = str(row["response"])
        parsed_json = parse_json(response)[0]
        new_row = dict(
            type=row["type"],
            subsection=row["subsection"],
            main=row["main"],
            context=row["context"],
            outcome=row["outcome"],
            predicted_context=parsed_json["context"],
            predicted_outcome=parsed_json["outcome"]
        )
        results.append(new_row)

    # Write the results to .jsonl format
    with open(results_jsonl, "w", encoding="utf-8") as f:
        for line in results[:]:
            f.write(json.dumps(line) + "\n")

    # Write the results to .csv format
    pd.DataFrame(results).to_csv(results_csv, index=False)

    return results_jsonl, results_csv

if __name__ == "__main__":
    # build_prompts(
    #     paper_path=Path("./data/casestudies/json/mechanical.json"),
    #     triplets_file=Path("./data/casestudies/triplets.linhhuynh.mechanical.tsv"),
    #     output_folder=Path("./data/casestudies/prediction/gemini-3-pro")
    # )
    aggregate_results(
        output_folder=Path("./data/casestudies/prediction/gemini-3-pro")
    )