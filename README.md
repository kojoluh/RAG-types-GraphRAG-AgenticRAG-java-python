# RAG Types: Production-Ready Graph RAG and Agentic RAG Implementations

This repository contains comprehensive implementations of Graph RAG and Agentic RAG architectures for aviation customer support and enterprise onboarding use cases, available in both Python and Java.

## 🚀 Quick Start

See [QUICK_START.md](QUICK_START.md) for immediate setup instructions.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stacks](#technology-stacks)
- [Implementations](#implementations)
- [CI/CD Pipeline](#cicd-pipeline)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Monitoring & Observability](#monitoring--observability)
- [Security](#security)
- [Performance](#performance)
- [Documentation](#documentation)

## 🎯 Overview

This project demonstrates production-ready implementations of two advanced RAG architectures:

### Graph RAG (Aviation Customer Support)
- **Use Case**: Aviation customer support with complex knowledge graphs
- **Architecture**: Graph-based retrieval with Neo4j and vector search
- **Features**: Multi-hop reasoning, contextual retrieval, knowledge graph traversal

### Agentic RAG (Enterprise Onboarding)
- **Use Case**: Enterprise employee onboarding with autonomous agents
- **Architecture**: Multi-agent system with task decomposition and orchestration
- **Features**: Autonomous task execution, workflow management, human-in-the-loop

## 🏗️ Architecture

### Graph RAG Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Parser   │───▶│  Graph Traversal│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Response Gen   │◀───│  Vector Search  │◀───│  Context Builder│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agentic RAG Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Task     │───▶│  Task Decomposer│───▶│  Agent Orchestrator│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Task Results   │◀───│  Agent Executor │◀───│  Agent Pool     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stacks

### Python Implementation
| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Vector DB** | Weaviate, ChromaDB | Latest |
| **Graph DB** | Neo4j | 5.14.1 |
| **Cache** | Redis | 7.2 |
| **Queue** | Celery + Redis | Latest |
| **Testing** | pytest, TestContainers | Latest |
| **Monitoring** | Prometheus, Grafana | Latest |

### Java Implementation
| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | Spring Boot | 3.2.0 |
| **AI Integration** | Spring AI | 0.8.0 |
| **Vector DB** | Weaviate, ChromaDB | Latest |
| **Graph DB** | Neo4j | 5.14.1 |
| **Cache** | Redis | 7.2 |
| **Queue** | RabbitMQ | 3.12 |
| **Testing** | JUnit 5, TestContainers | Latest |
| **Monitoring** | Micrometer, Actuator | Latest |

## 📁 Implementations

### Python Implementations
- **`aviation-graph-rag/`**: Graph RAG for aviation customer support
- **`onboarding-agentic-rag/`**: Agentic RAG for enterprise onboarding

### Java Implementations
- **`aviation-graph-rag-java/`**: Graph RAG for aviation customer support
- **`onboarding-agentic-rag-java/`**: Agentic RAG for enterprise onboarding

## 🔄 CI/CD Pipeline

The project includes comprehensive CI/CD pipelines with quality gates, security scanning, and automated deployment:

### Workflows
- **`python-ci-cd.yml`**: Python CI/CD pipeline
- **`java-ci-cd.yml`**: Java CI/CD pipeline
- **`security-scanning.yml`**: Security scanning & compliance
- **`performance-testing.yml`**: Performance testing & monitoring
- **`deployment.yml`**: Deployment pipeline
- **`quality-gates.yml`**: Quality gates enforcement

### Quality Gates
- **Code Quality**: Formatting, linting, type checking
- **Test Coverage**: 80% (Python), 75% (Java)
- **Security**: SAST, DAST, dependency scanning
- **Performance**: Response time < 200ms, throughput > 1000 req/s
- **Documentation**: Completeness validation

### Security Scanning
- **SAST**: Semgrep, CodeQL, Bandit, SpotBugs
- **DAST**: OWASP ZAP, Nuclei
- **Container Security**: Trivy, Snyk
- **Dependency Scanning**: Safety, OWASP Dependency Check
- **Secrets Scanning**: TruffleHog, GitGuardian, Gitleaks

See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for detailed documentation.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for Python implementations)
- Java 21+ (for Java implementations)
- Maven 3.9+ (for Java implementations)

### Quick Setup

#### Python Implementation
```bash
# Clone the repository
git clone https://github.com/your-org/rag-types.git
cd rag-types

# Start Python Graph RAG
cd aviation-graph-rag
docker-compose up -d
poetry install
poetry run python -m src.main

# Start Python Agentic RAG
cd ../onboarding-agentic-rag
docker-compose up -d
poetry install
poetry run python -m src.main
```

#### Java Implementation
```bash
# Start Java Graph RAG
cd aviation-graph-rag-java
docker-compose up -d
mvn spring-boot:run

# Start Java Agentic RAG
cd ../onboarding-agentic-rag-java
docker-compose up -d
mvn spring-boot:run
```

### Environment Configuration

#### Python Environment
```bash
# Copy environment template
cp aviation-graph-rag/.env.example aviation-graph-rag/.env
cp onboarding-agentic-rag/.env.example onboarding-agentic-rag/.env

# Configure environment variables
export OPENAI_API_KEY=your_openai_key
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
```

#### Java Environment
```bash
# Configure application properties
cp aviation-graph-rag-java/src/main/resources/application-example.yml aviation-graph-rag-java/src/main/resources/application.yml
cp onboarding-agentic-rag-java/src/main/resources/application-example.yml onboarding-agentic-rag-java/src/main/resources/application.yml
```

## 🔄 Development Workflow

### Code Quality Standards
- **Python**: Black, isort, flake8, mypy
- **Java**: Checkstyle, SpotBugs, PMD, SonarQube
- **Testing**: pytest (Python), JUnit 5 (Java)
- **Coverage**: 80% minimum (Python), 75% minimum (Java)

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Running Tests
```bash
# Python tests
cd aviation-graph-rag
poetry run pytest tests/ -v --cov=src

# Java tests
cd aviation-graph-rag-java
mvn test
```

### Running Quality Gates
```bash
# Manual quality gate check
gh workflow run quality-gates.yml

# View results
gh run list --workflow=quality-gates.yml
```

## 📊 Monitoring & Observability

### Metrics
- **Application Metrics**: Request rate, response time, error rate
- **Resource Metrics**: CPU, memory, disk usage
- **Business Metrics**: Query success rate, user satisfaction

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging with ELK stack

### Tracing
- **Distributed Tracing**: OpenTelemetry integration
- **Trace Propagation**: End-to-end request tracing
- **Performance Analysis**: Slow query identification

### Alerting
- **Critical Alerts**: Service down, high error rate
- **Warning Alerts**: High latency, resource usage
- **Business Alerts**: Low success rate, user complaints

## 🔒 Security

### Security Measures
- **Authentication**: JWT tokens, OAuth 2.0
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: TLS 1.3, AES-256
- **Input Validation**: Schema validation, sanitization
- **Rate Limiting**: API rate limiting, DDoS protection

### Security Scanning
- **SAST**: Static application security testing
- **DAST**: Dynamic application security testing
- **Container Security**: Vulnerability scanning
- **Dependency Scanning**: Known vulnerability detection

### Compliance
- **GDPR**: Data protection and privacy
- **SOC 2**: Security controls and monitoring
- **ISO 27001**: Information security management

## ⚡ Performance

### Performance Targets
- **Response Time**: < 200ms average
- **Throughput**: > 1000 requests/second
- **Availability**: 99.9% uptime
- **Error Rate**: < 1%

### Optimization Strategies
- **Caching**: Redis caching for frequent queries
- **Connection Pooling**: Database connection optimization
- **Async Processing**: Non-blocking I/O operations
- **Load Balancing**: Horizontal scaling with load balancers

### Load Testing
```bash
# Run performance tests
gh workflow run performance-testing.yml

# View performance results
gh run list --workflow=performance-testing.yml
```

## 📚 Documentation

### Project Documentation
- [QUICK_START.md](QUICK_START.md): Quick setup guide
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md): 8-week implementation plan
- [JAVA_VS_PYTHON_COMPARISON.md](JAVA_VS_PYTHON_COMPARISON.md): Technology comparison
- [CI_CD_GUIDE.md](CI_CD_GUIDE.md): CI/CD pipeline documentation

### API Documentation
- **Python**: FastAPI automatic documentation at `/docs`
- **Java**: Spring Boot Actuator at `/actuator`

### Architecture Documentation
- **Graph RAG**: Detailed architecture and flow diagrams
- **Agentic RAG**: Multi-agent system design and orchestration

## 🤝 Contributing

### Development Guidelines
1. Follow coding standards and quality gates
2. Write comprehensive tests
3. Update documentation
4. Use conventional commit messages
5. Create feature branches for changes

### Code Review Process
1. Create pull request with description
2. Ensure all CI/CD checks pass
3. Get approval from maintainers
4. Merge after review approval

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

## 📈 Roadmap

### Phase 1 (Weeks 1-4): Foundation
- ✅ Basic Graph RAG implementation
- ✅ Basic Agentic RAG implementation
- ✅ CI/CD pipeline setup
- ✅ Quality gates implementation

### Phase 2 (Weeks 5-6): Enhancement
- 🔄 Advanced graph traversal algorithms
- 🔄 Multi-agent orchestration improvements
- 🔄 Performance optimization
- 🔄 Security hardening

### Phase 3 (Weeks 7-8): Production
- 📋 Production deployment
- 📋 Monitoring and alerting setup
- 📋 Documentation completion
- 📋 Training and handover

## 📞 Support

### Getting Help
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check project documentation first
- **Community**: Join our community channels

### Contact Information
- **Email**: support@rag-types.com
- **Slack**: #rag-types-support
- **Discord**: RAG Types Community

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- Neo4j for graph database technology
- Weaviate and ChromaDB for vector databases
- Spring Boot and FastAPI communities
- All contributors and maintainers

---

**Note**: This is a production-ready implementation with comprehensive CI/CD, security scanning, and quality gates. For enterprise use, ensure proper security configuration and compliance with your organization's policies. 