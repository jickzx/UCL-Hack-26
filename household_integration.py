"""
Household Integration Module
Handles property detail view and session state management
Integrates with household_info_page.py for sustainability and price visualization
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scansan_client import get_valuation_frame, get_current_valuations, get_historical_valuations


def initialise_household_session_state():
    """Initialize session state variables for property selection and favorites."""
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None
    if "favorites" not in st.session_state:
        st.session_state.favorites = []


def has_selected_property() -> bool:
    """
    Check if a property has been selected for detailed view.
    
    Returns:
        bool: True if a property is selected, False otherwise
    """
    return (
        "selected_property" in st.session_state 
        and st.session_state.selected_property is not None
    )


def display_sustainability_from_score(sustainability_score):
    """
    Entry point to display sustainability score using household_info_page.
    Falls back to simple display if module not available.
    
    Args:
        sustainability_score: Score from 0-100
    """
    try:
        from household_info_page import display_sustainability_score
        display_sustainability_score(sustainability_score)
    except ImportError:
        # Fallback: Display simple sustainability info
        st.subheader("🌱 Sustainability Score")
        
        if sustainability_score >= 80:
            rating = "Excellent"
            color = "green"
        elif sustainability_score >= 60:
            rating = "Good"
            color = "lightgreen"
        elif sustainability_score >= 40:
            rating = "Fair"
            color = "orange"
        else:
            rating = "Poor"
            color = "red"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{sustainability_score}/100")
        with col2:
            st.metric("Rating", rating)
    except Exception as e:
        st.error(f"Error displaying sustainability: {str(e)}")


def display_price_forecast_from_dataframes(historical_data, forecast_data, market_data):
    """
    Entry point to display price history and forecast using household_info_page.
    Falls back to simple chart if module not available.
    
    Args:
        historical_data: DataFrame with columns ['date', 'price']
        forecast_data: DataFrame with columns ['date', 'price']
        market_data: DataFrame with columns ['date', 'price']
    """
    try:
        from household_info_page import display_price_history_forecast_and_market
        display_price_history_forecast_and_market(historical_data, forecast_data, market_data)
    except ImportError:
        # Fallback: Display simple price chart
        st.subheader("📈 Price History")
        if not historical_data.empty:
            import plotly.graph_objects as go
            
            df = historical_data.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines+markers',
                name='Price History'
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (£)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No price history available")
    except Exception as e:
        st.error(f"Error displaying price forecast: {str(e)}")


def render_household_details_view(property_data: dict):
    """
    Render detailed household information for a selected property.
    
    Args:
        property_data: Dictionary containing property information with keys:
            - address: str
            - postcode: str
            - area: str
            - current_price: int or None
            - future_price: int or None
            - last_sold_price: int or None
            - last_sold_date: str or None
            - score: int or None (sustainability score)
    """
    # Back button at the top
    if st.button("← Back to Search Results"):
        st.session_state.selected_property = None
        st.rerun()
    
    st.divider()
    
    # Property header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"🏠 {property_data.get('address', 'Unknown Property')}")
        if property_data.get("area"):
            st.caption(f"📍 {property_data['area']}")
    with col2:
        if property_data.get("postcode"):
            st.code(property_data["postcode"])
    
    st.divider()
    
    # Price Information Section
    st.subheader("💰 Price Information")
    price_col1, price_col2, price_col3 = st.columns(3)
    
    with price_col1:
        current_price = property_data.get('current_price')
        if current_price:
            st.metric("Current Price", f"£{current_price:,.0f}")
        else:
            st.metric("Current Price", "N/A")
    
    with price_col2:
        last_sold_price = property_data.get('last_sold_price')
        if last_sold_price:
            st.metric("Last Sold Price", f"£{last_sold_price:,.0f}")
        else:
            st.metric("Last Sold Price", "N/A")
    
    with price_col3:
        st.metric("Future Price (Predicted)", f"£{property_data.get('future_price', 'N/A'):,.0f}" if property_data.get('future_price') else "TBD")
    
    # Price history placeholder
    st.subheader(" Price History & Forecast")
    st.info("Price history chart will be displayed here")
    # TODO: Call display_price_forecast_from_dataframes() with historical, forecast, and market DataFrames
    
    # Sustainability score section
    st.subheader("🌱 Sustainability Information")
    score = property_data.get("score")
    if score is not None:
        # Use the household_info_page function if available
        display_sustainability_from_score(score)
    else:
        st.info("ℹ️ Sustainability data not available for this property")
    
    st.divider()
    
    # Additional information
    st.subheader("ℹ Additional Information")
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        last_sold_date = property_data.get('last_sold_date')
        if last_sold_date:
            st.write(f"**Last Sold Date:** {last_sold_date}")
        else:
            st.write("**Last Sold Date:** N/A")
    
    with info_col2:
        postcode = property_data.get('postcode')
        if postcode:
            st.write(f"**Postcode District:** {postcode}")
        else:
            st.write("**Postcode District:** N/A")
    
    st.divider()
    
    # Save to favorites button
    st.button(" Save to Favorites", use_container_width=True)


def initialise_household_session_state():
    """Initialise session state for household details view."""
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    # Check if already in favorites
    property_id = property_data.get('address', '') + property_data.get('postcode', '')
    existing_ids = [p.get('address', '') + p.get('postcode', '') for p in st.session_state.favorites]
    
    if property_id not in existing_ids:
        st.session_state.favorites.append(property_data)
        st.success("✅ Added to favorites!")
    else:
        st.info("Already in favorites")