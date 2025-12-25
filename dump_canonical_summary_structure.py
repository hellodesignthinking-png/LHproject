#!/usr/bin/env python3
"""
Canonical Summary Structure Dumper
===================================
Dumps the actual structure of canonical_summary from a real analysis
to understand what data is available for report generation.
"""

import requests
import json
from typing import Dict, Any

def extract_structure(data: Any, path: str = "", max_depth: int = 5) -> list:
    """Extract structure recursively"""
    results = []
    
    if max_depth == 0:
        return [f"{path} = <max depth reached>"]
    
    if data is None:
        results.append(f"{path} = None")
    elif isinstance(data, dict):
        if not data:
            results.append(f"{path} = {{}}")
        else:
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, (dict, list)):
                    results.extend(extract_structure(value, new_path, max_depth - 1))
                else:
                    value_type = type(value).__name__
                    if isinstance(value, str) and len(value) > 50:
                        value_preview = f"{value[:50]}..."
                    else:
                        value_preview = value
                    results.append(f"{new_path} = {value_preview} ({value_type})")
    elif isinstance(data, list):
        if not data:
            results.append(f"{path} = []")
        else:
            results.append(f"{path} = [list with {len(data)} items]")
            # Sample first item
            if data:
                results.extend(extract_structure(data[0], f"{path}[0]", max_depth - 1))
    else:
        value_type = type(data).__name__
        results.append(f"{path} = {data} ({value_type})")
    
    return results

def main():
    BASE_URL = "http://localhost:8005"
    CONTEXT_ID = "116801010001230045"
    
    print("="*80)
    print("CANONICAL SUMMARY STRUCTURE DUMP")
    print("="*80)
    print()
    
    # Try to get canonical summary through API
    print("🔍 Attempting to retrieve canonical_summary...")
    print()
    
    # Method 1: Check if there's a debug endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v4/analysis/{CONTEXT_ID}/canonical")
        if response.status_code == 200:
            canonical = response.json()
            print("✅ Retrieved canonical_summary via API")
            print()
            
            structure = extract_structure(canonical)
            
            print("📊 CANONICAL SUMMARY STRUCTURE")
            print("-"*80)
            for line in structure:
                print(line)
            
            # Save to file
            with open("/home/user/webapp/canonical_summary_structure.txt", "w") as f:
                f.write("CANONICAL SUMMARY STRUCTURE\n")
                f.write("="*80 + "\n\n")
                for line in structure:
                    f.write(line + "\n")
            
            print()
            print("✅ Structure saved to canonical_summary_structure.txt")
            
            # Also save raw JSON for reference
            with open("/home/user/webapp/canonical_summary_raw.json", "w") as f:
                json.dump(canonical, f, indent=2, ensure_ascii=False)
            
            print("✅ Raw data saved to canonical_summary_raw.json")
            
            return
    except Exception as e:
        print(f"⚠️  API method failed: {e}")
    
    # Method 2: Check database directly
    print()
    print("🔍 Attempting to retrieve from database...")
    print()
    
    try:
        import sys
        sys.path.insert(0, '/home/user/webapp')
        
        from app.database import SessionLocal
        from app.models.context_snapshot import ContextSnapshot
        
        db = SessionLocal()
        snapshot = db.query(ContextSnapshot).filter(
            ContextSnapshot.context_id == CONTEXT_ID
        ).first()
        
        if snapshot and snapshot.context_data:
            print("✅ Retrieved context from database")
            print()
            
            # Parse JSON context data
            context_data = json.loads(snapshot.context_data)
            canonical = context_data.get('canonical_summary') or context_data
            structure = extract_structure(canonical)
            
            print("📊 CANONICAL SUMMARY STRUCTURE")
            print("-"*80)
            for line in structure:
                print(line)
            
            # Save to file
            with open("/home/user/webapp/canonical_summary_structure.txt", "w") as f:
                f.write("CANONICAL SUMMARY STRUCTURE\n")
                f.write("="*80 + "\n\n")
                for line in structure:
                    f.write(line + "\n")
            
            print()
            print("✅ Structure saved to canonical_summary_structure.txt")
            
            # Also save raw JSON
            with open("/home/user/webapp/canonical_summary_raw.json", "w") as f:
                json.dump(canonical, f, indent=2, ensure_ascii=False)
            
            print("✅ Raw data saved to canonical_summary_raw.json")
            
            # Print module summary
            print()
            print("="*80)
            print("MODULE SUMMARY")
            print("="*80)
            
            for module_id in ["M2", "M3", "M4", "M5", "M6"]:
                if module_id in canonical:
                    module = canonical[module_id]
                    print(f"\n📦 {module_id}:")
                    if isinstance(module, dict):
                        print(f"   Keys: {', '.join(module.keys())}")
                        if 'summary' in module:
                            summary = module['summary']
                            if isinstance(summary, dict):
                                print(f"   Summary keys: {', '.join(summary.keys())}")
            
        else:
            print("❌ No context snapshot found in database")
        
        db.close()
        
    except Exception as e:
        print(f"⚠️  Database method failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print()
    print("1. Review canonical_summary_structure.txt")
    print("2. Identify available data fields for each module")
    print("3. Use this structure to write accurate report content")
    print()

if __name__ == "__main__":
    main()
