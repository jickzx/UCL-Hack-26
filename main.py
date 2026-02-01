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
    
    # For each area code, try to get property valuations
    for area_code in area_codes[:6]:  # Limit to 6 for performance
        # Try to get current valuations for this postcode
        valuations = get_current_valuations(area_code=area_code)
        
        if valuations and isinstance(valuations, dict):
            valuation_data = valuations.get("data", [])
            
            for val in valuation_data[:3]:  # Limit properties per area code
                property_address = val.get("property_address", f"Property in {area_code}")
                bounded_valuation = val.get("bounded_valuation", [])
                last_sold_price = val.get("last_sold_price")
                last_sold_date = val.get("last_sold_date", "")
                
                # Calculate current price from bounded valuation
                current_price = None
                if bounded_valuation and len(bounded_valuation) > 0:
                    # Use average of bounded valuation range
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
                    "future_price": None,  # To be set by prediction model
                    "last_sold_price": last_sold_price,
                    "last_sold_date": last_sold_date,
                    "score": None,  # To be set by sustainability model
                })
    
    return properties

# search func
def search_properties(area: str, query: str = "", postcode_district: str = "", street: str = "") -> list[dict]:
    """
    Search for properties in a given area.
    First tries the real API, falls back to mock data if needed.
    
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
        # Try to get real data from API first
        properties = search_properties_from_api(area, query, postcode_district, street)
        
        if properties:
            return properties
    except Exception:
        # If API call fails, continue to mock data
        pass
    
    # fall back to mock data if API returns nothing or fails
    properties = []
    
    if area in AREA_PROPERTIES:
        properties = AREA_PROPERTIES[area].copy()
    elif area in ["Anywhere in the UK", "Any", ""]:
        # mix properties from all areas
        all_properties = []
        for city_props in AREA_PROPERTIES.values():
            all_properties.extend(city_props)
        properties = all_properties[:6]  # return first 6 properties
    
    # filter by search query if provided
    if query and properties:
        q = query.strip().lower()
        properties = [p for p in properties if q in p.get("address", "").lower()]
    
    return properties

# property Data (Mock Database - Fallback)
AREA_PROPERTIES = {
    "London": [
        {"address": "42 Baker Street, W1U 3BW", "area": "London", "score": 85, "current_price": 850000},
        {"address": "15 Abbey Road, NW8 9AY", "area": "London", "score": 78, "current_price": 720000},
        {"address": "221B Baker Street, NW1 6XE", "area": "London", "score": 92, "current_price": 1200000},
    ],
    "Manchester": [
        {"address": "12 Deansgate, M3 2BY", "area": "Manchester", "score": 73, "current_price": 450000},
        {"address": "88 Oxford Road, M1 5NH", "area": "Manchester", "score": 68, "current_price": 380000},
        {"address": "5 Piccadilly, M1 1RG", "area": "Manchester", "score": 81, "current_price": 520000},
    ],
    "Birmingham": [
        {"address": "34 New Street, B2 4RH", "area": "Birmingham", "score": 70, "current_price": 320000},
        {"address": "19 Broad Street, B1 2HF", "area": "Birmingham", "score": 65, "current_price": 290000},
        {"address": "7 Corporation Street, B4 6QB", "area": "Birmingham", "score": 77, "current_price": 410000},
    ],
    "Leeds": [
        {"address": "25 Briggate, LS1 6HD", "area": "Leeds", "score": 74, "current_price": 340000},
        {"address": "10 The Headrow, LS1 8TL", "area": "Leeds", "score": 69, "current_price": 295000},
        {"address": "18 Park Row, LS1 5HN", "area": "Leeds", "score": 80, "current_price": 420000},
    ],
    "Glasgow": [
        {"address": "45 Buchanan Street, G1 3HL", "area": "Glasgow", "score": 76, "current_price": 310000},
        {"address": "8 Sauchiehall Street, G2 3JD", "area": "Glasgow", "score": 71, "current_price": 275000},
        {"address": "22 George Square, G2 1DS", "area": "Glasgow", "score": 83, "current_price": 480000},
    ],
    "Edinburgh": [
        {"address": "101 Princes Street, EH2 3AA", "area": "Edinburgh", "score": 88, "current_price": 650000},
        {"address": "12 Royal Mile, EH1 1TB", "area": "Edinburgh", "score": 90, "current_price": 780000},
        {"address": "7 Grassmarket, EH1 2HS", "area": "Edinburgh", "score": 79, "current_price": 520000},
    ],
    "Bristol": [
        {"address": "33 Park Street, BS1 5NH", "area": "Bristol", "score": 75, "current_price": 385000},
        {"address": "14 Clifton Down, BS8 3LT", "area": "Bristol", "score": 82, "current_price": 490000},
        {"address": "9 Whiteladies Road, BS8 2PH", "area": "Bristol", "score": 72, "current_price": 355000},
    ],
    "Liverpool": [
        {"address": "21 Bold Street, L1 4DJ", "area": "Liverpool", "score": 73, "current_price": 285000},
        {"address": "16 Lime Street, L1 1JQ", "area": "Liverpool", "score": 68, "current_price": 240000},
        {"address": "5 Hope Street, L1 9BQ", "area": "Liverpool", "score": 80, "current_price": 365000},
    ],
    "Cardiff": [
        {"address": "18 Queen Street, CF10 2BU", "area": "Cardiff", "score": 74, "current_price": 295000},
        {"address": "7 St Mary Street, CF10 1AT", "area": "Cardiff", "score": 69, "current_price": 260000},
        {"address": "25 Cathedral Road, CF11 9LL", "area": "Cardiff", "score": 81, "current_price": 420000},
    ],
    "Belfast": [
        {"address": "12 Royal Avenue, BT1 1DA", "area": "Belfast", "score": 72, "current_price": 245000},
        {"address": "8 Donegall Place, BT1 5AJ", "area": "Belfast", "score": 67, "current_price": 215000},
        {"address": "31 Botanic Avenue, BT7 1JG", "area": "Belfast", "score": 78, "current_price": 310000},
    ],
}

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
    
    # testing mock data fallback
    print("\n4. Testing mock data for 'London':")
    properties = search_properties("London")
    for p in properties:
        print(f"   - {p['address']} | Price: £{p.get('current_price', 'N/A')}")
    
    print("\nBackend tests complete!")