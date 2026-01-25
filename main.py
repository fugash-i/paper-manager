import argparse
import sys
from modules.input_handler import get_doi_from_input
from modules.metadata_fetcher import fetch_metadata
from modules.translator import translate_abstract
from modules.notion_api import create_notion_page
from modules.exporter import get_papers, nat, bib
from config.settings import validate_config, EXPORT_DIR
import os

def main():
    parser = argparse.ArgumentParser(description="Paper Manager: Fetch metadata and save to Notion.")
    # Make input optional because we might just be verifying config or exporting
    parser.add_argument("input", nargs='?', help="DOI string, URL, or path to PDF file.")
    
    # Export arguments
    parser.add_argument("--export", help="Export papers with this 'cite key' from Notion.")
    parser.add_argument("--format", choices=['nat', 'bib'], default='nat', help="Export format: 'nat' (Nature-style) or 'bib' (BibTeX). Default: nat.")
    parser.add_argument("--output", help="Path to save the exported file (e.g., output.rtf or output.bib). If not provided, prints to stdout.")
    
    # Translation options
    parser.add_argument("--no-translate", action="store_true", help="Skip automatic translation of the abstract.")

    args = parser.parse_args()

    # 0. Validate Config
    if not validate_config():
        sys.exit(1)

    # --- EXPORT MODE ---
    if args.export:
        print(f"Exporting papers with cite key: '{args.export}' in format: {args.format}...")
        papers = get_papers(args.export)
        
        if not papers:
            print(f"No papers found with cite key '{args.export}'.")
            return

        print(f"Found {len(papers)} papers.")
        if args.format == 'nat':
            output = nat(papers)
        else:
            output = bib(papers)
        
        if args.output:
            output_path = args.output
        else:
            # Default save location
            ext = ".txt" if args.format == 'nat' else ".bib"
            filename = f"{args.export}{ext}"
            
            # Ensure directory exists
            if not os.path.exists(EXPORT_DIR):
                try:
                    os.makedirs(EXPORT_DIR)
                    print(f"Created export directory: {EXPORT_DIR}")
                except Exception as e:
                    print(f"Error creating directory {EXPORT_DIR}: {e}")
                    return
            
            output_path = os.path.join(EXPORT_DIR, filename)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Successfully saved export to: {output_path}")
        except Exception as e:
            print(f"Error saving to file: {e}")
        return
    
    # --- IMPORT MODE ---
    if not args.input:
        parser.print_help()
        print("\nError: Please provide an input (DOI/PDF) OR use --export.")
        sys.exit(1)

    print(f"Processing input: {args.input}...")

    # 1. Extract DOI
    doi = get_doi_from_input(args.input)
    if not doi:
        print("Error: Could not extract a valid DOI from the input.")
        if args.input.endswith('.pdf'):
            print("Tip: Ensure the PDF is text-readable and contains a DOI string.")
        sys.exit(1)
    
    print(f"Found DOI: {doi}")

    # 2. Fetch Metadata
    print("Fetching metadata...")
    metadata = fetch_metadata(doi)
    if not metadata:
        print("Error: Failed to fetch metadata.")
        sys.exit(1)
    
    print(f"Title: {metadata.get('title')}")
    print(f"Authors: {metadata.get('display_authors')}")

    # 3. Translate Abstract
    abstract = metadata.get('abstract', '')
    translation = ""
    if abstract:
        if args.no_translate:
            print("Skipping translation as requested.")
        else:
            print("Translating abstract (this may take a moment)...")
            translation = translate_abstract(abstract)
            print("Translation completed.")
    else:
        print("No abstract found to translate.")

    # 4. Save to Notion
    print("Saving to Notion...")
    page_url = create_notion_page(metadata, translation)
    
    if page_url:
        print(f"Success! Page created: {page_url}")
    else:
        print("Error: Failed to create Notion page.")
        sys.exit(1)

if __name__ == "__main__":
    main()
