import time
import argparse
from pathlib import Path
from typing import Dict, Set, List

from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    NodeItem,
    ProvenanceItem,
    RefItem,
    TableData,
)
from docling_core.types.doc.document import ContentLayer
from docling_ibm_models.list_item_normalizer.list_marker_processor import (
    ListItemMarkerProcessor,
)
from docling_ibm_models.reading_order.reading_order_rb import (
    PageElement as ReadingOrderPageElement,
    ReadingOrderPredictor,
)
from pydantic import BaseModel, ConfigDict

from docling.datamodel.base_models import (
    BasePageElement,
    Cluster,
    ContainerElement,
    FigureElement,
    Table,
    TextElement,
)
from docling.datamodel.document import ConversionResult
from docling.utils.profiling import ProfilingScope, TimeRecorder

from docling.models.readingorder_model import ReadingOrderModel

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from docling.utils.layout_postprocessor import LayoutPostprocessor
from docling_core.types.doc import DocItemLabel

def patch_latyout_postprocessor(thresholds=None):
    if thresholds is None:
        thresholds = {DocItemLabel.TEXT: 0.9, DocItemLabel.SECTION_HEADER: 0.8}
    for label in thresholds:
        LayoutPostprocessor.CONFIDENCE_THRESHOLDS[label] = thresholds[label]

def patch_reading_order_model_with_filter(keep_labels: Set[DocItemLabel] = None):
    """
    Monkey patch the ReadingOrderModel to filter clusters during document assembly.
    Use this if you want to modify existing conversion pipelines.
    """
    if keep_labels is None:
        keep_labels = {DocItemLabel.TEXT, DocItemLabel.SECTION_HEADER}
    
    def custom_readingorder_elements_to_docling_doc(  # noqa: C901
        self,
        conv_res: ConversionResult,
        ro_elements: List[ReadingOrderPageElement],
        el_to_captions_mapping: Dict[int, List[int]],
        el_to_footnotes_mapping: Dict[int, List[int]],
        el_merges_mapping: Dict[int, List[int]],
    ) -> DoclingDocument:
        id_to_elem = {
            RefItem(cref=f"#/{elem.page_no}/{elem.cluster.id}").cref: elem
            for elem in conv_res.assembled.elements
        }
        cid_to_rels = {rel.cid: rel for rel in ro_elements}

        origin = DocumentOrigin(
            mimetype="application/pdf",
            filename=conv_res.input.file.name,
            binary_hash=conv_res.input.document_hash,
        )
        doc_name = Path(origin.filename).stem
        out_doc: DoclingDocument = DoclingDocument(name=doc_name, origin=origin)

        for page in conv_res.pages:
            page_no = page.page_no + 1
            size = page.size

            assert size is not None, "Page size is not initialized."

            out_doc.add_page(page_no=page_no, size=size)

        current_list = None
        skippable_cids = {
            cid
            for mapping in (
                el_to_captions_mapping,
                el_to_footnotes_mapping,
                el_merges_mapping,
            )
            for lst in mapping.values()
            for cid in lst
        }

        page_no_to_pages = {p.page_no: p for p in conv_res.pages}

        for rel in ro_elements:
            if rel.cid in skippable_cids: continue
            element = id_to_elem[rel.ref.cref]
            page_height = page_no_to_pages[element.page_no].size.height  # type: ignore

            ## KEY MODIFICATION, ONLY CARE ABOUT TEXT and HEADERS ##
            if element.label not in keep_labels: continue ##########
            ########################################################
            
            new_item, current_list = self._handle_text_element(
                element, out_doc, current_list, page_height
            )

            if rel.cid in el_merges_mapping.keys():
                for merged_cid in el_merges_mapping[rel.cid]:
                    merged_elem = id_to_elem[cid_to_rels[merged_cid].ref.cref]

                    self._merge_elements(
                        element, merged_elem, new_item, page_height
                    )

        return out_doc
    
    # Apply patches
    ReadingOrderModel._readingorder_elements_to_docling_doc = \
        custom_readingorder_elements_to_docling_doc

def create_converter(num_threads: int = 32) -> DocumentConverter:
    
    # Create converter with pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["en"]
    pipeline_options.layout_options.create_orphan_clusters = False # Still need this
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=num_threads, 
        device=AcceleratorDevice.AUTO
    )
    
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

def convert_document(
    input_path: Path, output_dir: Path, num_threads: int = 32
) -> None:

    converter = create_converter()
    
    # Convert document
    print(f"Converting: {input_path}")
    start_time = time.time()
    result = converter.convert(input_path)
    end_time = time.time() - start_time
    print(f"Document converted in {end_time:.2f} seconds.")
    
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
        description="Convert PDF documents to Markdown with some patching"
    )
    
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to input PDF file"
    )
    
    parser.add_argument(
        "output_dir",
        type=Path,
        default=Path("./output"),
        help="Output directory for converted files (default: ./output)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    # Read arguments
    args = parse_arguments()
    assert args.input_path.exists()
    assert args.input_path.suffix.lower() == '.pdf'
    
    # Apply the patch once
    keep_items = {DocItemLabel.TEXT: 0.9, DocItemLabel.SECTION_HEADER: 0.8}
    patch_reading_order_model_with_filter(keep_items)
    patch_latyout_postprocessor(keep_items)

    convert_document(
        input_path=args.input_path,
        output_dir=args.output_dir
    )
    
    