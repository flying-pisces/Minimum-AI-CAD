# Contributing to Minimum AI CAD

Thank you for your interest in contributing to Minimum AI CAD! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Ways to Contribute
- **Bug Reports**: Found a bug? Please report it!
- **Feature Requests**: Have ideas for improvements? Share them!
- **Code Contributions**: Fix bugs, add features, improve documentation
- **Testing**: Help test new features and report issues
- **Documentation**: Improve guides, examples, and explanations

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Environment**: OS, browser, Docker version
- **Steps to Reproduce**: Clear step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: Visual evidence when applicable
- **STEP Files**: Sample files that cause issues (if safe to share)

### Feature Requests
When requesting features:
- **Use Case**: Why is this feature needed?
- **User Story**: "As a [user type], I want [feature] so that [benefit]"
- **Acceptance Criteria**: How do we know it's done?
- **Priority**: How important is this feature?

## 💻 Development Setup

### Prerequisites
```bash
# Required software
- Docker Desktop
- Node.js 18+
- Python 3.11+
- Git
```

### Environment Setup
```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Minimum-AI-CAD.git
cd Minimum-AI-CAD

# 2. Set up development environment
docker-compose -f docker-compose.dev.yml up -d

# 3. Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements-dev.txt

# 4. Run tests to verify setup
npm test
pytest

# 5. Start development servers
npm run dev                    # Frontend (localhost:3000)
python -m uvicorn main:app --reload  # Backend (localhost:8000)
```

## 🏗️ Project Structure

```
Minimum-AI-CAD/
├── frontend/                   # React + Three.js web application
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── services/           # API clients
│   │   ├── types/              # TypeScript definitions
│   │   └── utils/              # Helper functions
│   ├── public/                 # Static assets
│   └── tests/                  # Frontend tests
├── backend/                    # Python microservices
│   ├── services/
│   │   ├── api_gateway/        # FastAPI main service
│   │   ├── file_processor/     # STEP file analysis
│   │   ├── nlp_service/        # Natural language processing
│   │   ├── cad_engine/         # FreeCAD integration
│   │   └── assembly_generator/ # Assembly creation
│   ├── shared/                 # Common utilities
│   └── tests/                  # Backend tests
├── docs/                       # Documentation
├── scripts/                    # Build and deployment scripts
├── tests/                      # Integration and E2E tests
└── docker/                     # Docker configurations
```

## 🔧 Development Workflow

### 1. Create a Branch
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/issue-description
```

### 2. Development Guidelines

#### Code Style
- **Frontend**: Use Prettier and ESLint configurations
- **Backend**: Follow PEP 8, use Black formatter
- **Commits**: Use conventional commit format

#### Naming Conventions
```bash
# Branch naming
feature/add-multi-constraint-parsing
fix/step-file-upload-error
docs/update-api-documentation

# Commit messages
feat: add support for angle constraints in NLP parser
fix: resolve STEP file validation error
docs: update API documentation for assembly endpoint
test: add integration tests for connector generation
```

### 3. Testing Requirements

#### Frontend Testing
```bash
# Run all tests
npm test

# Run specific test suites
npm test -- --testPathPattern=components
npm test -- --testPathPattern=services

# Coverage report
npm test -- --coverage
```

#### Backend Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Specific service tests
pytest tests/unit/test_nlp_service.py

# Coverage report
pytest --cov=src tests/
```

#### Testing Standards
- **Unit Tests**: Required for new functions and classes
- **Integration Tests**: Required for new API endpoints
- **E2E Tests**: Required for new user-facing features
- **Performance Tests**: Required for CAD processing changes

### 4. Code Review Process

#### Before Submitting PR
```bash
# Run full test suite
npm test && pytest

# Check code formatting
npm run lint
black backend/ --check
flake8 backend/

# Update documentation if needed
# Test on sample STEP files
```

#### PR Requirements
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] Breaking changes noted in description
- [ ] Performance impact considered
- [ ] Security implications reviewed

## 🧪 Testing Guidelines

### Test Categories

#### 1. Unit Tests
Focus on individual functions and classes:
```python
def test_constraint_parser_distance():
    parser = ConstraintParser()
    result = parser.parse("connect with 5cm distance")
    assert result['constraints'][0]['value'] == 50  # mm
    assert result['constraints'][0]['type'] == 'distance'
```

#### 2. Integration Tests
Test service interactions:
```python
def test_full_assembly_pipeline():
    # Upload STEP files
    part1 = upload_step_file("test_part1.step")
    part2 = upload_step_file("test_part2.step")
    
    # Process assembly request
    response = client.post("/api/v1/assembly", json={
        "part1_id": part1.id,
        "part2_id": part2.id,
        "constraints": "connect with 3cm distance"
    })
    
    assert response.status_code == 200
    assert "connector_id" in response.json()
```

#### 3. Performance Tests
Ensure processing time requirements:
```python
def test_assembly_generation_performance():
    start_time = time.time()
    
    result = generate_assembly(part1, part2, constraints)
    
    processing_time = time.time() - start_time
    assert processing_time < 30  # seconds
```

### Test Data

#### STEP Files
- Store test STEP files in `tests/fixtures/step_files/`
- Include variety: simple/complex, small/large, different CAD software
- Document each file's purpose and expected behavior

#### Test Cases
- **Valid Constraints**: "5cm distance", "45 degree angle", "vertical alignment"
- **Invalid Constraints**: Impossible geometries, conflicting requirements
- **Edge Cases**: Very small/large parts, minimal clearance, complex surfaces

## 📚 Documentation Standards

### Code Documentation
```python
def generate_connector(part1: PartAnalysis, part2: PartAnalysis, 
                      constraints: List[Constraint]) -> Connector:
    """
    Generate a custom connector between two parts based on constraints.
    
    Args:
        part1: Analysis results for first part
        part2: Analysis results for second part  
        constraints: List of spatial and mechanical constraints
        
    Returns:
        Connector object with geometry and mounting features
        
    Raises:
        ConstraintConflictError: When constraints cannot be satisfied
        GeometryError: When part geometries are incompatible
        
    Example:
        >>> connector = generate_connector(part1, part2, [
        ...     Constraint(type='distance', value=50, unit='mm')
        ... ])
        >>> connector.export_step("connector.step")
    """
```

### API Documentation
- Use OpenAPI/Swagger specifications
- Include request/response examples
- Document error codes and messages
- Provide curl examples

### User Documentation
- Step-by-step tutorials with screenshots
- Common use cases and examples
- Troubleshooting guides
- FAQ section

## 🚀 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass on main branch
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in package.json and setup.py
- [ ] Docker images built and tested
- [ ] Performance benchmarks run
- [ ] Security scan completed

## 🌟 Recognition

### Contributor Recognition
- All contributors listed in README.md
- Significant contributions highlighted in releases
- Optional: Contributor interview for project blog

### Types of Contributions Recognized
- **Code**: Features, bug fixes, performance improvements
- **Documentation**: Guides, examples, API docs
- **Testing**: Test cases, validation scripts, performance tests
- **Design**: UI/UX improvements, architectural decisions
- **Community**: Issue triage, user support, mentoring

## ❓ Questions and Support

### Getting Help
- **General Questions**: [GitHub Discussions](https://github.com/flying-pisces/Minimum-AI-CAD/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/flying-pisces/Minimum-AI-CAD/issues)
- **Development Chat**: Join our Discord server (link in README)
- **Email**: dev@minimum-ai-cad.com

### Development Resources
- [Product Requirements Document](PRD.md)
- [Technical Architecture](ARCHITECTURE.md)
- [API Documentation](docs/api.md)
- [Development Setup Guide](docs/development.md)

## 📄 License

By contributing to Minimum AI CAD, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Minimum AI CAD! Together we're building the future of AI-powered mechanical design. 🚀