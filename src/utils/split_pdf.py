#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def extract_pages(input_file, pages, output_file=None):
    """Extract specific pages from a PDF file."""
    
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        
        print(f"Input PDF has {total_pages} pages")
        
        # Validate page numbers
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            print(f"Error: Invalid page numbers: {invalid_pages}")
            print(f"Valid range is 1-{total_pages}")
            return False
        
        writer = PdfWriter()
        
        # Add requested pages (convert to 0-based indexing)
        for page_num in sorted(pages):
            writer.add_page(reader.pages[page_num - 1])
            print(f"Added page {page_num}")
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            stem = input_path.stem
            suffix = input_path.suffix
            output_file = f"{stem}_pages_{'_'.join(map(str, sorted(pages)))}{suffix}"
        
        # Write output PDF
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        print(f"Successfully created: {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return False
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Extract specific pages from a PDF file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python split.py document.pdf --pages 11 12 13
  python split.py document.pdf --slice 14 18
  python split.py document.pdf --pages 1 3 5 -o selected_pages.pdf
        """
    )
    
    parser.add_argument('filename', help='Input PDF file')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--pages', type=int, nargs='+', 
                      help='Specific page numbers to extract')
    group.add_argument('--slice', type=int, nargs=2, metavar=('START', 'END'),
                      help='Extract pages from START to END (inclusive)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.filename).exists():
        print(f"Error: File '{args.filename}' not found")
        sys.exit(1)
    
    # Determine pages to extract
    if args.pages:
        pages = args.pages
    else:  # args.slice
        start, end = args.slice
        if start > end:
            print(f"Error: Start page ({start}) must be less than or equal to end page ({end})")
            sys.exit(1)
        pages = list(range(start, end + 1))
    
    # Extract pages
    success = extract_pages(args.filename, pages, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
