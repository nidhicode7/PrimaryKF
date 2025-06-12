from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Construct the path to the .env file in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')

# Load environment variables from .env file
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def extract_seo_elements(html_content):
    """Extract title and metadata from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get title
    title = soup.title.string if soup.title else ""
    
    # Get meta description
    meta_description = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        meta_description = meta_desc.get('content', '')
    
    # Get meta keywords
    meta_keywords = ""
    meta_keys = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keys:
        meta_keywords = meta_keys.get('content', '')
    
    # Get h1 tags (often contain important keywords)
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
    
    return {
        "title": title,
        "meta_description": meta_description,
        "meta_keywords": meta_keywords,
        "h1_tags": h1_tags
    }

def extract_keywords(seo_elements):
    """Extract keywords using OpenAI API based on SEO elements."""
    try:
        # Prepare the SEO elements for analysis
        seo_text = f"""
        Page Title: {seo_elements['title']}
        Meta Description: {seo_elements['meta_description']}
        Meta Keywords: {seo_elements['meta_keywords']}
        H1 Tags: {', '.join(seo_elements['h1_tags'])}
        """
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert SEO keyword analyzer. Your task is to analyze webpage metadata and extract:
1. One primary keyword (most important, main topic)
2. Three secondary keywords (closely related to the primary keyword)

Focus ONLY on the page title, meta description, meta keywords, and H1 tags.
Do NOT analyze the main content of the page.

Return ONLY a JSON object in this exact format:
{
    "primary_keyword": "main keyword",
    "secondary_keywords": ["keyword1", "keyword2", "keyword3"]
}

The keywords should be SEO-optimized and reflect the main topic of the page based on its metadata."""
                },
                {
                    "role": "user",
                    "content": f"Analyze these SEO elements and extract the most relevant keywords: {seo_text}"
                }
            ],
            temperature=0.3,
            max_tokens=250
        )
        
        # Extract the response content
        result = response.choices[0].message.content.strip()
        
        # Validate and clean the response
        try:
            keywords_data = json.loads(result)
            if not isinstance(keywords_data, dict):
                raise ValueError("Response is not a dictionary")
            
            # Ensure required fields exist
            if "primary_keyword" not in keywords_data or "secondary_keywords" not in keywords_data:
                raise ValueError("Missing required fields")
            
            # Ensure secondary_keywords is a list with exactly 3 items
            if not isinstance(keywords_data["secondary_keywords"], list) or len(keywords_data["secondary_keywords"]) != 3:
                raise ValueError("secondary_keywords must be a list with exactly 3 items")
            
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                return match.group(0)
            raise ValueError("Invalid JSON response from OpenAI")
            
    except Exception as e:
        raise Exception(f"Error in keyword extraction: {str(e)}")

@app.route('/api/extract-keywords', methods=['POST'])
def extract_keywords_from_url():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return jsonify({"error": "Invalid URL format"}), 400

        # Fetch webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract SEO elements
        seo_elements = extract_seo_elements(response.text)
        
        # Validate that we have at least a title
        if not seo_elements['title']:
            return jsonify({"error": "Could not extract page title"}), 400

        # Extract keywords
        keywords_string = extract_keywords(seo_elements)
        
        try:
            keywords_data = json.loads(keywords_string)
            return jsonify(keywords_data)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse keywords from AI response"}), 500

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching URL: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 