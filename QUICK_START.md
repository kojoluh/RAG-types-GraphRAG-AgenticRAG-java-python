# Quick Start Guide

This guide will help you get both RAG projects up and running quickly.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key
- At least 8GB RAM available

## Project 1: Aviation Graph RAG

### Step 1: Clone and Setup

```bash
# Navigate to the aviation project
cd aviation-graph-rag

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Step 3: Initialize Data

```bash
# Run data ingestion
docker-compose exec aviation-api python -m src.data.ingestion.main

# Verify Neo4j connection
docker-compose exec aviation-api python -m src.core.graph_service
```

### Step 4: Test the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "query": "What is the status of flight AA123?",
    "user_context": {"role": "customer_service"}
  }'
```

### Step 5: Access Dashboards

- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Project 2: Agentic RAG Onboarding

### Step 1: Clone and Setup

```bash
# Navigate to the onboarding project
cd onboarding-agentic-rag

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

Add your API keys to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

### Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Step 3: Initialize Agents

```bash
# Initialize agent registry
docker-compose exec onboarding-api python -m src.agents.registry

# Load knowledge base
docker-compose exec onboarding-api python -m src.data.knowledge_loader
```

### Step 4: Test the API

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test query endpoint
curl -X POST http://localhost:8001/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "query": "What are the company policies for remote work?",
    "user_context": {
      "user_id": "user123",
      "role": "software_engineer",
      "department": "engineering"
    }
  }'
```

### Step 5: Access Dashboards

- **API Documentation**: http://localhost:8001/docs
- **ChromaDB**: http://localhost:8000
- **LangSmith**: http://localhost:1984
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)
- **RabbitMQ Management**: http://localhost:15672 (admin/password)

## Development Setup

### Local Development (Aviation Graph RAG)

```bash
cd aviation-graph-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here

# Run the application
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Local Development (Agentic RAG)

```bash
cd onboarding-agentic-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export LANGSMITH_API_KEY=your_key_here

# Run the application
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
```

## Testing

### Run Tests (Both Projects)

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage
pytest --cov=src --cov-report=html
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test for aviation project
cd aviation-graph-rag
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Run load test for onboarding project
cd onboarding-agentic-rag
locust -f tests/load/locustfile.py --host=http://localhost:8001
```

## Monitoring

### Check Service Health

```bash
# Aviation Graph RAG
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# Agentic RAG
curl http://localhost:8001/health
curl http://localhost:8001/metrics
```

### View Logs

```bash
# Aviation Graph RAG logs
docker-compose logs -f aviation-api

# Agentic RAG logs
docker-compose logs -f onboarding-api

# Agent worker logs
docker-compose logs -f agent-workers
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :8001
   
   # Stop conflicting services
   sudo systemctl stop conflicting_service
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   # In Docker Desktop: Settings > Resources > Memory > 8GB
   ```

3. **Database Connection Issues**
   ```bash
   # Check Neo4j status
   docker-compose exec neo4j neo4j status
   
   # Check ChromaDB status
   docker-compose exec chromadb curl http://localhost:8000/api/v1/heartbeat
   ```

4. **API Key Issues**
   ```bash
   # Verify API key is set
   echo $OPENAI_API_KEY
   
   # Test OpenAI connection
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Reset Everything

```bash
# Stop all services
docker-compose down

# Remove all data
docker-compose down -v

# Rebuild and start
docker-compose up --build -d
```

## Next Steps

1. **Customize Configuration**: Edit `.env` files for your specific needs
2. **Add Your Data**: Import your domain-specific data
3. **Train Models**: Fine-tune models for your use case
4. **Deploy to Production**: Follow the deployment guide in each project's README

## Support

- **Documentation**: See README.md in each project directory
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

## License

Both projects are licensed under the MIT License. See LICENSE files for details. 