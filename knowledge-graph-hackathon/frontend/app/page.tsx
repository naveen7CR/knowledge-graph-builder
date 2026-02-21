'use client';

import { useState } from 'react';
import { ApiService, GraphData } from '@/lib/api';
import KnowledgeGraph3D from '@/components/KnowledgeGraph3D';

export default function Home() {
  const [githubUsername, setGithubUsername] = useState('');
  const [notionDbId, setNotionDbId] = useState('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [error, setError] = useState('');

  const handleBuildGraph = async () => {
    if (!githubUsername) {
      setError('Please enter a GitHub username');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Build the graph
      await ApiService.buildGraph(githubUsername, notionDbId || undefined);
      
      // Fetch the graph data
      const data = await ApiService.getGraphData();
      setGraphData(data);
    } catch (error: any) {
      console.error('Error building graph:', error);
      setError(error.message || 'Failed to build graph. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">
            🧠 Knowledge Graph Visualizer
          </h1>
          <p className="text-gray-600 mt-1">
            Visualize your skills from GitHub and Notion in 3D
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Input Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Configuration</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    GitHub Username <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={githubUsername}
                    onChange={(e) => setGithubUsername(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., octocat"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notion Database ID (optional)
                  </label>
                  <input
                    type="text"
                    value={notionDbId}
                    onChange={(e) => setNotionDbId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Your Notion database ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty to only use GitHub data
                  </p>
                </div>
                
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                    {error}
                  </div>
                )}
                
                <button
                  onClick={handleBuildGraph}
                  disabled={loading || !githubUsername}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Building...
                    </span>
                  ) : 'Build Knowledge Graph'}
                </button>
              </div>
            </div>

            {/* Selected Node Info */}
            {selectedNode && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Selected Node</h2>
                <div className="space-y-2">
                  <p><span className="font-medium">Name:</span> {selectedNode.name}</p>
                  <p><span className="font-medium">Type:</span> {selectedNode.type}</p>
                  {selectedNode.properties && (
                    <div>
                      <p className="font-medium mb-1">Properties:</p>
                      <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                        {JSON.stringify(selectedNode.properties, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Stats Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Statistics</h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Nodes:</span>
                  <span className="font-semibold">{graphData.nodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Connections:</span>
                  <span className="font-semibold">{graphData.links.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Skills:</span>
                  <span className="font-semibold">
                    {graphData.nodes.filter(n => n.type === 'Skill').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Projects:</span>
                  <span className="font-semibold">
                    {graphData.nodes.filter(n => n.type === 'Project' || n.type === 'GitHub' || n.type === 'Notion').length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 3D Graph */}
          <div className="lg:col-span-3 bg-gray-900 rounded-lg shadow-lg overflow-hidden">
            <KnowledgeGraph3D 
              data={graphData} 
              onNodeClick={(node) => setSelectedNode(node)}
            />
          </div>
        </div>
      </div>
    </main>
  );
}