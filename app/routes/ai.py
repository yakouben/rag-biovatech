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
async def ai_chat(request: NOURRequest, x_internal_key: str = Header(None)) -> dict[str, Any]:
    verify_internal_api_key(x_internal_key)
    gemini_service = get_gemini_service()
    risk_service = get_risk_service()
    rag_service = get_rag_service()

    risk_assessment = await risk_service.assess_patient_risk(request.patient_data.dict())
    
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
