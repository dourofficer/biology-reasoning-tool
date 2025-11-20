from pathlib import Path
import argparse
import re
import json

def extract_results(text):
    """
    This function extracts (abstract + introduction) and results.
    """
    SEP1 = r"\n## results?\n"
    SEP2 = r"\n## discussion\n"

    context, results = re.split(SEP1, text, flags=re.IGNORECASE)
    results = re.split(SEP2, results, flags=re.IGNORECASE)[0]
    return context, results

def extract_subsections(text):
    # \n##          -> A newline, two hashes, and a space.
    # (?!Figure)    -> A "negative lookahead". Asserts that the following text is NOT "Figure".
    #                This is the key part for the exclusion.
    # [^\n]+        -> Matches one or more characters that are NOT a newline (the header text).
    # \n            -> The final newline ending the header line.
    # wrapping the whole pattern in a capturing group (...)
    SEP = r"(\n## (?!Figure)[^\n]+\n)"
    parts = re.split(SEP, text, flags=re.IGNORECASE)
    subsections = []
    for i in range(1, len(parts), 2): # deliberately omit the first, empty element
        subtitle = parts[i]
        content = parts[i+1]
        subsections.append({
            "subtitle": subtitle.strip(),
            "content": content.strip()
        })
    
    return subsections

def main(args):
    assert args.input_path.exists()
    assert args.input_path.suffix.lower() == ".md"

    with open(args.input_path, "r") as f:
        data = f.read()
        
    opening, results = extract_results(data)
    subsections = extract_subsections(results)
    output = {"opening": opening, "results": subsections}

    # Save output
    args.output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = args.input_path.stem
    output_path = args.output_dir / f"{doc_filename}.json"
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to input Markdown file"
    )
    
    parser.add_argument(
        "output_dir",
        type=Path,
        default=Path("./output"),
        help="Output directory for converted files (default: ./output)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)