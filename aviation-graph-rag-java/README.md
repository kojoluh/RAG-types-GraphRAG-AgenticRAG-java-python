# Aviation Graph RAG - Java/Spring Boot Edition

A production-ready Graph RAG (Retrieval-Augmented Generation) system for aviation customer support, built with **Spring Boot 3.2**, **Spring AI 0.8.0**, and **Neo4j** knowledge graphs.

## 🚀 Overview

This Java implementation provides a robust, enterprise-grade Graph RAG solution specifically designed for aviation customer support scenarios. It combines the power of Neo4j knowledge graphs with Spring AI's latest capabilities to deliver accurate, contextual responses for aviation-related queries.

### Key Features

- **Spring AI Integration**: Latest Spring AI 0.8.0 with OpenAI GPT-4 support
- **Neo4j Knowledge Graph**: Advanced graph traversal for aviation domain knowledge
- **Weaviate Vector Store**: High-performance vector search for document retrieval
- **Production-Ready**: Comprehensive monitoring, security, and scalability features
- **Enterprise Security**: JWT authentication, role-based access control
- **Real-time Processing**: Async processing with Redis caching
- **Comprehensive Monitoring**: Prometheus metrics, Grafana dashboards

## 🏗️ Architecture

### Core Components

1. **Graph RAG Service**: Orchestrates graph traversal and vector search
2. **Neo4j Repository**: Manages aviation knowledge graph operations
3. **Vector Service**: Handles document embedding and similarity search
4. **Intent Classifier**: Determines query intent using Spring AI
5. **Entity Extractor**: Extracts aviation-specific entities
6. **Response Generator**: Creates contextual responses using Spring AI

### Technology Stack

- **Framework**: Spring Boot 3.2.0
- **AI/ML**: Spring AI 0.8.0, OpenAI GPT-4
- **Database**: Neo4j 5.14.1 (Graph Database)
- **Vector Store**: Weaviate 1.22.4
- **Cache**: Redis 7.2
- **Monitoring**: Prometheus, Grafana
- **Security**: Spring Security, JWT
- **Build Tool**: Maven 3.9+

## 📋 Prerequisites

- Java 21+
- Maven 3.9+
- Docker & Docker Compose
- OpenAI API Key
- Neo4j Database
- Weaviate Vector Store

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd aviation-graph-rag-java
```

### 2. Environment Configuration

Create `.env` file:

```bash
# OpenAI Configuration
SPRING_AI_OPENAI_API_KEY=your-openai-api-key

# Neo4j Configuration
SPRING_NEO4J_URI=bolt://localhost:7687
SPRING_NEO4J_AUTHENTICATION_USERNAME=neo4j
SPRING_NEO4J_AUTHENTICATION_PASSWORD=password

# Weaviate Configuration
SPRING_AI_VECTOR_STORE_WEAVIATE_URL=http://localhost:8080

# Security
JWT_SECRET=your-secret-key-here
```

### 3. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up neo4j weaviate redis -d
```

### 4. Build and Run

```bash
# Build the application
mvn clean package

# Run the application
java -jar target/aviation-graph-rag-1.0.0.jar
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8080/api/actuator/health

# API documentation
curl http://localhost:8080/api/swagger-ui.html
```

## 📊 API Endpoints

### Core RAG Endpoints

```bash
# Process aviation query
POST /api/v1/rag/query
{
  "query": "What are the safety protocols for Boeing 737 maintenance?",
  "userContext": {
    "userId": "user123",
    "role": "technician"
  }
}

# Get query history
GET /api/v1/rag/history?userId=user123

# Get confidence metrics
GET /api/v1/rag/metrics/confidence
```

### Graph Management

```bash
# Add aviation entity to graph
POST /api/v1/graph/entities
{
  "type": "AIRCRAFT",
  "properties": {
    "model": "Boeing 737",
    "manufacturer": "Boeing",
    "capacity": 189
  }
}

# Query graph directly
POST /api/v1/graph/query
{
  "cypher": "MATCH (a:Aircraft) WHERE a.model CONTAINS '737' RETURN a"
}
```

### Vector Store Operations

```bash
# Add document to vector store
POST /api/v1/vector/documents
{
  "content": "Boeing 737 maintenance procedures...",
  "metadata": {
    "category": "maintenance",
    "aircraft": "Boeing 737"
  }
}

# Search similar documents
POST /api/v1/vector/search
{
  "query": "engine maintenance procedures",
  "topK": 5
}
```

## 🔧 Configuration

### Application Properties

```yaml
# Graph RAG Configuration
aviation:
  graph-rag:
    max-graph-results: 10
    max-vector-results: 5
    confidence-threshold: 0.1
    processing-timeout: 30s
    cache-enabled: true
    audit-enabled: true

# Neo4j Configuration
neo4j:
  connection-pool:
    max-connection-lifetime: 1h
    max-connection-pool-size: 50
    connection-acquisition-timeout: 1m

# Spring AI Configuration
spring:
  ai:
    openai:
      chat:
        options:
          model: gpt-4
          temperature: 0.1
          max-tokens: 1000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPRING_AI_OPENAI_API_KEY` | OpenAI API Key | Required |
| `SPRING_NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `SPRING_AI_VECTOR_STORE_WEAVIATE_URL` | Weaviate URL | `http://localhost:8080` |
| `JWT_SECRET` | JWT signing secret | Required |

## 📈 Monitoring & Observability

### Metrics Dashboard

Access Grafana at `http://localhost:3000`:
- **Username**: admin
- **Password**: admin

### Key Metrics

- **Query Processing Time**: Average response time
- **Confidence Scores**: Response quality metrics
- **Graph Traversal Performance**: Neo4j query metrics
- **Vector Search Performance**: Weaviate search metrics
- **Error Rates**: System reliability metrics

### Health Checks

```bash
# Application health
curl http://localhost:8080/api/actuator/health

# Neo4j health
curl http://localhost:7474/browser/

# Weaviate health
curl http://localhost:8081/v1/.well-known/ready
```

## 🔒 Security

### Authentication

```bash
# Get JWT token
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Use token in requests
Authorization: Bearer <jwt-token>
```

### Role-Based Access

- **ADMIN**: Full system access
- **TECHNICIAN**: Maintenance and technical queries
- **CUSTOMER_SERVICE**: General customer support
- **READONLY**: Query-only access

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
mvn test

# Run specific test
mvn test -Dtest=GraphRagServiceTest
```

### Integration Tests

```bash
# Run integration tests with TestContainers
mvn test -Dspring.profiles.active=test
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
   -p query.json http://localhost:8080/api/v1/rag/query
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale aviation-api-java=3
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n aviation-rag
```

## 📚 Data Sources

### Aviation Knowledge Graph Schema

```cypher
// Aircraft nodes
CREATE (a:Aircraft {
  model: "Boeing 737",
  manufacturer: "Boeing",
  capacity: 189,
  range: 5600
})

// Safety protocols
CREATE (sp:SafetyProtocol {
  name: "Engine Maintenance",
  category: "maintenance",
  priority: "high"
})

// Relationships
CREATE (a)-[:HAS_SAFETY_PROTOCOL]->(sp)
```

### Vector Store Collections

- **aviation-manuals**: Aircraft manuals and procedures
- **safety-guidelines**: Safety protocols and regulations
- **maintenance-records**: Maintenance history and procedures
- **customer-service**: FAQ and support documentation

## 🔧 Development

### Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/aviation/rag/
│   │       ├── AviationGraphRagApplication.java
│   │       ├── core/
│   │       │   ├── graph/
│   │       │   │   └── GraphRagService.java
│   │       │   ├── model/
│   │       │   ├── repository/
│   │       │   └── vector/
│   │       ├── api/
│   │       ├── config/
│   │       └── security/
│   └── resources/
│       └── application.yml
└── test/
    └── java/
        └── com/aviation/rag/
```

### Adding New Features

1. **New Entity Types**: Extend `EntityType` enum
2. **New Intent Types**: Extend `IntentType` enum
3. **Custom Cypher Queries**: Add to `GraphRagService`
4. **New Vector Collections**: Configure in `application.yml`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style

- Follow Spring Boot conventions
- Use Lombok for boilerplate reduction
- Implement comprehensive logging
- Add Javadoc for public methods

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)

## 🔄 Version History

- **v1.0.0**: Initial release with Spring Boot 3.2 and Spring AI 0.8.0
- **v0.9.0**: Beta release with core Graph RAG functionality
- **v0.8.0**: Alpha release with basic Neo4j integration

---

**Built with ❤️ using Spring Boot and Spring AI** 