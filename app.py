"""
Frontend module for UK Property Search application.
Streamlit UI that imports backend functions from main.py.
"""

import streamlit as st

# Import backend functions from main.py
from main import (search_properties, get_uk_areas)
st.set_page_config(page_title="UK Property Search", layout="wide")

st.title("Property / Area Search")

def get_street_view_image_url(address: str, postcode: str = "") -> str:
    """
    Generate a Google Maps Street View Static API URL for a property.
    Note: Requires a valid API key for production use.
    
    Parameters:
        address: Street address of the property
        postcode: Postcode of the property
    
    Returns:
        URL string for the Street View image
    """
    # Combine address and postcode for location query
    location = f"{address}, {postcode}, UK" if postcode else f"{address}, UK"
    # URL encode the location
    encoded_location = location.replace(" ", "+").replace(",", "%2C")
    
    # Google Street View Static API URL
    # Note: Replace YOUR_API_KEY with actual key for production
    # For demo, using a placeholder that shows the location on a map
    api_key = "370b0b6f-3f09-4807-b7fe-270a4e5ba2c2"  # Set this in backend/environment variable
    
    # Street View image URL (requires valid API key)
    street_view_url = f"https://maps.googleapis.com/maps/api/streetview?size=400x300&location={encoded_location}&key={api_key}"
    
    return street_view_url


def display_property_card(property_data: dict):
    """
    Display a single property card with image, current price, and future price.
    
    Parameters:
        property_data: Dictionary containing property information
            Expected keys (to be set by backend):
            - address: str
            - postcode: str (optional)
            - image_url: str (optional, will use Street View if not provided)
            - current_price: float/int (optional)
            - future_price: float/int (optional)
            - area: str (optional)
    """
    # Extract data with defaults for missing values
    address = property_data.get("address", "Address not available")
    postcode = property_data.get("postcode", "")
    area = property_data.get("area", "")
    
    # Image URL - use provided URL or generate Street View URL
    image_url = property_data.get("image_url")
    if not image_url:
        image_url = get_street_view_image_url(address, postcode)
    
    # Prices - will be set by backend, display placeholder if not available
    current_price = property_data.get("current_price")
    future_price = property_data.get("future_price")
    
    # Display the property card
    with st.container(border=True):
        # House Image
        st.image(
            image_url,
            use_container_width=True,
            caption=f"{address}" + (f", {postcode}" if postcode else "")
        )
        
        # Price information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Price**")
            if current_price is not None:
                st.markdown(f"### £{current_price:,.0f}")
            else:
                st.markdown("### —")
                st.caption("Price pending")
        
        with col2:
            st.markdown("**Future Price**")
            if future_price is not None:
                st.markdown(f"### £{future_price:,.0f}")
                # Show price change indicator
                if current_price is not None:
                    change = future_price - current_price
                    change_pct = (change / current_price) * 100 if current_price > 0 else 0
                    if change >= 0:
                        st.caption(f"📈 +£{change:,.0f} ({change_pct:+.1f}%)")
                    else:
                        st.caption(f"📉 £{change:,.0f} ({change_pct:.1f}%)")
            else:
                st.markdown("### —")
                st.caption("Forecast pending")


def display_property_grid(properties: list, columns: int = 4):
    """
    Display properties in a grid layout.
    
    Parameters:
        properties: List of property dictionaries
        columns: Number of columns in the grid (default 4 as per sketch)
    """
    if not properties:
        st.info("No properties to display. Search for an area to see results.")
        return
    
    # Create grid rows
    for i in range(0, len(properties), columns):
        cols = st.columns(columns)
        for j, col in enumerate(cols):
            if i + j < len(properties):
                with col:
                    display_property_card(properties[i + j])



# Sidebar: Search Panel

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



# Session State
if "results" not in st.session_state:
    st.session_state.results = []
if "last_search" not in st.session_state:
    st.session_state.last_search = {"area": None, "query": None}



# Search Trigger
if submitted:
    with st.spinner("Searching properties..."):
        # Call backend search function
        results = search_properties(area, query)
        st.session_state.results = results
        st.session_state.last_search = {"area": area, "query": query}


# Main Content: Display Results
last = st.session_state.last_search

# Initialize view state
if "current_view" not in st.session_state:
    st.session_state.current_view = "properties"  # Default to properties view

# Navigation tabs (clickable links)
tab_col1, tab_col2 = st.columns(2)

with tab_col1:
    if st.button("Individual Properties", use_container_width=True, 
                 type="primary" if st.session_state.current_view == "properties" else "secondary"):
        st.session_state.current_view = "properties"
        st.rerun()

with tab_col2:
    if st.button("🗺️ Heatmap View", use_container_width=True,
                 type="primary" if st.session_state.current_view == "heatmap" else "secondary"):
        st.session_state.current_view = "heatmap"
        st.rerun()

st.divider()

# Show content based on selected view

if st.session_state.current_view == "properties":

    # Individual Properties View - Grid Layout (3 columns)
    st.subheader("Individual Properties")
    
    if last["area"] is None:
        st.info("👋 Select an area to see property listings")
    else:
        results = st.session_state.results
        if results:
            st.success(f"Found {len(results)} properties in **{last['area']}**")
            
            # Display properties in a 3-column grid
            columns_per_row = 3
            for row_start in range(0, len(results), columns_per_row):
                cols = st.columns(columns_per_row)
                for col_idx, col in enumerate(cols):
                    prop_idx = row_start + col_idx
                    if prop_idx < len(results):
                        prop = results[prop_idx]
                        address = prop.get("address", "Unknown")
                        postcode = prop.get("postcode", "")
                        current_price = prop.get("current_price")
                        future_price = prop.get("future_price")
                        
                        with col:
                            with st.container(border=True):
                                # House Image
                                image_url = prop.get("image_url")
                                if not image_url:
                                    image_url = get_street_view_image_url(address, postcode)
                                st.image(image_url, use_container_width=True)
                                
                                # Address
                                st.markdown(f"**{address}**")
                                if postcode:
                                    st.caption(f"📍 {postcode}")
                                
                                # Price information
                                price_col1, price_col2 = st.columns(2)
                                with price_col1:
                                    st.caption("Current")
                                    if current_price:
                                        st.markdown(f"**£{current_price:,.0f}**")
                                    else:
                                        st.markdown("**—**")
                                with price_col2:
                                    st.caption("Future")
                                    if future_price:
                                        st.markdown(f"**£{future_price:,.0f}**")
                                    else:
                                        st.markdown("**—**")
                                
                                # View details button
                                if st.button("View Details", key=f"view_{prop_idx}", use_container_width=True):
                                    st.session_state.selected_property = prop_idx
        else:
            st.warning("No properties found. Try a different search.")

elif st.session_state.current_view == "heatmap":
    # Heatmap View
    st.subheader("Heatmap View")
    
    if last["area"] is None:
        st.info("Search for properties to see the heatmap here")
    else:
        st.caption(f"Showing results for: **{last['area']}** | Query: *{last['query'] or 'All'}*")
        
        results = st.session_state.results
        
        if results:
            st.success(f"Found {len(results)} properties")
            
            # Placeholder for heatmap - link to be added later
            st.info("🗺️ Heatmap visualization coming soon...")
            
            # Placeholder container for future heatmap
            with st.container(border=True):
                st.markdown("""
                <div style="
                    height: 500px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    flex-direction: column;
                ">
                    <span>Heatmap View</span>
                    <span style="font-size: 14px; font-weight: normal; margin-top: 10px;">Click to explore (coming soon)</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Button placeholder for future heatmap page link
                st.button("🔗 Open Full Heatmap", use_container_width=True, disabled=True,
                         help="Heatmap page coming soon")
        else:
            st.warning("No properties found. Try a different search.")