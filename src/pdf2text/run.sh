#!/bin/bash

PDF_FILE="./testdata/pdf/05.pdf"
MD_DIR="./testdata/markdown"
JSON_DIR="./testdata/structure"

export CUDA_VISIBLE_DEVICES=1

# Check if PDF file exists
if [ -f "$PDF_FILE" ]; then
    base_name=$(basename "$PDF_FILE")
    echo "Converting $base_name to markdown."
    python ocr.py "$PDF_FILE" "$MD_DIR"
    
    # Construct md_file path: remove .pdf extension and add .md, place in MD_DIR
    base_name_no_ext="${base_name%.pdf}"
    md_file="$MD_DIR/${base_name_no_ext}.md"
    
    # Check if markdown file was created successfully
    if [ -f "$md_file" ]; then
        echo "Parsing structure of $md_file"
        python structure.py "$md_file" "$JSON_DIR"
    else
        echo "Warning: Markdown file $md_file was not created"
        exit 1
    fi
else
    echo "Error: PDF file $PDF_FILE not found"
    exit 1
fi

echo "Finished."
