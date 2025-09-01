from pydantic import BaseModel
from typing import List, Optional, Union, Literal
from datetime import datetime

# File models
class UploadedFile(BaseModel):
    id: str
    name: str
    size: int
    type: str
    url: str

# Geometry models
class Point3D(BaseModel):
    x: float
    y: float
    z: float

class BoundingBox(BaseModel):
    min: List[float]
    max: List[float]

class GeometryInfo(BaseModel):
    center: List[float]
    bounding_box: BoundingBox
    volume: float
    surface_area: float

class Feature(BaseModel):
    type: str
    properties: dict

class PartAnalysis(BaseModel):
    id: str
    geometry: GeometryInfo
    features: List[Feature]
    mounting_points: List[dict]

# Constraint models
class Constraint(BaseModel):
    type: Literal['distance', 'angle', 'alignment']
    value: float
    unit: str
    references: List[str]
    confidence: float

# Assembly models
class AssemblyRequest(BaseModel):
    part1_id: str
    part2_id: str
    constraints: str

class AssemblyResult(BaseModel):
    id: str
    status: Literal['processing', 'completed', 'failed']
    part1: Optional[PartAnalysis] = None
    part2: Optional[PartAnalysis] = None
    connector: Optional[dict] = None
    assembly: Optional[dict] = None
    parsed_constraints: List[Constraint] = []
    processing_time: Optional[float] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None

# Export models
class ExportRequest(BaseModel):
    format: Literal['step', 'stl', 'obj']