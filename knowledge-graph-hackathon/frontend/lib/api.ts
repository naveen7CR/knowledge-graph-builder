import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export interface Node {
  id: string;
  name: string;
  type: string;
  properties: any;
}

export interface Link {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: Node[];
  links: Link[];
}

export class ApiService {
  static async fetchGitHub(username: string) {
    const response = await axios.post(`${API_BASE}/github/fetch`, { username });
    return response.data;
  }

  static async fetchNotion(databaseId: string) {
    const response = await axios.post(`${API_BASE}/notion/fetch`, { database_id: databaseId });
    return response.data;
  }

  static async buildGraph(githubUsername: string, notionDatabaseId?: string) {
    const response = await axios.post(`${API_BASE}/graph/build`, {
      github_username: githubUsername,
      notion_database_id: notionDatabaseId
    });
    return response.data;
  }

  static async getGraphData(): Promise<GraphData> {
    const response = await axios.get(`${API_BASE}/graph/data`);
    return response.data.data;
  }
}