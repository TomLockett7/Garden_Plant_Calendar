import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import calendar
import os # Import the os module for path handling

# --- Configuration for Local Development ---
# Define the directory where your CSV files are located.
# It's good practice to keep them in a 'data' subfolder,
# but if they are in the same directory as your app.py, set this to '.'
DATA_DIR = '.' # CORRECTED: Changed from 'data' to '.' as CSVs are in the same folder as app.py


# --- Main App Interface ---
# Keeping layout="wide" for optimal PC viewing.
st.set_page_config(layout="wide")

# --- Initialize ALL Session State variables centrally at the top ---
# This ensures all necessary keys exist before any widgets try to access them,
# preventing 'KeyError' issues and improving code clarity.
if 'app_initialized' not in st.session_state:
    st.session_state.app_initialized = True # Flag for one-time initialization
    st.session_state.search_query = ""
    st.session_state.selected_month_num = date.today().month # Default month on first load
    st.session_state.filter_primary_activities = False
    st.session_state.filter_plant_out_activity = False
    st.session_state.filter_flower_activity = False
    st.session_state.selected_light_types = [] # List to hold selected light types checkboxes
    st.session_state.sort_order = "Alphabetical (A-Z)" # New default sort order


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
    "Perennials From Seed": {'Sow': ('Sow Start (Indoors)', 'Sow End'), 'Plant Out': ('Plant Out Start (Outdoors)', 'Plant Out End'), 'Flower': ('Flower Start', 'Flower End')}, # CORRECTED Column Names
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
        {'label': 'Notes', 'cols': ['Notes'], 'type': 'single', 'unit': ''}, # Added Notes
    ],
    # MODIFIED: Added germination details for Perennials From Seed
    "Perennials From Seed": [
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
        {'label': 'Spacing', 'cols': ['Spacing (cm)'], 'type': 'single', 'unit': ''},
        {'label': 'Light', 'cols': ['Light'], 'type': 'single', 'unit': ''},
        {'label': 'Water Need', 'cols': ['Water Need'], 'type': 'single', 'unit': ''},
        {'label': 'Pollinator Friendly', 'cols': ['Pollinator Friendly'], 'type': 'single', 'unit': ''},
        {'label': 'How to Overwinter', 'cols': ['How to Overwinter'], 'type': 'single', 'unit': ''}, # CORRECTED: Changed back to 'How to Overwinter'
        {'label': 'Notes', 'cols': ['Notes'], 'type': 'single', 'unit': ''},
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
# Construct full path to the CSV file
LOCAL_CSV_FILE = os.path.join(DATA_DIR, FILE_OPTIONS[selected_option])
activity_periods = COLUMN_MAPPINGS[selected_option]


# --- Data Loading (using st.cache_data for efficiency) ---
@st.cache_data
def load_data(file_path):
    # Determine the correct 'Common Name' column based on the selected file
    common_name_col_map = {
        "Annuals_by_Seed.csv": "Common Name",  # CORRECTED: Changed from "Common Name (Scientific)"
        "Bulbs_Corms_Tubers.csv": "Common Name",
        "Perennials_by_Division.csv": "Common Name",
        "Perennials_by_Seed.csv": "Common Name",
        "Perennials_Shrubs_by_Cutting.csv": "Common Name"
    }
    
    file_name = os.path.basename(file_path)
    common_name_column = common_name_col_map.get(file_name, "Common Name") # Default to 'Common Name'

    # Ensure DATA_DIR exists if it's a subfolder
    if DATA_DIR != '.' and not os.path.exists(DATA_DIR):
        st.error(f"Error: Data directory '{DATA_DIR}' not found. Please create this folder and place your CSVs inside, or set DATA_DIR = '.' if CSVs are in the same folder as app.py.")
        st.stop()
        
    # Check if the specific CSV file exists before attempting to load
    if not os.path.exists(file_path):
        st.error(f"Error: CSV file not found at '{file_path}'. Please ensure your CSVs are in the '{DATA_DIR}' folder and correctly named.")
        st.stop()

    df_loaded = pd.read_csv(file_path, skipinitialspace=True)
    df_loaded.columns = df_loaded.columns.str.strip()
    
    # Drop rows where the determined 'Common Name' column is missing or empty, then reset index
    if common_name_column in df_loaded.columns:
        df_loaded.dropna(subset=[common_name_column], inplace=True)
        df_loaded = df_loaded[df_loaded[common_name_column] != ''].reset_index(drop=True)
    else:
        st.error(f"Error: Expected column '{common_name_column}' not found in '{file_name}'. Please check your CSV file.")
        st.stop()
    
    return df_loaded, common_name_column # Return both DataFrame and the common name column name

# --- Search Plants (SECOND) ---
st.sidebar.subheader("Search Plants")
search_query = st.sidebar.text_input("Enter plant name (e.g., 'rose', 'sweet pea'):", value=st.session_state.search_query, key='search_input')
st.session_state.search_query = search_query # Update session state


# --- App Body (Chart Generation - needs initial df to get plant_names for selectbox) ---
st.title(selected_option)

try:
    # Load data and get the correct common name column
    df, common_name_column = load_data(LOCAL_CSV_FILE)

    if st.session_state.search_query:
        df = df[df[common_name_column].str.contains(st.session_state.search_query, case=False, na=False)].reset_index(drop=True)
        if df.empty:
            st.warning(f"No plants found matching '{st.session_state.search_query}' in this calendar type.")
            st.stop() # Exit the script early

    # If df is empty after initial load or search, stop here
    if df.empty:
        st.warning(f"No plants loaded from '{os.path.basename(LOCAL_CSV_FILE)}' or none found matching the search query.")
        st.stop()

    # Pre-filter all_light_types_options on initial load or if calendar changes
    # This ensures that filter options are relevant to the *selected calendar file*
    # and don't reset every time other filters are touched.
    if 'last_selected_option' not in st.session_state or st.session_state.last_selected_option != selected_option:
        st.session_state.all_light_types_options = sorted(df['Light'].dropna().astype(str).unique().tolist())
        st.session_state.last_selected_option = selected_option


    # --- Plant Details Expander (THIRD - relies on plant_names after initial load/search) ---
    # `plant_names` will be refined after all filters, but needs to exist here for the selectbox
    current_plant_names_pre_filter = df[common_name_column].unique()
    if len(current_plant_names_pre_filter) > 0:
        with st.sidebar.expander("Plant Details", expanded=False):
            selected_plant_detail = st.selectbox(
                "Select a plant to see details:",
                options=current_plant_names_pre_filter, # Use pre-filtered names for initial detail selection
                key='detail_select'
            )
            
            if selected_plant_detail:
                plant_data = df[df[common_name_column] == selected_plant_detail].iloc[0]

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
                        # Always display the label, show "N/A" if value is None
                        display_value = value if value is not None else "N/A"
                        st.markdown(f"<div class='detail-item'><p class='no-margin-p'><b>{label}</b></p><p class='no-margin-p'>{display_value}{unit}</p></div>", unsafe_allow_html=True)
                
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
        
        # Activity checkboxes remain as individual checkboxes
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

        # Create individual checkboxes for each sunlight type from cached options
        if st.session_state.all_light_types_options:
            st.write("Sunlight Requirements:")
            # Dynamically update session state for each light type checkbox
            selected_light_types_from_checkboxes = []
            for light_type in st.session_state.all_light_types_options:
                key_name = f"light_checkbox_{light_type.replace(' ', '_').replace('.', '').replace('-', '_').replace('&', 'and')}" # More robust key
                if key_name not in st.session_state:
                    st.session_state[key_name] = False # Initialize to unchecked

                # If the checkbox is checked, add its value to the list
                if st.checkbox(
                    light_type,
                    value=st.session_state[key_name],
                    key=key_name,
                    # on_change is implicitly handled due to value binding
                ):
                    selected_light_types_from_checkboxes.append(light_type)
            # Update the central selected_light_types list in session state
            st.session_state.selected_light_types = selected_light_types_from_checkboxes
        else:
            st.info("No sunlight types found in data for current calendar type.")


        # Reset Filters Button
        if st.button("Reset All Filters", key='reset_filters_button'):
            st.session_state.search_query = ""
            st.session_state.selected_month_num = date.today().month # Reset to current month
            st.session_state.filter_primary_activities = False
            st.session_state.filter_plant_out_activity = False
            st.session_state.filter_flower_activity = False
            
            # Reset all dynamic sunlight checkboxes states
            for light_type in st.session_state.all_light_types_options:
                key_name = f"light_checkbox_{light_type.replace(' ', '_').replace('.', '').replace('-', '_').replace('&', 'and')}"
                if key_name in st.session_state: # Only reset if key exists
                    st.session_state[key_name] = False
            st.session_state.selected_light_types = [] # Clear the list of selected types
            
            st.rerun() # Rerun the app to apply the resets immediately

    # --- Data Quality Check Section (FIFTH) ---
    with st.sidebar.expander("Data Quality Check", expanded=False):
        st.subheader("Check Your Data")
        
        if st.button("Run Quality Check", key='run_quality_check'):
            st.write("### Quality Check Results for " + selected_option)
            
            critical_columns = ['Height (cm)', 'Spread (cm)', 'Light', 'Water Need', 'Pollinator Friendly']
            
            current_df_for_quality_check, common_name_column_qc = load_data(LOCAL_CSV_FILE) # Get common_name_column here too
            
            missing_data_plants = {}
            for col in critical_columns:
                if col in current_df_for_quality_check.columns:
                    missing_mask = current_df_for_quality_check[col].isna() | (current_df_for_quality_check[col].astype(str).str.strip() == '') # Corrected
                    plants_with_missing = current_df_for_quality_check[missing_mask][common_name_column_qc].tolist() # Use dynamic common_name_column
                    
                    if plants_with_missing:
                        missing_data_plants[col] = plants_with_missing
                else:
                    st.warning(f"Column '{col}' not found in '{os.path.basename(LOCAL_CSV_FILE)}'. Skipping check for this column.")

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
        else: # Range spans across year end (e.g., Nov-Feb)
            return check_m_num >= start_m or check_m_num <= end_m

    # Apply month/activity filters
    # This logic block only runs if a month is selected AND at least one activity filter is checked
    if selected_month_num != 0 and (st.session_state.filter_primary_activities or st.session_state.filter_plant_out_activity or st.session_state.filter_flower_activity):
        combined_mask_month = pd.Series([False] * len(df)) # Initialize mask for this filter block

        for activity_key, (start_col, end_col) in activity_periods.items():
            if start_col in df.columns and end_col in df.columns:
                # Only apply activity filter if the corresponding checkbox is true
                if st.session_state.filter_primary_activities and activity_key in ['Sow', 'Cut', 'Division', 'Plant']:
                    activity_mask = df.apply(lambda row: is_month_in_range(row[start_col], row[end_col], selected_month_num, month_map), axis=1)
                    combined_mask_month = combined_mask_month | activity_mask
                if st.session_state.filter_plant_out_activity and activity_key == 'Plant Out':
                    activity_mask = df.apply(lambda row: is_month_in_range(row[start_col], row[end_col], selected_month_num, month_map), axis=1)
                    combined_mask_month = combined_mask_month | activity_mask
                if st.session_state.filter_flower_activity and activity_key == 'Flower':
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

    # If 'All Months' is selected (selected_month_num == 0) and no activity filters are active,
    # or if any month is selected but no activity filters are active, no month/activity filtering happens.
    # If a month is selected, but *no* activity checkboxes are ticked, it effectively means "show all plants active in this month".
    # The current logic only applies the month filter if an activity checkbox is ticked. This is a design choice.
    # If you want "show all plants active in this month regardless of activity checkbox", then the `if selected_month_num != 0` check
    # should apply to the whole `combined_mask_month` logic, and if all checkboxes are false, it would effectively be an OR of all activities.
    # For now, I'll keep your current logic which means activity checkboxes must be selected for month filtering to apply.

    # Re-evaluate plant_names after all filters for the chart
    plant_names = df[common_name_column].unique() # Use dynamic common_name_column
    if len(plant_names) == 0:
        st.warning("No plants left after applying all filters. Adjust your filter selections.")
        st.stop()

    # --- Sorting the plant_names for the Y-axis ---
    plant_names_sorted = list(plant_names) # Start with current filtered names
    if st.session_state.sort_order == "Alphabetical (A-Z)":
        plant_names_sorted.sort()
    elif st.session_state.sort_order == "Alphabetical (Z-A)":
        plant_names_sorted.sort(reverse=True)
    # You could add other sorting options here if needed, e.g., by first sow date etc.

    st.sidebar.selectbox(
        "Sort Plants By:",
        options=["Alphabetical (A-Z)", "Alphabetical (Z-A)"],
        key="sort_order",
        on_change=lambda: setattr(st.session_state, 'sort_order', st.session_state.sort_order)
    )


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

    # Iterate through sorted plant names to draw traces
    for i, plant_name in enumerate(plant_names_sorted): # Use plant_names_sorted here
        row_data = df[df[common_name_column] == plant_name].iloc[0] # Use dynamic common_name_column
        for activity, (start_col, end_col) in activity_periods.items():
            start_month_str, end_month_str = row_data.get(start_col), row_data.get(end_col)
            if pd.notna(start_month_str) and pd.notna(end_month_str):
                start_month, end_month = month_map.get(str(start_month_str).strip()), month_map.get(str(end_month_str).strip())
                if start_month is None or end_month is None: continue

                bar_color, legend_name = get_bar_color_and_legend(selected_option, activity, row_data)

                def create_bar_trace(start_day, end_day, legend_name_for_trace):
                    return go.Bar(
                        y=[(i * row_spacing) + offsets[activity]], # Use current index 'i' for y-position
                        x=[end_day - start_day + 1],
                        base=[start_day],
                        orientation='h',
                        marker_color=bar_color,
                        name=legend_name_for_trace,
                        width=bar_width,
                        hoverinfo='none', # Keep this for simplicity, can be customized later
                        marker_line_width=0,
                        textposition='none',
                        showlegend=True,
                        legendgroup=legend_name_for_trace
                    )

                start_date = date(current_year, start_month, 1)
                end_month_last_day = calendar.monthrange(current_year, end_month)[1]
                end_date = date(current_year, end_month, end_month_last_day)

                if end_month < start_month: # Activity spans across year end
                    # Part 1: From start month to end of current year
                    trace1 = create_bar_trace(to_day_of_year(start_date), 365, legend_name)
                    all_traces.append((legend_name, trace1))
                    # Part 2: From beginning of year to end month
                    trace2 = create_bar_trace(1, to_day_of_year(date(current_year, end_month, end_month_last_day)), legend_name)
                    all_traces.append((legend_name, trace2))
                else: # Activity within the same year
                    trace = create_bar_trace(to_day_of_year(start_date), to_day_of_year(end_date), legend_name)
                    all_traces.append((legend_name, trace))

    # Sort traces to ensure consistent legend order
    sorted_traces = sorted(all_traces, key=lambda x: LEGEND_SORT_ORDER.get(x[0], 999))

    # Add traces to figure, ensuring legend items appear only once
    legend_items_added_to_figure = set()
    for legend_name, trace in sorted_traces:
        if legend_name not in legend_items_added_to_figure:
            trace.showlegend = True
            legend_items_added_to_figure.add(legend_name)
        else:
            trace.showlegend = False # Hide duplicate legend entries
        fig.add_trace(trace)

    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Restored bolding for month names and desktop-friendly font size for X-axis
    bold_month_names = [f'<b>{name}</b>' for name in month_names]
    x_tick_text = bold_month_names
    x_tick_font_size = 10

    month_midpoints = [to_day_of_year(date(current_year, m, 15)) for m in range(1, 13)]
    month_boundaries = [to_day_of_year(date(current_year, m, 1)) for m in range(1, 13)]; month_boundaries.append(366)
    shapes = []
    # Calculate total y-span dynamically based on number of plants and bar height
    total_y_span = (len(plant_names_sorted) - 1) * row_spacing + (bar_width * num_activities) if len(plant_names_sorted) > 0 else 10

    for x_pos in month_boundaries:
        shapes.append(go.layout.Shape(type="line", x0=x_pos, y0=-0.5, x1=x_pos, y1=total_y_span, line=dict(color="DimGray", width=1), layer='below'))

    frost_color = 'rgba(70, 130, 180, 0.3)';
    # Adjust frost dates for UK (approx. early Oct to end of March)
    shapes.append(go.layout.Shape(type="rect", x0=1, y0=-0.5, x1=to_day_of_year(date(current_year, 4, 1)), y1=total_y_span, fillcolor=frost_color, line_width=0, layer='below')) # Jan 1 to Apr 1
    # Corrected y0 parameter in the second rectangle shape (was y1=-0.5)
    shapes.append(go.layout.Shape(type="rect", x0=to_day_of_year(date(current_year, 10, 1)), y0=-0.5, x1=366, y1=total_y_span, fillcolor=frost_color, line_width=0, layer='below')) # Oct 1 to Dec 31

    # Restored bolding for plant names and desktop-friendly font size for Y-axis
    bold_plant_names_for_axis = [f'<b>{name}</b>' for name in plant_names_sorted] # Use sorted list for axis labels
    y_tick_text = bold_plant_names_for_axis
    y_tick_font_size = 10

    y_tick_vals = [i * row_spacing for i in range(len(plant_names_sorted))] # Use sorted list length

    fig.update_layout(
        height=max(600, len(plant_names_sorted) * 40), # Dynamic height, minimum 600, based on sorted list
        barmode='overlay',
        showlegend=True,
        # Restored desktop-friendly margins
        margin=dict(l=150, r=20, t=50, b=50),
        xaxis=dict(
            tickvals=month_midpoints,
            ticktext=x_tick_text,
            showgrid=False,
            range=[1, 366],
            tickfont=dict(color='black', size=x_tick_font_size),
            side='top'
        ),
        yaxis=dict(
            tickvals=y_tick_vals,
            ticktext=y_tick_text,
            autorange="reversed", # Puts first plant at top
            tickfont=dict(color='black', size=y_tick_font_size)
        ),
        plot_bgcolor='white',
        legend=dict(title_text='Activity'),
        shapes=shapes
    )

    # Chart renders to fill its container width for PC optimization
    st.plotly_chart(fig, use_container_width=True) 

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    st.info("Please check your CSV files and ensure they are correctly formatted and located in the specified 'data' folder.")
    import traceback
    st.text(traceback.format_exc())