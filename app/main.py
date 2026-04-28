"""
ChronicCare FastAPI Application.
Main entry point for the YAKOUB AI brain service.
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes import api
from app.schemas import GlossarySearchRequest
from app.services.drift_service import get_drift_service
from app.services.gemini_service import get_gemini_service
from app.services.rag_service import get_rag_service
from app.services.risk_service import get_risk_service
from app.utils.exceptions import ChronicCareException
from app.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("=" * 60)
    logger.info("ChronicCare AI Service Starting Up")
    logger.info("=" * 60)

    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Version: {settings.app_version}")

    try:
        # Initialize services
        logger.info("Initializing services...")
        gemini_service = get_gemini_service()
        logger.info("✓ Gemini service initialized")

        risk_service = get_risk_service()
        logger.info("✓ Risk scoring service initialized")

        rag_service = get_rag_service()
        logger.info("✓ RAG service initialized")

        drift_service = get_drift_service()
        logger.info("✓ Drift detection service initialized")

        logger.info("All services initialized successfully")
        logger.info("=" * 60)
        logger.info("ChronicCare AI Service Ready")
        logger.info("=" * 60)
    except Exception as e:
        logger.warning(f"Service initialization warning (database may be optional for demo): {str(e)}")
        logger.info("Continuing in demo mode...")

    yield

    # Shutdown
    logger.info("Shutting down ChronicCare AI Service...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    # Setup logging
    setup_logging(settings.log_level)

    # Create app
    app = FastAPI(
        title="ChronicCare AI",
        description="YAKOUB's AI brain for chronic disease management in Algeria",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(ChronicCareException)
    async def chroniccare_exception_handler(
        request: Request, exc: ChronicCareException
    ) -> JSONResponse:
        """Handle ChronicCare exceptions."""
        logger.error(
            f"ChronicCare exception: {exc.error_code} - {exc.message}",
            extra={"details": exc.details},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"][1:]),
                    "message": error["msg"],
                }
            )
        logger.warning(f"Validation error: {errors}")
        return JSONResponse(
            status_code=422,
            content={
                "status_code": 422,
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status_code": 500,
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {"error": str(exc)},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    # Include routes
    app.include_router(api.router)

    # ======================
    # CONTRACT-COMPLIANT ALIASES
    # Maps /ai/* to /api/v1/* for Seghir integration
    # ======================
    
    # Create an AI-prefixed router for contract compliance
    ai_router = APIRouter(prefix="/ai", tags=["ai-contract"])

    # Alias: /ai/chat → /api/v1/nour with risk merged
    @ai_router.post("/chat")
    async def ai_chat_alias(request: dict[str, Any]):
        """Alias to /api/v1/chat - delegates to NOUR endpoint."""
        # This is handled by the new /api/v1/chat endpoint
        # Client calls POST /ai/chat which routes here
        return await api.ai_chat(
            request=request,
            x_internal_key=None  # Will be passed through headers by FastAPI
        )

    # Alias: /ai/drift/{patient_id} → /api/v1/drift-detection
    @ai_router.post("/drift/{patient_id}")
    async def ai_drift_alias(patient_id: str):
        """Alias to drift detection endpoint."""
        return await api.detect_drift()

    # Alias: /ai/pdf/{patient_id} → /api/v1/reports/generate
    @ai_router.post("/pdf/{patient_id}")
    async def ai_pdf_alias(patient_id: str, request: dict[str, Any]):
        """Alias to PDF generation endpoint."""
        # Extract patient name from request or use patient_id
        patient_name = request.get("patient_name", f"Patient {patient_id}")
        return await api.generate_report(
            patient_id=patient_id,
            patient_name=patient_name,
            request=request
        )

    # Alias: /ai/glossary → /api/v1/glossary
    @ai_router.get("/glossary")
    async def ai_glossary_alias(skip: int = 0, limit: int = 100):
        """Alias to glossary endpoint."""
        return await api.get_full_glossary(skip=skip, limit=limit)

    # Alias: /ai/glossary/match → /api/v1/glossary/search
    @ai_router.post("/glossary/match")
    async def ai_glossary_match_alias(request: dict[str, Any]):
        """Alias to glossary search endpoint."""
        glossary_request = GlossarySearchRequest(
            query=request.get("query", ""),
            limit=request.get("limit", 10),
            language=request.get("language", "darija")
        )
        return await api.search_glossary(glossary_request)

    app.include_router(ai_router)

    # Root route
    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": "ChronicCare AI Service",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
            "primary_endpoint": "/ai/chat",
            "contract": "Seghir Integration v1.0",
        }

    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
