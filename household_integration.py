"""
Boilerplate for household_info_page integration into app.py

This module provides entry point functions that wrap household_info_page.py
without modifying its code. Functions are called dynamically as needed.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display_sustainability_from_score(sustainability_score):
    """
    Entry point to display sustainability score using household_info_page.
    
    Args:
        sustainability_score: Score from 0-100
    """
    try:
        from household_info_page import display_sustainability_score
        display_sustainability_score(sustainability_score)
    except ImportError:
        st.warning("Sustainability module not available")
    except Exception as e:
        st.error(f"Error displaying sustainability: {str(e)}")


def display_price_forecast_from_dataframes(historical_data, forecast_data, market_data):
    """
    Entry point to display price history and forecast using household_info_page.
    
    Args:
        historical_data: DataFrame with columns ['date', 'price']
        forecast_data: DataFrame with columns ['date', 'price']
        market_data: DataFrame with columns ['date', 'price']
    """
    try:
        from household_info_page import display_price_history_forecast_and_market
        display_price_history_forecast_and_market(historical_data, forecast_data, market_data)
    except ImportError:
        st.warning("Price history module not available")
    except Exception as e:
        st.error(f"Error displaying price forecast: {str(e)}")


def render_household_details_view(property_data):
    """
    Render detailed household information for a selected property.
    
    Args:
        property_data: Dictionary containing property information
    """
    st.subheader("Property Details")
    
    # Property header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(property_data.get("address", "Unknown Property"))
        if property_data.get("area"):
            st.caption(f"📍 {property_data['area']}")
    with col2:
        if property_data.get("postcode"):
            st.code(property_data["postcode"])
    
    st.divider()
    
    # Back button
    if st.button("← Back to Results", use_container_width=False):
        if "selected_property" in st.session_state:
            del st.session_state.selected_property
        st.rerun()
    
    # Price section
    st.subheader("💰 Price Information")
    price_col1, price_col2, price_col3 = st.columns(3)
    with price_col1:
        st.metric("Current Price", f"£{property_data.get('current_price', 'N/A'):,.0f}" if property_data.get('current_price') else "N/A")
    with price_col2:
        st.metric("Last Sold Price", f"£{property_data.get('last_sold_price', 'N/A'):,.0f}" if property_data.get('last_sold_price') else "N/A")
    with price_col3:
        st.metric("Future Price (Predicted)", f"£{property_data.get('future_price', 'N/A'):,.0f}" if property_data.get('future_price') else "TBD")
    
    # Price history placeholder
    st.subheader("📊 Price History & Forecast")
    st.info("Price history chart will be displayed here")
    # TODO: Call display_price_forecast_from_dataframes() with historical, forecast, and market DataFrames
    
    # Sustainability score section
    st.subheader("🌱 Sustainability Information")
    if property_data.get("score"):
        # TODO: Uncomment when sustainability score is available
        # display_sustainability_from_score(property_data['score'])
        st.info(f"Sustainability Score: {property_data['score']}/100")
    else:
        st.warning("Sustainability data not available for this property")
    
    # Additional information
    st.subheader("ℹ️ Additional Information")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.write(f"**Last Sold Date:** {property_data.get('last_sold_date', 'N/A')}")
    with info_col2:
        st.write(f"**Postcode District:** {property_data.get('postcode', 'N/A')}")
    
    st.divider()
    
    # Save to favorites button
    st.button("❤️ Save to Favorites", use_container_width=True)


def initialise_household_session_state():
    """Initialise session state for household details view."""
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None
    if "favorites" not in st.session_state:
        st.session_state.favorites = []


def has_selected_property():
    """Check if a property is currently selected."""
    return st.session_state.get("selected_property") is not None
