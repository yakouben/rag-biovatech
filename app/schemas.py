"""
Pydantic schemas for request/response validation.
Ensures type safety and proper API contracts.
"""
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field, validator


class PatientData(BaseModel):
    """Patient health metrics."""

    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    systolic_bp: int = Field(..., ge=60, le=250, description="Systolic blood pressure")
    diastolic_bp: int = Field(..., ge=30, le=150, description="Diastolic blood pressure")
    fasting_glucose: int = Field(..., ge=40, le=500, description="Fasting glucose in mg/dL")
    bmi: float = Field(..., ge=10, le=60, description="Body mass index")
    smoking: bool = Field(False, description="Current smoking status")
    family_history: bool = Field(False, description="Family history of chronic disease")
    comorbidities: int = Field(0, ge=0, le=10, description="Number of comorbidities")

    class Config:
        json_json_schema_extra = {
            "example": {
                "age": 52,
                "systolic_bp": 145,
                "diastolic_bp": 90,
                "fasting_glucose": 150,
                "bmi": 28.5,
                "smoking": False,
                "family_history": True,
                "comorbidities": 1,
            }
        }

class ClinicalEntities(BaseModel):
    """Extracted clinical entities from patient text."""

    symptoms: List[str] = Field(default_factory=list, description="List of symptoms mentioned")
    medications: List[str] = Field(default_factory=list, description="List of medications mentioned")
    missed_medications: List[str] = Field(default_factory=list, description="List of missed medications mentioned")
    vitals: Dict[str, Optional[float]] = Field(default_factory=dict, description="Extracted vitals like BP or glucose")
    severity_hints: List[str] = Field(default_factory=list, description="Keywords indicating severity")
    clinical_note: str = Field(..., description="Short summarized clinical note")

    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["chest pain", "shortness of breath"],
                "medications": ["Amlodipine"],
                "missed_medications": ["Metformin"],
                "vitals": {"systolic_bp": 150, "glucose": 210},
                "severity_hints": ["severe", "crushing"],
                "clinical_note": "Patient reports severe chest pain and missed morning Metformin dose."
            }
        }



class EmbedRequest(BaseModel):
    """Request to generate embeddings."""

    text: str = Field(..., min_length=1, max_length=5000, description="Text to embed")

    class Config:
        json_json_schema_extra = {
            "example": {
                "text": "Patient experiencing severe chest pain and shortness of breath"
            }
        }


class EmbedResponse(BaseModel):
    """Embedding response."""

    text: str = Field(description="Original text")
    embedding: list[float] = Field(description="Text embedding vector")
    model: str = Field(description="Model used for embedding")
    dimensions: int = Field(description="Dimension of embedding vector")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Patient symptoms",
                "embedding": [0.1, 0.2, 0.3],
                "model": "gemini-1.5-flash",
                "dimensions": 768,
            }
        }


class GlossarySearchRequest(BaseModel):
    """Request for glossary search."""

    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
    language: str = Field("french", description="Search language")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "chest pain and difficulty breathing",
                "limit": 10,
                "language": "french",
            }
        }


class GlossaryEntry(BaseModel):
    """Medical glossary entry."""

    id: Optional[int] = Field(None, description="Entry ID")
    darija: str = Field(description="Darija term")
    french: str = Field(description="French translation")
    english: str = Field(description="English translation")
    category: str = Field(description="Medical category")

    class Config:
        json_schema_extra = {
            "example": {
                "darija": "السكري",
                "french": "Diabète",
                "english": "Diabetes",
                "category": "endocrine",
            }
        }


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment."""

    patient_data: PatientData = Field(description="Patient health metrics")
    patient_symptoms: Optional[str] = Field(None, description="Patient symptom description")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_data": {
                    "age": 52,
                    "systolic_bp": 145,
                    "diastolic_bp": 90,
                    "fasting_glucose": 150,
                    "bmi": 28.5,
                    "smoking": False,
                    "family_history": True,
                    "comorbidities": 1,
                },
                "patient_symptoms": "Fatigue and frequent urination",
            }
        }


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""

    risk_level: int = Field(description="Risk level (0=low, 1=moderate, 2=high)")
    risk_score: float = Field(description="Risk score 0-10")
    category: str = Field(description="Risk category")
    probabilities: dict[str, float] = Field(description="Probability distribution")
    recommendations: list[str] = Field(description="Clinical recommendations")
    monitoring_frequency: str = Field(description="Recommended monitoring frequency")

    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": 1,
                "risk_score": 5.2,
                "category": "MODERATE",
                "probabilities": {
                    "low": 0.2,
                    "moderate": 0.65,
                    "high": 0.15,
                },
                "recommendations": [
                    "Semi-annual clinical review",
                    "Optimize blood pressure control",
                ],
                "monitoring_frequency": "Every 3-6 months",
            }
        }


class NOURRequest(BaseModel):
    """Request for NOUR clinical reasoning."""

    patient_symptoms: str = Field(..., min_length=10, description="Patient symptoms description")
    patient_data: PatientData = Field(description="Patient health metrics")
    include_glossary: bool = Field(True, description="Include glossary context")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_symptoms": "Severe fatigue, frequent urination, blurred vision",
                "patient_data": {
                    "age": 45,
                    "systolic_bp": 130,
                    "diastolic_bp": 80,
                    "fasting_glucose": 200,
                    "bmi": 26,
                    "smoking": False,
                    "family_history": True,
                    "comorbidities": 0,
                },
                "include_glossary": True,
            }
        }


class NOURResponse(BaseModel):
    """NOUR response."""

    clinical_assessment: str = Field(description="Clinical assessment from NOUR")
    risk_assessment: RiskAssessmentResponse = Field(description="Risk assessment")
    recommendations: list[str] = Field(description="Clinical recommendations")
    extracted_entities: Optional[ClinicalEntities] = Field(None, description="Extracted clinical entities")
    glossary_context: list[GlossaryEntry] = Field(description="Relevant glossary entries")

    class Config:
        json_schema_extra = {
            "example": {
                "clinical_assessment": "Patient presents with classic diabetes symptoms...",
                "risk_assessment": {
                    "risk_level": 2,
                    "risk_score": 7.5,
                    "category": "HIGH",
                    "probabilities": {
                        "low": 0.1,
                        "moderate": 0.25,
                        "high": 0.65,
                    },
                    "recommendations": [
                        "Urgent endocrinology consultation",
                    ],
                    "monitoring_frequency": "Monthly or more frequently",
                },
                "recommendations": ["Urgent clinical evaluation"],
                "glossary_context": [],
            }
        }


class DriftDetectionResponse(BaseModel):
    """Model drift detection response."""

    drift_detected: bool = Field(description="Whether drift was detected")
    accuracy_drift: float = Field(description="Accuracy degradation value")
    recent_accuracy: float = Field(description="Recent model accuracy")
    baseline_accuracy: float = Field(description="Baseline accuracy")
    predictions_analyzed: int = Field(description="Number of predictions analyzed")
    recommendation: str = Field(description="Recommended action")

    class Config:
        json_schema_extra = {
            "example": {
                "drift_detected": False,
                "accuracy_drift": 0.02,
                "recent_accuracy": 0.88,
                "baseline_accuracy": 0.9,
                "predictions_analyzed": 100,
                "recommendation": "Model performance is stable. Continue monitoring.",
            }
        }


class PredictionRecord(BaseModel):
    """Record of a prediction for monitoring."""

    predicted_risk: str = Field(description="Predicted risk category")
    actual_risk: str = Field(description="Actual/verified risk category")
    confidence: float = Field(ge=0, le=1, description="Model confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_risk": "MODERATE",
                "actual_risk": "HIGH",
                "confidence": 0.72,
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Current timestamp")
    services: dict[str, str] = Field(description="Status of each service")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "database": "connected",
                    "gemini": "initialized",
                    "model": "loaded",
                },
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""

    status_code: int = Field(description="HTTP status code")
    error_code: str = Field(description="Application error code")
    message: str = Field(description="Error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 400,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid patient data",
                "details": {"field": "age", "reason": "must be positive"},
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }

class DoctorChatRequest(BaseModel):
    """Request for doctor to chat with patient history."""
    patient_id: str = Field(..., description="Unique patient identifier")
    question: str = Field(..., description="Doctor's clinical question")
    include_raw_history: bool = Field(False, description="Whether to include raw history in response")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "p123",
                "question": "How many times did the patient miss Metformin this month?",
                "include_raw_history": False
            }
        }
