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
    """Mock STEP file analysis for MVP"""
    
    # In a real implementation, this would:
    # 1. Load STEP file using FreeCAD or OpenCascade
    # 2. Extract geometric properties
    # 3. Identify features like holes, edges, surfaces
    # 4. Find potential mounting points
    
    # Mock analysis with realistic values
    import random
    
    # Generate random but realistic geometry
    center = [
        round(random.uniform(-50, 50), 2),
        round(random.uniform(-50, 50), 2),
        round(random.uniform(-25, 25), 2)
    ]
    
    size = [
        round(random.uniform(10, 100), 2),
        round(random.uniform(10, 100), 2),
        round(random.uniform(5, 50), 2)
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "file_processor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)