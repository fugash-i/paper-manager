import os
from notion_client import Client
from config.settings import NOTION_TOKEN, DATABASE_ID
from notion_client.errors import APIResponseError

def get_papers(cite_key: str) -> list[dict]:
    """
    Query Notion database for papers with the specific cite key (Multi-select).
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Error: NOTION_TOKEN or DATABASE_ID not set.")
        return []

    database_id = DATABASE_ID
    notion = Client(auth=NOTION_TOKEN)
    
    import uuid
    try:
        formatted_id = str(uuid.UUID(database_id))
    except (ValueError, TypeError):
        formatted_id = database_id

    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try: 
        logger.info(f"Retrieving Notion database metadata with ID: {formatted_id}")
        
        # 1. Retrieve Database Metadata to find Data Source ID
        db_metadata = notion.databases.retrieve(formatted_id)
        
        # 2. Extract Data Source ID
        if "data_sources" in db_metadata and len(db_metadata["data_sources"]) > 0:
            data_source_id = db_metadata["data_sources"][0]["id"]
            logger.info(f"Found Data Source ID: {data_source_id}")
        else:
            # Fallback? Or maybe the Database ID IS the Data Source ID in some cases?
            # For now, let's assume if it fails we might try the DB ID, but the error suggested otherwise.
            # But let's log logic clearly.
            logger.warning("No 'data_sources' found in metadata. Trying Database ID as Data Source ID directly.")
            data_source_id = formatted_id

        # 3. Query Data Source
        logger.info(f"Querying Data Source: {data_source_id}")
        response = notion.data_sources.query(
            data_source_id,
            filter={
                "property": "cite key",
                "multi_select": {
                    "contains": cite_key
                }
            }
        )
        results = response.get("results", [])
        logger.info(f"Successfully retrieved {len(results)} entries.")
        return results 
    except APIResponseError as e:
        logger.error(f"Notion API Error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error querying Notion: {e}")
        return []

def format_name_for_nature(full_name: str) -> str:
    """
    Convert "Karan Singhal" -> "Singhal, K."
    """
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name
    
    # Simple heuristic: Last word is surname, rest are given names
    # This might fail for complex names, but good enough for MVP
    surname = parts[-1]
    given_names = parts[:-1]
    initials = "".join([f"{n[0]}." for n in given_names])
    
    return f"{surname}, {initials}"

def nat(papers: list[dict]) -> str:
    """
    Format papers in Nature style.
    Reference: Authors. Title. Journal Volume, Page (Year).
    """
    output_lines = []
    
    for i, page in enumerate(papers, 1):
        props = page.get('properties', {})
        
        # Authors
        # We need the list of authors. If stored in "Authors" (Multi-select), retrieve names.
        authors_prop = props.get('Authors', {}).get('multi_select', [])
        author_names = [a['name'] for a in authors_prop]
        
        if not author_names:
            formatted_authors = "Unknown Authors"
        elif len(author_names) > 5:
            # Nature style: "First Author et al." for > 5 authors
            # We assume the first name in the multi-select list is the first author.
            first_auth = format_name_for_nature(author_names[0])
            formatted_authors = f"{first_auth} *et al.*"
        else:
            # List all authors surname first
            formatted_list = [format_name_for_nature(name) for name in author_names]
            # Join with commas, last one with &? Nature style usually just commas or & before last.
            # Guide says: "Authors should be listed surname first, followed by a comma and initials..."
            # Example: "Hao, Z., AghaKouchak, A., Nakhjiri, N. & Farahmand, A."
            if len(formatted_list) > 1:
                formatted_authors = ", ".join(formatted_list[:-1]) + " & " + formatted_list[-1]
            else:
                formatted_authors = formatted_list[0]

        title = props.get('Title', {}).get('title', [{}])[0].get('text', {}).get('content', 'No Title')
        
        journal = props.get('Journal', {}).get('select', {}).get('name', '')
        # Nature uses italic for Journal. In markdown/text we can use *Journal*.
        
        # Volume (Number)
        volume = props.get('Volume', {}).get('number')
        volume_str = f"**{volume}**" if volume else ""
        
        # Pages (Rich Text)
        pages_list = props.get('Pages', {}).get('rich_text', [])
        pages = pages_list[0].get('text', {}).get('content', '') if pages_list else ""
        
        # Year (Number or Date)
        # We used 'Publication Date' (Date)
        date_prop = props.get('Publication Date', {}).get('date', {})
        year = ""
        if date_prop and date_prop.get('start'):
            year = f"({date_prop.get('start')[:4]})"
        
        # Construct line
        # Singhal, K. *et al.* Large language models encode clinical knowledge. *Nature* **620**, 172–180 (2023).
        
        parts = []
        parts.append(f"{formatted_authors}")
        parts.append(f"{title}.")
        if journal:
            parts.append(f"*{journal}*")
        if volume_str:
            parts.append(f"{volume_str}")
        if pages:
             if volume_str:
                 parts[-1] += "," 
             parts.append(pages)
        if year:
            parts.append(year + ".")
            
        line = " ".join(parts)
        line = line.replace("..", ".")
        
        output_lines.append(f"{i}. {line}")
        
    return "\n".join(output_lines)

def bib(papers: list[dict]) -> str:
    """
    Format papers as BibTeX.
    """
    entries = []
    for page in papers:
        props = page.get('properties', {})
        
        # --- BibTeX Citation Key Generation ---
        # Pattern: [FirstAuthorSurname][Year] (e.g., "doe2023")
        authors_prop = props.get('Authors', {}).get('multi_select', [])
        first_author_family = "Unknown"
        if authors_prop:
             first_name_parts = authors_prop[0]['name'].split()
             first_author_family = first_name_parts[-1].lower()
        
        date_prop = props.get('Publication Date', {}).get('date', {})
        year = date_prop.get('start')[:4] if date_prop and date_prop.get('start') else "year"
        
        cite_id = f"{first_author_family}{year}"
        
        title = props.get('Title', {}).get('title', [{}])[0].get('text', {}).get('content', 'No Title')
        journal = props.get('Journal', {}).get('select', {}).get('name', '')
        volume = props.get('Volume', {}).get('number', '')
        pages_list = props.get('Pages', {}).get('rich_text', [])
        pages = pages_list[0].get('text', {}).get('content', '') if pages_list else ""
        doi_list = props.get('DOI', {}).get('rich_text', [])
        doi = doi_list[0].get('text', {}).get('content', '') if doi_list else ""
        url = props.get('URL', {}).get('url', '')
        
        # BibTeX Entry
        entry = f"@article{{{cite_id},\n"
        entry += f"  author = {{{' and '.join([a['name'] for a in authors_prop])}}},\n"
        entry += f"  title = {{{title}}},\n"
        entry += f"  journal = {{{journal}}},\n"
        if year != "year":
            entry += f"  year = {{{year}}},\n"
        if volume:
            entry += f"  volume = {{{volume}}},\n"
        if pages:
            entry += f"  pages = {{{pages}}},\n"
        if doi:
            entry += f"  doi = {{{doi}}},\n"
        if url:
             entry += f"  url = {{{url}}}\n"
        entry += "}\n"
        entries.append(entry)
        
    return "\n".join(entries)
