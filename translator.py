import pandas as pd
import requests as rq

AUTH_TOKEN = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"

# HOUSE MAIN FEATURES:
def get_property_type (postcode, address):
    URL = "https://api.scansan.com/v1/postcode/" + postcode + "/sale/history"
    data = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json () ["data"]
    if (data is None):
        return None
    for p in data:
        pt = p ["property_type"]
        test_address = p ["street_address"]
        if test_address == address:
            if pt == None:
                return None
            if "flat" in pt.lower():
                return "F"
            elif "maisonette" in pt.lower():
                return "F"
            elif "detached" in pt.lower():
                return "D"
            elif "semi" in pt.lower():
                return "S"
            elif "terrace" in pt.lower():
                return "T"
            else:
                return None
    return None

def get_habitable_rooms (postcode, address):
    URL = "https://api.scansan.com/v1/area_codes/" + postcode + "/sale/listings"
    data = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json () ["data"] ["sale_listings"]
    if data is None:
        return None
    for p in data:
        test_address = p ["street_address"]
        bedrooms = p ["bedrooms"]
        living_rooms = p ["living_rooms"]
        if test_address == address and bedrooms is not None and living_rooms is not None:
            return bedrooms + living_rooms
    return None

def get_floor_area (postcode, address):
    URL = "https://api.scansan.com/v1/area_codes/" + postcode + "/sale/listings"
    data = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json () ["data"] ["sale_listings"]
    if data is None:
        return None
    for p in data:
        test_address = p ["street_address"]
        floor_area = p ["property_size"]
        if test_address == address and floor_area is not None:
            return int(floor_area)
        
    return None
    
# hash key - gives path in energy performace to wanted value
epc_key = {
    "CURRENT_ENERGY_RATING": {"category": "EPC", "value": "current_rating"},
    "ENERGY_CONSUMPTION_CURRENT": {"category": "energy_consumption", "value": "current_annual_energy_consumption"},
    "CO2_EMISSIONS_CURRENT": {"category": "annual_CO2_emissions", "value": "current_emissions"},
    "HEATING_COST_CURRENT": {"category": "annual_energy_costs", "value": "current_annual_heating_cost"},
    "HOT_WATER_COST_CURRENT": {"category": "annual_energy_costs", "value": "current_annual_hot_water_cost"},
    "MAINHEAT_ENERGY_EFF": {"category": "property_efficiency", "value": "property_main_heating_energy_efficiency"}
}

# def get_epc_values (postcode, address):
#     URL = "https://api.scansan.com/v1/postcode/" + postcode + "/energy/performance"
#     d = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json ()
#     if (d is None):
#         return None
#     data = d["data"]
#     epc_values = {}
#     for p in data:
#         if (p is None):
#             print("EXITING EARLY")
#         test_address = p ["street_address"]
#         if test_address == address:
#             for key in epc_key:
#                 if (key is None):
#                     print("EXXEIJXIJ")
#                     return None
#                 category = epc_key [key] ["category"]
#                 value = epc_key [key] ["value"]
#                 epc_values [key] = p [category] [value]

#     return epc_values

def get_epc_values (uprn, address):
    URL = "https://api.scansan.com/v1/postcode/" + uprn + "/energy/performance"
    d = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json()
    if (d is None):
        return None
    data = d["data"]
    epc_values = {}
    for p in data:
        if (p is None):
            return None
        test_address = p["street_address"]
        if test_address == address:
            for key in epc_key:
                if (key is None):
                    return None
                category = epc_key[key]["category"]
                value = epc_key[key]["value"]
                epc_values[key] = p[category][value]

    return epc_values

get_epc_values("SW1A", "10 Downing Street")

# hash key - gives path in energy performance to description values - handled separately due to more complex values

epc_desc_key = {
    "FLOOR_DESCRIPTION": "floor_description",
    "WINDOWS_DESCRIPTION": "property_windows_description",
    "WALLS_DESCRIPTION": "property_walls_description",
    "ROOF_DESCRIPTION": "roof_description",
    "MAINHEAT_DESCRIPTION": "property_main_heating_description"
}

def get_desc_df (postcode, address):
    URL = "https://api.scansan.com/v1/postcode/" + postcode + "/energy/performance"
    data = rq.get(URL, headers={"X-Auth-Token": AUTH_TOKEN}).json () ["data"]
    if data is None:
        return None
    for p in data:
        test_address = p ["street_address"]
        if test_address == address:
            return pd.DataFrame([{
                key: p ["property_efficiency"] [value]
                for key, value in epc_desc_key.items()
            }])

# Key word identifiers for descriptions - descriptions have more complicated values and are broken down with key word analysis
def sort_description (df, old_column_name, new_column_name, key):
    df[new_column_name] = pd.Series(pd.NA, index=df.index, dtype="string")
    for keyword in key:
        df.loc[df[old_column_name].str.contains(keyword, case=False, na=False), new_column_name] = key[keyword]

def sort_descriptions (df):
    values = {}
    values ["FLOOR_TYPE"] = sort_description (df, "FLOOR_DESCRIPTION", "FLOOR_TYPE", {
        "solid": "solid",
        "suspended": "suspended",
        "unheated space": "to unheated space",
        "external air": "to external air",
        "conservatory": "conservatory",
        "dwelling|premise": "premise below"
    })

    values ["FLOOR_INSULATED"] = sort_description (df, "FLOOR_DESCRIPTION", "FLOOR_INSULATED", {
        "insulated": "Y",
        "uninsulated|no insulation|limited": "N"
    })

    # WINDOWS_DESCRIPTION sorted
    values ["WINDOWS_TYPE"] = sort_description (df, "WINDOWS_DESCRIPTION", "WINDOWS_TYPE", {
        "single": "single",
        "double": "double",
        "triple": "triple",
        "secondary": "secondary",
        "multiple": "multiple"
    })

    values ["WINDOWS_DEGREE"] = sort_description (df, "WINDOWS_DESCRIPTION", "WINDOWS_DEGREE", {
        "full": "fully",
        "mostly": "mostly",
        "some|partial": "partial"
    })

    # WALLS_DESCRIPTION
    values ["WALLS_TYPE"] = sort_description (df, "WALLS_DESCRIPTION", "WALLS_TYPE", {
        "granite or whin": "granite or whinstone",
        "solid brick": "solid brick",
        "sandstone|limestone": "sandstone or limestone",
        "timber frame": "timber frame",
        "system built": "system built",
        "cob": "cob"
    })

    values ["WALLS_CAVITY"] = sort_description (df, "WALLS_DESCRIPTION", "WALLS_CAVITY", {
        "cavity": "unfilled",
        "filled": "filled"
    })

    values ["WALLS_INSULATED"] = sort_description (df, "WALLS_DESCRIPTION", "WALLS_INSULATED", {
        "insulated": "insulated",
        "internal": "internal",
        "external": "external",
        "partial": "partial",
        "no insulation": "no insulation"
    })

    # ROOF_DESCRIPTION
    values ["WALLS_CAVITY"] = sort_description (df, "ROOF_DESCRIPTION", "ROOF_TYPE", {
        "pitched": "pitched",
        "flat": "flat",
        "roof room": "roof rooms",
        "thatched": "thatched",
        "premise": "other premises above"
    })

    values ["ROOF_INSULATED"] = sort_description (df, "ROOF_DESCRIPTION", "ROOF_INSULATED", {
        "insulated|additional": "insulated",
        "limited": "limited insulation",
        "no insulation": "no insulation"
    })

    # MAINHEAT_DESCRIPTION
    values ["MAINHEAT_TYPE"] = sort_description (df, "MAINHEAT_DESCRIPTION", "MAINHEAT_TYPE",{
        "room heaters|electric heaters|no System": "room heaters",
        "electric ceiling": "electric ceiling",
        "coal|wood|dual fuel": "solid fuel",
        "air source heat pump": "heat pump",
        "electric underfloor heating": "electric underfloor",
        "warm air": "warm air system",
        "LPG": "LPG boiler",
        "community scheme": "community heating",
        "oil": "oil boiler",
        "electric storage heaters": "electric storage",
        "mains gas": "gas boiler"
    })

    return values



def translator (postcode, address):
    epc_values = get_epc_values (postcode, address)
    desc_df = get_desc_df (postcode, address)
    desc_values = sort_descriptions (desc_df)

    return {
        "postcode": postcode,
        "propertytype": get_property_type (postcode, address),
        "TOTAL_FLOOR_AREA": get_floor_area (postcode, address),
        "NUMBER_HABITABLE_ROOMS": get_habitable_rooms (postcode, address),
        "CURRENT_ENERGY_RATING": epc_values ["CURRENT_ENERGY_RATING"],
        "ENERGY_CONSUMPTION_CURRENT": epc_values ["ENERGY_CONSUMPTION_CURRENT"],
        "CO2_EMISSIONS_CURRENT": epc_values ["CO2_EMISSIONS_CURRENT"],
        "HEATING_COST_CURRENT": epc_values ["HEATING_COST_CURRENT"],
        "HOT_WATER_COST_CURRENT": epc_values ["HOT_WATER_COST_CURRENT"],
        "MAINHEAT_ENERGY_EFF": epc_values ["MAINHEAT_ENERGY_EFF"],
        "FLOOR_TYPE": desc_values ["FLOOR_TYPE"],
        "FLOOR_INSULATED": desc_values ["FLOOR_INSULATED"],
        "WINDOWS_TYPE": desc_values ["WINDOWS_TYPE"],
        "WINDOWS_DEGREE": desc_values ["WINDOWS_DEGREE"],
        "WALLS_TYPE": desc_values ["WALLS_TYPE"],
        "WALLS_CAVITY": desc_values ["WALLS_CAVITY"],
        "WALLS_INSULATED": desc_values ["WALLS_INSULATED"],
        "ROOF_TYPE": desc_values ["ROOF_TYPE"],
        "ROOF_INSULATED": desc_values ["ROOF_INSULATED"],
        "MAINHEAT_TYPE": desc_values ["MAINHEAT_TYPE"],
        "MAINHEAT_ENERGY_EFF": desc_values ["MAINHEAT_ENERGY_EFF"]
    }

