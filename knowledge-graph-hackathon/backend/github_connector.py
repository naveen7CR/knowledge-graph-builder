import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class GitHubConnector:
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('GITHUB_ACCESS_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.access_token else {}
    
    def fetch_repositories(self, username: str) -> List[Dict]:
        """Fetch all repositories for a user"""
        url = f"{self.base_url}/users/{username}/repos"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching repos: {response.status_code}")
            return []
    
    def extract_languages(self, username: str) -> Dict[str, int]:
        """Extract programming languages from user's repos"""
        repos = self.fetch_repositories(username)
        
        languages = {}
        for repo in repos:
            if 'languages_url' in repo:
                response = requests.get(repo['languages_url'], headers=self.headers)
                if response.status_code == 200:
                    repo_langs = response.json()
                    for lang, bytes_count in repo_langs.items():
                        languages[lang] = languages.get(lang, 0) + bytes_count
                
        return languages
    
    def get_readme(self, username: str, repo_name: str) -> str:
        """Get README content for a repository"""
        url = f"{self.base_url}/repos/{username}/{repo_name}/readme"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            import base64
            content = response.json()['content']
            return base64.b64decode(content).decode('utf-8')
        return ""
