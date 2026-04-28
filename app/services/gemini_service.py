"""
Gemini AI Service for ChronicCare.
Handles embeddings and NOUR reasoning with proper error handling.
Using the latest google-genai SDK.
"""
import asyncio
import json
from typing import Any, Optional

import google.genai as genai
from google.genai import types

from app.config import get_settings
from app.schemas import ClinicalEntities
from app.utils.exceptions import EmbeddingError, GeminiError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    _instance: "GeminiService | None" = None

    def __new__(cls) -> "GeminiService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize Gemini service."""
        if not self._initialized:
            settings = get_settings()
            # Initialize the new SDK client
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.embedding_model = settings.gemini_embedding_model
            self.generation_model = settings.gemini_model
            self._initialized = True
            logger.info("Gemini service initialized (using google-genai SDK)")

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for text using Gemini.
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                ),
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding failed for text: {str(e)}")
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    async def generate_nour_response(
        self,
        patient_symptoms: str,
        glossary_context: str,
        risk_assessment: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate NOUR (Nurturing Outcomes Using Reasoning) response.
        """
        try:
            prompt = self._build_nour_prompt(
                patient_symptoms, glossary_context, risk_assessment
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.generation_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=1024,
                    ),
                ),
            )

            if not response.text:
                raise GeminiError("Empty response from model")

            return response.text
        except Exception as e:
            logger.error(f"NOUR generation failed: {str(e)}")
            raise GeminiError(f"Failed to generate NOUR response: {str(e)}")

    def _build_nour_prompt(
        self, symptoms: str, glossary_context: str, risk_assessment: str
    ) -> str:
        """Build the NOUR clinical reasoning prompt."""
        return f"""You are NOUR, a specialized clinical reasoning engine for chronic disease management in Algeria.

PATIENT PRESENTATION:
{symptoms}

MEDICAL CONTEXT (Darija Medical Glossary):
{glossary_context if glossary_context else "No specific glossary matches"}

RISK ASSESSMENT:
{risk_assessment}

INSTRUCTIONS:
1. Provide clinical reasoning based on the patient's symptoms
2. Reference relevant medical terms from the glossary when applicable
3. Consider the risk assessment in your recommendations
4. Provide actionable next steps for the healthcare provider
5. Be concise and structured in your response
6. Prioritize patient safety and evidence-based practice

Please provide:
- Clinical Assessment
- Relevant Differential Diagnoses
- Recommended Actions
- Monitoring Recommendations
- Red Flags to Watch For"""

    async def extract_clinical_entities(self, text: str) -> ClinicalEntities:
        """
        Extract structured clinical entities from patient text.
        """
        try:
            prompt = f"""Extract clinical entities from the following patient description.
You MUST return a JSON object with the following structure:
{{
  "symptoms": ["list", "of", "symptoms"],
  "medications": ["list", "of", "meds"],
  "missed_medications": ["list", "of", "missed", "meds"],
  "vitals": {{"systolic_bp": null, "diastolic_bp": null, "glucose": null, "bmi": null}},
  "severity_hints": ["high", "severe", "urgent"],
  "clinical_note": "A short 1-sentence summary"
}}

The text may be in Algerian Darija, French, or English.
PATIENT TEXT:
"{text}"
"""
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.generation_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            )

            data = json.loads(response.text)
            return ClinicalEntities(**data)
        except Exception as e:
            logger.warning(f"Entity extraction failed: {str(e)}")
            return ClinicalEntities(clinical_note="Extraction failed")

    async def generate_nurture_notification(self, patient_name: str = "Khalti/Ammi") -> str:
        """Generate a warm, caring nurture notification in Algerian Darija."""
        prompt = f"""You are Nour, a kind and respectful Algerian clinical companion. 
Generate a short, warm check-in message in Algerian Darija for {patient_name} who hasn't recorded their medication in 3 days.
Use very respectful terms like 'Khalti' or 'Ammi'.
Sound like a concerned daughter or a kind nurse.
The goal is to check in on them and remind them of their medication.
KEEP IT IN DARIJA ONLY. NO FRENCH, NO ENGLISH."""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.generation_model,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Nurture generation failed: {str(e)}")
            return "Khalti/Ammi, labess? Maranich nchoufek f Nour had liyam. Matنسaych dwa dialek, sahtek hiya el sah."

    async def generate_doctor_answer(self, question: str, history_context: str) -> str:
        """Answer a doctor's question based on patient clinical history."""
        prompt = f"""You are a clinical assistant analyzing a patient's history for a doctor.
QUESTION: {question}

PATIENT HISTORY CONTEXT:
{history_context}

INSTRUCTIONS:
1. Answer the doctor's question precisely based ONLY on the provided history.
2. Highlight any trends (e.g., increasing BP, missed meds).
3. If the data doesn't contain the answer, say so clearly.
4. Maintain a professional, clinical tone.
"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.generation_model,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Doctor chat failed: {str(e)}")
            return "Unable to analyze history at this time."

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        """
        if not texts:
            return []

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=texts,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )
            )
            return [item.values for item in response.embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")


# Global service instance
_gemini_service: "GeminiService | None" = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
