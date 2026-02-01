"""
Backend module for UK Property Search application.
Contains API calls, data processing, and search logic.
"""

import re # regular expressions
from scansan_client import get_search, get_summary, get_sale_history, get_current_valuations, get_historical_valuations
from config import API_KEY, HEADERS, UK_AREAS

# API Config
def parse_api_search_response(api_response: dict) -> dict:
    """
    Parse the API search response to extract useful data.
    
    API Response format:
    {
        "search_query": "Brixton",
        "search_found": "ward",
        "response_time": "2.05",
        "data": [
            [
                {
                    "area_code": {
                        "area_code_district": "string",
                        "area_code_count": 1,
                        "area_code_list": ["string"]
                    },
                    "borough": ["string"],
                    "ward": ["string"],
                    "street": {
                        "street_count": 1,
                        "street_list": ["string"]
                    }
                }
            ]
        ]
    }
    
    Returns:
        Parsed data with area_codes, boroughs, wards, streets
    """
    if not api_response:
        return None
    
    # handle case where api_response is not a dict
    if not isinstance(api_response, dict):
        return None
    
    result = {
        "search_query": api_response.get("search_query", ""),
        "search_found": api_response.get("search_found", ""),
        "area_codes": [],
        "boroughs": [],
        "wards": [],
        "streets": [],
        "postcodes": []
    }
    
    data = api_response.get("data", [])
    
    # ensure data is a list
    if not isinstance(data, list):
        return result
    
    try:
        for outer_item in data:
            if isinstance(outer_item, list):
                items = outer_item
            elif isinstance(outer_item, dict):
                # fallback if not nested
                items = [outer_item]
            else:
                continue
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                    
                # extract area codes
                area_code_info = item.get("area_code", {})
                if area_code_info and isinstance(area_code_info, dict):
                    area_code_list = area_code_info.get("area_code_list", [])
                    if isinstance(area_code_list, list):
                        result["area_codes"].extend(area_code_list)
                    
                    district = area_code_info.get("area_code_district")
                    if district:
                        result["postcodes"].append(district)
                
                # boroughs
                boroughs = item.get("borough", [])
                if boroughs and isinstance(boroughs, list):
                    result["boroughs"].extend(boroughs)
                
                # wards
                wards = item.get("ward", [])
                if wards and isinstance(wards, list):
                    result["wards"].extend(wards)
                
                # streets
                street_info = item.get("street", {})
                if street_info and isinstance(street_info, dict):
                    street_list = street_info.get("street_list", [])
                    if street_list and isinstance(street_list, list):
                        result["streets"].extend(street_list)
    except Exception:
        pass
    
    return result

def search_properties_from_api(area: str, query: str = "", postcode_district: str = "", street: str = "") -> list[dict]:
    """
    Search for properties using the real API.
    
    Valid parameter combinations:
    1. area_name only (place name like 'Brixton', 'Aberdeen')
    2. gbr_district AND gbr_street (e.g., 'SW1A' + 'Downing Street')
    
    Parameters:
        area: The UK area to search in (used as area_name)
        query: Optional search query (used as area_name if no district/street)
        postcode_district: Postcode district (e.g., 'SW1A', 'NG8', 'SS0')
        street: Street name within the postcode district
    
    Returns:
        List of property dictionaries with addresses and area codes
    """
    properties = []
    api_response = None
    
    # determine search method based on provided parameters
    if postcode_district and street:
        # postcode district + street
        api_response = get_search(gbr_district=postcode_district.strip().upper(), gbr_street=street.strip())
    elif query:
        # area name
        api_response = get_search(area_name=query.strip())
    elif area and area not in ["Anywhere in the UK", "Any", ""]:
        # +selected area name
        api_response = get_search(area_name=area.strip())
    
    if not api_response:
        return []
    
    parsed = parse_api_search_response(api_response)
    
    if not parsed:
        return []
    
    area_codes = parsed.get("area_codes", []) # get codes
    boroughs = parsed.get("boroughs", [])
    wards = parsed.get("wards", [])
    
    # property valuations for each area code
    for area_code in area_codes[:6]:  # up to 6
        valuations = get_current_valuations(area_code=area_code)
        
        if valuations and isinstance(valuations, dict):
            valuation_data = valuations.get("data", [])
            
            for val in valuation_data[:3]:  # up to 3
                property_address = val.get("property_address", f"Property in {area_code}")
                bounded_valuation = val.get("bounded_valuation", [])
                last_sold_price = val.get("last_sold_price")
                last_sold_date = val.get("last_sold_date", "")
                
                current_price = None
                if bounded_valuation and len(bounded_valuation) > 0:
                    if len(bounded_valuation) >= 2:
                        current_price = (bounded_valuation[0] + bounded_valuation[-1]) // 2
                    else:
                        current_price = bounded_valuation[0]
                elif last_sold_price:
                    current_price = last_sold_price
                
                properties.append({
                    "address": property_address,
                    "postcode": area_code,
                    "area": boroughs[0] if boroughs else (wards[0] if wards else area),
                    "current_price": current_price,
                    "future_price": None,  # for catboost
                    "last_sold_price": last_sold_price,
                    "last_sold_date": last_sold_date,
                    "score": None,  # for catboost
                })
    
    return properties

# search func
def search_properties(area: str, query: str = "", postcode_district: str = "", street: str = "") -> list[dict]:
    """
    Search for properties in a given area using the API.
    
    Valid search methods:
    1. area_name only - use 'area' or 'query' parameter
    2. postcode_district + street - must provide BOTH
    
    Parameters:
        area: The UK area to search in
        query: Optional search query (place name)
        postcode_district: Postcode district (e.g., 'SW1A')
        street: Street name (required if postcode_district is provided)
    
    Returns:
        List of property dictionaries
    """
    try:
        properties = search_properties_from_api(area, query, postcode_district, street)
        return properties
    except Exception:
        return []


# helper functions
def get_uk_areas() -> list[str]:
    """
    Get list of UK areas for the dropdown.
    
    Returns:
        List of UK area names
    """
    return UK_AREAS

def get_sustainability_label(score: int) -> str:
    """
    Get sustainability label based on score.
    
    Parameters:
        score: Sustainability score (0-100)
    
    Returns:
        Label string
    """
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    else:
        return "Poor"

def get_sustainability_color(score: int) -> str:
    """
    Get color code based on sustainability score.
    
    Parameters:
        score: Sustainability score (0-100)
    
    Returns:
        Hex color code
    """
    if score >= 80:
        return "#28a745"  
    elif score >= 60:
        return "#ffc107"  
    elif score >= 40:
        return "#fd7e14"  
    else:
        return "#dc3545"  

def is_full_postcode(text: str) -> bool:
    """
    Check if input looks like a full UK postcode (e.g., SS0 0BW, NG8 1BB).
    
    Parameters:
        text: Input string to check
    
    Returns:
        True if text matches full postcode pattern, False otherwise
    """
    # UK postcode pattern: 1-2 letters, 1-2 digits, optional letter, space, digit, 2 letters
    pattern = r'^[A-Za-z]{1,2}\d{1,2}[A-Za-z]?\s+\d[A-Za-z]{2}$'
    return bool(re.match(pattern, text.strip()))

def sort_properties(properties: list, sort_option: str) -> list:
    """
    Sort properties based on the selected sort option.
    
    Parameters:
        properties: List of property dictionaries
        sort_option: One of:
            - "Default"
            - "Current Price: Low to High"
            - "Current Price: High to Low"
            - "Future Price: Low to High"
            - "Future Price: High to Low"
    
    Returns:
        Sorted list of properties
    """
    if not properties:
        return properties
    
    sorted_results = properties.copy()
    
    if sort_option == "Default":
        # In default view, show properties with current price first, N/A at the bottom
        sorted_results = sorted(properties, key=lambda x: (x.get("current_price") is None, 0))
    elif sort_option == "Current Price: Low to High":
        sorted_results = sorted(properties, key=lambda x: x.get("current_price") or float('inf'))
    elif sort_option == "Current Price: High to Low":
        sorted_results = sorted(properties, key=lambda x: x.get("current_price") or 0, reverse=True)
    elif sort_option == "Future Price: Low to High":
        sorted_results = sorted(properties, key=lambda x: x.get("future_price") or float('inf'))
    elif sort_option == "Future Price: High to Low":
        sorted_results = sorted(properties, key=lambda x: x.get("future_price") or 0, reverse=True)
    
    return sorted_results

def validate_search_input(query: str, postcode_district: str, street_name: str) -> str | None:
    """
    Validate search input parameters.
    
    Parameters:
        query: The main search query
        postcode_district: Postcode district for advanced search
        street_name: Street name for advanced search
    
    Returns:
        Error message string if validation fails, None if valid
    """
    # Check if user entered a full postcode in query field
    if query and is_full_postcode(query):
        return ("Full postcodes (e.g., 'SS0 0BW', 'NG8 1BB') are not supported.\n\n"
                "Please use either:\n"
                "• Area name (e.g., 'Brixton', 'Aberdeen')\n"
                "• Postcode District + Street (e.g., 'SW1A' + 'Downing Street')")
    
    # Check if only one of district/street is provided (need both)
    if (postcode_district and not street_name) or (street_name and not postcode_district):
        return "To search by street, you must provide BOTH the postcode district AND street name."
    
    return None

# DEBUG
if __name__ == "__main__":
    # function testing
    print("Testing backend functions...")
    
    # api testing
    print("\n1. Testing API fetch for 'Brixton':")
    result = get_search(area_name="Brixton")
    print(f"   Result: {result}")
    
    # parse testing
    if result:
        print("\n2. Parsing API response:")
        parsed = parse_api_search_response(result)
        print(f"   Area codes: {parsed.get('area_codes', [])[:5]}")
        print(f"   Boroughs: {parsed.get('boroughs', [])}")
        print(f"   Wards: {parsed.get('wards', [])}")
    
    # API property search testing
    print("\n3. Testing property search for 'Brixton':")
    properties = search_properties("Brixton")
    for p in properties[:3]:
        print(f"   - {p.get('address')} | Price: £{p.get('current_price', 'N/A')}")
    
