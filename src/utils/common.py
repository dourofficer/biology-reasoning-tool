import json
import re

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