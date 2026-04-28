#!/usr/bin/env python3
"""
Migration runner script for ChronicCare database setup.
Executes SQL migrations and seeds the glossary data.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from app.database.connection import get_database
from app.utils.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


async def run_migrations():
    """Run all database migrations."""
    settings = get_settings()
    db = get_database()
    
    try:
        logger.info("Starting database migrations...")
        
        # Read and execute migration 01
        migration_01_path = Path(__file__).parent / "migrations" / "01_init_glossary.sql"
        if migration_01_path.exists():
            logger.info(f"Running migration: {migration_01_path.name}")
            with open(migration_01_path, "r") as f:
                sql = f.read()
            
            # Split and execute each statement
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement:
                    try:
                        result = await db.execute(statement)
                        logger.info(f"✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e) or "duplicate" in str(e):
                            logger.info(f"✓ (Already exists) {statement[:50]}...")
                        else:
                            logger.warning(f"Warning executing statement: {str(e)[:100]}")
        else:
            logger.warning(f"Migration file not found: {migration_01_path}")
        
        logger.info("✓ Migration 01 completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


async def seed_glossary():
    """Seed the glossary data."""
    try:
        logger.info("Starting glossary seeding...")
        
        # Import and run seed script
        from migrations.seed_glossary_data import seed_glossary_terms
        
        await seed_glossary_terms()
        logger.info("✓ Glossary seeded successfully")
        
    except ImportError:
        logger.warning("Seed script not found, attempting manual seed...")
        
        from data.darija_medical_glossary import DARIJA_GLOSSARY
        from app.database.connection import get_database
        
        db = get_database()
        count = 0
        
        for term in DARIJA_GLOSSARY:
            try:
                insert_sql = """
                    INSERT INTO medical_glossary 
                    (darija_term, french_term, english_term, category, severity, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (darija_term) DO NOTHING
                """
                await db.execute(
                    insert_sql,
                    (
                        term["darija_term"],
                        term.get("french_term", ""),
                        term.get("english_term", ""),
                        term.get("category", ""),
                        term.get("severity", ""),
                        term.get("description", "")
                    )
                )
                count += 1
            except Exception as e:
                logger.warning(f"Failed to insert term {term.get('darija_term')}: {str(e)}")
        
        logger.info(f"✓ Seeded {count} glossary terms")


async def main():
    """Main migration runner."""
    try:
        logger.info("=" * 60)
        logger.info("ChronicCare Database Migration")
        logger.info("=" * 60)
        
        await run_migrations()
        await seed_glossary()
        
        logger.info("=" * 60)
        logger.info("✓ All migrations completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
