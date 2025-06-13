from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re

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
    
    return {
        "title": title,
        "meta_description": meta_description,
        "meta_keywords": meta_keywords
    }

def extract_keywords(seo_elements):
    """Extract keywords using OpenAI API based on SEO elements."""
    try:
        page_title = seo_elements['title']
        meta_description = seo_elements['meta_description']
        meta_keywords_str = seo_elements['meta_keywords'] # Get meta keywords as well

        prompt_text = f"Assume you are an SEO expert. What would the primary keyword of the page whose title is: {page_title} and the Description of the page is {meta_description} and meta keywords are {meta_keywords_str}. Give the answer in the following format - pk: <primary_keyword>. Also, give me 3 similar keywords to that of the primary keyword in the following format: kw: <k1>, <k2>, <k3>"

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO expert. You will be given a page title, meta description, and meta keywords. You must extract one primary keyword and three secondary keywords. Your output MUST strictly follow this format: pk: <primary_keyword>. Also, give me 3 similar keywords to that of the primary keyword in the following format: kw: <k1>, <k2>, <k3>."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            temperature=0.3,
            max_tokens=250 # Increased max_tokens to allow for longer responses if needed
            # Removed response_format={"type": "json_object"} as output format is now custom string
        )
        
        # Extract the response content
        result = response.choices[0].message.content.strip()
        print(f"DEBUG: OpenAI raw response (custom format): {result}") # Debugging the raw response

        primary_keyword = ""
        secondary_keywords = []

        pk_start = result.find("pk: ")
        kw_start = result.find("kw: ")

        if pk_start != -1:
            pk_start += len("pk: ")
            if kw_start != -1 and kw_start > pk_start:
                primary_keyword = result[pk_start:kw_start].strip()
            else:
                primary_keyword = result[pk_start:].strip()

        if kw_start != -1:
            kw_start += len("kw: ")
            secondary_keywords_str = result[kw_start:].strip()
            secondary_keywords = [k.strip() for k in secondary_keywords_str.split(',') if k.strip()]

        print(f"DEBUG: Parsed primary_keyword: '{primary_keyword}'") # New debug print

        # Ensure exactly 3 secondary keywords
        while len(secondary_keywords) < 3:
            secondary_keywords.append("") # Pad with empty strings if less than 3
        secondary_keywords = secondary_keywords[:3] # Take only the first 3 if more are returned

        # Format the output as JSON for the frontend
        output_data = {
            "primary_keyword": primary_keyword,
            "secondary_keywords": secondary_keywords
        }
        print(f"DEBUG: Backend returning JSON: {json.dumps(output_data)}") # Added debug print
        return json.dumps(output_data)
            
    except Exception as e:
        raise Exception(f"Error in keyword extraction: {str(e)}")

@app.route('/api/extract-keywords', methods=['POST'])
def extract_keywords_from_url():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Add https:// if no scheme is provided
        if not url.startswith(('http://', 'https://')):
            url = "https://" + url

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