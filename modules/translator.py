from google import genai
from google.genai import types
import os
import time
from config.settings import GEMINI_API_KEY

def translate_abstract(text: str) -> str:
    """
    Translate the given abstract to Japanese using Gemini API (google-genai).
    Includes retry logic for rate limits (429).
    """
    if not text:
        return ""
    
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Skipping translation.")
        return "(Translation skipped: API Key missing)"

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
#命令
あなたは学術論文の翻訳を専門とするAI翻訳家です。提供された英語論文を、専門用語や文脈を正確に理解し、自然かつ学術的に適切な日本語に翻訳してください。

#制約条件
・出力は翻訳された日本語の本文のみとします。
・専門用語は、日本の学術界で一般的に用いられる表現に統一し、意味の正確性を最優先とします。日本語であまり使われていない単語の場合、英語表記のままでよいです。
・基本的に逐語訳を行いますが、日本語として自然で、かつ学術論文として違和感のない表現を心がけてください。
・敬体（です・ます調）ではなく、常体（だ・である調）で統一してください。

Target Text:
{text}
    """
    
    max_retries = 3
    base_delay = 5  # Start with 5 seconds wait

    for attempt in range(max_retries):
        try:
            # Try gemini-2.0-flash first as it is fast and capable
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt) # Exponential backoff: 5, 10, 20
                    print(f"Gemini API Rate Limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
            
            print(f"Error translating text (Attempt {attempt+1}): {e}")
            # If it's not a rate limit, or we exhausted retries, verify fallback not needed or fail gracefully
            if attempt == max_retries - 1:
                 return "(Translation failed due to API Error)"

    return "(Translation failed)"
