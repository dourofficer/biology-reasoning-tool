#!/usr/bin/env python3
"""
Document converter using Docling VLM Pipeline with SmolDocling + VLLM.
Converts PDF documents to Markdown using Vision-Language Models.
"""

import argparse
import time
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import (
    InlineVlmOptions,
    InferenceFramework,
    ResponseFormat
)
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from docling.datamodel.vlm_model_specs import SMOLDOCLING_VLLM


def create_vlm_converter(
    response_format: ResponseFormat = ResponseFormat.DOCTAGS,
    force_backend_text: bool = False,
    scale: float = 2.0,
    num_threads: int = 32,
    artifacts_path: Optional[Path] = None
) -> DocumentConverter:
    """
    Create SmolDocling VLLM converter for PDF to Markdown conversion.
    
    Args:
        response_format: Output format from VLM
        force_backend_text: Whether to use backend text extraction over VLM text
        scale: Image scaling factor for VLM processing
        num_threads: Number of processing threads
        artifacts_path: Path to model artifacts
        
    Returns:
        Configured DocumentConverter instance
    """
    # Configure accelerator options
    accelerator_options = AcceleratorOptions(
        num_threads=num_threads,
        device=AcceleratorDevice.AUTO
    )
    
    # Use SmolDocling with VLLM
    vlm_options = SMOLDOCLING_VLLM
    vlm_options.scale = scale
    vlm_options.response_format = response_format
    
    print("Using SmolDocling with VLLM framework")
    
    # Create VLM pipeline options
    pipeline_options = VlmPipelineOptions(
        vlm_options=vlm_options,
        accelerator_options=accelerator_options,
        artifacts_path=str(artifacts_path) if artifacts_path else None,
        force_backend_text=force_backend_text,
        generate_page_images=False,  # Save memory
    )
    
    # Create format options with VLM pipeline
    pdf_format_option = PdfFormatOption(
        pipeline_cls=VlmPipeline,
        pipeline_options=pipeline_options
    )
    
    format_options = {
        InputFormat.PDF: pdf_format_option,
        InputFormat.IMAGE: pdf_format_option,
    }
    
    return DocumentConverter(format_options=format_options)


def convert_document(
    input_path: Path, 
    output_dir: Path, 
    response_format: ResponseFormat = ResponseFormat.DOCTAGS,
    force_backend_text: bool = False,
    scale: float = 2.0,
    num_threads: int = 32,
    artifacts_path: Optional[Path] = None
) -> None:
    """
    Convert a document using SmolDocling VLLM pipeline.
    
    Args:
        input_path: Path to input document
        output_dir: Directory for output files
        response_format: VLM response format
        force_backend_text: Use backend text extraction
        scale: Image scaling factor
        num_threads: Number of processing threads
        artifacts_path: Path to model artifacts
    """
    # Create VLM converter
    converter = create_vlm_converter(
        response_format=response_format,
        force_backend_text=force_backend_text,
        scale=scale,
        num_threads=num_threads,
        artifacts_path=artifacts_path
    )
    
    # Convert document
    print(f"Converting: {input_path}")
    print("Note: First run may take longer due to model download/initialization")
    
    start_time = time.time()
    result = converter.convert(input_path)
    end_time = time.time() - start_time
    print(f"Document converted in {end_time:.2f} seconds using SmolDocling VLLM")
    
    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = result.input.file.stem
    output_path = output_dir / f"{doc_filename}.md"
    
    with output_path.open("w", encoding="utf-8") as fp:
        fp.write(result.document.export_to_markdown())
    
    print(f"Output saved to: {output_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to Markdown using SmolDocling + VLLM"
    )
    
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to input PDF file"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Output directory for converted files (default: ./output)"
    )
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=32,
        help="Number of processing threads (default: 32)"
    )
    
    parser.add_argument(
        "--response-format",
        choices=["doctags", "html"],
        default="doctags",
        help="VLM response format (default: doctags)"
    )
    
    parser.add_argument(
        "--force-backend-text",
        action="store_true",
        help="Use backend text extraction instead of VLM text (requires doctags format)"
    )
    
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Image scaling factor for VLM processing (default: 2.0)"
    )
    
    parser.add_argument(
        "--artifacts-path",
        type=Path,
        help="Path to model artifacts directory"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_arguments()
    
    # Validate input file
    if not args.input_path.exists():
        print(f"Error: Input file '{args.input_path}' does not exist.")
        return
    
    if not args.input_path.suffix.lower() in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']:
        print(f"Warning: Input file '{args.input_path}' may not be a supported format.")
    
    # Validate arguments
    if args.force_backend_text and args.response_format != "doctags":
        print("Error: --force-backend-text requires --response-format doctags")
        return
    
    response_format = ResponseFormat.DOCTAGS if args.response_format == "doctags" else ResponseFormat.HTML
    
    # Convert document
    try:
        convert_document(
            input_path=args.input_path,
            output_dir=args.output_dir,
            response_format=response_format,
            force_backend_text=args.force_backend_text,
            scale=args.scale,
            num_threads=args.threads,
            artifacts_path=args.artifacts_path
        )
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
