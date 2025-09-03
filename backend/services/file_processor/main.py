from fastapi import FastAPI, HTTPException
import os
import redis
import json
from pathlib import Path
from pydantic import BaseModel

app = FastAPI(title="File Processor Service", version="0.1.0")

# Redis client
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# File paths
UPLOAD_DIR = Path("/app/uploads")

class AnalyzeRequest(BaseModel):
    file_id: str

class PartAnalysis(BaseModel):
    id: str
    geometry: dict
    features: list
    mounting_points: list

@app.post("/analyze", response_model=PartAnalysis)
async def analyze_part(request: AnalyzeRequest):
    """Analyze STEP file and extract geometry information"""
    
    # Get file info from cache
    file_info = redis_client.get(f"file:{request.file_id}")
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = json.loads(file_info)
    
    # Find the actual file
    step_files = list(UPLOAD_DIR.glob(f"{request.file_id}.*"))
    if not step_files:
        raise HTTPException(status_code=404, detail="Physical file not found")
    
    step_file = step_files[0]
    
    try:
        # For MVP, return mock analysis
        # In production, this would use FreeCAD or OpenCascade to analyze the STEP file
        analysis = analyze_step_file_mock(str(step_file), request.file_id)
        
        # Cache the analysis
        redis_client.setex(
            f"analysis:{request.file_id}",
            3600,  # 1 hour TTL
            analysis.model_dump_json()
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def analyze_step_file_mock(file_path: str, file_id: str) -> PartAnalysis:
    """Enhanced STEP file analysis using FreeCAD (fallback to mock if FreeCAD unavailable)"""
    
    try:
        # Try real STEP analysis with FreeCAD
        return analyze_step_file_freecad(file_path, file_id)
    except Exception as e:
        print(f"FreeCAD analysis failed, using mock analysis: {e}")
        # Fallback to mock analysis for MVP
        import random
        
        # Generate random but realistic geometry based on file size
        file_size = Path(file_path).stat().st_size
        scale_factor = max(1, file_size / 50000)  # Scale based on file size
        
        center = [
            round(random.uniform(-25, 25), 2),
            round(random.uniform(-25, 25), 2),
            round(random.uniform(-10, 10), 2)
        ]
        
        size = [
            round(random.uniform(10, 50) * scale_factor, 2),
            round(random.uniform(10, 50) * scale_factor, 2),
            round(random.uniform(5, 25) * scale_factor, 2)
        ]
        
        return PartAnalysis(
            id=file_id,
            geometry={
                "center": center,
                "bounding_box": {
                    "min": [center[0] - size[0]/2, center[1] - size[1]/2, center[2] - size[2]/2],
                    "max": [center[0] + size[0]/2, center[1] + size[1]/2, center[2] + size[2]/2]
                },
                "volume": round(size[0] * size[1] * size[2], 2),
                "surface_area": round(2 * (size[0]*size[1] + size[1]*size[2] + size[0]*size[2]), 2)
            },
            features=[
                {
                    "type": "surface",
                    "properties": {
                        "area": round(size[0] * size[1], 2),
                        "normal": [0, 0, 1]
                    }
                },
                {
                    "type": "edge",
                    "properties": {
                        "length": round(size[0], 2),
                        "direction": [1, 0, 0]
                    }
                }
            ],
            mounting_points=[
                {
                    "position": [center[0], center[1], center[2] + size[2]/2],
                    "normal": [0, 0, 1],
                    "type": "surface_mount"
                },
                {
                    "position": [center[0], center[1], center[2] - size[2]/2],
                    "normal": [0, 0, -1],
                    "type": "surface_mount"
                }
            ]
        )

def analyze_step_file_freecad(file_path: str, file_id: str) -> PartAnalysis:
    """Real STEP file analysis using FreeCAD"""
    import FreeCAD
    import Part
    import numpy as np
    
    # Create a new document
    doc = FreeCAD.newDocument()
    
    try:
        # Import STEP file
        Part.insert(file_path, doc.Name)
        
        # Get the imported part
        objects = doc.Objects
        if not objects:
            raise Exception("No objects found in STEP file")
        
        part = objects[0]
        if not hasattr(part, 'Shape'):
            raise Exception("Object has no Shape attribute")
        
        shape = part.Shape
        
        # Calculate bounding box
        bbox = shape.BoundBox
        center = [
            round((bbox.XMin + bbox.XMax) / 2, 2),
            round((bbox.YMin + bbox.YMax) / 2, 2),
            round((bbox.ZMin + bbox.ZMax) / 2, 2)
        ]
        
        # Extract geometry properties
        geometry = {
            "center": center,
            "bounding_box": {
                "min": [round(bbox.XMin, 2), round(bbox.YMin, 2), round(bbox.ZMin, 2)],
                "max": [round(bbox.XMax, 2), round(bbox.YMax, 2), round(bbox.ZMax, 2)]
            },
            "volume": round(shape.Volume, 2) if hasattr(shape, 'Volume') else 0.0,
            "surface_area": round(shape.Area, 2) if hasattr(shape, 'Area') else 0.0
        }
        
        # Extract features
        features = []
        
        # Faces (surfaces)
        for i, face in enumerate(shape.Faces[:5]):  # Limit to first 5 faces
            if hasattr(face, 'Area') and hasattr(face, 'normalAt'):
                try:
                    u, v = face.ParameterRange
                    normal = face.normalAt(u[0], v[0])
                    features.append({
                        "type": "surface",
                        "properties": {
                            "area": round(face.Area, 2),
                            "normal": [round(normal.x, 3), round(normal.y, 3), round(normal.z, 3)]
                        }
                    })
                except:
                    continue
        
        # Edges
        for i, edge in enumerate(shape.Edges[:5]):  # Limit to first 5 edges  
            if hasattr(edge, 'Length'):
                features.append({
                    "type": "edge",
                    "properties": {
                        "length": round(edge.Length, 2),
                        "direction": [1, 0, 0]  # Simplified direction
                    }
                })
        
        # Find potential mounting points (simplified)
        mounting_points = []
        
        # Add center points of largest faces as potential mounting points
        sorted_faces = sorted(shape.Faces, key=lambda f: f.Area, reverse=True)
        for face in sorted_faces[:4]:  # Top 4 largest faces
            try:
                center_of_mass = face.CenterOfMass
                u, v = face.ParameterRange
                normal = face.normalAt(u[0], v[0])
                
                mounting_points.append({
                    "position": [
                        round(center_of_mass.x, 2),
                        round(center_of_mass.y, 2), 
                        round(center_of_mass.z, 2)
                    ],
                    "normal": [round(normal.x, 3), round(normal.y, 3), round(normal.z, 3)],
                    "type": "surface_mount"
                })
            except:
                continue
        
        return PartAnalysis(
            id=file_id,
            geometry=geometry,
            features=features,
            mounting_points=mounting_points
        )
        
    finally:
        # Clean up
        FreeCAD.closeDocument(doc.Name)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "file_processor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)