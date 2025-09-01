# Minimum AI CAD - Product Requirements Document

## Executive Summary

**Product Name:** Minimum AI CAD  
**Version:** 1.0  
**Date:** September 1, 2025  

Minimum AI CAD is an AI-powered web application that enables users to upload two STEP CAD files and automatically generate assembly connector parts through natural language instructions. The system interprets spatial constraints (e.g., "mount unit 1 and unit 2 with 5cm distance between centers") and produces custom connector geometries to fulfill assembly requirements.

## Product Vision

Create the simplest, most intuitive AI-powered CAD assembly tool that bridges natural language understanding with precision mechanical design, enabling rapid prototyping and custom manufacturing through intelligent automation.

## Target Users

**Primary Users:**
- Mechanical Engineers (rapid prototyping)
- Product Designers (concept validation)
- Makers & Hobbyists (custom projects)
- Educational Institutions (engineering students)

**Secondary Users:**
- Manufacturing Engineers (assembly planning)
- Startup Hardware Teams (MVP development)

## Problem Statement

Current CAD software requires extensive training and manual connector design for assembly projects. Users need hours to create simple mounting brackets or connectors between existing parts. No solution exists that:
1. Accepts natural language assembly specifications
2. Automatically analyzes uploaded STEP files
3. Generates custom connector geometry
4. Provides immediate web-based preview

## Core Features (MVP)

### 1. File Upload & Processing
- **STEP File Upload**: Drag-and-drop interface for two STEP files
- **Automatic Analysis**: Extract geometry, centers, bounding boxes, surfaces
- **3D Visualization**: Three.js-based preview of uploaded parts

### 2. Natural Language Interface
- **Text Input**: Natural language assembly specifications
- **Constraint Parsing**: Extract distance, angle, orientation requirements
- **Clarification Dialog**: Interactive refinement of ambiguous requests

### 3. Assembly Generation
- **Connector Design**: Automatic generation of mounting brackets/connectors
- **Constraint Satisfaction**: Ensure specified distances and orientations
- **Material Properties**: Basic structural considerations

### 4. Preview & Export
- **Assembly Preview**: Real-time 3D visualization of complete assembly
- **Export Options**: STEP, STL, OBJ formats
- **Parametric Adjustment**: Fine-tune generated connector dimensions

## Technical Architecture

### Frontend (Web UI)
```
React Application
├── Upload Component (STEP files)
├── 3D Viewer (Three.js + CAD Exchanger)
├── Natural Language Input
├── Assembly Preview Panel
├── Export Controls
└── Chat Interface
```

### Backend (Microservices)
```
API Gateway → FastAPI
├── File Processing Service (STEP analysis)
├── NLP Service (constraint parsing)
├── CAD Engine Service (FreeCAD/OpenSCAD)
├── Assembly Generator Service
└── Export Service
```

### CAD Engine Options
- **Primary**: FreeCAD Python API (superior assembly handling)
- **Secondary**: OpenSCAD (parametric modeling)
- **Future**: Fusion 360 API integration

## Development Roadmap

### Phase 1: Core MVP (Months 1-3)
**Goal**: Basic two-part assembly with simple connectors

**Milestones:**
- **M1.1** (Week 2): STEP file upload and visualization
- **M1.2** (Week 4): Basic geometry analysis (centers, bounding boxes)
- **M1.3** (Week 6): Simple NLP parsing (predefined patterns)
- **M1.4** (Week 8): Template-based connector generation
- **M1.5** (Week 10): Assembly preview and basic export
- **M1.6** (Week 12): MVP deployment and testing

**Success Criteria:**
- Upload two STEP files successfully
- Generate simple bracket for "connect with 5cm distance"
- Export assembly in STEP format
- Processing time < 60 seconds

### Phase 2: Enhanced Intelligence (Months 4-6)
**Goal**: Advanced NLP and multi-constraint handling

**Milestones:**
- **M2.1** (Month 4): Advanced NLP model integration
- **M2.2** (Month 4.5): Multi-constraint parsing (distance + angle + orientation)
- **M2.3** (Month 5): Surface analysis and mounting point detection
- **M2.4** (Month 5.5): Complex connector geometries (L-brackets, custom joints)
- **M2.5** (Month 6): Interactive assembly refinement

**Success Criteria:**
- Parse complex instructions: "mount vertically with 45-degree angle"
- Generate custom connector shapes based on part geometry
- Handle conflicting constraints with user feedback
- Processing time < 30 seconds

### Phase 3: Multi-Modal Expansion (Months 7-9)
**Goal**: Camera input and text-to-CAD generation

**Milestones:**
- **M3.1** (Month 7): Mobile camera integration for part capture
- **M3.2** (Month 7.5): Multi-view 3D reconstruction
- **M3.3** (Month 8): Text-to-CAD generation ("1cm x 1cm x 1cm cube")
- **M3.4** (Month 8.5): Photo-to-STEP conversion pipeline
- **M3.5** (Month 9): Multi-modal assembly (photo + STEP + text)

**Success Criteria:**
- Generate STEP files from 3+ mobile photos
- Create basic shapes from text descriptions
- Maintain 80%+ accuracy in dimension extraction

### Phase 4: Production & Scale (Months 10-12)
**Goal**: Enterprise features and performance optimization

**Milestones:**
- **M4.1** (Month 10): User accounts and project management
- **M4.2** (Month 10.5): Batch processing and API access
- **M4.3** (Month 11): Advanced materials and structural analysis
- **M4.4** (Month 11.5): Integration with manufacturing services
- **M4.5** (Month 12): Enterprise deployment and documentation

## Technical Specifications

### API Endpoints

#### Core Assembly API
```
POST /api/v1/assembly
- Input: 2 STEP files + natural language specification
- Output: Generated assembly with connector
- Timeout: 120 seconds

GET /api/v1/assembly/{id}/preview
- Output: 3D model data for web viewer

POST /api/v1/assembly/{id}/export
- Input: Format (STEP, STL, OBJ)
- Output: Downloadable file
```

#### Multi-Modal Extensions
```
POST /api/v1/generate/text-to-cad
- Input: Text description of part
- Output: Generated STEP file

POST /api/v1/generate/photo-to-cad
- Input: Multiple photos of part
- Output: Reconstructed STEP file
```

### Performance Requirements
- **File Size**: Support STEP files up to 50MB
- **Processing Time**: 
  - MVP: < 60 seconds
  - Production: < 30 seconds
- **Concurrent Users**: 100+ simultaneous requests
- **Uptime**: 99.5% availability

### Security Requirements
- File upload validation and sanitization
- Rate limiting on API endpoints
- Temporary file cleanup (24-hour retention)
- User data privacy compliance

## Testing Strategy

### Unit Tests
```bash
# Backend API tests
pytest tests/api/
pytest tests/cad_engine/
pytest tests/nlp/

# Frontend component tests  
npm test src/components/
npm test src/services/
```

### Integration Tests
```bash
# End-to-end assembly generation
python tests/integration/test_full_pipeline.py

# Multi-modal workflow tests
python tests/integration/test_photo_to_assembly.py
```

### Performance Tests
```bash
# Load testing with Locust
locust -f tests/performance/load_test.py

# File processing benchmarks
python tests/performance/benchmark_cad_engine.py
```

### Validation Scripts

#### Geometry Validation
```python
def validate_connector_geometry(connector_step_file, part1, part2, constraints):
    """Verify generated connector satisfies all constraints"""
    # Distance validation
    # Angle validation  
    # Structural integrity checks
    pass
```

#### NLP Accuracy Tests
```python
def test_constraint_parsing_accuracy():
    """Test suite for natural language understanding"""
    test_cases = [
        ("mount 5cm apart", {"distance": 50, "unit": "mm"}),
        ("45 degree angle", {"angle": 45, "unit": "degrees"}),
        ("vertical alignment", {"orientation": "vertical"})
    ]
    # Accuracy measurement
```

## Risk Assessment & Mitigation

### Technical Risks
1. **STEP File Compatibility**: Mitigation - Support major CAD software exports
2. **NLP Accuracy**: Mitigation - Extensive test dataset and user feedback loop
3. **Processing Performance**: Mitigation - GPU acceleration and caching
4. **CAD Engine Stability**: Mitigation - Docker containerization and fallback engines

### Business Risks  
1. **User Adoption**: Mitigation - Focus on specific use cases and user education
2. **Competitor Response**: Mitigation - Rapid feature development and specialization
3. **Technical Complexity**: Mitigation - Phased approach with MVP validation

## Success Metrics

### Technical KPIs
- **Processing Success Rate**: >95% for standard STEP files
- **NLP Understanding Accuracy**: >90% for common constraints
- **System Uptime**: >99.5%
- **Average Processing Time**: <30 seconds (production)

### User Experience KPIs
- **User Onboarding**: <5 minutes to first successful assembly
- **Task Completion Rate**: >80% for intended assembly workflows
- **User Satisfaction**: >4.5/5 rating
- **Feature Usage**: >70% users try multi-modal features (Phase 3+)

### Business KPIs
- **Monthly Active Users**: 1,000+ by Month 6
- **API Usage**: 10,000+ assemblies generated monthly
- **Conversion Rate**: 25% trial-to-paid conversion
- **User Retention**: 60% monthly active user retention

## Future Extensions (Post-MVP)

### Advanced Features
- **Material Library**: Predefined materials with properties
- **Structural Analysis**: FEA integration for connector validation
- **Manufacturing Integration**: Direct export to 3D printing services
- **Collaborative Features**: Team workspaces and sharing
- **Mobile App**: Native iOS/Android applications

### AI/ML Enhancements
- **Learning from Usage**: Improve NLP from user corrections
- **Design Optimization**: AI-suggested connector improvements
- **Predictive Modeling**: Anticipate user needs based on uploaded parts
- **Computer Vision**: Advanced part recognition from photos

### Enterprise Features
- **API Access**: Developer integration capabilities
- **Batch Processing**: Multiple assemblies simultaneously
- **White-label Solutions**: Customizable deployments
- **Advanced Analytics**: Usage insights and optimization recommendations

## Conclusion

Minimum AI CAD represents a significant opportunity to democratize CAD assembly design through AI automation. The phased development approach ensures rapid market validation while building toward a comprehensive multi-modal platform.

The focus on natural language interfaces, combined with robust CAD engine integration, positions the product uniquely in the current market landscape dominated by complex traditional CAD tools.

Success depends on achieving high NLP accuracy, reliable CAD generation, and exceptional user experience in the core workflow of two-part assembly with custom connectors.