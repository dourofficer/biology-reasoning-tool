#!/bin/bash

# visualize predicted layout of a PDF file
CUDA_VISIBLE_DEVICES=1 python annotate.py input_file.pdf output_file.pdf

# visualize unmasked components that will be used for OCR
# CUDA_VISIBLE_DEVICES=1 python annotate.py input_file.pdf output_file.pdf --mask
