"""
Script to seed the medical glossary into Supabase.
This populates the glossary table with embeddings.
"""
import asyncio
import os
import sys

import google.generativeai as genai
from supabase import create_client

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.darija_medical_glossary import DARIJA_MEDICAL_GLOSSARY


async def get_embedding(text: str, client: genai.GenerativeAI) -> list[float]:
    """Generate embedding for text."""
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT",
        )
        return result["embedding"]
    except Exception as e:
        print(f"Error embedding '{text[:50]}...': {str(e)}")
        return [0.0] * 768  # Return zero vector as fallback


async def seed_glossary() -> None:
    """Seed medical glossary into Supabase."""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not all([supabase_url, supabase_key, gemini_api_key]):
        print("Error: Missing required environment variables")
        print("Required: SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY")
        sys.exit(1)

    # Initialize clients
    supabase = create_client(supabase_url, supabase_key)
    genai.configure(api_key=gemini_api_key)

    print(f"Seeding {len(DARIJA_MEDICAL_GLOSSARY)} glossary entries...")

    # Process entries
    success_count = 0
    error_count = 0

    for i, entry in enumerate(DARIJA_MEDICAL_GLOSSARY, 1):
        try:
            # Generate embedding for Darija term
            embedding = await get_embedding(entry["darija"], genai)

            # Prepare data for insertion
            data = {
                "darija": entry["darija"],
                "french": entry["french"],
                "english": entry["english"],
                "category": entry["category"],
                "embedding": embedding,
            }

            # Insert into Supabase
            response = (
                supabase.table("medical_glossary")
                .insert(data)
                .execute()
            )

            if response.data:
                success_count += 1
                if i % 10 == 0:
                    print(f"  Seeded {i}/{len(DARIJA_MEDICAL_GLOSSARY)} entries...")
            else:
                error_count += 1
                print(f"  Error seeding entry {i}: {entry['darija']}")

        except Exception as e:
            error_count += 1
            print(f"  Error processing entry {i}: {str(e)}")

    print("\n" + "=" * 60)
    print(f"Seeding Complete!")
    print(f"  Successfully seeded: {success_count}")
    print(f"  Errors: {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_glossary())
