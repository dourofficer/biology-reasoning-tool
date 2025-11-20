from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np
import random
import argparse

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.document import InputDocument
from docling.datamodel.base_models import InputFormat
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.pipeline_options import LayoutOptions
from docling.datamodel.base_models import BoundingBox, Cluster
from docling.models.layout_model import LayoutModel
from docling_core.types.doc import DocItemLabel
from PIL import ImageDraw, ImageFont, Image
from tqdm import tqdm


COLOR_MAP = {
    DocItemLabel.TEXT: "blue",
    DocItemLabel.SECTION_HEADER: "red", 
    DocItemLabel.TABLE: "green",
    DocItemLabel.PICTURE: "purple",
    DocItemLabel.CAPTION: "orange",
    DocItemLabel.FOOTNOTE: "brown",
    DocItemLabel.PAGE_HEADER: "pink",
    DocItemLabel.PAGE_FOOTER: "pink",
    DocItemLabel.LIST_ITEM: "cyan",
    DocItemLabel.FORMULA: "yellow",
    DocItemLabel.CODE: "gray",
}

def images_to_pdf(image_list, output_path):    
    # Convert all images to RGB mode (required for PDF)
    rgb_images = []
    for img in image_list:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        rgb_images.append(img)
    
    # Save first image as PDF, append the rest
    rgb_images[0].save(
        output_path, 
        format='PDF', 
        save_all=True, 
        append_images=rgb_images[1:]
    )

def analyze_layout(
    input_doc: InputDocument, 
    page: int = 0,
    layout_model: str = None, 
    scale: float = 3.0
) -> Tuple[Image.Image, List[Cluster]]:
    
    # 1. Load specific page
    backend = input_doc._backend
    page_backend = backend.load_page(page)
    assert page_backend.is_valid()
    
    # 2. Get page image (this is what the layout model expects)
    page_image = page_backend.get_page_image(scale=scale)
    page_size = page_backend.get_size()
    
    # 3. Run layout prediction
    predictions = layout_model.layout_predictor.predict_batch([page_image])
    page_predictions = predictions[0]
    
    # 4. Convert predictions to clusters
    clusters = []
    for ix, pred_item in enumerate(page_predictions):
        # Convert label string to DocItemLabel enum
        label_str = pred_item["label"].lower().replace(" ", "_").replace("-", "_")
        label = DocItemLabel(label_str)
        
        cluster = Cluster(
            id=ix,
            label=label,
            confidence=pred_item["confidence"],
            bbox=BoundingBox.model_validate(pred_item),
            cells=[]
        )
        clusters.append(cluster)
    
    # 5. Cleanup
    # page_backend.unload()
    # backend.unload()
    
    return page_image, clusters

def mask_page(
    image: Image.Image, 
    clusters: List[Cluster],
    allowed_labels: List[str]
):
    # Create a copy to avoid modifying original
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)

    for cluster in clusters:
        if cluster.label in allowed_labels: continue
            
        # Masking unwanted components
        color = "white"
        bbox = cluster.bbox
        rect = [bbox.l, bbox.t, bbox.r, bbox.b]
        draw.rectangle(rect, fill=color)
        
    return annotated_image

def mask_file(
    input_file_path, output_file_path,
    layout_model,
    allowed_labels = [DocItemLabel.TEXT, DocItemLabel.SECTION_HEADER]
):
    # 2. Load PDF using InputDocument (it handles backend internally)
    file_path = Path(input_file_path)
    input_doc = InputDocument(
        path_or_stream=file_path,
        format=InputFormat.PDF,
        backend=PyPdfiumDocumentBackend
    )
    if not input_doc.valid:
        raise ValueError(f"Document {file_path} is not valid")   
        
    backend = input_doc._backend
    page_count = backend.page_count()
    images, masked_images = [], []
    for page in tqdm(range(page_count)):
        image, clusters = analyze_layout(input_doc, page, layout_model)
        masked_image = mask_page(image, clusters, allowed_labels)
        images.append(image)
        masked_images.append(masked_image)

    output_file = Path(output_file_path)
    images_to_pdf(masked_images, output_file)
    # output_dir.mkdir(parents=True, exist_ok=True)
    # for i, img in enumerate(masked_images):
    #     img.save(output_dir / f"page_{i:02d}.png")

    return image, masked_images

## UNUSED
def annotate_page(
    image: Image.Image, 
    clusters: List[Cluster], 
    show_labels: bool = True, 
    show_confidence: bool = True
) -> Image.Image:
    """
    Draw layout annotations on the page image.
    
    Args:
        image: Page image
        clusters: Layout clusters from analyze_layout()
        show_labels: Whether to show label names
        show_confidence: Whether to show confidence scores
        
    Returns:
        Annotated image
    """
    # Create a copy to avoid modifying original
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)
    
    try:
        # Try to use a font (may not be available on all systems)
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    
    for cluster in clusters:
        # Get color for this element type
        color = COLOR_MAP.get(cluster.label, "black")
        
        # Draw bounding box
        bbox = cluster.bbox
        rect = [bbox.l, bbox.t, bbox.r, bbox.b]
        draw.rectangle(rect, outline=color, width=2)
        
        # Add label text
        if show_labels or show_confidence:
            label_text = ""
            if show_labels:
                label_text += cluster.label.value
            if show_confidence:
                if label_text:
                    label_text += f" ({cluster.confidence:.2f})"
                else:
                    label_text = f"{cluster.confidence:.2f}"
            
            # Draw text background
            text_bbox = draw.textbbox((bbox.l, bbox.t), label_text, font=font)
            draw.rectangle(text_bbox, fill=color, outline=color)
            
            # Draw text
            draw.text((bbox.l, bbox.t), label_text, fill="white", font=font)
    
    return annotated_image

def annotate_file(
    input_file_path, output_file_path, layout_model
):
    # 2. Load PDF using InputDocument (it handles backend internally)
    file_path = Path(input_file_path)
    input_doc = InputDocument(
        path_or_stream=file_path,
        format=InputFormat.PDF,
        backend=PyPdfiumDocumentBackend
    )
    if not input_doc.valid:
        raise ValueError(f"Document {file_path} is not valid")   
        
    backend = input_doc._backend
    page_count = backend.page_count()
    images, masked_images = [], []
    for page in tqdm(range(page_count)):
        image, clusters = analyze_layout(input_doc, page, layout_model)
        masked_image = annotate_page(image, clusters)
        images.append(image)
        masked_images.append(masked_image)

    output_file = Path(output_file_path)
    images_to_pdf(masked_images, output_file)
    # output_dir.mkdir(parents=True, exist_ok=True)
    # for i, img in enumerate(masked_images):
    #     img.save(output_dir / f"page_{i:02d}.png")

    return image, masked_images

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process PDF files with layout model masking"
    )
    
    parser.add_argument(
        "input_file", 
        type=str,
        help="Path to input PDF file"
    )
    
    parser.add_argument(
        "output_file", 
        type=str,
        help="Path to output masked PDF file"
    )
    
    parser.add_argument(
        "--threads", 
        type=int, 
        default=32,
        help="Number of threads for processing (default: 32)"
    )

    parser.add_argument(
        "--mask",
        action="store_true",
        help="Visualize unmasked components for OCR"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    ## RUN
    args = parse_arguments()
    layout_model = LayoutModel(
        artifacts_path=None,  # Will auto-download models
        accelerator_options=AcceleratorOptions(
            num_threads=args.threads, 
            device=AcceleratorDevice.AUTO
        ),
        options=LayoutOptions()  # Use default layout options
    )

    func = mask_file if args.mask else annotate_file
    images, masked_images = func(
        args.input_file, 
        args.output_file, 
        layout_model
    )