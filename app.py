import streamlit as st
# import app as st - do not include
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

st.title("UK Property / Area Search")


UK_AREAS = [
    "Any","London", "Manchester", "Birmingham", "Leeds", "Glasgow", "Edinburgh",
    "Bristol", "Liverpool", "Sheffield", "Newcastle upon Tyne", "Nottingham",
    
]

def mock_search(area: str, query: str):
    """
    Replace this with your real backend/API call.
    Must return a list (or dataframe) of results.
    """
    # Example fake results
    q = query.strip().lower()
    base = [
        {"address": "10 Example Rd", "area": area, "score": 72},
        {"address": "22 Demo St", "area": area, "score": 65},
        {"address": "7 Test Ave", "area": area, "score": 81},
    ]
    if not q:
        return base
    return [r for r in base if q in r["address"].lower()]

st.set_page_config(page_title="UK Area Search", layout="wide")

# --- Sidebar search panel ---
with st.sidebar:
    st.header("Search")
    area = st.selectbox("Choose an area", UK_AREAS, index=0)
    query = st.text_input("Search", placeholder="e.g. postcode, street, ward...")
    submitted = st.button("Search", use_container_width=True)

# --- Session state to keep results ---
if "results" not in st.session_state:
    st.session_state.results = []
if "last_search" not in st.session_state:
    st.session_state.last_search = {"area": None, "query": None}

# --- Trigger search ---
if submitted:
    results = mock_search(area, query)
    st.session_state.results = results
    st.session_state.last_search = {"area": area, "query": query}

# --- Main content area: show results ---
last = st.session_state.last_search
if last["area"] is None:
    st.info("Select an area, and a postcode/street/ward to search within that area. when you select this, make sure it is correct e.g, SS0 0BW")
else:
    st.subheader(f"Results for {last['area']} — query: {last['query']!r}")

    results = st.session_state.results
    if not results:
        st.warning("No results found.")
    else:
        # Simple card-style display
        for r in results:
            with st.container(border=True):
                st.write(f"**{r['address']}**")
                st.caption(f"Area: {r['area']} | Sustainability score: {r['score']}")

        # If you want a dataframe instead:
        # import pandas as pd
        # st.dataframe(pd.DataFrame(results), use_container_width=True)
