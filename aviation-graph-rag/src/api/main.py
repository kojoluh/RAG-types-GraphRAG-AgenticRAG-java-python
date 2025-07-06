"""
Aviation Graph RAG API - Main Application
Production-ready FastAPI application for aviation customer support chatbot
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import structlog

from .routers import query, flights, aircraft, maintenance, audit, graph
from .middleware import AuthMiddleware, LoggingMiddleware, MetricsMiddleware
from .dependencies import get_current_user, get_graph_service, get_vector_service
from ..core.config import settings
from ..core.monitoring import setup_monitoring

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Aviation Graph RAG API")
    setup_monitoring()
    
    # Initialize services
    from ..core.services import initialize_services
    await initialize_services()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aviation Graph RAG API")
    from ..core.services import cleanup_services
    await cleanup_services()

# Create FastAPI application
app = FastAPI(
    title="Aviation Graph RAG API",
    description="Production-ready Graph RAG system for aviation customer support",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(
    query.router,
    prefix="/api/v1",
    tags=["Query"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    flights.router,
    prefix="/api/v1/flights",
    tags=["Flights"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    aircraft.router,
    prefix="/api/v1/aircraft",
    tags=["Aircraft"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    maintenance.router,
    prefix="/api/v1/maintenance",
    tags=["Maintenance"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    audit.router,
    prefix="/api/v1/audit",
    tags=["Audit"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    graph.router,
    prefix="/api/v1/graph",
    tags=["Graph"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Aviation Graph RAG API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database connections
        graph_service = get_graph_service()
        vector_service = get_vector_service()
        
        graph_status = await graph_service.health_check()
        vector_status = await vector_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "graph_database": graph_status,
                "vector_database": vector_status
            },
            "timestamp": structlog.processors.TimeStamper(fmt="iso")
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 