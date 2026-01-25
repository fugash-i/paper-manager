from notion_client import Client
import os
from config.settings import NOTION_TOKEN, DATABASE_ID
from datetime import datetime

def create_notion_page(metadata: dict, translation: str) -> str | None:
    """
    Create a new page in the Notion database with the given metadata and translation.
    Returns the URL of the created page or None if failed.
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Error: NOTION_TOKEN or DATABASE_ID not set.")
        return None

    # Clean DATABASE_ID if it contains URL parameters (e.g. ?v=...)
    clean_database_id = DATABASE_ID.split("?")[0]


    try:
        notion = Client(auth=NOTION_TOKEN)
        
        # Construct date string YYYY-MM-DD
        date_parts = metadata.get('issued_date', [None])
        iso_date = None
        if date_parts and date_parts[0]:
            # parts can be [2023], [2023, 1], or [2023, 1, 15]
            y = date_parts[0]
            m = date_parts[1] if len(date_parts) > 1 else 1
            d = date_parts[2] if len(date_parts) > 2 else 1
            iso_date = f"{y:04d}-{m:02d}-{d:02d}"

        properties = {
            # title (テキスト) -> Usually the Title property in Notion is type 'title'
            "title": {"title": [{"text": {"content": metadata.get('title', 'Unknown Title')}}]},
            
            # read (チェックボックス)
            "read": {"checkbox": False},
            
            # First author (テキスト)
            "First Author": {"rich_text": [{"text": {"content": metadata.get('first_author', 'Unknown')}}]},
            
            # Authors (マルチセレクト)
            # Notion Multi-select has limits (color colors etc). 
            # If too many authors, it might fail or create too many tags. 
            # Taking top 5 to be safe.
            "Authors": {"multi_select": [{"name": auth[:100]} for auth in metadata.get('authors_list', [])[:5]]},
            
            # Publication date (日付)
            "Publication Date": {"date": {"start": iso_date}} if iso_date else {"date": None},
            
            # Journal (選択)
            "Journal": {"select": {"name": metadata.get('journal', 'Unknown')[:100]}},
            
            # Publisher (選択)
            "Publisher": {"select": {"name": metadata.get('publisher', 'Unknown')[:100]}},
            
            # Volume (数値)
            "Volume": {"number": int(metadata.get('volume'))} if metadata.get('volume', '').isdigit() else {"number": None},

            # Pages (テキスト)
            "Pages": {"rich_text": [{"text": {"content": metadata.get('page', '')}}]},

            # cite key (選択) - Leaving empty for now
            
            # DOI (テキスト)
            "DOI": {"rich_text": [{"text": {"content": metadata.get('doi', '')}}]},
            
            # URL (URL)
            "URL": {"url": metadata.get('url')},
            
            # PMID (テキスト) - Not fetching PMID from Crossref usually, leaving empty for now
            "PMID": {"rich_text": [{"text": {"content": metadata.get('pmid', '')}}]},
            
            # PDF (ファイル&メディア) - Cannot upload via API easily without public URL, leaving empty
        }

        # Content blocks
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Abstract"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": metadata.get('abstract', '') or "No abstract available."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Abstract (Japanese)"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": translation}}]
                }
            },
             {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Introduction"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [] # Empty placeholder
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Results"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Discussion"}}]
                }
            }
        ]

        response = notion.pages.create(
            parent={"database_id": clean_database_id},
            properties=properties,
            children=children
        )
        
        return response.get('url')

    except Exception as e:
        print(f"Error creating Notion page: {e}")
        # Print detailed response if available for debugging
        # if hasattr(e, 'body'): print(e.body)
        return None
