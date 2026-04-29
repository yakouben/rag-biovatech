import os
import json
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.connection import get_database
from app.services.gemini_service import get_gemini_service
from app.utils.logging import get_logger

logger = get_logger(__name__)

async def ingest_medical_knowledge():
    """Ingest medical knowledge from JSON into Supabase."""
    knowledge_file = Path(__file__).parent.parent / "data" / "medical_knowledge_mvp.json"
    
    if not knowledge_file.exists():
        logger.error(f"Knowledge file not found: {knowledge_file}")
        return

    with open(knowledge_file, "r") as f:
        knowledge_items = json.load(f)

    db = get_database()
    gemini = get_gemini_service()

    logger.info(f"Starting ingestion of {len(knowledge_items)} items...")

    # Clear existing knowledge for a clean start
    try:
        db.client.table("medical_knowledge").delete().neq("id", 0).execute()
        logger.info("Cleared existing medical knowledge.")
    except Exception as e:
        logger.warning(f"Failed to clear table: {e}")

    for item in knowledge_items:
        try:
            # Combine title and content for embedding
            text_to_embed = f"{item['title']}: {item['content']}"
            embedding = await gemini.embed_text(text_to_embed)

            record = {
                "category": item["category"],
                "title": item["title"],
                "content": item["content"],
                "source": item.get("source", ""),
                "embedding": embedding
            }

            # Insert into database
            db.client.table("medical_knowledge").insert(record).execute()
            logger.info(f"✓ Ingested: {item['title']}")
        except Exception as e:
            logger.error(f"Failed to ingest {item['title']}: {str(e)}")

    logger.info("Ingestion complete!")

if __name__ == "__main__":
    asyncio.run(ingest_medical_knowledge())
