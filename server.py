import requests as rq
from flask import Flask
import pandas as pd

app = Flask(__name__)

# constants
PORT = 8000
HOST = "0.0.0.0"
URL = "https://api.scansan.com/v1/area_codes/search"
AUTH_TOKEN = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"

# setup query params (LINK WITH FRONTEND)
"""
Valid Parameters: (area_name) OR (gbr_district AND gbr_street)

area_name: string
gbr_district: string (e.g. SW1A)
gbr_street: string (e.g. Downing Street)
"""

def construct_http_packet(area_name=None, gbr_district=None, gbr_street=None):
    """
    INPUTS:
    (area_name) OR (gbr_district AND gbr_street)

    area_name: string
    gbr_district: string (e.g. SW1A)
    gbr_street: string (e.g. Downing Street)

    OUTPUTS:
    None
    response: dict
    """

    # type 1
    if (area_name is not None):
        params = {"area_name": area_name}

    # type 2
    if (gbr_district is not None and gbr_street is not None):
        params = {"gbr_district": gbr_district, "gbr_street": gbr_street}
    
    if (not params):
        return None
    
    headers = {
    "X-Auth-Token": AUTH_TOKEN, # for authentication
    "Content-Type": "application/json" # indicates request is JSON
    }

    response = rq.get(URL, params=params, headers=headers)

    data = response.json()

    return data


# params = {"area_name": "Hammersmith"}
# params = {"gbr_district": "SW1A", "gbr_street": "Downing Street"}

# data = response.json()
# print(data)

area_name_test = "Paddington"

response = construct_http_packet(area_name=area_name_test)

if (response is not None):
    print(response)
else:
    print("NULL dummy")

# With error handling
# try:
#     response.raise_for_status()
#     print(f"Success: {data}")
# except rq.exceptions.RequestException as e:
#     print(f"Error: {e}")

if __name__ == "main":
    app.run(host=HOST, port=PORT, debug=True)