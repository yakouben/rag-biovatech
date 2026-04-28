#!/usr/bin/env python3
"""
Update Darija terms in the glossary table with corrected versions.
Reads corrections from the provided mapping and updates the database.
"""

import os
import json
from supabase import create_client, Client

# Mapping of old (wrong) → new (correct) Darija terms
CORRECTIONS = {
    "شياط الدم": "الضغط / ضغط الدم طالع",
    "قصور الكلى": "الكلاوي راهي ما تخدمش مليح",
    "ضعف القلب": "القلب ضعيف",
    "ذبحة صدرية": "وجع في الصدر / ضيق في الصدر",
    "دقات القلب": "القلب راهو يضرب بزاف",
    "السعال": "كحة",
    "ضيق التنفس": "نخنق / ما نقدرش نتنفس مليح",
    "التهاب الشعب الهوائية": "برونشيت",
    "حموضة المعدة": "حريق المعدة",
    "الإمساك": "قبض",
    "السكتة الدماغية": "جلطة في الراس",
    "الصداع": "وجع الراس / راسي يوجعني",
    "تنميل الأطراف": "تنميل / يدي ولا رجلي ترقد",
    "قصور الغدة الدرقية": "الغدة ما تخدمش مليح",
    "فرط الغدة الدرقية": "الغدة تخدم بزاف",
    "التهاب المفاصل": "وجع المفاصل",
    "هشاشة العظام": "العظام ضعاف",
}

# Terms to update with alternatives (keep both options)
ALTERNATIVES = {
    "نسبة السكر": "نسبة السكر / السكر في الدم",
    "شحوم الدم": "الشحوم / الدهون في الدم",
    "الإسهال": "إسهال / الكرش راهي تجري",
}

def update_database():
    """Update glossary table with corrected Darija terms."""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY env vars required")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("🔄 Updating Darija terms in database...")
    
    # Track updates
    total_updates = 0
    failed_updates = []
    
    # Update corrections (wrong → correct)
    print(f"\n📝 Processing {len(CORRECTIONS)} corrections...")
    for old_term, new_term in CORRECTIONS.items():
        try:
            response = supabase.table("medical_glossary").update(
                {"darija_term": new_term}
            ).eq("darija_term", old_term).execute()
            
            if response.data:
                count = len(response.data)
                print(f"  ✅ '{old_term}' → '{new_term}' ({count} rows)")
                total_updates += count
            else:
                print(f"  ⚠️  No rows found for '{old_term}'")
        except Exception as e:
            print(f"  ❌ Error updating '{old_term}': {str(e)}")
            failed_updates.append((old_term, str(e)))
    
    # Update alternatives (keep both options)
    print(f"\n📝 Processing {len(ALTERNATIVES)} alternatives...")
    for old_term, new_term in ALTERNATIVES.items():
        try:
            response = supabase.table("medical_glossary").update(
                {"darija_term": new_term}
            ).eq("darija_term", old_term).execute()
            
            if response.data:
                count = len(response.data)
                print(f"  ✅ '{old_term}' → '{new_term}' ({count} rows)")
                total_updates += count
            else:
                print(f"  ⚠️  No rows found for '{old_term}'")
        except Exception as e:
            print(f"  ❌ Error updating '{old_term}': {str(e)}")
            failed_updates.append((old_term, str(e)))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✨ Update Complete!")
    print(f"{'='*60}")
    print(f"Total rows updated: {total_updates}")
    if failed_updates:
        print(f"Failed updates: {len(failed_updates)}")
        for term, error in failed_updates:
            print(f"  - {term}: {error}")
    else:
        print(f"✅ All updates successful!")
    
    return total_updates, failed_updates


if __name__ == "__main__":
    try:
        total_updates, failed_updates = update_database()
        exit(0 if not failed_updates else 1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        exit(1)
