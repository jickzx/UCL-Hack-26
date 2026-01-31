import requests as rq
from flask import Flask
import pandas as pd

app = Flask(__name__)

# constants
PORT = 8000
HOST = "0.0.0.0"
AUTH_TOKEN = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"

# types of URLS
SEARCH_URL = "https://api.scansan.com/v1/area_codes/search"
SUMMARY_URL = """https://api.scansan.com/v1/area_codes/{area_code}/summary"""
SALE_HISTORY_URL = """https://api.scansan.com/v1/postcode/{area_code}/sale/history"""
CURRENT_VALUATIONS_URL = """https://api.scansan.com/v1/postcode/{area_code}/valuations/current"""
HISTORICAL_VALUATIONS_URL = """https://api.scansan.com/v1/postcode/{area_code}/valuations/historical"""


HEADERS = {
"X-Auth-Token": AUTH_TOKEN, # for authentication
"Content-Type": "application/json" # indicates request is JSON
}

# setup query params (LINK WITH FRONTEND)
"""
Valid Parameters: (area_name) OR (gbr_district AND gbr_street)

area_name: string
gbr_district: string (e.g. SW1A)
gbr_street: string (e.g. Downing Street)
"""

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


# helper methods - TODO: UPDATE
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


# params = {"area_name": "Hammersmith"}
# params = {"gbr_district": "SW1A", "gbr_street": "Downing Street"}

# data = response.json()
# print(data)

def test():
    UK_AREAS = [
    "Anywhere in the UK",

    "Aberdeen",
    "Aberdeenshire",
    "Anglesey",
    "Angus",
    "Antrim and Newtownabbey",
    "Ards and North Down",
    "Argyll and Bute",
    "Armagh City, Banbridge and Craigavon",

    "Bangor",
    "Barnet",
    "Bath",
    "Bedfordshire",
    "Belfast",
    "Berkshire",
    "Bexley",
    "Birmingham",
    "Blackburn",
    "Blackpool",
    "Blaenau Gwent",
    "Bolton",
    "Bournemouth",
    "Bracknell Forest",
    "Bradford",
    "Brent",
    "Bridgend",
    "Bristol",
    "Bromley",
    "Buckinghamshire",
    "Bury",

    "Caerphilly",
    "Cambridgeshire",
    "Cambridge",
    "Camden",
    "Cardiff",
    "Carmarthenshire",
    "Causeway Coast and Glens",
    "Ceredigion",
    "Cheshire",
    "Chelmsford",
    "Cheltenham",
    "Chester",
    "Clackmannanshire",
    "Colchester",
    "Conwy",
    "Cornwall",
    "Coventry",
    "Croydon",
    "Cumbria",

    "Darlington",
    "Denbighshire",
    "Derby",
    "Derbyshire",
    "Derry",
    "Devon",
    "Doncaster",
    "Dorset",
    "Dudley",
    "Dumfries and Galloway",
    "Dundee",
    "Durham",

    "Ealing",
    "East Ayrshire",
    "East Dunbartonshire",
    "East Lothian",
    "East Midlands",
    "East of England",
    "East Renfrewshire",
    "East Sussex",
    "Edinburgh",
    "Enfield",
    "England",
    "Essex",
    "Exeter",

    "Falkirk",
    "Fermanagh and Omagh",
    "Fife",
    "Flintshire",

    "Gateshead",
    "Glasgow",
    "Gloucester",
    "Gloucestershire",
    "Greater London",
    "Greater Manchester",
    "Greenwich",
    "Gwynedd",

    "Hackney",
    "Halifax",
    "Hammersmith and Fulham",
    "Hampshire",
    "Haringey",
    "Harrow",
    "Hartlepool",
    "Havering",
    "Hereford",
    "Herefordshire",
    "Hertfordshire",
    "Highland",
    "Hillingdon",
    "Hounslow",
    "Hove",
    "Huddersfield",

    "Inverness",
    "Ipswich",
    "Isle of Wight",
    "Islington",

    "Kensington and Chelsea",
    "Kent",
    "Kingston upon Thames",

    "Lambeth",
    "Lancashire",
    "Leeds",
    "Leicester",
    "Leicestershire",
    "Lewisham",
    "Lincolnshire",
    "Lisburn",
    "Liverpool",
    "London",
    "Luton",

    "Manchester",
    "Medway",
    "Merseyside",
    "Merthyr Tydfil",
    "Midlothian",
    "Milton Keynes",
    "Monmouthshire",
    "Moray",
    "Merton",
    "Middlesbrough",

    "Na h-Eileanan Siar",
    "Neath Port Talbot",
    "Newcastle upon Tyne",
    "Newham",
    "Newport",
    "Newry",
    "Norfolk",
    "North Ayrshire",
    "North East England",
    "North Lanarkshire",
    "North Northamptonshire",
    "North Somerset",
    "North Tyneside",
    "North West England",
    "North Yorkshire",
    "Northamptonshire",
    "Northumberland",
    "Northern Ireland",
    "Nottingham",
    "Nottinghamshire",
    "Norwich",

    "Oldham",
    "Orkney Islands",
    "Oxfordshire",

    "Pembrokeshire",
    "Perth",
    "Peterborough",
    "Plymouth",
    "Poole",
    "Portsmouth",
    "Powys",
    "Preston",

    "Reading",
    "Redbridge",
    "Renfrewshire",
    "Rhondda Cynon Taf",
    "Richmond upon Thames",
    "Rochdale",
    "Rutland",

    "Salford",
    "Scarborough",
    "Scotland",
    "Scottish Borders",
    "Sefton",
    "Sheffield",
    "Shetland Islands",
    "Shropshire",
    "Slough",
    "Solihull",
    "Somerset",
    "South Ayrshire",
    "South East England",
    "South Gloucestershire",
    "South Lanarkshire",
    "South Shields",
    "South Tyneside",
    "South West England",
    "Southampton",
    "Southend-on-Sea",
    "Southwark",
    "St Helens",
    "Staffordshire",
    "Stirling",
    "Stockport",
    "Stoke-on-Trent",
    "Suffolk",
    "Sunderland",
    "Surrey",
    "Sutton",
    "Swansea",
    "Swindon",

    "Telford",
    "Thurrock",
    "Torfaen",
    "Torquay",
    "Tower Hamlets",
    "Trafford",
    "Tyne and Wear",

    "Vale of Glamorgan",
    "Wakefield",
    "Wales",
    "Waltham Forest",
    "Wandsworth",
    "Warrington",
    "Warwickshire",
    "West Dunbartonshire",
    "West Lothian",
    "West Midlands",
    "West Sussex",
    "Westminster",
    "Wigan",
    "Wiltshire",
    "Wokingham",
    "Wolverhampton",
    "Worcester",
    "Worcestershire",
    "Wrexham",

    "York",
    "Yorkshire and the Humber"
]

    print("TESTING START")

    step = 0
    invalid = 0
    invalid_inputs = []

    for area in UK_AREAS:
        response = get_search(area_name=area)
        if (response is None):
            invalid += 1
            invalid_inputs.append(area)
        print(f"STEP: {step}")
        step += 1

    print("TESTING DONE")
    print(f"INVALID COUNT: {invalid}, INVALID INPUTS: {invalid_inputs}")

data = get_search(area_name="Stoke-on-Trent")

if (data is None):
    print("FAILED!")
else:
    # serialise into json file


# With error handling
# try:
#     response.raise_for_status()
#     print(f"Success: {data}")
# except rq.exceptions.RequestException as e:
#     print(f"Error: {e}")

if __name__ == "main":
    app.run(host=HOST, port=PORT, debug=True)


