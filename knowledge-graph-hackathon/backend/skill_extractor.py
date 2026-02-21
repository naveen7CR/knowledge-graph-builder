import spacy
from typing import Set, List, Dict
import re

class SkillExtractor:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
            self.nlp = spacy.load('en_core_web_sm')
        
        # Common tech skills dictionary
        self.tech_skills = {
            'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'node', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'java', 'spring', 'kotlin', 'scala', 'go', 'rust',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'html', 'css', 'sass', 'tailwind', 'bootstrap',
            'git', 'github', 'gitlab', 'jenkins', 'circleci', 'travis',
            'machine learning', 'deep learning', 'ai', 'data science',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'rest', 'graphql', 'grpc', 'websocket', 'oauth', 'jwt'
        }
    
    def extract_skills(self, text: str) -> Set[str]:
        """Extract skills from text"""
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        # Check for skills in text
        for skill in self.tech_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        return found_skills
    
    def extract_from_github(self, repos_data: List[Dict]) -> Dict[str, Set[str]]:
        """Extract skills from GitHub repository data"""
        repo_skills = {}
        
        for repo in repos_data:
            skills = set()
            repo_name = repo.get('name', 'unknown')
            
            # Add language as skill
            if repo.get('language'):
                skills.add(repo['language'].lower())
            
            # Add topics as skills
            if repo.get('topics'):
                skills.update([t.lower() for t in repo['topics']])
            
            # Extract from description
            if repo.get('description'):
                skills.update(self.extract_skills(repo['description']))
            
            repo_skills[repo_name] = skills
        
        return repo_skills
    
    def extract_from_notion(self, pages: List[Dict]) -> Dict[str, Set[str]]:
        """Extract skills from Notion pages"""
        page_skills = {}
        
        for page in pages:
            skills = set()
            page_id = page.get('id', 'unknown')
            
            # Extract from title
            if 'properties' in page:
                for prop_name, prop_value in page['properties'].items():
                    if prop_value.get('type') == 'title':
                        title_text = prop_value.get('title', [])
                        if title_text:
                            title = title_text[0].get('plain_text', '')
                            skills.update(self.extract_skills(title))
            
            page_skills[page_id] = skills
        
        return page_skills
