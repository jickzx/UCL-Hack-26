"""
Validate UK_AREAS list from config.py against the Scansan API.
Checks if each area is a valid search term for the dropdown list.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import UK_AREAS
from main import get_search
import json

def validate_areas():
    """
    Validate each UK area by checking if it returns valid results from the API.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": [],
        "invalid": [],
        "error": []
    }
    
    total = len(UK_AREAS)
    
    print(f"Validating {total} UK areas...")
    print("-" * 60)
    
    for idx, area in enumerate(UK_AREAS, 1):
        try:
            response = get_search(area_name=area)
            
            if response is None:
                results["invalid"].append(area)
                print(f"[{idx}/{total}] ❌ {area:<30} - No response from API")
            elif isinstance(response, dict):
                search_found = response.get("search_found")
                if search_found:
                    results["valid"].append(area)
                    print(f"[{idx}/{total}] ✓ {area:<30} - Found ({search_found})")
                else:
                    results["invalid"].append(area)
                    print(f"[{idx}/{total}] ❌ {area:<30} - No results found")
            else:
                results["error"].append(area)
                print(f"[{idx}/{total}] ⚠ {area:<30} - Unexpected response type")
        
        except Exception as e:
            results["error"].append(area)
            print(f"[{idx}/{total}] ⚠ {area:<30} - Error: {str(e)[:40]}")
    
    return results


def print_summary(results):
    """Print validation summary."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"✓ Valid areas:   {len(results['valid'])}")
    print(f"❌ Invalid areas: {len(results['invalid'])}")
    print(f"⚠ Errors:        {len(results['error'])}")
    print("=" * 60)
    
    if results["invalid"]:
        print("\n❌ INVALID AREAS (should be removed from config):")
        for area in sorted(results["invalid"]):
            print(f"   - {area}")
    
    if results["error"]:
        print("\n⚠ AREAS WITH ERRORS (check connectivity):")
        for area in sorted(results["error"]):
            print(f"   - {area}")
    
    if results["valid"]:
        print(f"\n✓ All {len(results['valid'])} valid areas are suitable for dropdown")


if __name__ == "__main__":
    print("UK Areas Validation Tool")
    print("=" * 60)
    
    results = validate_areas()
    print_summary(results)
    
    # Export results to JSON
    with open("validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to validation_results.json")
