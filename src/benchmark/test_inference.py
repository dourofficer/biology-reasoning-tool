from pathlib import Path
from ..utils.inference import run_inference

def main():
    root = Path(__file__).parent.parent.parent
    
    config_path = root / "configs/gpt-oss-20b.yaml"
    input_file = root / "data/inference_samples/prompts.jsonl"
    results_file = root / "data/inference_samples/results.jsonl"
    
    run_inference(str(config_path), str(input_file), str(results_file))

if __name__ == "__main__":
    main()