export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
}

export interface PartAnalysis {
  id: string;
  geometry: {
    center: [number, number, number];
    boundingBox: {
      min: [number, number, number];
      max: [number, number, number];
    };
    volume: number;
    surfaceArea: number;
  };
  features: {
    holes: Array<{
      center: [number, number, number];
      diameter: number;
    }>;
    edges: Array<{
      start: [number, number, number];
      end: [number, number, number];
    }>;
    surfaces: Array<{
      type: 'plane' | 'cylinder' | 'sphere';
      normal: [number, number, number];
    }>;
  };
  mountingPoints: Array<{
    position: [number, number, number];
    normal: [number, number, number];
  }>;
}

export interface Constraint {
  type: 'distance' | 'angle' | 'alignment';
  value: number;
  unit: string;
  references: string[];
  confidence: number;
}

export interface AssemblyRequest {
  part1Id: string;
  part2Id: string;
  constraints: string;
}

export interface AssemblyResult {
  id: string;
  status: 'processing' | 'completed' | 'failed';
  part1: PartAnalysis;
  part2: PartAnalysis;
  connector?: {
    id: string;
    url: string;
  };
  assembly?: {
    id: string;
    url: string;
  };
  parsedConstraints: Constraint[];
  processingTime?: number;
  error?: string;
}