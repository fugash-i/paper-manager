import streamlit as st
import os
import tempfile
from modules.input_handler import get_doi_from_input
from modules.metadata_fetcher import fetch_metadata
from modules.translator import translate_abstract
from modules.notion_api import create_notion_page
from modules.exporter import get_papers, nat, bib
from config.settings import validate_config, EXPORT_DIR

def main():
    st.set_page_config(page_title="Paper Manager", page_icon="📄")
    st.title("📄 Paper Manager")

    # Check Configuration
    with st.sidebar:
        st.header("Status")
        if validate_config():
            st.success("Configuration Valid")
        else:
            st.error("Missing Environment Variables")
            st.warning("Please check .env file")

    tab1, tab2 = st.tabs(["Import Paper", "Export Citations"])

    # --- TAB 1: IMPORT ---
    with tab1:
        st.header("Import Paper to Notion")
        
        # Input Method 1: Text Input
        doi_input = st.text_input("Enter DOI or URL", placeholder="10.1038/s41586-023-06291-2")
        
        # Input Method 2: File Upload
        uploaded_file = st.file_uploader("Or drop a PDF file", type=["pdf"])
        
        if st.button("Fetch & Save"):
            target_input = None
            temp_path = None
            
            if uploaded_file:
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_path = tmp.name
                target_input = temp_path
                st.info(f"Processing uploaded file: {uploaded_file.name}")
            elif doi_input:
                target_input = doi_input.strip()
            else:
                st.warning("Please provide a DOI or upload a PDF.")
            
            if target_input:
                with st.spinner("Extracting DOI..."):
                    doi = get_doi_from_input(target_input)
                
                # Cleanup temp file
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

                if doi:
                    st.success(f"Found DOI: {doi}")
                    
                    with st.spinner("Fetching Metadata..."):
                        metadata = fetch_metadata(doi)
                    
                    if metadata:
                        st.write("### Metadata Preview")
                        st.write(f"**Title**: {metadata.get('title')}")
                        st.write(f"**Authors**: {metadata.get('display_authors')}")
                        
                        abstract = metadata.get('abstract', '')
                        translation = ""
                        if abstract:
                            with st.spinner("Translating Abstract..."):
                                translation = translate_abstract(abstract)
                            st.write("### Translated Abstract")
                            with st.expander("Show Translation"):
                                st.write(translation)
                        
                        with st.spinner("Saving to Notion..."):
                            page_url = create_notion_page(metadata, translation)
                        
                        if page_url:
                            st.success("Successfully saved to Notion!")
                            st.markdown(f"[Open Notion Page]({page_url})")
                        else:
                            st.error("Failed to save to Notion.")
                    else:
                        st.error("Failed to fetch metadata.")
                else:
                    st.error("Could not find a valid DOI.")

    # --- TAB 2: EXPORT ---
    with tab2:
        st.header("Export Citations")
        
        cite_key = st.text_input("Cite Key (Notion)", placeholder="e.g., maita2023")
        export_format = st.radio("Format", ["Nature (nat)", "BibTeX (bib)"])
        
        if st.button("Search & Export"):
            if not cite_key:
                st.warning("Please enter a Cite Key.")
            else:
                with st.spinner("Querying Notion..."):
                    papers = get_papers(cite_key)
                
                if not papers:
                    st.warning(f"No papers found for key: {cite_key}")
                else:
                    st.success(f"Found {len(papers)} papers.")
                    
                    fmt_code = 'nat' if "Nature" in export_format else 'bib'
                    if fmt_code == 'nat':
                        output_text = nat(papers)
                        file_ext = ".txt"
                    else:
                        output_text = bib(papers)
                        file_ext = ".bib"
                    
                    st.text_area("Citation Preview", output_text, height=200)
                    
                    # Download Button
                    st.download_button(
                        label="Download Citation File",
                        data=output_text,
                        file_name=f"{cite_key}{file_ext}",
                        mime="text/plain"
                    )
                    
                    # Also save to default path (replicating main.py behavior)
                    if EXPORT_DIR:
                         # Ensure directory exists
                        if not os.path.exists(EXPORT_DIR):
                            try:
                                os.makedirs(EXPORT_DIR)
                            except Exception as e:
                                st.error(f"Error creating directory {EXPORT_DIR}: {e}")

                        if os.path.exists(EXPORT_DIR):
                            save_path = os.path.join(EXPORT_DIR, f"{cite_key}{file_ext}")
                            try:
                                with open(save_path, "w", encoding="utf-8") as f:
                                    f.write(output_text)
                                st.info(f"Auto-saved to: `{save_path}`")
                            except Exception as e:
                                st.error(f"Error auto-saving: {e}")

if __name__ == "__main__":
    main()
