"""
Household Integration Module - Connects property details view with charts and API data
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display_sustainability_from_score(sustainability_score):
    """Display sustainability score using household_info_page."""
    try:
        from household_info_page import display_sustainability_score
        display_sustainability_score(sustainability_score)
    except ImportError:
        st.warning("Sustainability module not available")
    except Exception as e:
        st.error(f"Error displaying sustainability: {str(e)}")


def display_price_forecast_from_dataframes(historical_data, forecast_data, market_data):
    """Display price history and forecast chart."""
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
    Shows price chart using historical API data.
    """
    
    # Back button at top
    if st.button("← Back to Results"):
        if "selected_property" in st.session_state:
            del st.session_state.selected_property
        st.rerun()
    
    st.divider()
    
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
    
    # Price metrics section
    st.subheader("💰 Price Information")
    price_col1, price_col2, price_col3 = st.columns(3)
    
    with price_col1:
        current = property_data.get('current_price')
        st.metric("Current Valuation", f"£{current:,.0f}" if current else "N/A")
    
    with price_col2:
        last_sold = property_data.get('last_sold_price')
        st.metric("Last Sold Price", f"£{last_sold:,.0f}" if last_sold else "N/A")
    
    with price_col3:
        future = property_data.get('future_price')
        st.metric("Predicted Future Price", f"£{future:,.0f}" if future else "Coming Soon")
    
    st.divider()
    
    # ========== PRICE HISTORY CHART ==========
    st.subheader("📈 Price History & Forecast")
    
    postcode = property_data.get("postcode", "")
    address = property_data.get("address", "")
    
    if postcode:
        with st.spinner("Loading price history..."):
            try:
                from scansan_client import get_historical_valuation_frame
                
                # Get historical data from API
                historical_data = get_historical_valuation_frame(
                    area_code=postcode,
                    property_address=address
                )
                
                if historical_data is not None and not historical_data.empty:
                    st.success(f"✅ Found {len(historical_data)} historical data points")
                    
                    # Show raw data in expander (for debugging)
                    with st.expander("View Raw Data"):
                        st.dataframe(historical_data)
                    
                    # Create empty DataFrames for forecast and market (placeholders for now)
                    empty_df = pd.DataFrame(columns=["date", "price"])
                    
                    # TODO: Replace empty_df with actual forecast data from your ML model
                    forecast_data = empty_df
                    
                    # TODO: Replace empty_df with market average data
                    market_data = empty_df
                    
                    # Display the chart
                    display_price_forecast_from_dataframes(
                        historical_data, 
                        forecast_data, 
                        market_data
                    )
                    
                else:
                    st.warning("⚠️ No historical valuation data available from API")
                    st.info("The API may not have historical data for this specific property/postcode.")
                    
            except Exception as e:
                st.error(f"Error loading price history: {str(e)}")
                import traceback
                with st.expander("Debug Info"):
                    st.code(traceback.format_exc())
    else:
        st.warning("No postcode available - cannot load price history")
    
    st.divider()
    
    # ========== SUSTAINABILITY SECTION ==========
    st.subheader("🌱 Sustainability Information")
    
    score = property_data.get("score")
    if score:
        display_sustainability_from_score(score)
    else:
        st.info("Sustainability data not available for this property")
    
    st.divider()
    
    # ========== ADDITIONAL INFO ==========
    st.subheader("ℹ️ Additional Information")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.write(f"**Last Sold Date:** {property_data.get('last_sold_date', 'N/A')}")
    with info_col2:
        st.write(f"**Postcode:** {property_data.get('postcode', 'N/A')}")
    
    st.divider()
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❤️ Save to Favorites", use_container_width=True):
            if "favorites" not in st.session_state:
                st.session_state.favorites = []
            
            # Check if already in favorites
            existing = [p.get('postcode') for p in st.session_state.favorites]
            if property_data.get('postcode') not in existing:
                st.session_state.favorites.append(property_data)
                st.success("Added to favorites!")
            else:
                st.info("Already in favorites")
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Debug: Show raw property data
    with st.expander("📋 View Raw Property Data"):
        st.json(property_data)


def initialise_household_session_state():
    """Initialise session state for household details view."""
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None
    if "favorites" not in st.session_state:
        st.session_state.favorites = []


def has_selected_property():
    """Check if a property is currently selected."""
    return st.session_state.get("selected_property") is not None