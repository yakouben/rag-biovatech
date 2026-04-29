"""
FastAPI routes for ChronicCare AI service.
Implements all 7+ endpoints with proper error handling and validation.
"""
import os
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Header, Query, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.config import get_settings
from app.database.connection import get_database
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
    RiskAssessmentResponse,
    DoctorChatRequest,
    PatientProfile,
    OnboardingRequest,
    OnboardingResponse,
)
from app.services.adherence_service import get_adherence_service
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
# Auth Dependency
# ======================

def verify_internal_api_key(x_internal_key: str = Header(None)) -> None:
    """Verify the internal API key for secure inter-service communication."""
    expected_key = os.getenv("INTERNAL_API_KEY")
    if expected_key and x_internal_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing INTERNAL_API_KEY header"
        )


# ======================
# Contract-Compliant Routes (/ai/* prefix)
# ======================


@router.post(
    "/chat",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="AI Chat with Integrated Risk Assessment",
    description="Main endpoint for patient conversations with automatic risk scoring and clinical reasoning",
    tags=["ai-contract"]
)
async def ai_chat(
    request: NOURRequest,
    x_internal_key: str = Header(None),
) -> dict[str, Any]:
    """
    Contract-compliant /ai/chat endpoint.
    Combines NOUR clinical reasoning with automatic risk assessment in a single response.
    This is the PRIMARY endpoint that Seghir's Express service calls.

    Args:
        request: NOURRequest with patient_id, text, and patient_profile
        x_internal_key: Internal API key for service-to-service auth

    Returns:
        Unified response with clinical assessment, risk score, and confidence
    """
    try:
        # Verify API key if configured
        verify_internal_api_key(x_internal_key)

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

        # Get medical knowledge guidelines
        medical_knowledge = await rag_service.get_medical_knowledge(
            request.patient_symptoms, limit=3
        )

        # Generate HELA response and extract entities in parallel
        hela_response_task = gemini_service.generate_hela_response(
            patient_symptoms=request.patient_symptoms,
            glossary_context=f"{glossary_context}\n\nMEDICAL GUIDELINES:\n{medical_knowledge}",
            risk_assessment=risk_assessment["category"],
        )
        extraction_task = gemini_service.extract_clinical_entities(request.patient_symptoms)
        
        hela_response, real_extracted_entities = await asyncio.gather(
            hela_response_task, extraction_task
        )

        # SAVE TO SUPABASE (Background)
        db = get_database()
        asyncio.create_task(db.save_patient_assessment(
            patient_id=request.patient_id,
            assessment_data=risk_assessment,
            entities=real_extracted_entities.dict(),
            glossary_terms=[s.get("darija", "") for s in glossary_entries]
        ))

        # UNIFIED RESPONSE - matches Seghir's contract exactly
        return {
            "hela_response": hela_response,
            "extracted_entities": real_extracted_entities,
            "risk_score": risk_assessment["category"],  # HIGH, MODERATE, LOW
            "confidence": risk_assessment["probabilities"].get(
                risk_assessment["category"].lower(), 0.5
            ),
            "factors": risk_assessment["recommendations"],
            "monitoring_frequency": risk_assessment["monitoring_frequency"],
            "glossary_context": glossary_entries,
        }
    except ChronicCareException as e:
        logger.error(f"AI chat error: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
            },
        )


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
    Actually tests DB connection with a real query.
    """
    settings = get_settings()
    db_status = "disconnected"
    gemini_status = "uninitialized"
    model_status = "unloaded"
    overall_status = "degraded"

    # 1. Test real DB connection
    try:
        db = get_database()
        result = db.client.table("medical_glossary").select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check - DB connection failed: {str(e)}")
        db_status = f"error: {str(e)[:80]}"

    # 2. Check Gemini service
    try:
        get_gemini_service()
        gemini_status = "initialized"
    except Exception as e:
        gemini_status = f"error: {str(e)[:80]}"

    # 3. Check Risk model
    try:
        get_risk_service()
        model_status = "loaded"
    except Exception as e:
        model_status = f"error: {str(e)[:80]}"

    if db_status == "connected" and gemini_status == "initialized":
        overall_status = "healthy"

    return {
        "status": overall_status,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "gemini": gemini_status,
            "model": model_status,
            "environment": settings.environment,
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

        # Get patient data from request or database
        patient_data = request.patient_data
        if not patient_data:
            from app.database.connection import get_database
            from app.schemas import PatientData
            db = get_database()
            latest_vitals = await db.get_latest_patient_vitals(request.patient_id)
            
            def safe_get(vitals_dict, key, default):
                if not vitals_dict: return default
                val = vitals_dict.get(key)
                return float(val) if val is not None else default

            patient_data = PatientData(
                age=int(safe_get(latest_vitals, "age", 50)),
                systolic_bp=int(safe_get(latest_vitals, "systolic_bp", 120)),
                diastolic_bp=int(safe_get(latest_vitals, "diastolic_bp", 80)),
                fasting_glucose=int(safe_get(latest_vitals, "glucose", 100)),
                bmi=float(safe_get(latest_vitals, "bmi", 22.0)),
                smoking=False,
                family_history=False,
                comorbidities=0
            )

        # Get risk assessment
        risk_assessment = await risk_service.assess_patient_risk(
            patient_data.dict()
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

        # Get medical knowledge guidelines
        medical_knowledge = await rag_service.get_medical_knowledge(
            request.patient_symptoms, limit=3
        )

        # Generate HELA response and extract entities in parallel
        hela_response_task = gemini_service.generate_hela_response(
            patient_symptoms=request.patient_symptoms,
            glossary_context=f"{glossary_context}\n\nMEDICAL GUIDELINES:\n{medical_knowledge}",
            risk_assessment=risk_assessment["category"],
        )
        extraction_task = gemini_service.extract_clinical_entities(request.patient_symptoms)
        
        hela_response, real_extracted_entities = await asyncio.gather(
            hela_response_task, extraction_task
        )

        # SAVE TO SUPABASE (Background)
        db = get_database()
        asyncio.create_task(db.save_patient_assessment(
            patient_id=request.patient_id,
            assessment_data=risk_assessment,
            entities=real_extracted_entities.dict(),
            glossary_terms=[s.get("darija", "") for s in glossary_entries]
        ))

        return {
            "clinical_assessment": hela_response,
            "risk_assessment": risk_assessment,
            "recommendations": risk_assessment["recommendations"],
            "extracted_entities": real_extracted_entities,
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
    adherence_days: int = Query(30, ge=7, le=90, description="Number of days for adherence calculation"),
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
        adherence_service = get_adherence_service()

        # Perform assessments
        risk_assessment = await risk_service.assess_patient_risk(
            request.patient_data.dict()
        )
        
        # Calculate Adherence
        adherence_score = await adherence_service.calculate_adherence(patient_id, days=adherence_days)

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
            adherence_score=adherence_score,
        )

        # Return as stream
        from io import BytesIO
        filename = f"chronicare_report_{patient_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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

# ======================
# Doctor Intelligence
# ======================

@router.post(
    "/doctor/chat",
    status_code=status.HTTP_200_OK,
    summary="Chat with Patient History",
    description="Allows doctors to ask clinical questions about a patient's historical records.",
)
async def doctor_chat_history(request: DoctorChatRequest) -> dict[str, Any]:
    """
    RAG over patient history for clinical decision support.
    """
    try:
        db = get_database()
        gemini_service = get_gemini_service()
        
        # 1. Fetch historical interactions (last 50)
        result = db.client.table("patient_assessments") \
            .select("assessment_date, clinical_entities, symptoms") \
            .eq("patient_id", request.patient_id) \
            .order("assessment_date", desc=True) \
            .limit(50) \
            .execute()
            
        history = result.data if hasattr(result, "data") else []
        
        if not history:
            return {"answer": "No historical data found for this patient.", "history_analyzed": 0}
            
        # 2. Build history context
        context_parts = []
        for entry in history:
            date = entry.get("assessment_date", "Unknown Date")
            entities = entry.get("clinical_entities", {})
            note = entry.get("symptoms", "No note")
            context_parts.append(f"Date: {date}\nSummary: {note}\nEntities: {entities}\n---")
            
        history_context = "\n".join(context_parts)
        
        # 3. Generate Answer
        answer = await gemini_service.generate_doctor_answer(request.question, history_context)
        
        return {
            "answer": answer,
            "patient_id": request.patient_id,
            "history_analyzed": len(history),
            "raw_history": history if request.include_raw_history else None
        }
    except Exception as e:
        logger.error(f"Doctor chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/patient/{patient_id}/check-drift",
    summary="Proactive Adherence Check",
    description="Checks for sharp adherence drops and generates a nurture message if needed.",
)
async def check_patient_drift(patient_id: str) -> dict[str, Any]:
    """
    Triggers proactive drift reasoning for a specific patient.
    """
    try:
        drift_service = get_drift_service()
        analysis = await drift_service.analyze_adherence_proactively(patient_id)
        return analysis
    except Exception as e:
        logger.error(f"Drift check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# Clinical Data History
# ======================

@router.get(
    "/patient/{patient_id}/history",
    summary="Get Patient Clinical History",
    description="Returns structured historical clinical data for dashboard trend graphs.",
)
async def get_patient_history(
    patient_id: str,
    days: int = Query(30, ge=1, le=90)
) -> dict[str, Any]:
    """
    Fetches historical assessments for trend visualization (BP, Glucose, Adherence).
    """
    try:
        db = get_database()
        
        # Calculate date range
        # (Assuming the database manager has a way to query this)
        # For the hackathon, we'll use a direct supabase call for maximum speed
        result = db.client.table("patient_assessments") \
            .select("assessment_date, clinical_entities, risk_score, symptoms") \
            .eq("patient_id", patient_id) \
            .order("assessment_date", desc=True) \
            .limit(days) \
            .execute()
            
        history = result.data if hasattr(result, "data") else []
        
        # Format for charts (e.g., recharts)
        chart_data = []
        for entry in history:
            entities = entry.get("clinical_entities", {})
            vitals = entities.get("vitals", {})
            chart_data.append({
                "date": entry.get("assessment_date"),
                "risk": entry.get("risk_score"),
                "systolic": vitals.get("systolic_bp"),
                "diastolic": vitals.get("diastolic_bp"),
                "glucose": vitals.get("glucose"),
                "summary": entry.get("symptoms")
            })
            
        return {
            "patient_id": patient_id,
            "count": len(history),
            "history": chart_data[::-1] # Return in chronological order for the chart
        }
    except Exception as e:
        logger.error(f"Failed to fetch patient history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/patients/risk-queue",
    summary="Get High-Risk Patient Queue",
    description="Returns latest assessments for all patients, prioritized by risk score.",
)
async def get_risk_queue() -> list[dict[str, Any]]:
    """
    Fetches the latest clinical state for all patients to populate the doctor's dashboard.
    Returns an empty list if the table is empty or doesn't exist yet.
    """
    try:
        db = get_database()
        result = db.client.table("patient_assessments") \
            .select("patient_id, assessment_date, risk_score, predicted_risk_level, symptoms") \
            .order("assessment_date", desc=True) \
            .limit(100) \
            .execute()

        data = result.data if (hasattr(result, "data") and result.data) else []
        logger.info(f"Risk queue returned {len(data)} patients")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch risk queue: {str(e)}")
        # Return empty list instead of crashing the dashboard
        return []

# ======================
# Patient Management
# ======================

@router.post(
    "/patients/onboard",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard New or Existing Patient",
    description="Creates a detailed patient profile, handles history import, and performs initial risk assessment.",
)
async def onboard_patient(request: OnboardingRequest) -> dict[str, Any]:
    """
    Onboarding workflow:
    1. Create/Update Profile (including family contact and clinic origin)
    2. Perform initial risk assessment if vitals are provided
    3. Save initial assessment to history
    4. Run AI analysis for clinical summary and welcome message
    """
    try:
        db = get_database()
        risk_service = get_risk_service()
        gemini_service = get_gemini_service()
        
        # 1. Save Profile
        profile_dict = request.profile.dict(exclude_none=True)
        saved_profile = await db.upsert_patient_profile(profile_dict)
        patient_id = saved_profile["id"]
        
        message = "New patient onboarded successfully."
        if request.is_import:
            message = f"Patient profile imported from clinic {request.profile.previous_clinic_id}."
            
        # 2. Initial Assessment
        initial_risk = None
        vitals_dict = None
        if request.initial_vitals:
            vitals_dict = request.initial_vitals.dict()
            initial_risk = await risk_service.assess_patient_risk(vitals_dict)
            
            # Save to history
            await db.save_patient_assessment(
                patient_id=patient_id,
                assessment_data=initial_risk,
                entities={
                    "clinical_note": f"Initial onboarding assessment. {'Imported history: ' + request.profile.medical_history_summary if request.is_import else ''}",
                    "vitals": vitals_dict
                }
            )

        # 3. AI Analysis
        ai_analysis = await gemini_service.analyze_onboarding_data(
            name=request.profile.name,
            history_summary=request.profile.medical_history_summary,
            initial_vitals=vitals_dict
        )
            
        return {
            "patient_id": patient_id,
            "status": "success",
            "message": message,
            "initial_risk": initial_risk,
            "ai_analysis": ai_analysis
        }
    except Exception as e:
        logger.error(f"Onboarding failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Onboarding failed: {str(e)}")

@router.get(
    "/patient/{patient_id}/profile",
    response_model=PatientProfile,
    summary="Get Detailed Patient Profile",
)
async def get_patient_profile(patient_id: str) -> dict[str, Any]:
    """Fetches the detailed profile including family contact info."""
    db = get_database()
    profile = await db.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile
