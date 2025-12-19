import json
import requests
import time
import argparse
import os
import yaml
import base64
import mimetypes
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def encode_file_to_base64(file_path):
    """Read and encode file to base64, also detect MIME type."""
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Fallback MIME type detection based on extension
    if mime_type is None:
        ext = os.path.splitext(file_path)[1].lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')
    
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')
    
    return file_data, mime_type

def send_request(url, generation_config, api_key, data, request_id):
    """Sends a single request to the Google Gemini API with optional file attachment."""
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    prompt = data.get("prompt")
    file_path = data.get("file_path")
    
    # Build parts array
    parts = []
    
    # Add text prompt
    if prompt:
        parts.append({"text": prompt})

    # Add file if provided
    if file_path:
        try:
            file_data, mime_type = encode_file_to_base64(file_path)
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": file_data
                }
            })
        except Exception as e:
            error_entry = (request_id, f"File encoding error: {str(e)}")
            result_entry = {
                "request_id": request_id,
                "prompt": prompt,
                "response": None,
                "error": f"File encoding error: {str(e)}",
                **data
            }
            return request_id, result_entry, error_entry
    
    # Gemini payload structure
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": generation_config
    }
    
    result_entry = {}
    error_entry = None
    
    try:
        # Timeout set to 60s per request, adjust as needed
        response = requests.post(url, headers=headers, json=payload, timeout=900)
        
        # Check for HTTP errors
        if response.status_code != 200:
            try:
                err_msg = response.json().get('error', {}).get('message', response.text)
            except:
                err_msg = response.text
            raise Exception(f"HTTP {response.status_code}: {err_msg}")
        
        response_json = response.json()
        
        # Parse Gemini Response
        candidates = response_json.get("candidates", [])
        
        if not candidates:
            prompt_feedback = response_json.get("promptFeedback", {})
            raise Exception(f"No candidates returned. Feedback: {prompt_feedback}")
        
        candidate = candidates[0]
        finish_reason = candidate.get("finishReason")
        
        # Check if content was generated
        if "content" in candidate and "parts" in candidate["content"]:
            text_content = candidate["content"]["parts"][0]["text"]
        else:
            text_content = None
            if finish_reason != "STOP":
                raise Exception(f"Generation stopped due to: {finish_reason}")
        
        reasoning = None 
        
        result_entry = {
            "request_id": request_id,
            "reasoning": reasoning,
            "response": text_content,
            "finish_reason": finish_reason,
            **data
        }
        
    except Exception as e:
        error_entry = (request_id, str(e))
        result_entry = {
            "request_id": request_id,
            "prompt": prompt,
            "response": None,
            "error": str(e),
            **data
        }
    
    return request_id, result_entry, error_entry

def run_inference(config_path, input_file, results_file):
    """Run batch inference with config file using ThreadPoolExecutor."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Extract connection specific details
    api_key = config.pop("api_key")
    model_name = config.pop("model_name", "gemini-2.0-flash")
    concurrent_requests = config.pop("concurrent_requests", 10)
    
    # Google API Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    # Remaining config keys (temp, top_p, thinkingConfig) become generationConfig
    generation_config = config
    
    dataset = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip(): # Skip empty lines
                dataset.append(json.loads(line))
    
    results = {}
    errors = {}
    
    start_time = time.time()
    print(f"Starting inference on {model_name} with {concurrent_requests} concurrent workers...")
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        # Submit all tasks to the pool
        future_to_req = {
            executor.submit(send_request, url, generation_config, api_key, data, i): i 
            for i, data in enumerate(dataset)
        }
        
        # Process results as they complete
        with tqdm(total=len(dataset), desc="Processing requests") as pbar:
            for future in as_completed(future_to_req):
                request_id, result_data, error_data = future.result()
                
                results[request_id] = result_data
                if error_data:
                    errors[error_data[0]] = error_data[1]
                
                pbar.update(1)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Write sorted results
    sorted_results = [results[i] for i in sorted(results.keys())]
    with open(results_file, "w") as outfile:
        for result in sorted_results:
            json.dump(result, outfile)
            outfile.write('\n')
    
    successful_requests = sum(1 for res in results.values() if res.get("response") is not None)
    total_requests = len(dataset)
    throughput = successful_requests / elapsed_time if elapsed_time > 0 else 0
    
    stats = {
        "model": model_name,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": total_requests - successful_requests,
        "failed_request_ids": list(errors.keys()),
        "elapsed_time": elapsed_time,
        "throughput": throughput,
    }
    
    input_file_name = os.path.splitext(input_file)[0]
    stats_file_name = f"{input_file_name}_stats.json"
    
    with open(stats_file_name, "w") as f:
        json.dump(stats, f, indent=4)
    
    print(f"\nStatistics written to {stats_file_name}")
    print(f"Throughput: {throughput:.2f} requests/second")
    
    if errors:
        print("=" * 20)
        print(f"Encountered {len(errors)} errors. First 5:")
        for i, (rid, err) in enumerate(errors.items()):
            if i >= 5: break
            print(f"ID {rid}: {err}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch inference script for Google Gemini API.")
    parser.add_argument("--config", type=str, required=True, help="YAML config file")
    parser.add_argument("--input-file", type=str, required=True, help="JSONL file with input prompts")
    parser.add_argument("--results-file", type=str, required=True, help="Output file for results (JSONL)")
    
    args = parser.parse_args()
    
    run_inference(args.config, args.input_file, args.results_file)