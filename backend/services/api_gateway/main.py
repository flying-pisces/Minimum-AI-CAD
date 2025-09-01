from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import uuid
import aiofiles
import httpx
from typing import Dict, Any
import time
import redis
import json
from pathlib import Path

# Import shared models
import sys
sys.path.append('/app/shared')
from models import UploadedFile, AssemblyRequest, AssemblyResult, ExportRequest

app = FastAPI(title="Minimum AI CAD API", version="0.1.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client for caching and session management
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# File storage configuration
UPLOAD_DIR = Path("/app/uploads")
EXPORT_DIR = Path("/app/exports")
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# Service URLs
FILE_PROCESSOR_URL = os.getenv("FILE_PROCESSOR_URL", "http://localhost:8001")
CAD_ENGINE_URL = os.getenv("CAD_ENGINE_URL", "http://localhost:8003")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/v1/files/upload", response_model=UploadedFile)
async def upload_file(file: UploadFile = File(...)):
    """Upload and validate STEP file"""
    
    # Validate file type
    allowed_extensions = {'.step', '.stp', '.STEP', '.STP'}
    file_extension = Path(file.filename).suffix
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique file ID and path
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create file record
    uploaded_file = UploadedFile(
        id=file_id,
        name=file.filename,
        size=len(content),
        type=file.content_type or "application/step",
        url=f"/api/v1/files/{file_id}"
    )
    
    # Cache file info in Redis
    redis_client.setex(
        f"file:{file_id}", 
        3600,  # 1 hour TTL
        uploaded_file.model_dump_json()
    )
    
    return uploaded_file

@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: str):
    """Retrieve file metadata"""
    cached = redis_client.get(f"file:{file_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="File not found")
    
    return json.loads(cached)

@app.post("/api/v1/assembly", response_model=AssemblyResult)
async def create_assembly(request: AssemblyRequest, background_tasks: BackgroundTasks):
    """Create assembly from two parts and constraints"""
    
    # Generate assembly ID
    assembly_id = str(uuid.uuid4())
    
    # Verify files exist
    part1_info = redis_client.get(f"file:{request.part1_id}")
    part2_info = redis_client.get(f"file:{request.part2_id}")
    
    if not part1_info or not part2_info:
        raise HTTPException(status_code=404, detail="One or more files not found")
    
    # Create initial assembly result
    assembly_result = AssemblyResult(
        id=assembly_id,
        status="processing",
        parsed_constraints=[]
    )
    
    # Cache assembly status
    redis_client.setex(
        f"assembly:{assembly_id}",
        7200,  # 2 hours TTL
        assembly_result.model_dump_json()
    )
    
    # Start background processing
    background_tasks.add_task(
        process_assembly, 
        assembly_id, 
        request.part1_id, 
        request.part2_id, 
        request.constraints
    )
    
    return assembly_result

async def process_assembly(assembly_id: str, part1_id: str, part2_id: str, constraints: str):
    """Background task to process assembly"""
    start_time = time.time()
    
    try:
        # Step 1: Analyze parts
        async with httpx.AsyncClient() as client:
            part1_analysis = await client.post(
                f"{FILE_PROCESSOR_URL}/analyze", 
                json={"file_id": part1_id}
            )
            part2_analysis = await client.post(
                f"{FILE_PROCESSOR_URL}/analyze", 
                json={"file_id": part2_id}
            )
            
            if part1_analysis.status_code != 200 or part2_analysis.status_code != 200:
                raise Exception("Failed to analyze parts")
        
        # Step 2: Parse constraints (simple version for MVP)
        parsed_constraints = parse_simple_constraints(constraints)
        
        # Step 3: Generate assembly using CAD engine
        async with httpx.AsyncClient(timeout=120.0) as client:
            assembly_response = await client.post(
                f"{CAD_ENGINE_URL}/generate_assembly",
                json={
                    "part1_analysis": part1_analysis.json(),
                    "part2_analysis": part2_analysis.json(),
                    "constraints": [c.dict() for c in parsed_constraints]
                }
            )
            
            if assembly_response.status_code != 200:
                raise Exception("Failed to generate assembly")
        
        # Update assembly result
        processing_time = time.time() - start_time
        assembly_result = AssemblyResult(
            id=assembly_id,
            status="completed",
            part1=part1_analysis.json(),
            part2=part2_analysis.json(),
            connector={"id": f"{assembly_id}_connector", "url": f"/api/v1/assembly/{assembly_id}/connector"},
            assembly={"id": f"{assembly_id}_assembly", "url": f"/api/v1/assembly/{assembly_id}/download"},
            parsed_constraints=parsed_constraints,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        assembly_result = AssemblyResult(
            id=assembly_id,
            status="failed",
            parsed_constraints=[],
            processing_time=round(processing_time, 2),
            error=str(e)
        )
    
    # Update cache
    redis_client.setex(
        f"assembly:{assembly_id}",
        7200,
        assembly_result.model_dump_json()
    )

def parse_simple_constraints(constraints_text: str):
    """Simple constraint parser for MVP"""
    from models import Constraint
    
    constraints = []
    text = constraints_text.lower()
    
    # Simple distance parsing
    if "cm" in text or "centimeter" in text:
        # Extract number before "cm"
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*cm', text)
        if numbers:
            constraints.append(Constraint(
                type="distance",
                value=float(numbers[0]) * 10,  # Convert cm to mm
                unit="mm",
                references=["part1", "part2"],
                confidence=0.8
            ))
    
    elif "mm" in text or "millimeter" in text:
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*mm', text)
        if numbers:
            constraints.append(Constraint(
                type="distance",
                value=float(numbers[0]),
                unit="mm",
                references=["part1", "part2"],
                confidence=0.8
            ))
    
    # Simple angle parsing
    if "degree" in text or "°" in text:
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(?:degree|°)', text)
        if numbers:
            constraints.append(Constraint(
                type="angle",
                value=float(numbers[0]),
                unit="degrees",
                references=["part1", "part2"],
                confidence=0.7
            ))
    
    # Default distance if no specific constraint found
    if not constraints:
        constraints.append(Constraint(
            type="distance",
            value=50.0,  # Default 50mm
            unit="mm",
            references=["part1", "part2"],
            confidence=0.5
        ))
    
    return constraints

@app.get("/api/v1/assembly/{assembly_id}", response_model=AssemblyResult)
async def get_assembly(assembly_id: str):
    """Get assembly status and results"""
    cached = redis_client.get(f"assembly:{assembly_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="Assembly not found")
    
    return AssemblyResult.model_validate_json(cached)

@app.post("/api/v1/assembly/{assembly_id}/export")
async def export_assembly(assembly_id: str, request: ExportRequest):
    """Export assembly in specified format"""
    
    # Check if assembly exists and is completed
    assembly_data = redis_client.get(f"assembly:{assembly_id}")
    if not assembly_data:
        raise HTTPException(status_code=404, detail="Assembly not found")
    
    assembly = AssemblyResult.model_validate_json(assembly_data)
    if assembly.status != "completed":
        raise HTTPException(status_code=400, detail="Assembly not completed")
    
    # For MVP, return a mock file
    # In production, this would call the CAD engine to export the actual file
    mock_content = f"# Mock {request.format.upper()} file for assembly {assembly_id}\n"
    mock_content += "# This is a placeholder for the actual CAD export\n"
    
    def generate():
        yield mock_content.encode()
    
    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=assembly_{assembly_id}.{request.format}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)