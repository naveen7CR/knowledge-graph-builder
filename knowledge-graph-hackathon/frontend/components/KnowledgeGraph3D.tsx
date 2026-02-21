'use client';

import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { Node, Link } from '@/lib/api';

interface GraphProps {
  data: {
    nodes: Node[];
    links: Link[];
  };
  onNodeClick?: (node: Node) => void;
}

function NodeComponent({ node, position, onClick }: { node: Node; position: [number, number, number]; onClick: () => void }) {
  const getColor = () => {
    switch (node.type) {
      case 'Skill': return '#ff3333';
      case 'Project': return '#00ffaa';
      case 'GitHub': return '#00cc88';
      case 'Notion': return '#ffaa00';
      default: return '#3399ff';
    }
  };

  return (
    <group position={position}>
      <Sphere args={[0.5, 32, 32]} onClick={onClick}>
        <meshStandardMaterial color={getColor()} />
      </Sphere>
      <Html distanceFactor={12}>
        <div style={{ 
          background: '#0a0a14',
          color: '#ff3333',
          padding: '8px 16px', 
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: 'bold',
          whiteSpace: 'nowrap',
          transform: 'translate(-50%, -50%)',
          border: '2px solid #ff3333',
          boxShadow: '0 0 15px #ff3333',
          textShadow: '0 0 5px white',
          pointerEvents: 'none'
        }}>
          {node.name}
        </div>
      </Html>
    </group>
  );
}

function LinkComponent({ start, end }: { start: [number, number, number]; end: [number, number, number] }) {
  const points = [new THREE.Vector3(...start), new THREE.Vector3(...end)];
  return (
    <Line points={points} color="#88aaff" lineWidth={1} opacity={0.5} transparent />
  );
}

export default function KnowledgeGraph3D({ data, onNodeClick }: GraphProps) {
  const [nodePositions, setNodePositions] = useState<Map<string, [number, number, number]>>(new Map());

  useEffect(() => {
    if (!data.nodes.length) return;
    const positions = new Map<string, [number, number, number]>();
    data.nodes.forEach((node, i) => {
      const angle = (i / data.nodes.length) * Math.PI * 2;
      const radius = 6;
      positions.set(node.id, [
        Math.cos(angle) * radius,
        Math.sin(angle) * radius,
        Math.sin(angle * 2) * 2
      ]);
    });
    setNodePositions(positions);
  }, [data.nodes]);

  if (!nodePositions.size) return null;

  return (
    <div style={{ width: '100%', height: '100vh', background: '#1a1a1a' }}>
      <Canvas camera={{ position: [10, 10, 10], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        {data.nodes.map((node) => {
          const position = nodePositions.get(node.id);
          if (!position) return null;
          return (
            <NodeComponent
              key={node.id}
              node={node}
              position={position}
              onClick={() => onNodeClick?.(node)}
            />
          );
        })}
        {data.links.map((link, i) => {
          const startPos = nodePositions.get(link.source as string);
          const endPos = nodePositions.get(link.target as string);
          if (!startPos || !endPos) return null;
          return <LinkComponent key={i} start={startPos} end={endPos} />;
        })}
        <OrbitControls />
        <gridHelper args={[20, 20]} />
      </Canvas>
    </div>
  );
}