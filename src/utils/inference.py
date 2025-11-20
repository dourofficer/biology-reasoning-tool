import json
import requests
import time
import argparse
import threading
import os
import yaml
from tqdm import tqdm

def send_request(url, pload_config, data, request_id, results, errors, semaphore, pbar):
    """Sends a single request to the vLLM server."""
    headers = {"Content-Type": "application/json"}
    prompt = data.get("prompt")
    
    pload = {
        **pload_config,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        semaphore.acquire()
        response = requests.post(url, headers=headers, json=pload, timeout=1200)
        response.raise_for_status()

        response_json = response.json()
        results[request_id] = {
            "request_id": request_id,
            "reasoning": response_json["choices"][0]["message"]["reasoning_content"],
            "response": response_json["choices"][0]["message"]["content"],
            **data
        }
    except requests.exceptions.RequestException as e:
        errors[request_id] = str(e)
        results[request_id] = {
            "prompt": prompt,
            "response": None,
            **data
        }
    finally:
        semaphore.release()
        pbar.update(1)

def run_inference(config_path, input_file, results_file):
    """Run batch inference with config file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Extract connection params
    hostname = config.pop("hostname")
    port = config.pop("port")
    concurrent_requests = config.pop("concurrent_requests", 10)
    
    url = f"http://{hostname}:{port}/v1/chat/completions"
    pload_config = config  # Remaining config is for payload
    
    dataset = []
    with open(input_file, "r") as f:
        for line in f:
            dataset.append(json.loads(line))

    results = {}
    errors = {}
    start_time = time.time()

    semaphore = threading.Semaphore(concurrent_requests)

    with tqdm(total=len(dataset), desc="Processing requests") as pbar:
        threads = []
        for i, data in enumerate(dataset):
            thread = threading.Thread(
                target=send_request, 
                args=(url, pload_config, data, i, results, errors, semaphore, pbar)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time

    sorted_results = [results[i] for i in sorted(results.keys())]

    with open(results_file, "w") as outfile:
        for result in sorted_results:
            json.dump(result, outfile)
            outfile.write('\n')

    successful_requests = sum(1 for res in results.values() if res["response"] is not None)
    total_requests = len(dataset)
    throughput = successful_requests / elapsed_time if elapsed_time > 0 else 0

    stats = {
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
        print("Errors:")
        print("=" * 20)
        for request_id, error in errors.items():
            print(f"Request ID: {request_id}, Error: {error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch inference script for vLLM server.")
    parser.add_argument("--config", type=str, required=True, help="YAML config file")
    parser.add_argument("--input-file", type=str, required=True, help="JSONL file with input prompts")
    parser.add_argument("--results-file", type=str, required=True, help="Output file for results (JSONL)")
    args = parser.parse_args()

    run_inference(args.config, args.input_file, args.results_file)