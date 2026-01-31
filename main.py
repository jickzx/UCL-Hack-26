import app as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from io import BytesIO
import base64
import requests

# Set up API
URL = "https://api.scansan.com/v1/area_codes/search"
API_KEY = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"
params = {"area_name": "Hammersmith"}
headers = {
    "X-Auth-Token": API_KEY,
    "Content-Type": "application/json"
}

response = requests.get(URL, params=params, headers=headers)
data = response.json()
print(data)

# With error handling
try:
    response.raise_for_status()
    print(f"Success: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

### MAIN CODE

