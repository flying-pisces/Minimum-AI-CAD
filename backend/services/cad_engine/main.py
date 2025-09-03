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
    """Enhanced template-based connector generation for MVP"""
    
    # Try real connector generation, fallback to mock if unavailable
    try:
        return generate_connector_freecad(part1, part2, distance_constraint)
    except Exception as e:
        print(f"FreeCAD connector generation failed, using template approach: {e}")
        return generate_connector_template(part1, part2, distance_constraint)

def generate_connector_template(part1: dict, part2: dict, distance_constraint: dict) -> dict:
    """Template-based connector generation using predefined designs"""
    import math
    import uuid
    
    # Extract part centers and bounding boxes
    p1_center = part1.get('geometry', {}).get('center', [0, 0, 0])
    p2_center = part2.get('geometry', {}).get('center', [0, 0, 0])
    p1_bbox = part1.get('geometry', {}).get('bounding_box', {})
    p2_bbox = part2.get('geometry', {}).get('bounding_box', {})
    
    # Calculate current distance and direction
    distance_vector = [p2_center[i] - p1_center[i] for i in range(3)]
    current_distance = math.sqrt(sum(d**2 for d in distance_vector))
    
    # Normalize direction vector
    if current_distance > 0:
        direction = [d / current_distance for d in distance_vector]
    else:
        direction = [1, 0, 0]  # Default direction
    
    # Get target distance and other constraints
    target_distance = distance_constraint.get('value', 50.0)
    
    # Determine connector template based on requirements
    connector_template = determine_connector_template(
        target_distance, current_distance, direction, p1_bbox, p2_bbox
    )
    
    # Generate connector geometry using template
    connector_id = str(uuid.uuid4())
    assembly_id = str(uuid.uuid4())
    
    connector_geometry = generate_connector_from_template(
        connector_template, p1_center, p2_center, target_distance, direction
    )
    
    # Cache connector design
    redis_client.setex(
        f"connector:{connector_id}",
        7200,  # 2 hours TTL
        json.dumps(connector_geometry)
    )
    
    # Calculate assembly positioning
    assembly_info = calculate_assembly_positioning(
        p1_center, p2_center, target_distance, direction, connector_geometry
    )
    
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

def determine_connector_template(target_distance, current_distance, direction, p1_bbox, p2_bbox):
    """Determine which connector template to use based on requirements"""
    
    # Template selection logic
    if target_distance < 20:
        return "direct_mount"  # Small bolted connection
    elif target_distance < 50:
        return "bracket"       # L-bracket or similar
    elif target_distance < 100:
        return "spacer"        # Spacer block
    elif abs(direction[2]) > 0.8:  # Mostly vertical
        return "vertical_post"  # Vertical mounting post
    else:
        return "horizontal_beam"  # Horizontal connecting beam

def generate_connector_from_template(template_type, p1_center, p2_center, target_distance, direction):
    """Generate connector geometry based on template type"""
    
    if template_type == "direct_mount":
        return {
            "type": "direct_mount",
            "template": template_type,
            "dimensions": {
                "length": target_distance,
                "width": min(15.0, target_distance * 0.8),
                "height": min(10.0, target_distance * 0.5),
                "bolt_diameter": 5.0,
                "bolt_spacing": max(10.0, target_distance * 0.3)
            },
            "mounting_points": [
                {"position": p1_center, "type": "bolt_hole", "diameter": 5.0},
                {"position": p2_center, "type": "bolt_hole", "diameter": 5.0}
            ],
            "material": "aluminum",
            "features": ["bolt_holes", "chamfered_edges"]
        }
    
    elif template_type == "bracket":
        return {
            "type": "l_bracket",
            "template": template_type,
            "dimensions": {
                "length": target_distance,
                "width": max(20.0, target_distance * 0.4),
                "height": max(15.0, target_distance * 0.3),
                "thickness": 5.0,
                "flange_width": max(15.0, target_distance * 0.25)
            },
            "mounting_points": [
                {"position": p1_center, "type": "bolt_hole", "diameter": 6.0},
                {"position": p2_center, "type": "bolt_hole", "diameter": 6.0},
                {"position": [(p1_center[0] + p2_center[0])/2, p1_center[1], p1_center[2] - 10], "type": "bolt_hole", "diameter": 6.0}
            ],
            "material": "steel",
            "features": ["reinforcement_ribs", "bolt_holes", "chamfered_edges"]
        }
    
    elif template_type == "spacer":
        return {
            "type": "spacer_block",
            "template": template_type,
            "dimensions": {
                "length": target_distance,
                "width": max(25.0, target_distance * 0.5),
                "height": max(20.0, target_distance * 0.4),
                "bore_diameter": 8.0
            },
            "mounting_points": [
                {"position": p1_center, "type": "threaded_hole", "diameter": 8.0, "thread": "M8"},
                {"position": p2_center, "type": "threaded_hole", "diameter": 8.0, "thread": "M8"}
            ],
            "material": "aluminum",
            "features": ["threaded_bores", "hex_socket"]
        }
    
    elif template_type == "vertical_post":
        return {
            "type": "vertical_post",
            "template": template_type,
            "dimensions": {
                "height": target_distance,
                "diameter": max(20.0, target_distance * 0.2),
                "base_diameter": max(30.0, target_distance * 0.3),
                "base_thickness": 10.0
            },
            "mounting_points": [
                {"position": [p1_center[0], p1_center[1], p1_center[2] - 5], "type": "bolt_hole", "diameter": 6.0},
                {"position": p2_center, "type": "bolt_hole", "diameter": 6.0}
            ],
            "material": "steel",
            "features": ["base_plate", "cylindrical_post", "top_flange"]
        }
    
    else:  # horizontal_beam
        return {
            "type": "horizontal_beam",
            "template": template_type,
            "dimensions": {
                "length": target_distance,
                "width": max(30.0, target_distance * 0.3),
                "height": max(25.0, target_distance * 0.25),
                "wall_thickness": 3.0
            },
            "mounting_points": [
                {"position": p1_center, "type": "bolt_hole", "diameter": 8.0},
                {"position": p2_center, "type": "bolt_hole", "diameter": 8.0},
                # Additional mounting points for stability
                {"position": [p1_center[0], p1_center[1], p1_center[2] + 15], "type": "bolt_hole", "diameter": 6.0},
                {"position": [p2_center[0], p2_center[1], p2_center[2] + 15], "type": "bolt_hole", "diameter": 6.0}
            ],
            "material": "aluminum_extrusion",
            "features": ["hollow_section", "bolt_holes", "end_caps"]
        }

def calculate_assembly_positioning(p1_center, p2_center, target_distance, direction, connector_geometry):
    """Calculate final positioning for assembly based on connector"""
    
    # Calculate new part2 position to achieve target distance
    new_p2_position = [
        p1_center[0] + direction[0] * target_distance,
        p1_center[1] + direction[1] * target_distance,
        p1_center[2] + direction[2] * target_distance
    ]
    
    # Connector position (center between parts)
    connector_position = [
        (p1_center[0] + new_p2_position[0]) / 2,
        (p1_center[1] + new_p2_position[1]) / 2,
        (p1_center[2] + new_p2_position[2]) / 2
    ]
    
    # Adjust based on connector type
    connector_type = connector_geometry.get("type", "bracket")
    if connector_type == "vertical_post":
        # Post sits at part1 location, extends to part2
        connector_position = p1_center
    elif connector_type == "l_bracket":
        # L-bracket might be offset to provide better support
        connector_position[2] = min(p1_center[2], new_p2_position[2]) - 5
    
    return {
        "part1_position": p1_center,
        "part2_position": new_p2_position,
        "connector_position": connector_position,
        "connector_rotation": [0, 0, 0],  # No rotation for now
        "assembly_constraints": {
            "distance_achieved": target_distance,
            "connector_template": connector_geometry.get("template", "unknown")
        }
    }

def generate_connector_freecad(part1: dict, part2: dict, distance_constraint: dict) -> dict:
    """Real connector generation using FreeCAD (placeholder for future implementation)"""
    # This would use FreeCAD to generate actual 3D geometry
    # For now, fall back to template method
    raise Exception("FreeCAD connector generation not implemented yet")

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