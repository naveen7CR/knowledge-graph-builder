from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

from github_connector import GitHubConnector
from notion_connector import NotionConnector
from skill_extractor import SkillExtractor
from graph_manager import GraphManager

load_dotenv()

app = FastAPI(title="Knowledge Graph API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
github = GitHubConnector()
notion = NotionConnector()
extractor = SkillExtractor()
graph = GraphManager()

# Request/Response models
class GitHubRequest(BaseModel):
    username: str

class NotionRequest(BaseModel):
    database_id: str

class BuildGraphRequest(BaseModel):
    github_username: str
    notion_database_id: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Knowledge Graph API", "status": "running"}

@app.post("/api/github/fetch")
async def fetch_github(request: GitHubRequest):
    """Fetch GitHub repositories"""
    try:
        repos = github.fetch_repositories(request.username)
        languages = github.extract_languages(request.username)
        
        return {
            "status": "success",
            "data": {
                "repositories": repos,
                "languages": languages,
                "count": len(repos)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notion/fetch")
async def fetch_notion(request: NotionRequest):
    """Fetch Notion database"""
    try:
        pages = notion.query_database(request.database_id)
        return {
            "status": "success",
            "data": {
                "pages": pages,
                "count": len(pages)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/graph/build")
async def build_graph(request: BuildGraphRequest):
    """Build knowledge graph"""
    try:
        # Fetch GitHub data
        repos = github.fetch_repositories(request.github_username)
        github_skills = extractor.extract_from_github(repos)
        
        notion_skills = {}
        if request.notion_database_id:
            pages = notion.query_database(request.notion_database_id)
            notion_skills = extractor.extract_from_notion(pages)
        
        # Create graph
        graph.create_graph(github_skills, notion_skills)
        
        return {
            "status": "success",
            "message": f"Graph built with {len(github_skills)} GitHub projects and {len(notion_skills)} Notion pages"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/data")
async def get_graph_data():
    """Get graph data for visualization"""
    try:
        data = graph.get_graph_data()
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown():
    graph.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
