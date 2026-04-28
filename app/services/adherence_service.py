"""
Medication Adherence Service for ChronicCare.
Calculates adherence scores based on clinical entity extraction from Nour interactions.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List
import json

from app.database.connection import get_database
from app.utils.logging import get_logger

logger = get_logger(__name__)

class AdherenceService:
    """Service to calculate patient medication adherence."""

    def __init__(self):
        self.db = get_database()

    async def calculate_adherence(self, patient_id: str, days: int = 30) -> float:
        """
        Calculates the adherence percentage for a flexible number of days.
        Adherence = (interactions without missed meds) / (total interactions where meds were discussed)
        
        Args:
            patient_id: Unique patient identifier
            days: Number of days to look back
            
        Returns:
            Adherence score (0.0 to 1.0)
        """
        try:
            # Query assessments from the last X days
            lookback_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            result = (
                self.db.client.table("patient_assessments")
                .select("clinical_entities")
                .eq("patient_id", patient_id)
                .gte("assessment_date", lookback_date)
                .execute()
            )
            
            assessments = result.data if hasattr(result, "data") else []
            
            if not assessments:
                return 1.0  # Default to perfect adherence if no data (or maybe 0.0?)
            
            total_med_discussions = 0
            taken_med_discussions = 0
            
            for assessment in assessments:
                entities = assessment.get("clinical_entities", {})
                if isinstance(entities, str):
                    entities = json.loads(entities)
                
                meds = entities.get("medications", [])
                missed = entities.get("missed_medications", [])
                
                # If either list is non-empty, meds were discussed
                if meds or missed:
                    total_med_discussions += 1
                    # If nothing was missed in this specific interaction
                    if not missed:
                        taken_med_discussions += 1
            
            if total_med_discussions == 0:
                return 1.0 # No data about meds
                
            adherence_rate = taken_med_discussions / total_med_discussions
            logger.info(f"Adherence for {patient_id}: {adherence_rate:.2f} ({taken_med_discussions}/{total_med_discussions})")
            return adherence_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate adherence for {patient_id}: {str(e)}")
            return 0.0

# Global service instance
_adherence_service: "AdherenceService | None" = None

def get_adherence_service() -> AdherenceService:
    """Get or create adherence service instance."""
    global _adherence_service
    if _adherence_service is None:
        _adherence_service = AdherenceService()
    return _adherence_service
