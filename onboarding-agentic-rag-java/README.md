# Onboarding Agentic RAG - Java/Spring Boot Edition

A production-ready Agentic RAG (Retrieval-Augmented Generation) system for enterprise employee onboarding, built with **Spring Boot 3.2**, **Spring AI 0.8.0**, and **LangChain4j** for multi-agent orchestration.

## 🚀 Overview

This Java implementation provides a sophisticated, enterprise-grade Agentic RAG solution designed for personalized employee onboarding experiences. It leverages multiple specialized agents working in concert to deliver comprehensive, contextual responses tailored to individual employee needs.

### Key Features

- **Multi-Agent Orchestration**: Specialized agents for different onboarding domains
- **Spring AI Integration**: Latest Spring AI 0.8.0 with OpenAI GPT-4 support
- **LangChain4j Framework**: Advanced multi-agent coordination
- **ChromaDB Vector Store**: High-performance vector search for knowledge retrieval
- **Personalization Engine**: Adaptive responses based on user profile and progress
- **Real-time WebSocket Support**: Live conversation capabilities
- **Enterprise Security**: JWT authentication, role-based access control
- **Comprehensive Monitoring**: Prometheus metrics, Grafana dashboards, LangSmith

## 🏗️ Architecture

### Multi-Agent System

1. **Policy Agent**: Handles company policies and procedures
2. **Technical Agent**: Manages technical documentation and tools
3. **HR Agent**: Provides HR-related information and support
4. **Security Agent**: Covers security protocols and compliance
5. **Culture Agent**: Shares company culture and values
6. **Orchestrator**: Coordinates multiple agents for complex queries

### Technology Stack

- **Framework**: Spring Boot 3.2.0
- **AI/ML**: Spring AI 0.8.0, LangChain4j 0.27.1, OpenAI GPT-4
- **Database**: PostgreSQL 15 (User data), ChromaDB (Vector store)
- **Message Queue**: RabbitMQ 3.12
- **Cache**: Redis 7.2
- **Monitoring**: Prometheus, Grafana, LangSmith
- **Security**: Spring Security, JWT
- **Build Tool**: Maven 3.9+

## 📋 Prerequisites

- Java 21+
- Maven 3.9+
- Docker & Docker Compose
- OpenAI API Key
- PostgreSQL Database
- ChromaDB Vector Store

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd onboarding-agentic-rag-java
```

### 2. Environment Configuration

Create `.env` file:

```bash
# OpenAI Configuration
SPRING_AI_OPENAI_API_KEY=your-openai-api-key

# Database Configuration
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/onboarding
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=password

# ChromaDB Configuration
SPRING_AI_VECTOR_STORE_CHROMA_URL=http://localhost:8000

# Message Queue
SPRING_RABBITMQ_HOST=localhost
SPRING_RABBITMQ_PORT=5672
SPRING_RABBITMQ_USERNAME=admin
SPRING_RABBITMQ_PASSWORD=password

# Security
JWT_SECRET=your-secret-key-here

# LangSmith (Optional)
LANGSMITH_API_KEY=your-langsmith-api-key
```

### 3. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up chromadb redis message-queue postgres -d
```

### 4. Build and Run

```bash
# Build the application
mvn clean package

# Run the application
java -jar target/onboarding-agentic-rag-1.0.0.jar
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8081/api/actuator/health

# API documentation
curl http://localhost:8081/api/swagger-ui.html
```

## 📊 API Endpoints

### Core Agentic RAG Endpoints

```bash
# Process onboarding query with multi-agent orchestration
POST /api/v1/agentic/query
{
  "query": "What are the security protocols for accessing company systems?",
  "userContext": {
    "userId": "emp123",
    "role": "software_engineer",
    "department": "engineering",
    "onboardingStage": "week_2"
  }
}

# Get personalized onboarding path
GET /api/v1/agentic/path?userId=emp123&stage=week_1

# Get agent performance metrics
GET /api/v1/agentic/metrics
```

### WebSocket Endpoints

```bash
# Real-time conversation
WS /api/v1/agentic/chat/{userId}

# Agent status updates
WS /api/v1/agentic/status/{sessionId}
```

### Agent Management

```bash
# Get available agents
GET /api/v1/agents

# Get agent status
GET /api/v1/agents/{agentId}/status

# Add agent to conversation
POST /api/v1/agents/{agentId}/join
{
  "sessionId": "session123",
  "priority": "high"
}
```

### User Management

```bash
# Create user profile
POST /api/v1/users
{
  "userId": "emp123",
  "name": "John Doe",
  "role": "software_engineer",
  "department": "engineering",
  "startDate": "2024-01-15"
}

# Update user progress
PUT /api/v1/users/{userId}/progress
{
  "completedModules": ["security", "tools"],
  "currentStage": "week_2"
}
```

## 🔧 Configuration

### Application Properties

```yaml
# Agentic RAG Configuration
onboarding:
  agentic-rag:
    max-agents-per-query: 5
    agent-timeout: 30s
    confidence-threshold: 0.1
    cache-enabled: true
    audit-enabled: true
    personalization-enabled: true

# LangChain4j Configuration
langchain4j:
  open-ai:
    api-key: ${SPRING_AI_OPENAI_API_KEY}
    model: gpt-4
    temperature: 0.1
    max-tokens: 1500

# ChromaDB Configuration
chromadb:
  client:
    timeout: 30s
    retry-attempts: 3
    retry-delay: 1s
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPRING_AI_OPENAI_API_KEY` | OpenAI API Key | Required |
| `SPRING_DATASOURCE_URL` | PostgreSQL connection URL | `jdbc:postgresql://localhost:5432/onboarding` |
| `SPRING_AI_VECTOR_STORE_CHROMA_URL` | ChromaDB URL | `http://localhost:8000` |
| `SPRING_RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `JWT_SECRET` | JWT signing secret | Required |

## 📈 Monitoring & Observability

### Metrics Dashboard

Access Grafana at `http://localhost:3001`:
- **Username**: admin
- **Password**: admin

### Key Metrics

- **Agent Performance**: Individual agent response times and success rates
- **Orchestration Efficiency**: Multi-agent coordination metrics
- **Personalization Accuracy**: User-specific response quality
- **System Reliability**: Error rates and availability
- **User Engagement**: Session duration and interaction patterns

### LangSmith Integration

Access LangSmith at `http://localhost:1984` for:
- Agent conversation traces
- Performance analytics
- Debugging and optimization

### Health Checks

```bash
# Application health
curl http://localhost:8081/api/actuator/health

# ChromaDB health
curl http://localhost:8000/api/v1/heartbeat

# RabbitMQ health
curl -u admin:password http://localhost:15672/api/overview
```

## 🔒 Security

### Authentication

```bash
# Get JWT token
POST /api/v1/auth/login
{
  "username": "emp@company.com",
  "password": "password"
}

# Use token in requests
Authorization: Bearer <jwt-token>
```

### Role-Based Access

- **ADMIN**: Full system access and agent management
- **HR_MANAGER**: HR-related queries and user management
- **EMPLOYEE**: Personal onboarding queries
- **READONLY**: Query-only access

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
mvn test

# Run specific test
mvn test -Dtest=AgentOrchestratorTest
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
   -p query.json http://localhost:8081/api/v1/agentic/query
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale agent workers
docker-compose up -d --scale agent-workers-java=5
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n onboarding-rag
```

## 📚 Knowledge Base

### Vector Store Collections

- **company-policies**: HR policies and procedures
- **technical-docs**: Technical documentation and tools
- **security-protocols**: Security guidelines and compliance
- **company-culture**: Values, mission, and culture information
- **onboarding-materials**: Structured onboarding content

### User Profile Schema

```json
{
  "userId": "emp123",
  "name": "John Doe",
  "role": "software_engineer",
  "department": "engineering",
  "startDate": "2024-01-15",
  "onboardingStage": "week_2",
  "completedModules": ["security", "tools"],
  "preferences": {
    "learningStyle": "visual",
    "pace": "moderate"
  }
}
```

## 🔧 Development

### Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/onboarding/rag/
│   │       ├── OnboardingAgenticRagApplication.java
│   │       ├── core/
│   │       │   ├── orchestration/
│   │       │   │   └── AgentOrchestrator.java
│   │       │   ├── agent/
│   │       │   │   ├── BaseAgent.java
│   │       │   │   ├── PolicyAgent.java
│   │       │   │   ├── TechnicalAgent.java
│   │       │   │   └── ...
│   │       │   ├── model/
│   │       │   └── repository/
│   │       ├── api/
│   │       ├── config/
│   │       └── security/
│   └── resources/
│       └── application.yml
└── test/
    └── java/
        └── com/onboarding/rag/
```

### Adding New Agents

1. **Extend BaseAgent**: Create new agent class
2. **Implement Agent Logic**: Define agent-specific behavior
3. **Register Agent**: Add to AgentRegistry
4. **Add Tests**: Create comprehensive test coverage

### Customizing Orchestration

1. **Routing Logic**: Modify agent selection criteria
2. **Response Synthesis**: Customize multi-agent response fusion
3. **Quality Assessment**: Implement custom confidence scoring

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
- Follow LangChain4j patterns for agent development

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)

## 🔄 Version History

- **v1.0.0**: Initial release with Spring Boot 3.2 and Spring AI 0.8.0
- **v0.9.0**: Beta release with multi-agent orchestration
- **v0.8.0**: Alpha release with basic agent framework

---

**Built with ❤️ using Spring Boot, Spring AI, and LangChain4j** 