from neo4j import GraphDatabase
from typing import List, Dict, Any, Set
import os
from dotenv import load_dotenv

load_dotenv()

class GraphManager:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password123')
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def create_graph(self, github_skills: Dict, notion_skills: Dict):
        """Create knowledge graph from extracted skills"""
        if not self.driver:
            print("No database connection")
            return
        
        with self.driver.session() as session:
            # Clear existing data (for demo purposes)
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create constraints
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
            
            # Add GitHub projects and their skills
            for repo_name, skills in github_skills.items():
                # Create project node
                session.run(
                    """
                    CREATE (p:Project:GitHub {
                        name: $name,
                        type: 'github'
                    })
                    """,
                    name=repo_name
                )
                
                # Add skills
                for skill in skills:
                    session.run(
                        """
                        MERGE (s:Skill {name: $skill})
                        WITH s
                        MATCH (p:Project {name: $project})
                        CREATE (p)-[:USES]->(s)
                        """,
                        skill=skill,
                        project=repo_name
                    )
            
            # Add Notion pages and their skills
            for page_id, skills in notion_skills.items():
                # Create page node
                session.run(
                    """
                    CREATE (p:Project:Notion {
                        id: $id,
                        type: 'notion'
                    })
                    """,
                    id=page_id
                )
                
                # Add skills
                for skill in skills:
                    session.run(
                        """
                        MERGE (s:Skill {name: $skill})
                        WITH s
                        MATCH (p:Project {id: $page_id})
                        CREATE (p)-[:RELATES_TO]->(s)
                        """,
                        skill=skill,
                        page_id=page_id
                    )
    
    def get_graph_data(self) -> Dict:
        """Get graph data for visualization"""
        if not self.driver:
            return {"nodes": [], "links": []}
        
        with self.driver.session() as session:
            # Get all nodes and relationships
            result = session.run(
                """
                MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT 200
                """
            )
            
            nodes = {}
            links = []
            
            for record in result:
                source = record['n']
                target = record['m']
                
                # Add source node
                source_id = source.element_id
                if source_id not in nodes:
                    nodes[source_id] = {
                        'id': source_id,
                        'name': source.get('name') or source.get('id') or 'Unknown',
                        'type': list(source.labels)[0],
                        'properties': dict(source)
                    }
                
                # Add target node
                target_id = target.element_id
                if target_id not in nodes:
                    nodes[target_id] = {
                        'id': target_id,
                        'name': target.get('name') or target.get('id') or 'Unknown',
                        'type': list(target.labels)[0],
                        'properties': dict(target)
                    }
                
                # Add link
                links.append({
                    'source': source_id,
                    'target': target_id,
                    'type': record['r'].type
                })
            
            return {
                'nodes': list(nodes.values()),
                'links': links
            }
