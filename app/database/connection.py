"""
Database connection manager for ChronicCare.
Handles Supabase connection with pgvector support.
"""
from typing import Any, Optional

from supabase import Client, create_client

from app.config import get_settings
from app.utils.exceptions import DatabaseError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    _instance: Optional["DatabaseManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "DatabaseManager":
        """Singleton pattern for database manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize database connection."""
        if not self._client:
            self._connect()

    def _connect(self) -> None:
        """Establish connection to Supabase."""
        settings = get_settings()
        try:
            self._client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            raise DatabaseError(
                "Failed to initialize database connection",
                details={"error": str(e)},
            )

    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if self._client is None:
            self._connect()
        return self._client

    async def execute_query(
        self, query: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Execute a SQL query using Supabase."""
        try:
            # Use RPC for custom SQL queries
            result = self.client.rpc(query, params or {}).execute()
            return result.data if hasattr(result, "data") else result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseError(
                f"Query execution failed: {str(e)}",
                details={"query": query, "params": params},
            )

    async def get_glossary_by_id(self, glossary_id: int) -> dict[str, Any]:
        """Fetch a single glossary entry by ID."""
        try:
            result = (
                self.client.table("medical_glossary")
                .select("*")
                .eq("id", glossary_id)
                .single()
                .execute()
            )
            return result.data if hasattr(result, "data") else {}
        except Exception as e:
            logger.error(f"Failed to fetch glossary entry: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch glossary entry {glossary_id}",
                details={"error": str(e)},
            )

    async def search_glossary_by_embedding(
        self, embedding: list[float], limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search glossary using vector similarity."""
        try:
            # Supabase uses RPC for pgvector similarity search
            result = self.client.rpc(
                "search_glossary_embedding",
                {
                    "query_embedding": embedding,
                    "match_count": limit,
                    "similarity_threshold": 0.3,
                },
            ).execute()
            return result.data if hasattr(result, "data") else []
        except Exception as e:
            logger.error(f"Embedding search failed: {str(e)}")
            raise DatabaseError(
                "Embedding search failed",
                details={"error": str(e)},
            )

    async def save_patient_assessment(
        self, 
        patient_id: str, 
        assessment_data: dict[str, Any],
        entities: dict[str, Any],
        glossary_terms: list[str] = None
    ) -> dict[str, Any]:
        """
        Save patient assessment and clinical entities to Supabase.
        
        Args:
            patient_id: Unique patient identifier
            assessment_data: Risk assessment results
            entities: Extracted clinical entities
            glossary_terms: List of darija terms matched
            
        Returns:
            Saved record
        """
        try:
            from datetime import datetime
            record = {
                "patient_id": patient_id,
                "predicted_risk_level": assessment_data.get("risk_level"),
                "risk_score": assessment_data.get("risk_score"),
                "confidence": assessment_data.get("confidence"),
                "symptoms": entities.get("clinical_note", ""),
                "glossary_terms_used": glossary_terms or [],
                "clinical_entities": entities,  # We'll assume this column exists or will be added
                "assessment_date": datetime.utcnow().isoformat(),
            }
            
            result = self.client.table("patient_assessments").insert(record).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to save patient assessment: {str(e)}")
            # Don't raise here to avoid breaking the user response, just log it
            return {}

    async def close(self) -> None:
        """Close database connection."""
        self._client = None
        logger.info("Database connection closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
