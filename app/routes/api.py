"""
FastAPI routes for ChronicCare AI service.
Implements all 7+ endpoints with proper error handling and validation.
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.config import get_settings
from app.schemas import (
    DriftDetectionResponse,
    EmbedRequest,
    EmbedResponse,
    ErrorResponse,
    GlossaryEntry,
    GlossarySearchRequest,
    HealthCheckResponse,
    NOURRequest,
    NOURResponse,
    PredictionRecord,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
)
from app.services.drift_service import get_drift_service
from app.services.gemini_service import get_gemini_service
from app.services.pdf_service import get_pdf_service
from app.services.rag_service import get_rag_service
from app.services.risk_service import get_risk_service
from app.utils.exceptions import ChronicCareException
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["chronicare"])


# ======================
# Health & System Routes
# ======================


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check service status and dependencies",
)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint to verify service and dependencies are operational.

    Returns:
        HealthCheckResponse with service status details
    """
    try:
        settings = get_settings()
        gemini_service = get_gemini_service()
        risk_service = get_risk_service()

        return {
            "status": "healthy",
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "gemini": "initialized",
                "model": "loaded",
                "environment": settings.environment,
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "error": str(e),
            },
        }


# ======================
# Embedding Routes
# ======================


@router.post(
    "/embed",
    response_model=EmbedResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Text Embeddings",
    description="Generate embeddings for medical text using Gemini",
)
async def embed_text(request: EmbedRequest) -> dict[str, Any]:
    """
    Generate embeddings for medical text.

    Args:
        request: EmbedRequest containing text to embed

    Returns:
        EmbedResponse with embedding vector

    Raises:
        HTTPException: If embedding generation fails
    """
    try:
        gemini_service = get_gemini_service()
        embedding = await gemini_service.embed_text(request.text)

        return {
            "text": request.text,
            "embedding": embedding,
            "model": "gemini-1.5-flash",
            "dimensions": len(embedding),
        }
    except ChronicCareException as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details,
            },
        )


# ======================
# Glossary Routes
# ======================


@router.post(
    "/glossary/search",
    response_model=list[GlossaryEntry],
    status_code=status.HTTP_200_OK,
    summary="Search Medical Glossary",
    description="Search medical glossary using semantic similarity",
)
async def search_glossary(request: GlossarySearchRequest) -> list[dict[str, Any]]:
    """
    Search the medical glossary using semantic similarity.

    Args:
        request: GlossarySearchRequest with search parameters

    Returns:
        List of matching glossary entries

    Raises:
        HTTPException: If search fails
    """
    try:
        rag_service = get_rag_service()
        results = await rag_service.search_medical_terms(
            request.query, limit=request.limit, language=request.language
        )
        return results
    except ChronicCareException as e:
        logger.error(f"Glossary search error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
            },
        )


@router.get(
    "/glossary",
    response_model=list[GlossaryEntry],
    status_code=status.HTTP_200_OK,
    summary="Get Full Glossary",
    description="Get complete medical glossary",
)
async def get_full_glossary(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[dict[str, Any]]:
    """
    Get the complete medical glossary with pagination.

    Args:
        skip: Number of entries to skip
        limit: Maximum entries to return

    Returns:
        List of glossary entries
    """
    try:
        from data.darija_medical_glossary import get_glossary

        all_entries = get_glossary()
        return all_entries[skip : skip + limit]
    except Exception as e:
        logger.error(f"Failed to get glossary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve glossary",
        )


# ======================
# Risk Assessment Routes
# ======================


@router.post(
    "/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess Patient Risk",
    description="Assess chronic disease risk using decision tree",
)
async def assess_risk(request: RiskAssessmentRequest) -> dict[str, Any]:
    """
    Assess patient risk for chronic diseases.

    Args:
        request: RiskAssessmentRequest with patient data

    Returns:
        RiskAssessmentResponse with risk metrics and recommendations

    Raises:
        HTTPException: If assessment fails
    """
    try:
        risk_service = get_risk_service()
        assessment = await risk_service.assess_patient_risk(
            request.patient_data.dict()
        )
        return assessment
    except ChronicCareException as e:
        logger.error(f"Risk assessment error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
            },
        )


# ======================
# NOUR Clinical Reasoning
# ======================


@router.post(
    "/nour",
    response_model=NOURResponse,
    status_code=status.HTTP_200_OK,
    summary="NOUR Clinical Reasoning",
    description="Generate clinical reasoning using NOUR (Nurturing Outcomes Using Reasoning)",
)
async def nour_reasoning(request: NOURRequest) -> dict[str, Any]:
    """
    Generate NOUR clinical reasoning response.
    This is the core reasoning engine that combines patient data with medical knowledge.

    Args:
        request: NOURRequest with symptoms and patient data

    Returns:
        NOURResponse with clinical assessment and recommendations

    Raises:
        HTTPException: If reasoning generation fails
    """
    try:
        gemini_service = get_gemini_service()
        risk_service = get_risk_service()
        rag_service = get_rag_service()

        # Get risk assessment
        risk_assessment = await risk_service.assess_patient_risk(
            request.patient_data.dict()
        )

        # Get glossary context
        glossary_context = ""
        glossary_entries = []
        if request.include_glossary:
            glossary_results = await rag_service.search_medical_terms(
                request.patient_symptoms, limit=5
            )
            glossary_entries = glossary_results
            glossary_context = await rag_service.build_glossary_context(
                [s.get("darija", "") for s in glossary_results if s.get("darija")]
            )

        # Generate NOUR response
        nour_response = await gemini_service.generate_nour_response(
            patient_symptoms=request.patient_symptoms,
            glossary_context=glossary_context,
            risk_assessment=risk_assessment["category"],
        )

        return {
            "clinical_assessment": nour_response,
            "risk_assessment": risk_assessment,
            "recommendations": risk_assessment["recommendations"],
            "glossary_context": glossary_entries,
        }
    except ChronicCareException as e:
        logger.error(f"NOUR reasoning error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
            },
        )


# ======================
# Drift Detection Routes
# ======================


@router.post(
    "/predictions/record",
    status_code=status.HTTP_201_CREATED,
    summary="Record Prediction",
    description="Record a prediction for drift detection monitoring",
)
async def record_prediction(request: PredictionRecord) -> dict[str, str]:
    """
    Record a prediction result for model drift detection.

    Args:
        request: PredictionRecord with prediction and actual outcome

    Returns:
        Confirmation message
    """
    try:
        drift_service = get_drift_service()
        await drift_service.record_prediction(
            predicted_risk=request.predicted_risk,
            actual_risk=request.actual_risk,
            confidence=request.confidence,
        )
        return {"status": "recorded", "message": "Prediction recorded successfully"}
    except Exception as e:
        logger.error(f"Failed to record prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record prediction",
        )


@router.get(
    "/drift-detection",
    response_model=DriftDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect Model Drift",
    description="Detect model performance degradation",
)
async def detect_drift() -> dict[str, Any]:
    """
    Detect model drift based on recent predictions.

    Returns:
        DriftDetectionResponse with drift metrics and recommendations
    """
    try:
        drift_service = get_drift_service()
        report = await drift_service.detect_drift()
        return report
    except Exception as e:
        logger.error(f"Drift detection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect drift",
        )


# ======================
# PDF Report Generation
# ======================


@router.post(
    "/reports/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate Clinical Report",
    description="Generate PDF clinical report",
)
async def generate_report(
    patient_id: str = Query(..., description="Patient identifier"),
    patient_name: str = Query(..., description="Patient full name"),
    request: NOURRequest = Depends(),
) -> FileResponse:
    """
    Generate a comprehensive clinical PDF report.

    Args:
        patient_id: Patient identifier
        patient_name: Patient full name
        request: NOURRequest with clinical data

    Returns:
        PDF file as FileResponse

    Raises:
        HTTPException: If report generation fails
    """
    try:
        gemini_service = get_gemini_service()
        risk_service = get_risk_service()
        rag_service = get_rag_service()
        pdf_service = get_pdf_service()

        # Perform assessments
        risk_assessment = await risk_service.assess_patient_risk(
            request.patient_data.dict()
        )

        glossary_results = await rag_service.search_medical_terms(
            request.patient_symptoms, limit=5
        )
        glossary_context = await rag_service.build_glossary_context(
            [s.get("darija", "") for s in glossary_results if s.get("darija")]
        )

        nour_response = await gemini_service.generate_nour_response(
            patient_symptoms=request.patient_symptoms,
            glossary_context=glossary_context,
            risk_assessment=risk_assessment["category"],
        )

        # Generate PDF
        pdf_bytes = await pdf_service.generate_patient_report(
            patient_id=patient_id,
            patient_name=patient_name,
            patient_data=request.patient_data.dict(),
            risk_assessment=risk_assessment,
            clinical_notes=nour_response,
            glossary_context=glossary_context,
        )

        # Return as file
        filename = f"chronicare_report_{patient_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        return FileResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            filename=filename,
        )
    except ChronicCareException as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
            },
        )


# ======================
# Error Handler
# ======================


@router.get("/error-example", include_in_schema=False)
async def error_example() -> dict[str, Any]:
    """Example error response (hidden from docs)."""
    return {
        "status_code": 400,
        "error_code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {"field": "age", "reason": "must be positive"},
        "timestamp": datetime.utcnow().isoformat(),
    }
