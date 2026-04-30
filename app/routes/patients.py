from fastapi import APIRouter, Query, HTTPException
from app.database.connection import get_database
from app.services.drift_service import get_drift_service
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/patients", tags=["Patient Data"])

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

@router.post("/check-in")
async def patient_check_in(data: dict):
    """Patient daily health check-in."""
    db = get_database()
    try:
        # Save to check-ins table
        result = db.client.table("patient_checkins").upsert(data).execute()
        
        # Also save to assessments table for risk tracking if vitals exist
        if any(k in data.get("vitals", {}) for k in ["fasting_glucose", "systolic_bp"]):
            assessment_record = {
                "patient_id": data["patient_id"],
                "symptoms": data.get("symptoms", ""),
                "risk_score": data.get("risk_score", 0),
                "assessment_date": data.get("checkin_date")
            }
            db.client.table("patient_assessments").insert(assessment_record).execute()
            
        return {"status": "success", "data": result.data[0] if result.data else {}}
    except Exception as e:
        logger.error(f"Check-in failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}/prescriptions")
async def get_patient_prescriptions(patient_id: str):
    """Fetch active prescriptions for a patient."""
    db = get_database()
    result = db.client.table("prescriptions").select("*, prescription_medications(*)").eq("patient_id", patient_id).eq("is_active", True).execute()
    return result.data

@router.post("/{patient_id}/prescriptions")
async def add_patient_prescription(patient_id: str, data: dict):
    """Add a new prescription with medications."""
    db = get_database()
    try:
        # 1. Create prescription header
        header = {
            "patient_id": patient_id,
            "doctor_notes": data.get("doctor_notes", ""),
            "is_active": True
        }
        res_h = db.client.table("prescriptions").insert(header).execute()
        pres_id = res_h.data[0]["id"]
        
        # 2. Add medications
        meds = data.get("medications", [])
        for med in meds:
            med["prescription_id"] = pres_id
            
        if meds:
            db.client.table("prescription_medications").insert(meds).execute()
            
        return {"status": "success", "prescription_id": pres_id}
    except Exception as e:
        logger.error(f"Failed to add prescription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medications/catalog")
async def get_medications_catalog():
    """Returns the static medication catalog JSON."""
    import json
    import os
    catalog_path = "/Users/yakoub/BIOVATECH-V2/rag-biovatech/data/medications_catalog.json"
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r') as f:
            return json.load(f)
    return []
