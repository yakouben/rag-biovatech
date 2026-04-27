"""
Gemini AI Service for ChronicCare.
Handles embeddings and NOUR reasoning with proper error handling.
"""
import asyncio
from typing import Any

import google.generativeai as genai

from app.config import get_settings
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
            genai.configure(api_key=settings.gemini_api_key)
            self.embedding_model = settings.gemini_embedding_model
            self.generation_model = settings.gemini_model
            self._initialized = True
            logger.info("Gemini service initialized")

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for text using Gemini.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        try:
            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT",
                ),
            )
            return embedding["embedding"]
        except Exception as e:
            logger.error(f"Embedding failed for text: {str(e)}")
            raise EmbeddingError(
                f"Failed to generate embedding: {str(e)}",
                details={"text_length": len(text)},
            )

    async def generate_nour_response(
        self,
        patient_symptoms: str,
        glossary_context: str,
        risk_assessment: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate NOUR (Nurturing Outcomes Using Reasoning) response.
        This is the core clinical reasoning engine.

        Args:
            patient_symptoms: Description of patient symptoms in Darija/French
            glossary_context: Relevant medical terms from glossary
            risk_assessment: Risk level assessment from decision tree
            temperature: Model temperature for response variation

        Returns:
            Clinical reasoning response with recommendations

        Raises:
            GeminiError: If generation fails
        """
        try:
            prompt = self._build_nour_prompt(
                patient_symptoms, glossary_context, risk_assessment
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: genai.GenerativeModel(self.generation_model).generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
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
        except GeminiError:
            raise
        except Exception as e:
            logger.error(f"NOUR generation failed: {str(e)}")
            raise GeminiError(
                f"Failed to generate NOUR response: {str(e)}",
                details={
                    "symptoms_length": len(patient_symptoms),
                    "has_context": bool(glossary_context),
                    "risk_level": risk_assessment,
                },
            )

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

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If any embedding fails
        """
        if not texts:
            return []

        try:
            embeddings = []
            # Process in batches to avoid rate limiting
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = await asyncio.gather(
                    *[self.embed_text(text) for text in batch],
                    return_exceptions=False,
                )
                embeddings.extend(batch_embeddings)
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            raise EmbeddingError(
                f"Failed to generate batch embeddings: {str(e)}",
                details={"batch_size": len(texts)},
            )


# Global service instance
_gemini_service: "GeminiService | None" = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
