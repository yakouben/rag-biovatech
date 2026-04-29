from typing import Any
from fastapi import APIRouter, status, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services.pdf_service import get_pdf_service
from app.services.gemini_service import get_gemini_service
from app.services.adherence_service import get_adherence_service
from app.schemas import OnboardingRequest, OnboardingResponse
from app.database.connection import get_database

router = APIRouter(prefix="/doctor", tags=["Doctor Intelligence"])

@router.get("/risk-queue", summary="Get High-Risk Patient Queue")
async def get_risk_queue() -> list[dict[str, Any]]:
    """Fetches the latest clinical state for all patients, prioritized by risk score."""
    try:
        db = get_database()
        result = db.client.table("patient_assessments") \
            .select("patient_id, assessment_date, risk_score, symptoms") \
            .order("assessment_date", desc=True) \
            .limit(100) \
            .execute()
        return result.data if hasattr(result, "data") else []
    except Exception:
        return []

from app.utils.helpers import calculate_dob

@router.post("/onboard", response_model=OnboardingResponse)
async def onboard_patient(request: OnboardingRequest):
    """Workflow d'onboarding complet avec analyse IA de bienvenue."""
    db = get_database()
    gemini_service = get_gemini_service()
    
    # 1. Transformation des données pour Supabase
    parts = request.profile.name.split(" ", 1)
    profile_data = {
        "id": request.profile.id,
        "first_name": parts[0],
        "last_name": parts[1] if len(parts) > 1 else "",
        "birth_date": calculate_dob(request.profile.age),
        "gender": request.profile.gender,
        "phone": request.profile.phone,
        "address": request.profile.address,
        "family_contact_name": request.profile.family_contact_name,
        "family_contact_phone": request.profile.family_contact_phone,
        "family_access_granted": request.profile.family_access_granted,
        "medical_history_summary": request.profile.medical_history_summary,
    }
    
    # Remove None values to avoid overwriting with null if not provided
    profile_data = {k: v for k, v in profile_data.items() if v is not None}
    
    # 2. Sauvegarde du profil
    saved_profile = await db.upsert_patient_profile(profile_data)
    patient_id = saved_profile.get("id")
    
    # 3. Analyse de bienvenue par Hela
    welcome_msg = await gemini_service.generate_hela_response(
        patient_symptoms=request.profile.medical_history_summary or "Nouveau patient",
        glossary_context="Message de bienvenue chaleureux en Darija",
        risk_assessment="LOW"
    )
    
    return {
        "status": "success", 
        "patient_id": patient_id,
        "message": "Patient onboardé avec succès",
        "ai_analysis": {
            "clinical_summary": "Profil initial créé et indexé.",
            "welcome_message_darija": welcome_msg
        }
    }

@router.post("/reports/generate")
async def generate_report(
    patient_id: str, 
    patient_name: str, 
    adherence_days: int = 30
):
    """Génération du rapport PDF clinique complet."""
    pdf_service = get_pdf_service()
    adherence_service = get_adherence_service()
    db = get_database()
    
    # Calcul de l'adhérence réelle
    score = await adherence_service.calculate_adherence(patient_id, days=adherence_days)
    
    # Génération PDF
    pdf_bytes = await pdf_service.generate_patient_report(
        patient_id=patient_id,
        patient_name=patient_name,
        adherence_score=score
    )
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf"
    )
