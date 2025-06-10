import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import calendar

# --- Main App Interface ---
st.set_page_config(layout="wide")

# --- Initialize ALL Session State variables at the top ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'selected_month_num' not in st.session_state:
    st.session_state.selected_month_num = 0 # Default to All Months

# Initialize activity filters
if 'filter_primary_activities' not in st.session_state:
    st.session_state.filter_primary_activities = False
if 'filter_plant_out_activity' not in st.session_state:
    st.session_state.filter_plant_out_activity = False
if 'filter_flower_activity' not in st.session_state:
    st.session_state.filter_flower_activity = False

# Initialize sunlight checkboxes (NEW)
# We'll populate `all_light_types_options` once, then create session state keys for each
if 'all_light_types_options' not in st.session_state:
    st.session_state.all_light_types_options = []


# --- Inject Custom CSS for Tighter Spacing ---
st.markdown("""
    <style>
        .no-margin-p {
            margin-top: 0rem;
            margin-bottom: 0rem;
            line-height: 1.2; /* Adjust line height for tighter text if desired */
        }
        .detail-item {
            margin-bottom: 0.5rem;
        }
        p {
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.title("Controls")

# --- File and Column Mapping Configuration ---
FILE_OPTIONS = {
    "Annuals From Seed": "Annuals_by_Seed.csv",
    "Perennials From Seed": "Perennials_by_Seed.csv",
    "Perennials & Shrubs From Cuttings": "Perennials_Shrubs_by_Cutting.csv",
    "Perennials by Division": "Perennials_by_Division.csv",
    "Bulbs Corms & Tubers": "Bulbs_Corms_Tubers.csv"
}

COLUMN_MAPPINGS = {
    "Annuals From Seed": {'Sow': ('Sow Start', 'Sow End'), 'Plant Out': ('Plant Out Start', 'Plant Out End'), 'Flower': ('Flower Start', 'Flower End')},
    "Perennials From Seed": {'Sow': ('Sow Start', 'Sow End'), 'Plant Out': ('Plant Out Start', 'Plant Out End'), 'Flower': ('Flower Start', 'Flower End')},
    "Perennials & Shrubs From Cuttings": {'Cut': ('Cut Start', 'Cut End'), 'Plant Out': ('Plant Out Start', 'Plant Out End'), 'Flower': ('Flower Start', 'Flower End')},
    "Perennials by Division": {'Division': ('Division Start', 'Division End'), 'Flower': ('Flower Start', 'Flower End')},
    "Bulbs Corms & Tubers": {'Plant': ('Plant Start', 'Plant End'), 'Flower': ('Flower Start', 'Flower End')}
}

# --- Plant Details Configuration Mapping ---
PLANT_DETAILS_MAPPING = {
    "Annuals From Seed": [
        {'label': 'Germination Temperature Range', 'cols': ['Germ Temp Min (°C)', 'Germ Temp Max (°C)'], 'type': 'range', 'unit': '°C'},
        {'label': 'Germination Days Range', 'cols': ['Germ Days Min', 'Germ Days Max'], 'type': 'range', 'unit': ' days'},
        {'label': 'Height', 'cols': ['Height (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spread', 'cols': ['Spread (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''},
        {'label': 'Notes', 'cols': ['Notes'], 'type': 'single', 'unit': ''},
    ],
    "Perennials & Shrubs From Cuttings": [
        {'label': 'Root Temperature Range', 'cols': ['Root Temp Min (°C)', 'Root Temp Max (°C)'], 'type': 'range', 'unit': '°C'},
        {'label': 'Days to Root', 'cols': ['Root Days Min', 'Root Days Max'], 'type': 'range', 'unit': ' days'},
        {'label': 'Height', 'cols': ['Height (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spread', 'cols': ['Spread (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''},
    ],
    "Perennials From Seed": [
        {'label': 'Height', 'cols': ['Height (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spread', 'cols': ['Spread (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''},
        {'label': 'Notes', 'cols': ['Notes'], 'type': 'single', 'unit': ''},
    ],
    "Perennials by Division": [
        {'label': 'Height', 'cols': ['Height (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spread', 'cols': ['Spread (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''},
        {'label': 'Notes', 'cols': ['Notes'], 'type': 'single', 'unit': ''},
    ],
    "Bulbs Corms & Tubers": [
        {'label': 'Height', 'cols': ['Height (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spread', 'cols': ['Spread (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ' cm'},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''},
    ],
}

LEGEND_SORT_ORDER = {
    'Sow': 1,
    'Cut': 2,
    'Softwood Cutting': 3,
    'Semi-Ripe Cutting': 4,
    'Hardwood Cutting': 5,
    'Division': 6,
    'Plant': 7,
    'Plant Out': 8,
    'Flower': 9
}

# --- Advanced Color Logic Function ---
def get_bar_color_and_legend(option, activity, row_data):
    """
    Determines the bar color and legend text based on the selected option,
    the activity, and data from the row (for cutting types).
    """
    if option == "Perennials & Shrubs From Cuttings":
        if activity == 'Cut':
            cutting_type = row_data.get('Cutting Type', '').lower()
            if 'softwood' in cutting_type:
                return 'limegreen', 'Softwood Cutting'
            elif 'semi-ripe' in cutting_type:
                return 'darkgreen', 'Semi-Ripe Cutting'
            elif 'hardwood' in cutting_type:
                return 'saddlebrown', 'Hardwood Cutting'
            else:
                return 'purple', 'Cut'
        elif activity == 'Plant Out':
            return 'blue', 'Plant Out'
        elif activity == 'Flower':
            return 'yellow', 'Flower'
            
    elif option == "Perennials by Division":
        if activity == 'Division':
            return 'blue', 'Division'
        elif activity == 'Flower':
            return 'yellow', 'Flower'
            
    elif option == "Bulbs Corms & Tubers":
        if activity == 'Plant':
            return 'green', 'Plant'
        elif activity == 'Flower':
            return 'yellow', 'Flower'
            
    else: # Default rules for Seed files
        if activity == 'Sow':
            return 'blue', 'Sow'
        elif activity == 'Plant Out':
            return 'green', 'Plant Out'
        elif activity == 'Flower':
            return 'yellow', 'Flower'
            
    return 'grey', activity # Fallback color

# --- Calendar Selection (FIRST) ---
selected_option = st.sidebar.selectbox("Choose a Calendar to View:", options=list(FILE_OPTIONS.keys()))
LOCAL_CSV_FILE = FILE_OPTIONS[selected_option]
activity_periods = COLUMN_MAPPINGS[selected_option]


# --- Data Loading (using st.cache_data for efficiency) ---
@st.cache_data
def load_data(file_path):
    df_loaded = pd.read_csv(file_path, skipinitialspace=True)
    df_loaded.columns = df_loaded.columns.str.strip()
    df_loaded.dropna(subset=['Common Name'], inplace=True)
    df_loaded = df_loaded[df_loaded['Common Name'] != ''].reset_index(drop=True)
    return df_loaded

# --- Search Plants (SECOND) ---
st.sidebar.subheader("Search Plants")
# st.session_state.search_query is initialized at the top
search_query = st.sidebar.text_input("Enter plant name (e.g., 'rose', 'sweet pea'):", value=st.session_state.search_query, key='search_input')
st.session_state.search_query = search_query # Update session state


# --- App Body (Chart Generation - needs initial df to get plant_names for selectbox) ---
st.title(selected_option)

try:
    df = load_data(LOCAL_CSV_FILE)

    # Apply search filter first to get correct plant_names for details and filters
    if st.session_state.search_query:
        df = df[df['Common Name'].str.contains(st.session_state.search_query, case=False, na=False)].reset_index(drop=True)
        if df.empty:
            st.warning(f"No plants found matching '{st.session_state.search_query}' in this calendar type.")
            st.stop() # Exit the script early

    # If df is empty after loading or search, handle it before proceeding
    if df.empty:
        st.warning(f"No plants loaded from '{LOCAL_CSV_FILE}' or none found matching the search query.")
        st.stop() # Exit the script early

    plant_names = df['Common Name'].unique() # Define plant_names here, used for selectbox

    st.success(f"Successfully loaded {len(df)} plants from '{LOCAL_CSV_FILE}'!", icon="✅")

    # --- Plant Details Expander (THIRD - relies on plant_names) ---
    if len(plant_names) > 0: # Check if there are any plants after search
        with st.sidebar.expander("Plant Details", expanded=False):
            selected_plant_detail = st.selectbox(
                "Select a plant to see details:",
                options=plant_names,
                key='detail_select'
            )
            
            if selected_plant_detail:
                plant_data = df[df['Common Name'] == selected_plant_detail].iloc[0]

                def get_clean_value(row_data, col_name):
                    value = row_data.get(col_name, None)
                    if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                        return None
                    return str(value).strip()

                details_config = PLANT_DETAILS_MAPPING.get(selected_option, [])    
                
                for detail_item in details_config:
                    label = detail_item['label']
                    col_names = detail_item['cols']
                    item_type = detail_item['type']
                    unit = detail_item['unit']

                    if item_type == 'range':
                        min_val = get_clean_value(plant_data, col_names[0])
                        max_val = get_clean_value(plant_data, col_names[1])
                        display_text = ""
                        if min_val is not None and max_val is not None:
                            display_text = f"{min_val}{unit} - {max_val}{unit}"
                        elif min_val is not None:
                            display_text = f"Min: {min_val}{unit}"
                        elif max_val is not None:
                            display_text = f"Max: {max_val}{unit}"
                        
                        if display_text:
                            st.markdown(f"<div class='detail-item'><p class='no-margin-p'><b>{label}</b></p><p class='no-margin-p'>{display_text}</p></div>", unsafe_allow_html=True)
                    elif item_type == 'single':
                        value = get_clean_value(plant_data, col_names[0])
                        if value is not None:
                            st.markdown(f"<div class='detail-item'><p class='no-margin-p'><b>{label}</b></p><p class='no-margin-p'>{value}{unit}</p></div>", unsafe_allow_html=True)
                
    else:
        st.sidebar.info("No plants available to display details for.")


    # --- Filters Expander (FOURTH) ---
    with st.sidebar.expander("Filters", expanded=False):
        # --- Month Selection (Moved back here) ---
        month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        month_names_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        st.subheader("Filter by Month & Activities") # Consolidated subheader

        month_options = [("All Months", 0)] + [(name, i+1) for i, name in enumerate(month_names_list)]
        
        # default_month_index_filter correctly uses st.session_state.selected_month_num
        default_month_index_filter = 0 
        for idx, (name, num) in enumerate(month_options):
            if num == st.session_state.selected_month_num:
                default_month_index_filter = idx
                break

        selected_month_name, selected_month_num = st.selectbox( # Use st.selectbox (not st.sidebar.selectbox here)
            "Select Month:",
            options=month_options,
            index=default_month_index_filter,
            format_func=lambda x: x[0],
            key='month_selector_filter_in_expander', # Changed key to avoid conflict
            on_change=lambda: setattr(st.session_state, 'selected_month_num', st.session_state.month_selector_filter_in_expander[1])
        )
        # selected_month_num is directly used below, so no need to update session_state.selected_month_num = selected_month_num

        # Activity checkboxes remain as individual checkboxes
        # st.session_state.filter_primary_activities etc. are initialized at top
        filter_primary_activities = st.checkbox(
            f"Primary Activities (Sow/Cut/Divide/Plant)",
            value=st.session_state.filter_primary_activities, key='check_primary_activities',
            on_change=lambda: setattr(st.session_state, 'filter_primary_activities', st.session_state.check_primary_activities)
        )
        filter_plant_out_activity = st.checkbox(
            f"Plant Out",
            value=st.session_state.filter_plant_out_activity, key='check_plant_out',
            on_change=lambda: setattr(st.session_state, 'filter_plant_out_activity', st.session_state.check_plant_out)
        )
        filter_flower_activity = st.checkbox(
            f"Flower",
            value=st.session_state.filter_flower_activity, key='check_flower',
            on_change=lambda: setattr(st.session_state, 'filter_flower_activity', st.session_state.check_flower)
        )
        
        st.subheader("Filter by Characteristics")

        # Dynamically get unique light types for checkboxes
        temp_df_for_light_options = load_data(LOCAL_CSV_FILE)
        all_light_types = sorted(temp_df_for_light_options['Light'].dropna().astype(str).unique().tolist())

        selected_light_types_checkboxes = [] # List to hold selected sunlight types

        # Create individual checkboxes for each sunlight type
        if all_light_types:
            st.write("Sunlight Requirements:")
            for light_type in all_light_types:
                # Ensure each checkbox has a unique key and its state is managed in session_state
                key_name = f"light_checkbox_{light_type.replace(' ', '_').replace('.', '')}"
                if key_name not in st.session_state:
                    st.session_state[key_name] = False # Initialize to unchecked

                if st.checkbox(
                    light_type,
                    value=st.session_state[key_name],
                    key=key_name,
                    on_change=lambda lt=light_type, kn=key_name: setattr(st.session_state, kn, st.session_state[kn])
                ):
                    selected_light_types_checkboxes.append(light_type)
        else:
            st.info("No sunlight types found in data.")

        # Update a single session state variable that holds the list of selected light types
        st.session_state.selected_light_types = selected_light_types_checkboxes


        # Reset Filters Button
        if st.button("Reset All Filters", key='reset_filters_button'):
            st.session_state.search_query = ""
            st.session_state.selected_month_num = 0 # Reset to All Months
            st.session_state.filter_primary_activities = False
            st.session_state.filter_plant_out_activity = False
            st.session_state.filter_flower_activity = False
            
            # Reset all dynamic sunlight checkboxes
            for light_type in all_light_types:
                key_name = f"light_checkbox_{light_type.replace(' ', '_').replace('.', '')}"
                if key_name in st.session_state:
                    st.session_state[key_name] = False
            st.session_state.selected_light_types = [] # Clear the list of selected types
            
            st.rerun()

    # --- Data Quality Check Section (FIFTH) ---
    with st.sidebar.expander("Data Quality Check", expanded=False):
        st.subheader("Check Your Data")
        
        if st.button("Run Quality Check", key='run_quality_check'):
            st.write("### Quality Check Results for " + selected_option)
            
            critical_columns = ['Height (cm)', 'Spread (cm)', 'Light', 'Water Need', 'Pollinator Friendly']
            
            current_df_for_quality_check = load_data(LOCAL_CSV_FILE)
            
            missing_data_plants = {}
            for col in critical_columns:
                if col in current_df_for_quality_check.columns:
                    missing_mask = current_df_for_quality_check[col].isna() | (current_df_for_quality_check[col].astype(str).str.strip() == '')
                    plants_with_missing = current_df_for_quality_check[missing_mask]['Common Name'].tolist()
                    
                    if plants_with_missing:
                        missing_data_plants[col] = plants_with_missing
                else:
                    st.warning(f"Column '{col}' not found in '{LOCAL_CSV_FILE}'. Skipping check for this column.")

            if not missing_data_plants:
                st.success("✅ No critical missing data found in the selected columns!")
            else:
                st.warning("⚠️ Plants with missing critical data:")
                for col, plants in missing_data_plants.items():
                    st.markdown(f"**Missing '{col}':**")
                    for plant_name in plants:
                        rhs_search_url = f"https://www.rhs.org.uk/search?query={plant_name.replace(' ', '+')}"
                        st.markdown(f"- [{plant_name}]({rhs_search_url})")
                st.info("Consider researching these plants on the RHS website to fill in the gaps. "
                        "Remember to save your CSV changes for the app to pick them up!")

            st.markdown("---")
            st.markdown("### Compare with Local Reference (Future Enhancement)")
            st.markdown("This section would compare your current data against a manually curated 'golden standard' CSV "
                        "to highlight discrepancies beyond just missing values.")

    # --- Apply Filters to DataFrame (this happens after all sidebar inputs are gathered) ---
    # Helper function for month-in_range
    def is_month_in_range(start_month_str, end_month_str, check_m_num, month_map_dict):
        if pd.isna(start_month_str) or pd.isna(end_month_str):
            return False
        start_m = month_map_dict.get(str(start_month_str).strip())
        end_m = month_map_dict.get(str(end_month_str).strip())
        if start_m is None or end_m is None:
            return False
        if start_m <= end_m:
            return start_m <= check_m_num <= end_m
        else:
            return check_m_num >= start_m or check_m_num <= end_m

    # Apply month/activity filters
    # These filters now use the selected_month_num from the global month selector
    if selected_month_num != 0 and (filter_primary_activities or filter_plant_out_activity or filter_flower_activity):
        combined_mask_month = pd.Series([False] * len(df)) # Initialize mask for this filter block
        
        for activity_key, (start_col, end_col) in activity_periods.items():
            if start_col in df.columns and end_col in df.columns:
                # Only apply activity filter if the corresponding checkbox is true AND month is selected
                if selected_month_num != 0: # Ensure month filter is active if any activity checkbox is active
                    if filter_primary_activities and activity_key in ['Sow', 'Cut', 'Division', 'Plant']:
                        activity_mask = df.apply(lambda row: is_month_in_range(row[start_col], row[end_col], selected_month_num, month_map), axis=1)
                        combined_mask_month = combined_mask_month | activity_mask
                    if filter_plant_out_activity and activity_key == 'Plant Out':
                        activity_mask = df.apply(lambda row: is_month_in_range(row[start_col], row[end_col], selected_month_num, month_map), axis=1)
                        combined_mask_month = combined_mask_month | activity_mask
                    if filter_flower_activity and activity_key == 'Flower':
                        activity_mask = df.apply(lambda row: is_month_in_range(row[start_col], row[end_col], selected_month_num, month_map), axis=1)
                        combined_mask_month = combined_mask_month | activity_mask
        
        df = df[combined_mask_month].reset_index(drop=True)
        if df.empty:
            st.warning(f"No plants found for the selected activities in {selected_month_name} for this calendar type, after applying name search and other filters.")
            st.stop()

    # Apply Sunlight filter (now uses selected_light_types from checkboxes)
    if st.session_state.selected_light_types:
        if 'Light' in df.columns:
            # Filter where 'Light' column value is IN the list of selected checkbox types
            df = df[df['Light'].astype(str).isin(st.session_state.selected_light_types)].reset_index(drop=True)
        else:
            st.warning("'Light' column not found in the current dataset. Skipping sunlight filter.")

        if df.empty:
            st.warning(f"No plants found for the selected Sunlight Requirement(s): {', '.join(st.session_state.selected_light_types)}.")
            st.stop()
            
    # Re-evaluate plant_names after all filters for the chart
    plant_names = df['Common Name'].unique()
    if len(plant_names) == 0:
        st.warning("No plants left after applying all filters. Adjust your filter selections.")
        st.stop() # Stop if no plants to plot

    # --- Chart Drawing (LAST) ---
    fig = go.Figure()
    
    bar_width, row_spacing = 0.28, 0.88
    num_activities = len(activity_periods)
    if num_activities > 1: base_offsets = np.linspace(-bar_width * (num_activities - 1) / 2, bar_width * (num_activities - 1) / 2, num_activities)
    else: base_offsets = [0]
    offsets = {list(activity_periods.keys())[i]: offset for i, offset in enumerate(base_offsets)}

    current_year = date.today().year
    def to_day_of_year(dt): return dt.timetuple().tm_yday

    all_traces = []
    
    for i, plant_name in enumerate(plant_names):
        row_data = df[df['Common Name'] == plant_name].iloc[0]
        for activity, (start_col, end_col) in activity_periods.items():
            start_month_str, end_month_str = row_data.get(start_col), row_data.get(end_col)
            if pd.notna(start_month_str) and pd.notna(end_month_str):
                start_month, end_month = month_map.get(str(start_month_str).strip()), month_map.get(str(end_month_str).strip())
                if start_month is None or end_month is None: continue
                
                bar_color, legend_name = get_bar_color_and_legend(selected_option, activity, row_data)
                
                def create_bar_trace(start_day, end_day, legend_name_for_trace):
                    return go.Bar(
                        y=[(i * row_spacing) + offsets[activity]],
                        x=[end_day - start_day + 1],
                        base=[start_day],
                        orientation='h',
                        marker_color=bar_color,
                        name=legend_name_for_trace,
                        width=bar_width,
                        hoverinfo='none',
                        marker_line_width=0,
                        textposition='none',
                        showlegend=True,
                        legendgroup=legend_name_for_trace
                    )
                    
                start_date = date(current_year, start_month, 1)
                end_month_last_day = calendar.monthrange(current_year, end_month)[1]
                end_date = date(current_year, end_month, end_month_last_day)

                if end_month < start_month:
                    trace1 = create_bar_trace(to_day_of_year(start_date), 365, legend_name)
                    all_traces.append((legend_name, trace1))
                    trace2 = create_bar_trace(1, to_day_of_year(date(current_year, end_month, end_month_last_day)), legend_name)
                    all_traces.append((legend_name, trace2))
                else:
                    trace = create_bar_trace(to_day_of_year(start_date), to_day_of_year(end_date), legend_name)
                    all_traces.append((legend_name, trace))

    sorted_traces = sorted(all_traces, key=lambda x: LEGEND_SORT_ORDER.get(x[0], 999))

    legend_items_added_to_figure = set()
    for legend_name, trace in sorted_traces:
        if legend_name not in legend_items_added_to_figure:
            trace.showlegend = True
            legend_items_added_to_figure.add(legend_name)
        else:
            trace.showlegend = False
        fig.add_trace(trace)

    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    bold_month_names = [f'<b>{name}</b>' for name in month_names]    
    
    month_midpoints = [to_day_of_year(date(current_year, m, 15)) for m in range(1, 13)]
    month_boundaries = [to_day_of_year(date(current_year, m, 1)) for m in range(1, 13)]; month_boundaries.append(366)
    shapes = []
    total_y_span = (len(plant_names) - 1) * row_spacing + (bar_width * num_activities) if len(plant_names) > 0 else 10

    for x_pos in month_boundaries:
        shapes.append(go.layout.Shape(type="line", x0=x_pos, y0=-0.5, x1=x_pos, y1=total_y_span, line=dict(color="DimGray", width=1), layer='below'))

    frost_color = 'rgba(70, 130, 180, 0.3)';
    shapes.append(go.layout.Shape(type="rect", x0=1, y0=-0.5, x1=to_day_of_year(date(current_year, 4, 1)), y1=total_y_span, fillcolor=frost_color, line_width=0, layer='below'))
    shapes.append(go.layout.Shape(type="rect", x0=to_day_of_year(date(current_year, 10, 1)), y0=-0.5, x1=366, y1=total_y_span, fillcolor=frost_color, line_width=0, layer='below'))
    
    bold_plant_names = [f'<b>{name}</b>' for name in plant_names]
    y_tick_vals = [i * row_spacing for i in range(len(plant_names))]

    fig.update_layout(
        height=max(600, len(plant_names) * 40),
        barmode='overlay',
        showlegend=True,
        margin=dict(l=150, r=20, t=50, b=50),
        xaxis=dict(
            tickvals=month_midpoints,
            ticktext=bold_month_names,
            showgrid=False,
            range=[1, 366],
            tickfont=dict(color='black'),
            side='top'
        ),
        yaxis=dict(
            tickvals=y_tick_vals,
            ticktext=bold_plant_names,
            autorange="reversed",
            tickfont=dict(color='black')
        ),
        plot_bgcolor='white',
        legend=dict(title_text='Activity'),
        shapes=shapes
    )
    
    st.plotly_chart(fig, use_container_width=True)


except FileNotFoundError:
    st.error(f"File not found: '{LOCAL_CSV_FILE}'. Please make sure all your CSV files are in the same folder as the app.")
except Exception as e:
    st.error(f"An error occurred while processing '{LOCAL_CSV_FILE}': {e}")
    import traceback
    st.text(traceback.format_exc())