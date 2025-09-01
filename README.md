# Minimum AI CAD

An AI-powered web application that automatically generates assembly connector parts from natural language instructions and uploaded STEP CAD files.

## 🎯 Overview

Minimum AI CAD bridges the gap between natural language and precision mechanical design. Upload two STEP files, describe how they should be connected ("mount unit 1 and unit 2 with 5cm distance between centers"), and get custom connector geometry that satisfies your assembly requirements.

## ✨ Key Features

- **Natural Language Assembly**: Describe spatial constraints in plain English
- **STEP File Processing**: Direct upload and analysis of CAD files
- **Automatic Connector Generation**: AI-generated mounting brackets and connectors
- **3D Web Preview**: Real-time visualization of complete assembly
- **Multi-Format Export**: STEP, STL, OBJ file outputs
- **Future Multi-Modal**: Camera-based part capture and text-to-CAD generation

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for backend services)

### Installation

```bash
# Clone the repository
git clone https://github.com/flying-pisces/Minimum-AI-CAD.git
cd Minimum-AI-CAD

# Start development environment
docker-compose up -d

# Install frontend dependencies
cd frontend
npm install
npm run dev

# Access application
open http://localhost:3000
```

## 📋 Development Roadmap

### Phase 1: Core MVP (Months 1-3)
- [x] Project structure and documentation
- [ ] STEP file upload and visualization
- [ ] Basic geometry analysis
- [ ] Simple NLP constraint parsing
- [ ] Template-based connector generation
- [ ] Assembly preview and export

### Phase 2: Enhanced Intelligence (Months 4-6)
- [ ] Advanced NLP model integration
- [ ] Multi-constraint handling
- [ ] Surface analysis and mounting point detection
- [ ] Complex connector geometries
- [ ] Interactive assembly refinement

### Phase 3: Multi-Modal (Months 7-9)
- [ ] Mobile camera integration
- [ ] Multi-view 3D reconstruction
- [ ] Text-to-CAD generation
- [ ] Photo-to-STEP conversion

### Phase 4: Production (Months 10-12)
- [ ] User accounts and project management
- [ ] API access and batch processing
- [ ] Advanced materials and structural analysis
- [ ] Manufacturing service integration

## 🏗️ Architecture

```
Frontend (React + Three.js) 
    ↓
API Gateway (FastAPI)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ File Processing │   NLP Service   │  CAD Engine     │
│    Service      │                 │   Service       │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
Assembly Generator
    ↓
Redis Cache + File Storage + PostgreSQL
```

## 🔧 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Three.js** for 3D visualization
- **CAD Exchanger** for STEP file processing
- **Material-UI** for components

### Backend
- **FastAPI** for API gateway
- **FreeCAD Python API** for CAD processing
- **Transformers** for NLP
- **Open3D** for 3D data processing
- **Redis** for caching
- **PostgreSQL** for metadata

### Infrastructure
- **Docker** containerization
- **Kubernetes** for production
- **GitHub Actions** for CI/CD

## 🧪 Testing

```bash
# Run all tests
npm test                           # Frontend tests
pytest tests/                     # Backend tests
python tests/integration/         # Integration tests
locust -f tests/performance/       # Load tests

# Validate specific components
python tests/validation/test_cad_engine.py
python tests/validation/test_nlp_accuracy.py
```

## 📊 Usage Examples

### Basic Assembly
```
Input: "Connect these parts with 50mm distance"
Output: Generated bracket maintaining specified distance
```

### Complex Constraints
```
Input: "Mount vertically at 45-degree angle, 3cm apart"
Output: Custom L-bracket with angle and distance constraints
```

### Future Multi-Modal
```
Input: Photos of two parts + "connect them securely"
Output: Reconstructed parts + generated assembly
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Run tests
npm test
pytest
```

## 📖 Documentation

- [Product Requirements Document](PRD.md) - Complete product specification
- [Technical Architecture](ARCHITECTURE.md) - Detailed system design
- [API Documentation](docs/api.md) - Backend API reference
- [Contributing Guidelines](CONTRIBUTING.md) - Development workflow

## 🔒 Security & Privacy

- Temporary file storage (24-hour retention)
- No permanent storage of user CAD files
- GDPR/CCPA compliant data handling
- File validation and sanitization

## 📈 Performance

- **Processing Time**: <30 seconds (production target)
- **File Size Support**: Up to 50MB STEP files
- **Concurrent Users**: 100+ simultaneous requests
- **Uptime**: 99.5% availability target

## 🌟 Future Vision

Minimum AI CAD aims to become the simplest way to create custom mechanical assemblies through natural language. Future capabilities include:

- **Multi-Modal Input**: Camera + voice + text + CAD files
- **Advanced AI**: GPT-powered design optimization
- **Manufacturing Integration**: Direct-to-3D-printing workflows
- **Collaborative Features**: Team workspaces and sharing
- **Enterprise Solutions**: API access and white-label deployments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Product Vision**: AI-powered mechanical design automation
- **Technical Focus**: Natural language to CAD conversion
- **Target Users**: Engineers, designers, makers, students

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/flying-pisces/Minimum-AI-CAD/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flying-pisces/Minimum-AI-CAD/discussions)
- **Email**: support@minimum-ai-cad.com

---

**Built with ❤️ for the maker community**