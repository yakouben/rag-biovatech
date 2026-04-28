#!/usr/bin/env python3
"""
Seed script for glossary data.
Populates medical_glossary table with Darija medical terms.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.darija_medical_glossary import DARIJA_GLOSSARY
from app.database.connection import get_database
from app.services.gemini_service import get_gemini_service
from app.utils.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


async def seed_glossary_terms() -> int:
    """
    Seed glossary terms with embeddings.
    
    Returns:
        Number of terms seeded
    """
    db = get_database()
    gemini = get_gemini_service()
    count = 0
    
    logger.info(f"Seeding {len(DARIJA_GLOSSARY)} glossary terms...")
    
    for i, term in enumerate(DARIJA_GLOSSARY, 1):
        try:
            # Generate embedding for the Darija term
            darija = term["darija_term"]
            description = term.get("description", darija)
            
            logger.info(f"Processing ({i}/{len(DARIJA_GLOSSARY)}): {darija}")
            
            # Get embedding
            embedding = await gemini.embed_text(description)
            
            # Insert into database
            insert_sql = """
                INSERT INTO medical_glossary 
                (darija_term, french_term, english_term, category, severity, 
                 description, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (darija_term) DO UPDATE
                SET french_term = EXCLUDED.french_term,
                    english_term = EXCLUDED.english_term,
                    embedding = EXCLUDED.embedding
            """
            
            await db.execute(
                insert_sql,
                (
                    darija,
                    term.get("french_term", ""),
                    term.get("english_term", ""),
                    term.get("category", ""),
                    term.get("severity", 1),
                    description,
                    embedding
                )
            )
            
            count += 1
            
            if i % 10 == 0:
                logger.info(f"  Progress: {i}/{len(DARIJA_GLOSSARY)} terms seeded")
                
        except Exception as e:
            logger.warning(f"Failed to seed term {term.get('darija_term')}: {str(e)}")
    
    logger.info(f"✓ Successfully seeded {count} glossary terms")
    return count


async def main():
    """Main seed runner."""
    try:
        logger.info("=" * 60)
        logger.info("Seeding ChronicCare Glossary")
        logger.info("=" * 60)
        
        count = await seed_glossary_terms()
        
        logger.info("=" * 60)
        logger.info(f"✓ Glossary seeding completed! ({count} terms)")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
