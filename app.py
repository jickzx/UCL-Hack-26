import streamlit as st
from main import search_properties, get_uk_areas, is_full_postcode, sort_properties, validate_search_input, get_detected_area_from_properties, get_dynamic_uk_areas
from household_integration import render_household_details_view, initialise_household_session_state, has_selected_property

st.set_page_config(page_title="UK Property Search", layout="wide")

st.title("🏠 UK Property / Area Search")


def render_sidebar_search():
    """Render search controls in sidebar and return search parameters."""
    with st.sidebar:
        st.header("Search")
        
        # dynamic list
        detected_area = st.session_state.get("detected_area")
        uk_areas = get_dynamic_uk_areas(detected_area)
        

        default_index = 0
        if detected_area and detected_area in uk_areas:
            default_index = uk_areas.index(detected_area)
        elif st.session_state.last_search.get("area") in uk_areas:
            default_index = uk_areas.index(st.session_state.last_search["area"])
        

        with st.form(key="search_form"):
            area = st.selectbox("Choose an area", uk_areas, index=default_index)
            query = st.text_input(
                "Search", 
                placeholder="Street name here...",
                help="Enter a place/area name. For street search, use the fields below."
            )
            
            with st.expander("Search by Postcode District + Street"):
                st.caption("To search by street, provide BOTH the postcode district AND street name.")
                col_district, col_street = st.columns(2)
                with col_district:
                    postcode_district = st.text_input(
                        "Postcode District",
                        placeholder="e.g. SW1A, NG8, SS0",
                        help="The first part of a postcode (before the space)"
                    )
                with col_street:
                    street_name = st.text_input(
                        "Street Name",
                        placeholder="e.g. Downing Street, High Street",
                        help="Street name within the postcode district"
                    )
            
            submitted = st.form_submit_button("Search", use_container_width=True, type="primary")
    
    return area, query, postcode_district, street_name, submitted


def initialise_session_state():
    """Initialise session state variables."""
    if "results" not in st.session_state:
        st.session_state.results = []
    if "last_search" not in st.session_state:
        st.session_state.last_search = {"area": None, "query": None}
    if "current_view" not in st.session_state:
        st.session_state.current_view = "properties"
    if "detected_area" not in st.session_state:
        st.session_state.detected_area = None

    initialise_household_session_state()


def handle_search_submission(submitted, area, query, postcode_district, street_name):
    """Handle search form submission."""
    if submitted:
        error_message = validate_search_input(query, postcode_district, street_name)
        
        if error_message:
            st.error(error_message)
        else:
            with st.spinner("Searching properties..."): 
                results = search_properties(
                    area=area, 
                    query=query,
                    postcode_district=postcode_district.strip() if postcode_district else "",
                    street=street_name.strip() if street_name else ""
                )
                st.session_state.results = results
                
                # detect area, then update dropdown to area name
                detected = get_detected_area_from_properties(results)
                if detected:
                    st.session_state.detected_area = detected
                    st.session_state.last_search = {"area": detected, "query": query or f"{postcode_district} {street_name}".strip()}
                else:
                    st.session_state.last_search = {"area": area, "query": query or f"{postcode_district} {street_name}".strip()}


def render_navigation_tabs():
    """Render navigation tabs for view selection."""
    tab_col1, tab_col2 = st.columns(2)

    with tab_col1:
        if st.button("🏘️ Properties", use_container_width=True, 
                     type="primary" if st.session_state.current_view == "properties" else "secondary"):
            st.session_state.current_view = "properties"
            st.rerun()

    with tab_col2:
        if st.button("🗺️ Heatmap", use_container_width=True,
                     type="primary" if st.session_state.current_view == "heatmap" else "secondary"):
            st.session_state.current_view = "heatmap"
            st.rerun()


def render_properties_view(last):
    """Render individual properties grid view."""
    st.subheader("Individual Properties")
    
    if last["area"] is None:
        st.info("👆 Select an area and click Search to see property listings")
        return
    
    results = st.session_state.results
    
    if not results:
        st.warning("No properties found. Try a different search.")
        return
    
    # Sort controls
    sort_col1, sort_col2 = st.columns([3, 1])
    with sort_col1:
        st.success(f"Found **{len(results)}** properties in **{last['area']}**")
    with sort_col2:
        sort_option = st.selectbox(
            "Sort by",
            options=[
                "Default",
                "Current Price: Low to High",
                "Current Price: High to Low",
                "Future Price: Low to High",
                "Future Price: High to Low"
            ],
            label_visibility="collapsed"
        )

    sorted_results = sort_properties(results, sort_option)
    
    # Display properties in 3-column grid
    columns_per_row = 3
    for row_start in range(0, len(sorted_results), columns_per_row):
        cols = st.columns(columns_per_row)
        for col_idx, col in enumerate(cols):
            prop_idx = row_start + col_idx
            if prop_idx < len(sorted_results):
                prop = sorted_results[prop_idx]
                
                with col:
                    with st.container(border=True):
                        # address
                        st.markdown(f"**{prop.get('address', 'Unknown')}**")
                        
                        # postcode
                        postcode = prop.get("postcode", "")
                        if postcode:
                            st.caption(f"📮 {postcode}")
                        
                        # prices
                        price_col1, price_col2 = st.columns(2)
                        with price_col1:
                            st.caption("Current")
                            current_price = prop.get("current_price")
                            if current_price:
                                st.markdown(f"**£{current_price:,.0f}**")
                            else:
                                st.markdown("**N/A**")
                        
                        with price_col2:
                            st.caption("Future")
                            future_price = prop.get("future_price")
                            if future_price:
                                st.markdown(f"**£{future_price:,.0f}**")
                            else:
                                st.markdown("**—**")
                        
                        # view deets
                        if st.button("View Details", key=f"view_{prop_idx}", use_container_width=True):
                            st.session_state.selected_property = prop
                            st.rerun()


def render_heatmap_view(last):
    """Render heatmap view (placeholder)."""
    st.subheader("🗺️ Heatmap View")
    
    if last["area"] is None:
        st.info("Search for properties to see the heatmap")
        return
    
    results = st.session_state.results
    
    if not results:
        st.warning("No properties found.")
        return
    
    st.success(f"Found {len(results)} properties")
    st.info("🚧 Heatmap visualisation coming soon...")
    
    # Placeholder
    with st.container(border=True):
        st.markdown("""
        <div style="
            height: 400px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        ">
            Heatmap Coming Soon
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    initialise_session_state()
    
    # Check if viewing property details
    if has_selected_property():
        render_household_details_view(st.session_state.selected_property)
    else:
        # Main search view
        area, query, postcode_district, street_name, submitted = render_sidebar_search()
        handle_search_submission(submitted, area, query, postcode_district, street_name)
        
        last = st.session_state.last_search
        
        render_navigation_tabs()
        st.divider()
        
        if st.session_state.current_view == "properties":
            render_properties_view(last)
        elif st.session_state.current_view == "heatmap":
            render_heatmap_view(last)