#!/usr/bin/env python3
"""
Export all medical glossary terms (maladies) from Supabase to JSON.
This allows editing translations in real Darija.
"""

import json
import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a database connection to Supabase."""
    return psycopg2.connect(
        host=os.getenv("SUPABASE_DB_HOST"),
        port=int(os.getenv("SUPABASE_DB_PORT", 5432)),
        database=os.getenv("SUPABASE_DB_NAME"),
        user=os.getenv("SUPABASE_DB_USER"),
        password=os.getenv("SUPABASE_DB_PASSWORD"),
        sslmode="require"
    )

def export_glossary_to_json() -> list[dict[str, Any]]:
    """
    Fetch all medical glossary terms from the database.
    Returns list of maladies with their current translations.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch all glossary terms, excluding embeddings (too large)
        cur.execute("""
            SELECT 
                id,
                darija_term,
                french_term,
                english_term,
                category,
                severity,
                description,
                related_terms,
                created_at
            FROM medical_glossary
            ORDER BY category ASC, darija_term ASC
        """)

        glossary_terms = cur.fetchall()
        cur.close()
        conn.close()

        # Convert to list of dicts
        maladies = []
        for term in glossary_terms:
            maladies.append({
                "id": term["id"],
                "darija_term": term["darija_term"],
                "french_term": term["french_term"],
                "english_term": term["english_term"],
                "category": term["category"],
                "severity": term["severity"],
                "description": term["description"],
                "related_terms": term["related_terms"] or [],
                "created_at": term["created_at"].isoformat() if term["created_at"] else None
            })

        return maladies

    except Exception as e:
        print(f"Error fetching glossary: {e}")
        raise

def save_to_json(maladies: list[dict[str, Any]], filename: str = "maladies.json"):
    """Save maladies to a JSON file for editing."""
    output_path = f"/vercel/share/v0-project/{filename}"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(maladies, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(maladies)} medical terms to {filename}")
    print(f"File location: {output_path}")
    return output_path

def main():
    """Main function to export glossary."""
    print("Fetching maladies from Supabase...")
    maladies = export_glossary_to_json()
    
    if maladies:
        print(f"Found {len(maladies)} terms in medical glossary")
        save_to_json(maladies)
        
        # Print summary by category
        categories = {}
        for malady in maladies:
            cat = malady["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nBreakdown by category:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} terms")
    else:
        print("No glossary terms found in database")

if __name__ == "__main__":
    main()
