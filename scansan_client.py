import requests as rq
import pandas as pd
from config import SEARCH_URL, SUMMARY_URL, SALE_HISTORY_URL, CURRENT_VALUATIONS_URL, HISTORICAL_VALUATIONS_URL, HEADERS

# helper method - TODO: UPDATE
def check_http_status(response):
    try:
        response.raise_for_status()
        print(f"Success!")
        return True
    except rq.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False
    # error 429
    except rq.exceptions.TooManyRedirects as e:
        print(f"Error: {e}")
        return False

# route methods for API
def get_search(area_name=None, gbr_district=None, gbr_street=None):
    """
    INPUTS:
    (area_name) OR (gbr_district AND gbr_street)

    area_name: string
    gbr_district: string (e.g. SW1A)
    gbr_street: string (e.g. Downing Street)

    OUTPUTS:
    data: JSON
    None (if invalid input)
    """

    params = None

    # type 1
    if (area_name is not None):
        params = {"area_name": area_name}

    # type 2
    elif (gbr_district is not None and gbr_street is not None):
        params = {"gbr_district": gbr_district, "gbr_street": gbr_street}
    
    if (params is None):
        return None

    response = rq.get(url=SEARCH_URL, params=params, headers=HEADERS)

    # check HTTP status before parsing JSON
    if (not check_http_status(response=response)):
        return None
        
    return response.json()

# summary
def get_summary(area_code=None, area_code_district=None):
    """
    INPUTS:
    area_code
    area_code | area_code_district

    DATA:
    total_properties: int
    sold_price_range_in_last_5yrs: int
    current_valuation_range: int
    current_rent_listings: int
    current_sale_listings: int

    OUTPUTS:
    Response: JSON
    None (if invalid input)
    """

    # NULL check
    if (area_code is None):
        return None

    url = SUMMARY_URL.format(area_code=area_code)
    params = {}

    if (area_code is not None):
        params["area_code"] = area_code
    
    if (area_code_district is not None):
        params["area_code_district"] = area_code_district

    response = rq.get(url=url, params=params, headers=HEADERS)

    if (not check_http_status(response=response)):
        return None

    return response.json()

# history
def get_sale_history(area_code_postal=None, area_code=None):
    """
    INPUTS:
    area_code_postal: str (e.g. NW1 0BH)
    area_code: str (e.g. SE255NF)
    
    DATA:

    
    OUTPUTS:
    Response: JSON
    None (if invalid input)
    """

    if (area_code_postal is None and area_code is None):
        return None

    url = SALE_HISTORY_URL.format(area_code=area_code if (area_code is not None) else area_code_postal)
    params = {}

    if (area_code_postal is not None):
        params["area_code_postal"] = area_code_postal
    
    elif (area_code is not None):
        params["area_code"] = area_code
    
    response = rq.get(url=url, params=params, headers=HEADERS)

    if (not check_http_status(response=response)):
        return None
    
    return response.json()

# helper functions for nirmal
def get_current_valuations(area_code_postal=None, area_code=None):
    """
    "property_address": "string",
    "last_sold_price": 1,
    "last_sold_date": "string",
    "lower_outlier": true,
    "upper_outlier": true,
    "bounded_valuation": [1]
    """
    # NULL check
    if (area_code_postal is None and area_code is None):
        return None
    
    url = CURRENT_VALUATIONS_URL.format(area_code=area_code if (area_code is not None) else area_code_postal)
    params = {}

    if (area_code_postal is not None):
        params["area_code_postal"] = area_code_postal

    elif (area_code is not None):
        params["area_code"] = area_code
    
    response = rq.get(url=url, params=params, headers=HEADERS)

    if (not check_http_status(response=response)):
        return None

    return response.json()

def get_historical_valuations(area_code_postal=None, area_code=None):
    """
    "property_address": "string",
    "valuations": [
    {
        "date": "2026-01-31",
        "valuation": 1
    }]
    """

    # NULL check
    if (area_code_postal is None and area_code is None):
        return None
    
    url = HISTORICAL_VALUATIONS_URL.format(area_code=area_code if (area_code is not None) else area_code_postal)
    params = {}

    if (area_code_postal is not None):
        params["area_code_postal"] = area_code_postal
    
    elif (area_code is not None):
        params["area_code"] = area_code

    response = rq.get(url=url, params=params, headers=HEADERS)

    if (not check_http_status(response)):
        return None
    
    return response.json()

def get_historical_valuation_frame(area_code_postal=None, area_code=None, property_address=None):
    """
    Uses get_historical_valuations() and returns a DataFrame with columns:
    ['date', 'price'] (ready for your plot function)
    """
    resp = get_historical_valuations(area_code_postal=area_code_postal, area_code=area_code)
    if not resp:
        return pd.DataFrame(columns=["date", "price"])

    # Many APIs wrap results in {"data": [...]}
    if isinstance(resp, dict) and isinstance(resp.get("data"), list) and resp["data"]:
        props = resp["data"]
    else:
        # Or return a single property object
        props = [resp] if isinstance(resp, dict) else []

    if not props:
        return pd.DataFrame(columns=["date", "price"])

    # If multiple properties returned, select one
    chosen = None
    if property_address:
        for p in props:
            addr = p.get("property_address") or p.get("address")
            if addr == property_address:
                chosen = p
                break
    if chosen is None:
        chosen = props[0]

    vals = chosen.get("valuations") or []
    df = pd.DataFrame([{"date": v.get("date"), "price": v.get("valuation")} for v in vals])

    if df.empty:
        return pd.DataFrame(columns=["date", "price"])

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna().sort_values("date")
    return df[["date", "price"]]
