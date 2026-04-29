"""
RAG (Retrieval-Augmented Generation) Service for ChronicCare.
Handles semantic search over the medical glossary using embeddings.
"""
from typing import Any

from app.database.connection import get_database
from app.services.gemini_service import get_gemini_service
from app.utils.exceptions import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RAGService:
    """Service for semantic search and retrieval augmented generation."""

    def __init__(self) -> None:
        """Initialize RAG service with dependencies."""
        self.db: Any = None  # Lazy-loaded
        self.gemini = get_gemini_service()
        self.similarity_threshold = 0.3

    def _get_db(self) -> Any:
        """Get database lazily."""
        if self.db is None:
            self.db = get_database()
        return self.db

    async def search_medical_terms(
        self,
        query: str,
        limit: int = 10,
        language: str = "french",
    ) -> list[dict[str, Any]]:
        """
        Search for relevant medical terms using semantic similarity.

        Args:
            query: Patient symptom or medical term description
            limit: Maximum number of results to return
            language: Language for search context (french, english, darija)

        Returns:
            List of relevant medical glossary entries

        Raises:
            ValidationError: If inputs are invalid
        """
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")

        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")

        try:
            # Generate embedding for the query
            query_embedding = await self.gemini.embed_text(query)

            # Search using vector similarity
            db = self._get_db()
            results = await db.search_glossary_by_embedding(
                query_embedding, limit=limit
            )

            logger.info(f"Found {len(results)} glossary matches for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Medical term search failed: {str(e)}")
            raise ValidationError(
                f"Failed to search medical terms: {str(e)}",
                details={"query": query},
            )

    async def build_glossary_context(
        self, medical_terms: list[str]
    ) -> str:
        """
        Build contextual information from medical terms.
        Enriches the context for NOUR reasoning.

        Args:
            medical_terms: List of medical terms to enrich

        Returns:
            Formatted glossary context string

        Raises:
            ValidationError: If inputs are invalid
        """
        if not medical_terms:
            return ""

        try:
            context_parts = []
            for term in medical_terms:
                # Search for the term in the glossary
                search_results = await self.search_medical_terms(
                    term, limit=1
                )
                if search_results:
                    entry = search_results[0]
                    context_parts.append(
                        f"• {entry.get('darija', term)} ({entry.get('french', '')}) - {entry.get('english', '')}"
                    )

            context = "\n".join(context_parts)
            logger.info(f"Built glossary context for {len(context_parts)} terms")
            return context
        except Exception as e:
            logger.error(f"Glossary context building failed: {str(e)}")
            raise ValidationError(
                f"Failed to build glossary context: {str(e)}",
                details={"term_count": len(medical_terms)},
            )

    async def semantic_search_with_fallback(
        self,
        query: str,
        fallback_language: str = "french",
    ) -> list[dict[str, Any]]:
        """
        Perform semantic search with fallback to keyword search.

        Args:
            query: Search query
            fallback_language: Language for fallback search

        Returns:
            List of relevant results

        Raises:
            ValidationError: If search completely fails
        """
        try:
            # Try semantic search first
            results = await self.search_medical_terms(query)
            if results:
                return results

            # Fallback: do simple keyword matching
            logger.warning(f"No semantic results for '{query}', using keyword fallback")
            from data.darija_medical_glossary import search_glossary

            fallback_results = search_glossary(query, fallback_language)
            return fallback_results[:10]
        except Exception as e:
            logger.error(f"Semantic search with fallback failed: {str(e)}")
            raise ValidationError(
                f"Search failed: {str(e)}",
                details={"query": query},
            )

    def get_context_summary(
        self, glossary_entries: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Generate a summary of the glossary context for the response.

        Args:
            glossary_entries: List of glossary entries

        Returns:
            Summary dictionary with key information

        Raises:
            ValidationError: If entries are invalid
        """
        if not glossary_entries:
            return {"total_entries": 0, "categories": [], "by_category": {}}

        categories = {}
        for entry in glossary_entries:
            category = entry.get("category", "uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(
                {
                    "darija": entry.get("darija"),
                    "french": entry.get("french"),
                    "english": entry.get("english"),
                }
            )

        return {
            "total_entries": len(glossary_entries),
            "categories": list(categories.keys()),
            "by_category": categories,
        }


    async def get_medical_knowledge(
        self,
        query: str,
        limit: int = 3,
    ) -> str:
        """
        Retrieve medical knowledge guidelines for a query.
        
        Args:
            query: Clinical query
            limit: Number of guidelines to retrieve
            
        Returns:
            Formatted knowledge string
        """
        try:
            query_embedding = await self.gemini.embed_text(query)
            db = self._get_db()
            results = await db.search_medical_knowledge(query_embedding, limit=limit)
            
            if not results:
                return "No specific medical guidelines found for this query."
            
            knowledge_parts = []
            for res in results:
                knowledge_parts.append(
                    f"Guideline [{res.get('category')}]: {res.get('title')} - {res.get('content')} (Source: {res.get('source')})"
                )
            
            return "\n\n".join(knowledge_parts)
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {str(e)}")
            return "Error retrieving medical guidelines."


# Global RAG service instance
_rag_service: "RAGService | None" = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
