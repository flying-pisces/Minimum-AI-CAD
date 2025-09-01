import axios from 'axios';
import { AssemblyRequest, AssemblyResult, UploadedFile } from '../types/assembly';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for CAD processing
});

export const api = {
  // File upload endpoints
  uploadFile: async (file: File): Promise<UploadedFile> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/v1/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Assembly endpoints
  createAssembly: async (request: AssemblyRequest): Promise<AssemblyResult> => {
    const response = await apiClient.post('/api/v1/assembly', request);
    return response.data;
  },

  getAssembly: async (id: string): Promise<AssemblyResult> => {
    const response = await apiClient.get(`/api/v1/assembly/${id}`);
    return response.data;
  },

  exportAssembly: async (id: string, format: 'step' | 'stl' | 'obj'): Promise<Blob> => {
    const response = await apiClient.post(`/api/v1/assembly/${id}/export`, 
      { format },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Health check
  health: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};