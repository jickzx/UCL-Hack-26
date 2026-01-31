"""
Frontend module for UK Property Search application.
Streamlit UI that imports backend functions from main.py.
"""

import streamlit as st

# Import backend functions from main.py
from main import (
    search_properties,
    get_uk_areas,
    get_sustainability_label,
    get_sustainability_color,
)

# =============================================================================
# Page Configuration (must be first Streamlit command)
# =============================================================================
st.set_page_config(page_title="UK Property Search", layout="wide")

# =============================================================================
# App Title
# =============================================================================
st.title("🏠 Property / Area Search")

# =============================================================================
# Sidebar: Search Panel
# =============================================================================
with st.sidebar:
    st.header("🔍 Search")
    
    # Get areas from backend
    uk_areas = get_uk_areas()
    
    area = st.selectbox("Choose an area", uk_areas, index=0)
    query = st.text_input(
        "Search", 
        placeholder="e.g. postcode, street, ward...",
        help="Enter a postcode, street name, or leave empty to see all"
    )
    submitted = st.button("Search", use_container_width=True, type="primary")

# =============================================================================
# Session State
# =============================================================================
if "results" not in st.session_state:
    st.session_state.results = []
if "last_search" not in st.session_state:
    st.session_state.last_search = {"area": None, "query": None}

# =============================================================================
# Trigger Search (calls backend)
# =============================================================================
if submitted:
    with st.spinner("Searching properties..."):
        # Call backend search function
        results = search_properties(area, query)
        st.session_state.results = results
        st.session_state.last_search = {"area": area, "query": query}

# =============================================================================
# Display Results
# =============================================================================
last = st.session_state.last_search

if last["area"] is None:
    st.info("👋 Select an area and optionally enter a postcode/street to search. Example: SW1A 1AA")
else:
    st.subheader(f"📍 Results for {last['area']} — query: {last['query']!r}")

    results = st.session_state.results
    
    if not results:
        st.warning("No results found. Try a different search.")
    else:
        st.success(f"Found {len(results)} properties")
        
        # Display property cards
        for r in results:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{r['address']}**")
                    st.caption(f"📍 Area: {r['area']}")
                    if "price" in r:
                        st.caption(f"💰 Price: £{r['price']:,}")
                
                with col2:
                    score = r.get("score", 0)
                    label = get_sustainability_label(score)
                    color = get_sustainability_color(score)
                    
                    st.markdown(
                        f"<div style='text-align: center; padding: 10px; "
                        f"background-color: {color}22; border-radius: 8px; "
                        f"border: 2px solid {color};'>"
                        f"<span style='font-size: 24px; font-weight: bold; color: {color};'>{score}%</span><br>"
                        f"<span style='color: {color};'>{label}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
        
        # Summary stats
        if len(results) > 1:
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_score = sum(r.get("score", 0) for r in results) / len(results)
                st.metric("Avg Sustainability", f"{avg_score:.1f}%")
            
            with col2:
                if all("price" in r for r in results):
                    avg_price = sum(r["price"] for r in results) / len(results)
                    st.metric("Avg Price", f"£{avg_price:,.0f}")
            
            with col3:
                st.metric("Properties Found", len(results))
