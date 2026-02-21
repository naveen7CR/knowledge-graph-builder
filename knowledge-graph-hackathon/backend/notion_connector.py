import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class NotionConnector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NOTION_API_KEY')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        } if self.api_key else {}
    
    def query_database(self, database_id: str) -> List[Dict]:
        """Query a Notion database"""
        if not self.api_key:
            print("No Notion API key provided")
            return []
            
        url = f"{self.base_url}/databases/{database_id}/query"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            print(f"Error querying database: {response.status_code}")
            return []
    
    def get_page_content(self, page_id: str) -> str:
        """Get content of a page"""
        if not self.api_key:
            return ""
            
        url = f"{self.base_url}/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            blocks = response.json().get('results', [])
            content = []
            for block in blocks:
                if block['type'] == 'paragraph':
                    text = block['paragraph'].get('rich_text', [])
                    if text:
                        content.append(text[0].get('plain_text', ''))
            return '\n'.join(content)
        return ""
