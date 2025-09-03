import React, { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { ConstraintInput } from './components/ConstraintInput';
import { AssemblyStatus } from './components/AssemblyStatus';
import { StepViewer } from './components/StepViewer';
import { UploadedFile, AssemblyResult } from './types/assembly';
import { api } from './services/api';
import { saveAs } from 'file-saver';

function App() {
  const [part1, setPart1] = useState<UploadedFile | null>(null);
  const [part2, setPart2] = useState<UploadedFile | null>(null);
  const [constraints, setConstraints] = useState<string>('');
  const [assemblyResult, setAssemblyResult] = useState<AssemblyResult | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleGenerateAssembly = async () => {
    if (!part1 || !part2 || !constraints.trim()) {
      alert('Please upload both parts and enter assembly instructions');
      return;
    }

    setProcessing(true);
    setAssemblyResult(null);

    try {
      const result = await api.createAssembly({
        part1Id: part1.id,
        part2Id: part2.id,
        constraints: constraints.trim()
      });
      
      setAssemblyResult(result);

      // Poll for completion if processing
      if (result.status === 'processing') {
        const pollInterval = setInterval(async () => {
          try {
            const updatedResult = await api.getAssembly(result.id);
            setAssemblyResult(updatedResult);
            
            if (updatedResult.status !== 'processing') {
              clearInterval(pollInterval);
            }
          } catch (error) {
            clearInterval(pollInterval);
            console.error('Error polling assembly status:', error);
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Error creating assembly:', error);
      setAssemblyResult({
        id: 'error',
        status: 'failed',
        part1: {} as any,
        part2: {} as any,
        parsedConstraints: [],
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleExport = async (format: 'step' | 'stl' | 'obj') => {
    if (!assemblyResult?.id) return;

    try {
      const blob = await api.exportAssembly(assemblyResult.id, format);
      saveAs(blob, `assembly.${format}`);
    } catch (error) {
      console.error('Error exporting assembly:', error);
      alert('Failed to export assembly');
    }
  };

  const handleReset = () => {
    setPart1(null);
    setPart2(null);
    setConstraints('');
    setAssemblyResult(null);
  };

  const canGenerate = part1 && part2 && constraints.trim() && !processing;

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ color: '#333', fontSize: '36px', margin: '0 0 8px 0' }}>
          Minimum AI CAD
        </h1>
        <p style={{ color: '#666', fontSize: '16px', margin: '0' }}>
          Generate assembly connectors from natural language instructions
        </p>
      </header>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '30px'
      }}>
        <div>
          <h2 style={{ fontSize: '20px', marginBottom: '12px' }}>Part 1</h2>
          <FileUpload
            onFileUploaded={setPart1}
            accept=".step,.stp,.STEP,.STP"
            label="Upload Part 1"
            disabled={processing}
          />
          {part1 && (
            <div style={{ 
              marginTop: '8px', 
              padding: '8px', 
              backgroundColor: '#e8f5e8', 
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              ✓ {part1.name} ({(part1.size / 1024).toFixed(1)} KB)
            </div>
          )}
          <div style={{ marginTop: '12px' }}>
            <StepViewer file={part1} width={300} height={200} />
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: '20px', marginBottom: '12px' }}>Part 2</h2>
          <FileUpload
            onFileUploaded={setPart2}
            accept=".step,.stp,.STEP,.STP"
            label="Upload Part 2"
            disabled={processing}
          />
          {part2 && (
            <div style={{ 
              marginTop: '8px', 
              padding: '8px', 
              backgroundColor: '#e8f5e8', 
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              ✓ {part2.name} ({(part2.size / 1024).toFixed(1)} KB)
            </div>
          )}
          <div style={{ marginTop: '12px' }}>
            <StepViewer file={part2} width={300} height={200} />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <ConstraintInput
          onConstraintChange={setConstraints}
          disabled={processing}
        />
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '16px',
        marginBottom: '30px'
      }}>
        <button
          onClick={handleGenerateAssembly}
          disabled={!canGenerate}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: 'bold',
            backgroundColor: canGenerate ? '#4caf50' : '#cccccc',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: canGenerate ? 'pointer' : 'not-allowed',
            minWidth: '200px'
          }}
        >
          {processing ? '🔄 Processing...' : '🚀 Generate Assembly'}
        </button>

        <button
          onClick={handleReset}
          disabled={processing}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: '#ff9800',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: processing ? 'not-allowed' : 'pointer'
          }}
        >
          🔄 Reset
        </button>
      </div>

      {assemblyResult && (
        <AssemblyStatus
          result={assemblyResult}
          onExport={handleExport}
        />
      )}

      <footer style={{
        textAlign: 'center',
        marginTop: '40px',
        padding: '20px',
        borderTop: '1px solid #eee',
        color: '#666',
        fontSize: '12px'
      }}>
        <p>
          Upload two STEP files and describe how they should be connected.
          The AI will generate a custom connector part to satisfy your requirements.
        </p>
        <p>
          Supported formats: STEP (.step, .stp) | 
          Export formats: STEP, STL, OBJ
        </p>
      </footer>
    </div>
  );
}

export default App;