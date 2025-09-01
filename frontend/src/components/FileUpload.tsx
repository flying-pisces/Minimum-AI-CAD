import React, { useCallback, useState } from 'react';
import { UploadedFile } from '../types/assembly';
import { api } from '../services/api';

interface FileUploadProps {
  onFileUploaded: (file: UploadedFile) => void;
  accept: string;
  label: string;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileUploaded,
  accept,
  label,
  disabled = false
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const uploadedFile = await api.uploadFile(file);
      onFileUploaded(uploadedFile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onFileUploaded]);

  return (
    <div style={{ 
      border: '2px dashed #ccc', 
      borderRadius: '8px', 
      padding: '20px', 
      textAlign: 'center',
      backgroundColor: disabled ? '#f5f5f5' : 'white'
    }}>
      <input
        type="file"
        accept={accept}
        onChange={handleFileSelect}
        disabled={disabled || uploading}
        style={{ display: 'none' }}
        id={`file-input-${label}`}
      />
      <label 
        htmlFor={`file-input-${label}`}
        style={{
          cursor: disabled || uploading ? 'not-allowed' : 'pointer',
          color: disabled ? '#999' : '#007bff'
        }}
      >
        {uploading ? (
          <div>
            <div>Uploading...</div>
            <div style={{ fontSize: '12px', color: '#666' }}>Please wait</div>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '16px', marginBottom: '8px' }}>📁 {label}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              Click to select STEP file (.step, .stp)
            </div>
          </div>
        )}
      </label>
      {error && (
        <div style={{ color: 'red', fontSize: '14px', marginTop: '8px' }}>
          Error: {error}
        </div>
      )}
    </div>
  );
};