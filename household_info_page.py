"""
Todo: Make a sustainability function:
Input:  This will need the sustainabilty score from the file

Output: Should display a sustainability score


Todo: Make a price display graph function:
Input: 

Todo: Make a household description
"""

"""
Streamlit Product Sustainability and Price Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from scansan_client import get_historical_valuation_frame


def display_sustainability_score(sustainability_score):
    """
    Display sustainability score with visual gauge and rating.
    
    This function creates a Streamlit section that shows:
    - A gauge chart displaying the sustainability score (0-100)
    - A color-coded rating (Poor/Fair/Good/Excellent)
    - Text description based on the score level
    
    Args:
        sustainability_score (float): Score from 0-100
    """
    # Create a container for the sustainability section
    st.subheader("Sustainability Score")
    
    # Determine rating category based on score
    # 80-100: Excellent, 60-79: Good, 40-59: Fair, 0-39: Poor
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
    
    # Create two columns: one for gauge, one for text info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create a Plotly gauge chart for visual representation
        # This shows the score on a semi-circular gauge with color coding
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = sustainability_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 60], 'color': "lightyellow"},
                    {'range': [60, 80], 'color': "lightgreen"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        # Adjust figure size for streamlit
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display rating and explanation text
        st.metric(label="Rating", value=rating)
        st.write(f"**Score:** {sustainability_score}/100")
        
        # Add contextual description based on rating
        if rating == "Excellent":
            st.success("This house has exceptional sustainability credentials!")
        elif rating == "Good":
            st.info("This house meets good sustainability standards.")
        elif rating == "Fair":
            st.warning("This house has room for sustainability improvement.")
        else:
            st.error("This house has low sustainability performance.")



def display_price_history_forecast_and_market(
    historical_data: pd.DataFrame,
    forecast_data: pd.DataFrame,
    market_data: pd.DataFrame,
):
    """
    Plot:
      - historical prices (solid)
      - forecast prices (dashed)
      - local market prices (solid, different style)
    All DataFrames expect columns: ['date', 'price'].
    """

    if historical_data is None or forecast_data is None or market_data is None:
        st.warning("No data provided.")
        return

    if historical_data.empty and forecast_data.empty and market_data.empty:
        st.warning("No data to plot.")
        return

    # Copy + clean/sort
    def prep(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        out["date"] = pd.to_datetime(out["date"])
        out = out.sort_values("date")
        return out

    historical = prep(historical_data)
    forecast   = prep(forecast_data)
    market     = prep(market_data)

    fig = go.Figure()

    # Historical (solid)
    if not historical.empty:
        fig.add_trace(go.Scatter(
            x=historical["date"],
            y=historical["price"],
            mode="lines",
            name="This property (historical)",
        ))

    # Forecast (dashed)
    if not forecast.empty:
        fig.add_trace(go.Scatter(
            x=forecast["date"],
            y=forecast["price"],
            mode="lines",
            name="This property (forecast)",
            line=dict(dash="dash"),
        ))

    # Market (dotted)
    if not market.empty:
        fig.add_trace(go.Scatter(
            x=market["date"],
            y=market["price"],
            mode="lines",
            name="Local market",
            line=dict(dash="dot"),
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


# np.random.seed(42)

# historical_data = pd.DataFrame({
#     "date": pd.date_range(start="2024-01-01", periods=18, freq="MS"),
#     "price": 350_000 + np.cumsum(np.random.normal(1500, 800, 18))
# })

# forecast_data = pd.DataFrame({
#     "date": pd.date_range(start="2025-07-01", periods=6, freq="MS"),
#     "price": historical_data["price"].iloc[-1] + np.cumsum(np.random.normal(1800, 600, 6))
# })

# # Market data covering the same whole span (hist + forecast)
# all_dates = pd.date_range(start="2024-01-01", periods=24, freq="MS")
# market_data = pd.DataFrame({
#     "date": all_dates,
#     "price": 345_000 + np.cumsum(np.random.normal(1300, 700, len(all_dates)))
# })

# st.title("Price Trend Test")
# display_price_history_forecast_and_market(historical_data, forecast_data, market_data)


# Testing



