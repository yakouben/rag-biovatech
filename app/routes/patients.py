from fastapi import APIRouter, Query, HTTPException
from app.database.connection import get_database
from app.services.drift_service import get_drift_service
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/patient", tags=["Patient Data"])

@router.get("/{patient_id}/history")
async def get_patient_history(patient_id: str, days: int = Query(30, ge=1, le=90)):
    db = get_database()
    result = db.client.table("patient_assessments").select("*").eq("patient_id", patient_id).limit(days).execute()
    return {"patient_id": patient_id, "history": result.data}

@router.get("/{patient_id}/check-drift")
async def check_patient_drift(patient_id: str):
    drift_service = get_drift_service()
    return await drift_service.analyze_adherence_proactively(patient_id)

@router.get("/{patient_id}/profile")
async def get_patient_profile(patient_id: str):
    """Fetches the detailed profile including family contact info."""
    db = get_database()
    profile = await db.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile
