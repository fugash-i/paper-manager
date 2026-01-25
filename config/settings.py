import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Notion Settings
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

# Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Export Settings
# Default path for exported files if --output is not specified
EXPORT_DIR = os.getenv("EXPORT_DIR", "/Users/kent/Documents/citation")

def validate_config():
    """Check if essential environment variables are set."""
    missing = []
    if not NOTION_TOKEN:
        missing.append("NOTION_TOKEN")
    if not DATABASE_ID:
        missing.append("DATABASE_ID")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    
    if missing:
        print(f"Warning: Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        # We might not want to exit hard here if we want to allow partial functionality,
        # but for now these seem critical based on requirements.
        return False
    return True
