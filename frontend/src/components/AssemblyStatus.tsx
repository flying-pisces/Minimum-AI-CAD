import React from 'react';
import { AssemblyResult } from '../types/assembly';

interface AssemblyStatusProps {
  result: AssemblyResult | null;
  onExport?: (format: 'step' | 'stl' | 'obj') => void;
}

export const AssemblyStatus: React.FC<AssemblyStatusProps> = ({
  result,
  onExport
}) => {
  if (!result) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing': return '#ff9800';
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing': return '⏳';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  return (
    <div style={{
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9'
    }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '18px' }}>Assembly Status</h3>
      
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <span style={{ fontSize: '24px', marginRight: '8px' }}>
          {getStatusIcon(result.status)}
        </span>
        <span style={{ 
          fontSize: '16px', 
          fontWeight: 'bold',
          color: getStatusColor(result.status),
          textTransform: 'capitalize'
        }}>
          {result.status}
        </span>
        {result.processingTime && (
          <span style={{ fontSize: '12px', color: '#666', marginLeft: '12px' }}>
            ({result.processingTime}s)
          </span>
        )}
      </div>

      {result.error && (
        <div style={{
          padding: '12px',
          backgroundColor: '#ffebee',
          border: '1px solid #ffcdd2',
          borderRadius: '4px',
          color: '#c62828',
          marginBottom: '16px'
        }}>
          <strong>Error:</strong> {result.error}
        </div>
      )}

      {result.parsedConstraints && result.parsedConstraints.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
            Understood Constraints:
          </div>
          {result.parsedConstraints.map((constraint, index) => (
            <div key={index} style={{
              padding: '8px 12px',
              margin: '4px 0',
              backgroundColor: 'white',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              <span style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                {constraint.type}:
              </span> {constraint.value} {constraint.unit}
              <span style={{ color: '#666', marginLeft: '8px' }}>
                (confidence: {Math.round(constraint.confidence * 100)}%)
              </span>
            </div>
          ))}
        </div>
      )}

      {result.status === 'completed' && result.assembly && onExport && (
        <div>
          <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
            Export Assembly:
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => onExport('step')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              STEP
            </button>
            <button
              onClick={() => onExport('stl')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              STL
            </button>
            <button
              onClick={() => onExport('obj')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#ff9800',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              OBJ
            </button>
          </div>
        </div>
      )}

      {result.part1 && result.part2 && (
        <div style={{ marginTop: '16px', fontSize: '12px', color: '#666' }}>
          <div><strong>Part 1:</strong> Center at ({result.part1.geometry.center.map(c => c.toFixed(1)).join(', ')})</div>
          <div><strong>Part 2:</strong> Center at ({result.part2.geometry.center.map(c => c.toFixed(1)).join(', ')})</div>
        </div>
      )}
    </div>
  );
};