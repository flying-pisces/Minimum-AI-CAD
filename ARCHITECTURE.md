# Minimum AI CAD - Technical Architecture

## System Overview

Minimum AI CAD follows a microservices architecture with clear separation between frontend web UI and backend CAD processing engines. The system is designed for extensibility, supporting future multi-modal inputs and advanced AI features.

## Architecture Principles

1. **Modularity**: Each service handles specific functionality
2. **Scalability**: Independent scaling of components
3. **Extensibility**: Plugin architecture for new CAD engines and AI models
4. **Reliability**: Fault tolerance and graceful degradation
5. **Performance**: Optimized for sub-30-second processing times

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Upload    │ │   3D        │ │   Natural Language      │ │
│  │  Component  │ │  Viewer     │ │   Interface             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                             │
│                   (FastAPI + Load Balancer)                │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  File Processing│ │   NLP Service   │ │  CAD Engine     │
│    Service      │ │                 │ │   Service       │
│                 │ │                 │ │                 │
│ • STEP Analysis │ │ • Constraint    │ │ • FreeCAD API   │
│ • Geometry      │ │   Parsing       │ │ • OpenSCAD      │
│   Extraction    │ │ • Intent        │ │ • Assembly Gen  │
│ • 3D Conversion │ │   Recognition   │ │ • Export        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Assembly Generator                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ Constraint  │ │ Connector   │ │  Validation &           │ │
│  │ Solver      │ │ Generator   │ │  Optimization           │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Redis     │ │ File System │ │   PostgreSQL            │ │
│  │  (Cache)    │ │   (STEP     │ │  (Metadata &            │ │
│  │             │ │   Files)    │ │   User Data)            │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Technology Stack
- **Framework**: React 18 with TypeScript
- **3D Visualization**: Three.js + CAD Exchanger Web Toolkit
- **UI Components**: Material-UI or Tailwind CSS
- **State Management**: Redux Toolkit or Zustand
- **Build Tool**: Vite for fast development and building

### Component Structure
```
src/
├── components/
│   ├── FileUpload/
│   │   ├── DropZone.tsx
│   │   ├── FileValidator.ts
│   │   └── ProgressIndicator.tsx
│   ├── Viewer3D/
│   │   ├── ThreeJSViewer.tsx
│   │   ├── CameraControls.ts
│   │   └── ModelLoader.ts
│   ├── NLInterface/
│   │   ├── TextInput.tsx
│   │   ├── ConstraintBuilder.tsx
│   │   └── ChatInterface.tsx
│   └── Assembly/
│       ├── PreviewPanel.tsx
│       ├── ParameterControls.tsx
│       └── ExportOptions.tsx
├── services/
│   ├── apiClient.ts
│   ├── fileProcessing.ts
│   └── websocketClient.ts
├── types/
│   ├── assembly.ts
│   ├── geometry.ts
│   └── api.ts
└── utils/
    ├── fileConversion.ts
    ├── geometryHelpers.ts
    └── validation.ts
```

## Backend Microservices

### 1. API Gateway (FastAPI)

**Responsibilities:**
- Request routing and load balancing
- Authentication and rate limiting
- WebSocket connections for real-time updates
- Response caching and compression

**Endpoints:**
```python
# Core Assembly API
POST /api/v1/assembly          # Create new assembly
GET  /api/v1/assembly/{id}     # Get assembly status
POST /api/v1/assembly/{id}/export # Export assembly

# Multi-Modal Extensions (Future)
POST /api/v1/generate/text-to-cad
POST /api/v1/generate/photo-to-cad
POST /api/v1/analyze/part-features
```

### 2. File Processing Service

**Technology**: Python + Open3D + FreeCAD Python API

**Capabilities:**
- STEP file validation and parsing
- Geometry analysis (centers, bounding boxes, surfaces)
- Feature extraction (holes, edges, mounting points)
- 3D model conversion for web visualization

```python
class StepAnalyzer:
    def analyze_part(self, step_file_path):
        return {
            'geometry': {
                'center': [x, y, z],
                'bounding_box': {'min': [x,y,z], 'max': [x,y,z]},
                'volume': float,
                'surface_area': float
            },
            'features': {
                'holes': [{'center': [x,y,z], 'diameter': float}],
                'edges': [{'start': [x,y,z], 'end': [x,y,z]}],
                'surfaces': [{'type': 'plane|cylinder|sphere', 'normal': [x,y,z]}]
            },
            'mounting_points': [{'position': [x,y,z], 'normal': [x,y,z]}]
        }
```

### 3. NLP Service

**Technology**: Python + Transformers + LangChain

**Core Components:**
- Intent recognition for assembly constraints
- Named entity recognition for dimensions and orientations
- Constraint validation and conflict resolution

```python
class ConstraintParser:
    def parse_requirements(self, user_input: str):
        return {
            'constraints': [
                {
                    'type': 'distance|angle|alignment',
                    'value': float,
                    'unit': 'mm|degrees|relative',
                    'references': ['part1', 'part2'],
                    'confidence': float
                }
            ],
            'clarifications_needed': [str],
            'feasibility': float
        }
```

### 4. CAD Engine Service

**Primary Engine**: FreeCAD Python API  
**Secondary**: OpenSCAD (for parametric designs)

**Docker Container Configuration:**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y freecad-python3
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY cad_service/ /app/
WORKDIR /app
CMD ["python", "service.py"]
```

**Connector Generation Pipeline:**
```python
class ConnectorGenerator:
    def generate_connector(self, part1_analysis, part2_analysis, constraints):
        # 1. Determine mounting strategy
        strategy = self.analyze_mounting_strategy(part1_analysis, part2_analysis)
        
        # 2. Generate base connector geometry
        base_geometry = self.create_base_connector(constraints, strategy)
        
        # 3. Add mounting features (holes, slots, flanges)
        connector = self.add_mounting_features(base_geometry, part1_analysis, part2_analysis)
        
        # 4. Validate structural integrity
        if self.validate_connector(connector, constraints):
            return self.export_step(connector)
        else:
            return self.generate_alternative_design(constraints)
```

### 5. Assembly Generator Service

**Responsibilities:**
- Constraint solving and optimization
- Assembly validation
- Collision detection
- Structural analysis (basic)

**Core Algorithm:**
```python
class AssemblyGenerator:
    def create_assembly(self, part1, part2, connector, constraints):
        # 1. Position parts according to constraints
        positions = self.solve_constraints(constraints)
        
        # 2. Validate no collisions
        if self.detect_collisions(part1, part2, connector, positions):
            return self.resolve_collisions(positions)
        
        # 3. Generate final assembly
        return self.combine_parts(part1, part2, connector, positions)
```

## Data Architecture

### Storage Systems

**1. Redis Cache**
- Session data and processing status
- Geometry analysis results
- Constraint parsing cache
- Real-time processing updates

**2. File System (with CDN)**
- Original STEP files (temporary, 24-hour retention)
- Generated assemblies and connectors
- 3D model files for web viewing
- Export files (STEP, STL, OBJ)

**3. PostgreSQL Database**
- User accounts and projects (future)
- Assembly metadata and history
- Performance metrics and analytics
- A/B testing data

### Data Flow

```
Upload → Validation → Analysis → NLP Processing → 
Constraint Solving → Connector Generation → Assembly → 
Validation → Export → Cleanup
```

## Multi-Modal Extensions (Phase 3+)

### Photo-to-CAD Pipeline

```
Mobile Photos → Multi-View Reconstruction → Point Cloud → 
Mesh Generation → CAD Feature Recognition → STEP Export
```

**Technology Stack:**
- **Computer Vision**: OpenCV + COLMAP for 3D reconstruction
- **Deep Learning**: Custom CNN for feature recognition
- **Point Cloud Processing**: Open3D for mesh generation
- **CAD Conversion**: Custom algorithms for parametric feature extraction

### Text-to-CAD Pipeline

```
Text Description → Geometric Parsing → Parameter Extraction → 
Parametric Modeling → STEP Generation
```

**Examples:**
- "1cm x 1cm x 1cm cube" → Parametric cube with 10mm dimensions
- "cylindrical rod 50mm long, 5mm diameter" → Parametric cylinder
- "L-bracket with 90-degree bend" → Template-based L-bracket generation

## Performance Optimization

### Caching Strategy
- **L1 Cache**: In-memory results during processing
- **L2 Cache**: Redis for session and repeated analysis
- **L3 Cache**: CDN for static 3D models and exports

### Parallel Processing
- Concurrent analysis of multiple parts
- Parallel constraint evaluation
- Asynchronous connector generation

### Resource Management
- Container-based CAD engine isolation
- GPU acceleration for AI/ML models
- Automatic scaling based on load

## Security & Privacy

### File Security
- STEP file validation and sanitization
- Temporary file encryption at rest
- Automatic cleanup after 24 hours
- Scan for embedded malware

### API Security
- Rate limiting per user/IP
- JWT-based authentication
- Request validation and sanitization
- CORS configuration

### Privacy Protection
- No permanent storage of user files
- Anonymized analytics data
- GDPR/CCPA compliance
- User consent management

## Deployment Architecture

### Development Environment
```
docker-compose.yml:
  - frontend (React dev server)
  - api-gateway (FastAPI with hot reload)
  - file-processor (Python service)
  - nlp-service (Python + GPU support)
  - cad-engine (FreeCAD container)
  - redis (cache)
  - postgresql (metadata)
```

### Production Environment
```
Kubernetes Cluster:
  - Frontend (Nginx + React build)
  - API Gateway (FastAPI + Gunicorn)
  - Microservices (auto-scaling pods)
  - Redis Cluster (high availability)
  - PostgreSQL (managed service)
  - File Storage (S3-compatible)
  - Monitoring (Prometheus + Grafana)
```

## Monitoring & Observability

### Metrics Collection
- **Performance**: Processing time, success rates, error rates
- **Usage**: API calls, feature usage, user flows
- **System**: CPU, memory, disk usage per service
- **Business**: Assembly generation success, user satisfaction

### Logging Strategy
- Structured logging with JSON format
- Distributed tracing across microservices
- Error aggregation and alerting
- User activity logging (privacy-compliant)

### Health Checks
- Service health endpoints
- Database connectivity checks
- CAD engine availability
- External dependency monitoring

## Extensibility Framework

### Plugin Architecture
```python
class CADEnginePlugin:
    def analyze_part(self, step_file) -> PartAnalysis: pass
    def generate_connector(self, constraints) -> Connector: pass
    def create_assembly(self, parts, connector) -> Assembly: pass

class NLPPlugin:
    def parse_constraints(self, text) -> List[Constraint]: pass
    def validate_feasibility(self, constraints) -> bool: pass
```

### Configuration Management
- Feature flags for A/B testing
- Dynamic model loading
- Engine selection based on requirements
- Performance parameter tuning

This architecture provides a solid foundation for the MVP while enabling future expansion into multi-modal capabilities, advanced AI features, and enterprise-scale deployment.