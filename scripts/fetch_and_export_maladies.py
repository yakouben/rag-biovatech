#!/usr/bin/env python3
"""
Fetch all medical maladies from Supabase and export as JSON for editing.
"""
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    sys.exit(1)

def export_maladies():
    """Fetch all maladies from medical_glossary table and export as JSON."""
    
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Fetch all records from medical_glossary table
        print("[v0] Fetching maladies from medical_glossary table...")
        response = supabase.table("medical_glossary").select("*").execute()
        
        if not response.data:
            print("WARNING: No maladies found in database")
            maladies = []
        else:
            maladies = response.data
            print(f"[v0] Successfully fetched {len(maladies)} maladies")
        
        # Format for export
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(maladies),
            "maladies": []
        }
        
        for malady in maladies:
            export_data["maladies"].append({
                "id": malady.get("id"),
                "darija_term": malady.get("darija_term", ""),
                "french_term": malady.get("french_term", ""),
                "english_term": malady.get("english_term", ""),
                "category": malady.get("category", ""),
                "severity": malady.get("severity", 1),
                "description": malady.get("description", ""),
                "related_terms": malady.get("related_terms", []),
                # Don't export embedding vector
            })
        
        # Save to JSON file
        output_file = "/vercel/share/v0-project/maladies_export.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"[v0] Successfully exported {len(maladies)} maladies to {output_file}")
        
        # Print first few entries as preview
        print("\n[v0] PREVIEW - First 3 maladies:")
        print(json.dumps(export_data["maladies"][:3], ensure_ascii=False, indent=2))
        
        return output_file
    
    except Exception as e:
        print(f"ERROR: Failed to export maladies: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    export_maladies()
