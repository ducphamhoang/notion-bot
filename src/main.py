"""Main application entrypoint for the Notion Bot API."""

import logging
import logging.handlers
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

# Import application components
from src.config.settings import get_settings
from src.core.database.connection import DatabaseConnection
from src.core.errors.error_handler import global_exception_handler
from src.features.tasks.routes import router as tasks_router
from src.features.workspaces.routes import router as workspaces_router


# Configure structured logging
def configure_logging():
    """Configure structured logging with log levels from settings."""
    settings = get_settings()
    
    # Configure standard library logger for structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level)
    )
    
    # Configure structlog
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown handling."""
    logger = structlog.get_logger()
    
    # Startup
    logger.info("Starting Notion Bot API...")
    
    try:
        # Initialize database connection
        await DatabaseConnection.get_database()
        logger.info("Database connection established")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    # Shutdown
    logger.info("Shutting down Notion Bot API...")
    await DatabaseConnection.close_connection()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Configure logging first
    configure_logging()
    logger = structlog.get_logger()
    
    # Create FastAPI app
    settings = get_settings()
    
    app = FastAPI(
        title="Notion Bot API",
        description="Core task management APIs for Notion integration",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # Add CORS middleware
    # Parse allowed origins from settings
    allowed_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add unique request ID to each request for tracing."""
        import uuid
        
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        # Log request
        logger.info(
            "API request",
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            request_id=request_id
        )
        
        return response
    
    # Add logging middleware
    @app.middleware("http")
    async def log_responses(request: Request, call_next):
        """Log API responses with timing."""
        import time
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            logger.info(
                "API response",
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "API error",
                method=request.method,
                path=str(request.url.path),
                error=str(e),
                duration=duration
            )
            raise
    
    # Include routers
    app.include_router(tasks_router)
    app.include_router(workspaces_router)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler_wrapper(request: Request, exc: Exception):
        """Wrap the global exception handler."""
        return await global_exception_handler(request, exc)
    
    # Health check endpoint
    @app.get("/health", tags=["health"], summary="Health check")
    async def health_check():
        """Check the health of the application and its dependencies."""
        db_health = await DatabaseConnection.health_check()
        
        # Overall status is unhealthy if any component is unhealthy
        overall_status = "healthy"
        if db_health["status"] != "healthy":
            overall_status = "unhealthy"
        
        return JSONResponse(
            status_code=200 if overall_status == "healthy" else 503,
            content={
                "status": overall_status,
                "checks": {
                    "database": db_health
                }
            }
        )
    
    # Root endpoint
    @app.get("/", tags=["root"], summary="API root")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Notion Bot API",
            "version": "0.1.0",
            "docs_url": "/docs" if settings.debug else "disabled"
        }
    
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
