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



def main():
    st.set_page_config(
        page_title="Test Sustainability Score",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 Sustainability Score Tester")
    st.write("Use the slider below to test different sustainability scores")
    
    # Add a slider to test different scores
    test_score = st.slider(
        "Select a sustainability score to test:",
        min_value=0.0,
        max_value=100.0,
        value=75.0,
        step=1.0
    )
    
    st.markdown("---")
    
    # Display the function with the selected score
    display_sustainability_score(test_score)
    
    # Show some example scores below
    st.markdown("---")
    st.subheader("Quick Test Examples")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Test Poor (25)"):
            st.session_state.test_score = 25.0
    
    with col2:
        if st.button("Test Fair (55)"):
            st.session_state.test_score = 55.0
    
    with col3:
        if st.button("Test Good (72)"):
            st.session_state.test_score = 72.0
    
    with col4:
        if st.button("Test Excellent (90)"):
            st.session_state.test_score = 90.0
    
    # Display selected test if button was clicked
    if 'test_score' in st.session_state:
        st.markdown("---")
        st.write(f"### Testing with score: {st.session_state.test_score}")
        display_sustainability_score(st.session_state.test_score)


if __name__ == "__main__":
    main()