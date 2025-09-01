# Quick Start Guide - MVP Phase 1

This guide will help you get the Minimum AI CAD MVP running locally in under 10 minutes.

## Prerequisites

- **Docker Desktop** installed and running
- **Git** installed
- At least 4GB of available RAM

## 🚀 Quick Start

### 1. Clone and Start

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/flying-pisces/Minimum-AI-CAD.git
cd Minimum-AI-CAD

# Run the automated test script
./scripts/test-mvp.sh
```

### 2. Open the Application

Once all services are running, open your browser to:
**http://localhost:3000**

### 3. Test the Workflow

1. **Upload Two STEP Files**
   - Click on "Upload Part 1" and "Upload Part 2"
   - Select any STEP files (.step or .stp format)
   - For testing, you can create dummy files with `.step` extension

2. **Enter Assembly Instructions**
   - Try examples like:
     - "Connect with 5cm distance"
     - "Mount vertically with 3cm gap"
     - "Attach at 45-degree angle, 2cm apart"

3. **Generate Assembly**
   - Click "Generate Assembly"
   - Watch the processing status
   - View parsed constraints and results

4. **Export Results**
   - Once completed, export in STEP, STL, or OBJ format

## 🔧 Manual Setup (Alternative)

If the script doesn't work, you can start services manually:

```bash
# Start all services
docker-compose -f docker-compose.simple.yml up --build

# Or start in background
docker-compose -f docker-compose.simple.yml up --build -d
```

## 📊 Service Architecture

The MVP consists of 4 main services:

- **Frontend (Port 3000)**: React web application
- **API Gateway (Port 8000)**: Main API and file handling
- **File Processor (Port 8001)**: STEP file analysis
- **CAD Engine (Port 8003)**: Assembly generation

## 🧪 Testing Features

### Current MVP Capabilities

✅ **File Upload**: STEP file validation and storage  
✅ **Basic NLP**: Distance and angle constraint parsing  
✅ **Mock Analysis**: Simulated STEP file geometry extraction  
✅ **Assembly Generation**: Template-based connector creation  
✅ **Export**: STEP, STL, OBJ format downloads  

### Limitations (MVP Phase 1)

⚠️ **Mock Processing**: Uses simulated CAD analysis (no real STEP parsing yet)  
⚠️ **Simple Constraints**: Only basic distance/angle parsing  
⚠️ **No 3D Viewer**: Assembly preview not implemented yet  
⚠️ **Template Connectors**: Limited connector geometry options  

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check Docker status
docker ps

# View service logs
docker-compose -f docker-compose.simple.yml logs api-gateway
docker-compose -f docker-compose.simple.yml logs file-processor
docker-compose -f docker-compose.simple.yml logs cad-engine
```

### Port Conflicts
If ports 3000, 8000, 8001, or 8003 are in use:
```bash
# Stop other services using these ports
# Or modify ports in docker-compose.simple.yml
```

### Frontend Not Loading
```bash
# Rebuild frontend container
docker-compose -f docker-compose.simple.yml up --build frontend
```

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.simple.yml down

# Stop and remove volumes
docker-compose -f docker-compose.simple.yml down -v
```

## 📈 Next Steps

Once you've tested the MVP, check out:

1. **Phase 2 Development**: Enhanced NLP and real STEP processing
2. **3D Visualization**: Three.js integration for assembly preview
3. **FreeCAD Integration**: Real CAD engine for geometry processing
4. **Advanced Constraints**: Multi-constraint handling

## 🤝 Development

To contribute to the project:

```bash
# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd backend/services/api_gateway && pip install -r requirements.txt

# See CONTRIBUTING.md for detailed guidelines
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/flying-pisces/Minimum-AI-CAD/issues)
- **Documentation**: See README.md and ARCHITECTURE.md
- **Testing**: Run `./scripts/test-mvp.sh` to verify setup

---

**Happy building!** 🚀