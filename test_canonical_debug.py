import sys
sys.path.append('/home/user/webapp')

from app.services.context_storage import context_storage

# Test with the user's context
context_id = "116801010001230045"
frozen_context = context_storage.get_frozen_context(context_id)

if frozen_context:
    canonical_summary = frozen_context.get("canonical_summary", {})
    
    print("\n" + "="*80)
    print("CANONICAL_SUMMARY STRUCTURE FOR:", context_id)
    print("="*80)
    
    for module_id in ["M2", "M3", "M4", "M5", "M6"]:
        print(f"\n{module_id}:")
        module_data = canonical_summary.get(module_id, {})
        if module_data:
            summary = module_data.get("summary", {})
            if summary:
                print(f"  summary keys: {list(summary.keys())}")
                for key, val in summary.items():
                    print(f"    {key}: {val}")
            else:
                print(f"  summary: MISSING")
        else:
            print(f"  MISSING")
else:
    print(f"Context {context_id} not found")
