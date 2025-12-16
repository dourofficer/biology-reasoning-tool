import json
import csv
import re
import pandas as pd

def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def read_jsonl(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                json_object = json.loads(line.strip())
                data.append(json_object)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line.strip()}. Error: {e}")
    return data

def read_csv(filepath):
    df = pd.read_csv(filepath, keep_default_na=False)
    return df.to_dict(orient='records')

def read_tsv(filepath):
    df = pd.read_csv(filepath, sep='\t', keep_default_na=False)
    return df.to_dict(orient='records')

def parse_json_from_text(text_blob: str):
    pattern = r"```json(.*?)```"
    match = re.search(pattern, text_blob, re.DOTALL)

    if not match: return None

    json_string = match.group(1).strip()
    try: 
        data = json.loads(json_string)
    except: 
        data = None
    return data

def parse_json(text_blob: str):
    text_blob = text_blob.strip()
    try:
        data = json.loads(text_blob)
        return [data]
    except:
        pass

    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, text_blob, re.DOTALL)

    if not matches:
        return []

    results = []
    for json_string in matches:
        json_string = json_string.strip()
        try:
            data = json.loads(json_string)
            results.append(data)
        except:
            pass
    
    return results

def flatten_json_to_csv(json_file, csv_file):
    """

    This is the data structure to flatten out:
    ```json
    {
    "paper_title": "Title of the paper",
    "extractions": [
        {
        "subsection": "Name of subsection",
        "triplets": [
            {
            "type": "Q1",
            "main_content": "The research question or goal (verbatim) OR (missing)",
            "context": "Background/justification for approach (verbatim) OR (missing)",
            "outcome": "The method/analysis performed (verbatim) OR (missing)"
            },
            {
            "type": "Q2",
            "main_content": "The empirical observation (verbatim) OR (missing)",
            "context": "Literature or established principle (verbatim) OR (missing)",
            "outcome": "The interpretation/conclusion (verbatim) OR (missing)"
            }
        ]
        }
    ]
    }
    ```
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Paper Title', 'Subsection', 'Type', 'Main Content', 'Context', 'Outcome'])

        title = data.get('paper_title', '')
        for section in data.get('extractions', []):
            sub_name = section.get('subsection', '')
            for triplet in section.get('triplets', []):
                writer.writerow([
                    title,
                    sub_name,
                    triplet.get('type', ''),
                    triplet.get('main_content', ''),
                    triplet.get('context', ''),
                    triplet.get('outcome', '')
                ])