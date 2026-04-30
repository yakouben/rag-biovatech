import asyncio
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.services.gemini_service import get_gemini_service
from app.services.risk_service import get_risk_service
from app.services.rag_service import get_rag_service
from app.database.connection import get_database
from app.schemas import NOURRequest, EmbedRequest, NOURResponse
from app.routes.deps import verify_internal_api_key
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Reasoning"])

@router.post("/chat", summary="Main AI Chat with RAG")
async def ai_chat(request: NOURRequest) -> dict[str, Any]:
    gemini_service = get_gemini_service()
    risk_service = get_risk_service()
    rag_service = get_rag_service()

    if request.patient_data:
        patient_dict = request.patient_data.dict()
    else:
        # Fallback values for risk assessment if the frontend doesn't send them
        patient_dict = {
            "age": 50,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "fasting_glucose": 100,
            "bmi": 25.0,
            "smoking": False,
            "family_history": False,
            "comorbidities": 0
        }
        try:
            db = get_database()
            # Attempt to fetch age from profile
            profile = await db.get_patient_profile(request.patient_id)
            if profile and profile.get("age"):
                patient_dict["age"] = profile.get("age")
            
            # Attempt to fetch vitals from latest check-in
            result = db.client.table("patient_checkins").select("*").eq("patient_id", request.patient_id).order("checkin_date", desc=True).limit(1).execute()
            if result.data:
                latest = result.data[0]
                patient_dict["systolic_bp"] = latest.get("systolic_bp") or 120
                patient_dict["diastolic_bp"] = latest.get("diastolic_bp") or 80
                patient_dict["fasting_glucose"] = latest.get("fasting_glucose") or 100
        except Exception as e:
            logger.warning(f"Could not fetch patient history for AI chat: {e}")

    risk_assessment = await risk_service.assess_patient_risk(patient_dict)

    
    glossary_entries = []
    medical_knowledge = ""
    if request.include_glossary:
        glossary_entries = await rag_service.search_medical_terms(request.patient_symptoms, limit=5)
        medical_knowledge = await rag_service.get_medical_knowledge(request.patient_symptoms, limit=3)

    hela_response = await gemini_service.generate_hela_response(
        patient_symptoms=request.patient_symptoms,
        glossary_context=str(glossary_entries),
        risk_assessment=risk_assessment["category"]
    )
    
    entities = await gemini_service.extract_clinical_entities(request.patient_symptoms)

    return {
        "hela_response": hela_response,
        "extracted_entities": entities,
        "risk_score": risk_assessment["category"],
        "confidence": risk_assessment["probabilities"].get(risk_assessment["category"].lower(), 0.5),
        "thinking_steps": [
            "🔍 Searching medical glossary...",
            "📊 Running risk assessment...",
            "🧠 Generating clinical reasoning..."
        ]
    }
