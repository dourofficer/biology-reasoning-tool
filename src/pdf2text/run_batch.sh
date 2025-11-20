#!/bin/bash

PDF_DIR="./testdata/casestudies/pdf"
MD_DIR="./testdata/casestudies/markdown"
JSON_DIR="./testdata/casestudies/json"

export CUDA_VISIBLE_DEVICES=1


for pdf_file in "$PDF_DIR"/*.pdf; do
    base_name=$(basename "$pdf_file")
    if [ -f "$pdf_file" ]; then # check if file really exists
        echo "Converting $base_name to markdown."
        python ocr.py "$pdf_file" "$MD_DIR"
    fi
    
    # Construct md_file path: remove .pdf extension and add .md, place in MD_DIR
    base_name_no_ext="${base_name%.pdf}"
    md_file="$MD_DIR/${base_name_no_ext}.md"
    if [ -f "$md_file" ]; then
        echo "Parsing structure of $md_file"
        python structure.py "$md_file" "$JSON_DIR"
    else
        echo "Warning: Markdown file $md_file was not created"
    fi

    echo "Finished."
done
