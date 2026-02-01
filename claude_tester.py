import json
from scansan_client import get_search, get_current_valuations

def test_api():
    print("=" * 50)
    print("TESTING SCANSAN API")
    print("=" * 50)
    
    # Test 1: Search for Brixton
    print("\n1. Testing search for 'Brixton'...")
    search_result = get_search(area_name="Brixton")
    
    if search_result is None:
        print("   ❌ FAILED - No response from API")
        return
    
    print(f"   ✅ Got response!")
    print(f"   Search found: {search_result.get('search_found')}")
    
    # Extract area codes
    data = search_result.get("data", [])
    area_codes = []
    
    for outer in data:
        if isinstance(outer, list):
            for item in outer:
                if isinstance(item, dict):
                    ac = item.get("area_code", {})
                    if ac:
                        area_codes.extend(ac.get("area_code_list", []))
    
    print(f"   Found {len(area_codes)} area codes")
    if area_codes:
        print(f"   First 5: {area_codes[:5]}")
    
    # Test 2: Get valuations for first area code
    if area_codes:
        test_code = area_codes[0]
        print(f"\n2. Testing valuations for '{test_code}'...")
        
        valuations = get_current_valuations(area_code=test_code)
        
        if valuations is None:
            print("   ❌ FAILED - No valuations returned")
        else:
            val_data = valuations.get("data", [])
            print(f"   ✅ Got {len(val_data)} properties!")
            
            if val_data:
                print("\n   Sample property:")
                prop = val_data[0]
                print(f"   - Address: {prop.get('property_address')}")
                print(f"   - Last Sold: £{prop.get('last_sold_price')} on {prop.get('last_sold_date')}")
                print(f"   - Valuation Range: {prop.get('bounded_valuation')}")
    
    print("\n" + "=" * 50)
    print("API TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_api()