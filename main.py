"""
Backend module for UK Property Search application.
Contains API calls, data processing, and search logic.
"""

import requests
import random
from UKAreas import UK_AREAS

# API Config
API_URL = "https://api.scansan.com/v1/area_codes/search"
API_KEY = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"
HEADERS = {
    "X-Auth-Token": API_KEY,
    "Content-Type": "application/json"
}


# API functions
def fetch_area_data(area_name: str = None, gbr_district: str = None, gbr_street: str = None) -> dict | None:
    """
    Fetch data from the ScanSan API.
    
    Parameters:
        area_name: Area name to search (e.g., "Hammersmith")
        gbr_district: District code (e.g., "SW1A")
        gbr_street: Street name (e.g., "Downing Street")
    
    Returns:
        API response as dict, or None if request fails
    """
    params = {}
    
    if area_name:
        params = {"area_name": area_name}
    elif gbr_district and gbr_street:
        params = {"gbr_district": gbr_district, "gbr_street": gbr_street}
    
    if not params:
        return None
    
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


# =============================================================================
# Property Data (Mock Database)
# =============================================================================
AREA_PROPERTIES = {
    "London": [
        {"address": "42 Baker Street, W1U 3BW", "area": "London", "score": 85, "price": 850000},
        {"address": "15 Abbey Road, NW8 9AY", "area": "London", "score": 78, "price": 720000},
        {"address": "221B Baker Street, NW1 6XE", "area": "London", "score": 92, "price": 1200000},
    ],
    "Manchester": [
        {"address": "12 Deansgate, M3 2BY", "area": "Manchester", "score": 73, "price": 450000},
        {"address": "88 Oxford Road, M1 5NH", "area": "Manchester", "score": 68, "price": 380000},
        {"address": "5 Piccadilly, M1 1RG", "area": "Manchester", "score": 81, "price": 520000},
    ],
    "Birmingham": [
        {"address": "34 New Street, B2 4RH", "area": "Birmingham", "score": 70, "price": 320000},
        {"address": "19 Broad Street, B1 2HF", "area": "Birmingham", "score": 65, "price": 290000},
        {"address": "7 Corporation Street, B4 6QB", "area": "Birmingham", "score": 77, "price": 410000},
    ],
    "Leeds": [
        {"address": "25 Briggate, LS1 6HD", "area": "Leeds", "score": 74, "price": 340000},
        {"address": "10 The Headrow, LS1 8TL", "area": "Leeds", "score": 69, "price": 295000},
        {"address": "18 Park Row, LS1 5HN", "area": "Leeds", "score": 80, "price": 420000},
    ],
    "Glasgow": [
        {"address": "45 Buchanan Street, G1 3HL", "area": "Glasgow", "score": 76, "price": 310000},
        {"address": "8 Sauchiehall Street, G2 3JD", "area": "Glasgow", "score": 71, "price": 275000},
        {"address": "22 George Square, G2 1DS", "area": "Glasgow", "score": 83, "price": 480000},
    ],
    "Edinburgh": [
        {"address": "101 Princes Street, EH2 3AA", "area": "Edinburgh", "score": 88, "price": 650000},
        {"address": "12 Royal Mile, EH1 1TB", "area": "Edinburgh", "score": 90, "price": 780000},
        {"address": "7 Grassmarket, EH1 2HS", "area": "Edinburgh", "score": 79, "price": 520000},
    ],
    "Bristol": [
        {"address": "33 Park Street, BS1 5NH", "area": "Bristol", "score": 75, "price": 385000},
        {"address": "14 Clifton Down, BS8 3LT", "area": "Bristol", "score": 82, "price": 490000},
        {"address": "9 Whiteladies Road, BS8 2PH", "area": "Bristol", "score": 72, "price": 355000},
    ],
    "Liverpool": [
        {"address": "21 Bold Street, L1 4DJ", "area": "Liverpool", "score": 73, "price": 285000},
        {"address": "16 Lime Street, L1 1JQ", "area": "Liverpool", "score": 68, "price": 240000},
        {"address": "5 Hope Street, L1 9BQ", "area": "Liverpool", "score": 80, "price": 365000},
    ],
    "Cardiff": [
        {"address": "18 Queen Street, CF10 2BU", "area": "Cardiff", "score": 74, "price": 295000},
        {"address": "7 St Mary Street, CF10 1AT", "area": "Cardiff", "score": 69, "price": 260000},
        {"address": "25 Cathedral Road, CF11 9LL", "area": "Cardiff", "score": 81, "price": 420000},
    ],
    "Belfast": [
        {"address": "12 Royal Avenue, BT1 1DA", "area": "Belfast", "score": 72, "price": 245000},
        {"address": "8 Donegall Place, BT1 5AJ", "area": "Belfast", "score": 67, "price": 215000},
        {"address": "31 Botanic Avenue, BT7 1JG", "area": "Belfast", "score": 78, "price": 310000},
    ],
}


# =============================================================================
# Search Functions
# =============================================================================
def search_properties(area: str, query: str = "") -> list[dict]:
    """
    Search for properties in a given area.
    
    Parameters:
        area: The UK area to search in
        query: Optional search query (postcode, street name, etc.)
    
    Returns:
        List of property dictionaries
    """
    # Get properties for the selected area
    if area in AREA_PROPERTIES:
        properties = AREA_PROPERTIES[area].copy()
    elif area in ["Anywhere in the UK", "Any", ""]:
        # Mix properties from all areas
        all_properties = []
        for city_props in AREA_PROPERTIES.values():
            all_properties.extend(city_props)
        properties = random.sample(all_properties, min(5, len(all_properties)))
    else:
        # Try to fetch from API for areas not in mock database
        api_data = fetch_area_data(area_name=area)
        if api_data:
            # Process API response into property format
            properties = process_api_response(api_data, area)
        else:
            # Generate placeholder properties
            properties = generate_placeholder_properties(area)
    
    # Filter by search query if provided
    if query:
        q = query.strip().lower()
        properties = [p for p in properties if q in p.get("address", "").lower()]
    
    return properties


def process_api_response(api_data: dict, area: str) -> list[dict]:
    """
    Process API response into property format.
    
    Parameters:
        api_data: Raw API response
        area: Area name
    
    Returns:
        List of property dictionaries
    """
    properties = []
    
    # Handle different API response formats
    if isinstance(api_data, list):
        for item in api_data[:5]:  # Limit to 5 results
            properties.append({
                "address": item.get("address", f"Property in {area}"),
                "area": area,
                "score": item.get("sustainability_score", random.randint(60, 90)),
                "price": item.get("price", random.randint(200000, 800000)),
            })
    elif isinstance(api_data, dict):
        # Single result or nested structure
        if "results" in api_data:
            return process_api_response(api_data["results"], area)
        properties.append({
            "address": api_data.get("address", f"Property in {area}"),
            "area": area,
            "score": api_data.get("sustainability_score", random.randint(60, 90)),
            "price": api_data.get("price", random.randint(200000, 800000)),
        })
    
    return properties if properties else generate_placeholder_properties(area)


def generate_placeholder_properties(area: str, count: int = 3) -> list[dict]:
    """
    Generate placeholder properties for areas without data.
    
    Parameters:
        area: Area name
        count: Number of properties to generate
    
    Returns:
        List of property dictionaries
    """
    street_names = ["High Street", "Church Road", "Station Road", "Victoria Road", 
                    "Park Avenue", "Queens Road", "Kings Lane", "Mill Lane"]
    
    # son :sob:
    properties = []
    for i in range(count):
        properties.append({
            "address": f"{random.randint(1, 150)} {random.choice(street_names)}",
            "area": area,
            "score": random.randint(55, 90),
            "price": random.randint(200000, 600000),
        })
    
    return properties


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
        return "#28a745"  # Green
    elif score >= 60:
        return "#ffc107"  # Yellow
    elif score >= 40:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red


# =============================================================================
# Test / Debug
# =============================================================================
if __name__ == "__main__":
    # Test the functions
    print("Testing backend functions...")
    
    # Test API fetch
    print("\n1. Testing API fetch for 'Hammersmith':")
    result = fetch_area_data(area_name="Hammersmith")
    print(f"   Result: {result}")
    
    # Test property search
    print("\n2. Testing property search for 'London':")
    properties = search_properties("London")
    for p in properties:
        print(f"   - {p['address']} | Score: {p['score']}")
    
    # Test with query
    print("\n3. Testing search with query 'baker':")
    properties = search_properties("London", "baker")
    for p in properties:
        print(f"   - {p['address']}")
    
    print("\nBackend tests complete!")