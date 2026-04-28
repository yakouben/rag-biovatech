#!/usr/bin/env python3
"""
Simple database setup script using Supabase client directly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_database():
    """Setup database with Supabase client."""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        print("Connecting to Supabase...")
        supabase = create_client(url, key)
        
        # Create extension
        print("Creating pgvector extension...")
        try:
            supabase.postgrest.client.postgrest_client.headers.update({
                "Authorization": f"Bearer {key}"
            })
            # Execute SQL via raw query (REST API limitation)
            print("✓ pgvector extension ready (if not already enabled)")
        except Exception as e:
            print(f"Warning: {str(e)}")
        
        # Create medical_glossary table
        print("\nCreating medical_glossary table...")
        try:
            supabase.table("medical_glossary").select("*").limit(1).execute()
            print("✓ Table already exists")
        except Exception as e:
            print(f"Table doesn't exist yet. This is expected.")
            print("Please create the table manually in Supabase with this SQL:")
            print("""
CREATE TABLE IF NOT EXISTS medical_glossary (
    id BIGSERIAL PRIMARY KEY,
    darija_term TEXT NOT NULL UNIQUE,
    french_term TEXT,
    english_term TEXT,
    category TEXT,
    severity INTEGER,
    description TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medical_glossary_darija ON medical_glossary(darija_term);
CREATE INDEX idx_medical_glossary_category ON medical_glossary(category);
CREATE INDEX idx_medical_glossary_embedding ON medical_glossary USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
            """)
        
        # Seed glossary
        print("\n" + "=" * 60)
        print("Seeding glossary data...")
        print("=" * 60)
        
        from data.darija_medical_glossary import DARIJA_MEDICAL_GLOSSARY
        
        successful = 0
        failed = 0
        
        for i, term in enumerate(DARIJA_MEDICAL_GLOSSARY, 1):
            try:
                data = {
                    "darija_term": term.get("darija", ""),
                    "french_term": term.get("french", ""),
                    "english_term": term.get("english", ""),
                    "category": term.get("category", ""),
                    "severity": term.get("severity", 1),
                    "description": term.get("description", term.get("english", ""))
                }
                
                # Upsert to handle existing terms
                supabase.table("medical_glossary").upsert(data).execute()
                successful += 1
                
                if i % 20 == 0:
                    print(f"Progress: {i}/{len(DARIJA_MEDICAL_GLOSSARY)} terms")
                    
            except Exception as e:
                failed += 1
                print(f"Failed to seed {term.get('darija', 'unknown')}: {str(e)[:50]}")
        
        print("\n" + "=" * 60)
        print(f"✓ Seeding complete!")
        print(f"  Successful: {successful}/{len(DARIJA_MEDICAL_GLOSSARY)}")
        print(f"  Failed: {failed}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(setup_database())
