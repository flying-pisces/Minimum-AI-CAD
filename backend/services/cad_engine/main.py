from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import redis
import json
import time

app = FastAPI(title="CAD Engine Service", version="0.1.0")

# Redis client
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class AssemblyRequest(BaseModel):
    part1_analysis: Dict[str, Any]
    part2_analysis: Dict[str, Any]
    constraints: List[Dict[str, Any]]

class AssemblyResult(BaseModel):
    connector_id: str
    assembly_id: str
    success: bool
    error: str = None

@app.post("/generate_assembly", response_model=AssemblyResult)
async def generate_assembly(request: AssemblyRequest):
    """Generate connector and assembly based on part analysis and constraints"""
    
    try:
        # Parse the JSON strings if they come as strings
        if isinstance(request.part1_analysis, str):
            part1 = json.loads(request.part1_analysis)
        else:
            part1 = request.part1_analysis
            
        if isinstance(request.part2_analysis, str):
            part2 = json.loads(request.part2_analysis)
        else:
            part2 = request.part2_analysis
        
        # Extract constraint information
        distance_constraint = None
        for constraint in request.constraints:
            if constraint.get('type') == 'distance':
                distance_constraint = constraint
                break
        
        if not distance_constraint:
            raise Exception("No distance constraint found")
        
        # Generate connector using mock CAD engine logic
        connector_result = generate_connector_mock(part1, part2, distance_constraint)
        
        return AssemblyResult(
            connector_id=connector_result['connector_id'],
            assembly_id=connector_result['assembly_id'],
            success=True
        )
        
    except Exception as e:
        return AssemblyResult(
            connector_id="",
            assembly_id="",
            success=False,
            error=str(e)
        )

def generate_connector_mock(part1: dict, part2: dict, distance_constraint: dict) -> dict:
    """Mock connector generation for MVP"""
    
    # In a real implementation, this would:
    # 1. Analyze part geometries and mounting points
    # 2. Calculate required connector dimensions
    # 3. Generate 3D connector geometry using FreeCAD
    # 4. Create assembly with proper positioning
    # 5. Export STEP files for connector and assembly
    
    # Extract part centers
    p1_center = part1.get('geometry', {}).get('center', [0, 0, 0])
    p2_center = part2.get('geometry', {}).get('center', [0, 0, 0])
    
    # Calculate distance between parts
    import math
    current_distance = math.sqrt(
        (p2_center[0] - p1_center[0])**2 +
        (p2_center[1] - p1_center[1])**2 +
        (p2_center[2] - p1_center[2])**2
    )
    
    # Get target distance from constraint
    target_distance = distance_constraint.get('value', 50.0)
    
    # Mock connector design logic
    if target_distance > current_distance:
        # Need spacer/extension connector
        connector_type = "spacer"
        connector_length = target_distance - current_distance
    else:
        # Need mounting bracket
        connector_type = "bracket"
        connector_length = target_distance
    
    # Generate unique IDs
    import uuid
    connector_id = str(uuid.uuid4())
    assembly_id = str(uuid.uuid4())
    
    # Mock connector geometry generation
    connector_geometry = {
        "type": connector_type,
        "dimensions": {
            "length": connector_length,
            "width": 20.0,  # Default width
            "height": 10.0  # Default height
        },
        "mounting_points": [
            {"position": p1_center, "type": "bolt_hole", "diameter": 5.0},
            {"position": p2_center, "type": "bolt_hole", "diameter": 5.0}
        ]
    }
    
    # Cache connector design
    redis_client.setex(
        f"connector:{connector_id}",
        7200,  # 2 hours TTL
        json.dumps(connector_geometry)
    )
    
    # Mock assembly positioning
    assembly_info = {
        "part1_position": p1_center,
        "part2_position": [
            p1_center[0] + target_distance,
            p1_center[1],
            p1_center[2]
        ],
        "connector_position": [
            (p1_center[0] + p2_center[0]) / 2,
            (p1_center[1] + p2_center[1]) / 2,
            (p1_center[2] + p2_center[2]) / 2
        ]
    }
    
    # Cache assembly info
    redis_client.setex(
        f"assembly:{assembly_id}",
        7200,  # 2 hours TTL
        json.dumps(assembly_info)
    )
    
    return {
        "connector_id": connector_id,
        "assembly_id": assembly_id,
        "connector_geometry": connector_geometry,
        "assembly_info": assembly_info
    }

@app.get("/connector/{connector_id}")
async def get_connector(connector_id: str):
    """Get connector design details"""
    cached = redis_client.get(f"connector:{connector_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    return json.loads(cached)

@app.get("/assembly/{assembly_id}")
async def get_assembly_info(assembly_id: str):
    """Get assembly positioning information"""
    cached = redis_client.get(f"assembly:{assembly_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="Assembly not found")
    
    return json.loads(cached)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cad_engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)