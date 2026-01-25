import requests
import re

def clean_author_name(author_list):
    """
    Convert author list to 'FirstAuthor et al.' if multiple, or just 'FirstAuthor'.
    Expects list of dicts from Crossref [{given, family}, ...] or similar.
    """
    if not author_list:
        return "Unknown"
    
    # Try to extract family name of first author
    first_auth = author_list[0]
    name = first_auth.get('family', first_auth.get('name', 'Unknown'))
    
    if len(author_list) > 1:
        return f"{name} et al."
    return name

def fetch_pmid(doi: str) -> str | None:
    """
    Fetch PMID from DOI using NCBI E-utilities (Esearch).
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": doi,
        "retmode": "json"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            return None
            
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if id_list:
            return id_list[0]
        return None
    except Exception as e:
        print(f"Error fetching PMID: {e}")
        return None


def fetch_crossref_metadata(doi: str) -> dict | None:
    """
    Fetch metadata from Crossref API.
    """
    base_url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            print(f"Crossref API failed with status {response.status_code} for DOI: {doi}")
            return None
        
        data = response.json().get('message', {})
        
        title = data.get('title', [''])[0] if data.get('title') else "No Title"
        authors = data.get('author', [])
        container_title = data.get('container-title', [''])[0] if data.get('container-title') else "Unknown Journal"
        publisher = data.get('publisher', 'Unknown Publisher')
        
        # Date parts: [[2023, 1, 15]]
        issued = data.get('issued', {}).get('date-parts', [[None]])[0][0]
        year = str(issued) if issued else "Unknown Year"
        
        url = data.get('URL', f"https://doi.org/{doi}")
        
        # Abstract (often XML/HTML escaped or not present)
        # Crossref abstracts are rare or messy, but let's try
        abstract = data.get('abstract', '')
        # Simple cleanup if it contains tags
        abstract = re.sub(r'<[^>]+>', '', abstract).strip()

        # Authors processing
        def format_name(a):
            given = a.get('given', '')
            family = a.get('family', a.get('name', 'Unknown'))
            return f"{given} {family}".strip() if given else family

        author_list = [format_name(a) for a in authors]
        first_author = author_list[0] if author_list else "Unknown"
        
        # Cleaned display string (e.g. "Smith et al.")
        # If full name "John Smith", display "Smith et al." or "John Smith et al."?
        # Usually "Smith et al." is preferred for citations, but "First Author" column wants full name.
        # Let's keep display_authors as "Family et al." for console/logging cleanliness if preferred, 
        # or stick to full name. 
        # Requirement: "First Author column -> Full name". 
        # "Authors" column -> Multi-select.
        
        family_name_first = authors[0].get('family', authors[0].get('name', 'Unknown')) if authors else "Unknown"
        display_authors = f"{family_name_first} et al." if len(author_list) > 1 else family_name_first

        # Fetch PMID
        pmid = fetch_pmid(doi)


        return {
            "title": title,
            "authors_list": author_list, # List of strings for Multi-select
            "first_author": first_author, # String for First author field
            "display_authors": display_authors,
            "journal": container_title,
            "publisher": publisher,
            "year": year,
            "issued_date": data.get('issued', {}).get('date-parts', [[None]])[0], # [2023, 1, 15]
            "volume": data.get('volume', ''),
            "page": data.get('page', ''),
            "doi": doi,
            "url": url,
            "pmid": pmid,
            "is_arxiv": False,
            "abstract": abstract
        }
    except Exception as e:
        print(f"Error fetching Crossref metadata: {e}")
        return None

def fetch_arxiv_metadata(doi: str) -> dict | None:
    """
    Fetch from ArXiv API if DOI looks like an arXiv ID or belongs to arXiv.
    Also handles when input is just an arXiv ID (e.g. 2101.12345).
    """
    # Basic check if it might be an arxiv ID (usually 10.48550/arXiv.2301.12345 or just 2301.12345)
    # The input_handler should give us a DOI or ID.
    
    # For now, implemented as a fallback or specific check if requested.
    # Crossref usually indexes arXiv via 10.48550.
    return None

def fetch_metadata(doi: str) -> dict | None:
    """
    Main entry point to fetch metadata. 
    Currently prioritizes Crossref.
    """
    # TODO: Add logic to switch to arXiv API if Crossref result is poor or DOI is 10.48550
    return fetch_crossref_metadata(doi)
