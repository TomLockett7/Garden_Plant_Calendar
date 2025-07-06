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
    "Perennials From Seed": {'Sow': ('Sow Start', 'Sow End'), 'Plant Out': ('Plant Out Start', 'Plant Out End'), 'Flower': ('Flower Start', 'Flower End')}, # CORRECTED Column Names
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
    ]
}

# --- Utility Functions ---
@st.cache_data # Cache data loading to prevent re-reading on every rerun
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Convert month names to numerical representation for sorting and filtering
        month_to_num = {name: i for i, name in enumerate(calendar.month_abbr[1:] + calendar.month_name[1:], 1)}

        # Iterate through the specific column mappings for the selected file type
        for activity_type in COLUMN_MAPPINGS[st.session_state.selected_file_type]:
            start_col, end_col = COLUMN_MAPPINGS[st.session_state.selected_file_type][activity_type]
            if start_col in df.columns:
                df[start_col + '_Num'] = df[start_col].astype(str).str.split('-').str[0].str.strip().map(month_to_num).fillna(0).astype(int)
            if end_col in df.columns:
                df[end_col + '_Num'] = df[end_col].astype(str).str.split('-').str[-1].str.strip().map(month_to_num).fillna(0).astype(int)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the '{DATA_DIR}' directory.")
        return pd.DataFrame() # Return an empty DataFrame on error
    except Exception as e:
        st.error(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()

# Helper function to convert month number to day of year (approximate midpoint)
def month_num_to_day_of_year(month_num):
    if month_num == 0: # Handle cases where month might be 0 (e.g., if parsing failed)
        return 0
    return date(2000, month_num, 15).timetuple().tm_yday # Use 2000 as a non-leap year reference

def to_day_of_year(d):
    return d.timetuple().tm_yday

def get_month_name(month_num):
    return calendar.month_name[month_num]

# --- Sidebar Widgets ---
# Dropdown for file selection
st.sidebar.header("Data Selection")
selected_file_label = st.sidebar.selectbox(
    "Choose Plant Type:",
    options=list(FILE_OPTIONS.keys()),
    key="selected_file_type", # Use session state to persist selection
    help="Select the category of plants you want to view."
)
st.session_state.selected_file = FILE_OPTIONS[selected_file_label]

# Initialize `df` outside the main try-except block to ensure it's always defined
df = pd.DataFrame()
try:
    df = load_data(os.path.join(DATA_DIR, st.session_state.selected_file))
except Exception as e:
    st.error(f"Failed to load initial data: {e}")
    st.stop() # Stop the app if essential data cannot be loaded

# Check if df is empty after loading
if df.empty:
    st.warning("No data available to display. Please check the selected file and its contents.")
    st.stop() # Stop further execution if DataFrame is empty


# Search input
st.sidebar.header("Search & Filter")
st.session_state.search_query = st.sidebar.text_input("Search Plants:", value=st.session_state.search_query, placeholder="e.g., 'Rose', 'Daisy'", help="Type to search by Common Name.").lower()

# Month selection
current_month_name = get_month_name(st.session_state.selected_month_num)
selected_month_name = st.sidebar.selectbox(
    "Select Month:",
    options=[get_month_name(i) for i in range(1, 13)],
    index=st.session_state.selected_month_num - 1, # Set initial selection
    key="selected_month", # Use a key for the widget
    help="Filter plants by their active period in the selected month."
)
st.session_state.selected_month_num = [i for i, name in enumerate(calendar.month_name) if name == selected_month_name][0]

# Activity Type Filters
st.sidebar.subheader("Filter by Activity:")
st.session_state.filter_primary_activities = st.sidebar.checkbox("Show Primary Activities (Sow/Cut/Plant)", value=st.session_state.filter_primary_activities, help="Display the main planting activity for the selected plant type.")
st.session_state.filter_plant_out_activity = st.sidebar.checkbox("Show Plant Out Activities", value=st.session_state.filter_plant_out_activity, help="Display when plants should be transplanted outdoors.")
st.session_state.filter_flower_activity = st.sidebar.checkbox("Show Flowering Activities", value=st.session_state.filter_flower_activity, help="Display the period when plants are in bloom.")

# Light type filter (dynamic based on available data)
if 'Light' in df.columns:
    all_light_types = df['Light'].dropna().unique().tolist()
    if all_light_types:
        st.sidebar.subheader("Filter by Light:")
        # Allow multiple selections
        st.session_state.selected_light_types = st.sidebar.multiselect(
            "Select Light Needs:",
            options=all_light_types,
            default=st.session_state.selected_light_types, # Persist selections
            help="Filter plants by their light requirements."
        )

# Sort Order
st.sidebar.subheader("Sort Order:")
st.session_state.sort_order = st.sidebar.radio(
    "Choose sort order:",
    ("Alphabetical (A-Z)", "Alphabetical (Z-A)", "Reverse Chronological"),
    index=0 if st.session_state.sort_order == "Alphabetical (A-Z)" else (1 if st.session_state.sort_order == "Alphabetical (Z-A)" else 2),
    key="sort_order",
    help="Change the order in which plants are displayed."
)

# --- Main Content Area ---
st.title(f"{selected_file_label} Gardening Planner")

try:
    # --- Data Filtering ---
    filtered_df = df.copy()

    # Apply search query filter
    if st.session_state.search_query:
        filtered_df = filtered_df[filtered_df['Common Name'].str.lower().str.contains(st.session_state.search_query, na=False)]

    # Apply month filter for any activity
    month_filter_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
    for activity_type, (start_col, end_col) in COLUMN_MAPPINGS[st.session_state.selected_file_type].items():
        if start_col + '_Num' in filtered_df.columns and end_col + '_Num' in filtered_df.columns:
            # Handle cross-year ranges (e.g., Oct-Mar)
            # If start month is greater than end month, it spans across year end.
            # In such cases, the selected month should be >= start OR <= end.
            cross_year_mask = (filtered_df[start_col + '_Num'] > filtered_df[end_col + '_Num'])
            
            # Case 1: Activity within a single year (e.g., Apr-Jul)
            single_year_active = (filtered_df[start_col + '_Num'] <= st.session_state.selected_month_num) & \
                                 (filtered_df[end_col + '_Num'] >= st.session_state.selected_month_num)
            
            # Case 2: Activity spans year end (e.g., Oct-Mar)
            cross_year_active = (filtered_df[start_col + '_Num'] <= st.session_state.selected_month_num) | \
                                (filtered_df[end_col + '_Num'] >= st.session_state.selected_month_num)

            # Combine masks: use cross_year_active for cross-year ranges, single_year_active otherwise
            month_filter_mask |= (single_year_active & ~cross_year_mask) | (cross_year_active & cross_year_mask)

    filtered_df = filtered_df[month_filter_mask]


    # Apply light type filter
    if st.session_state.selected_light_types and 'Light' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Light'].isin(st.session_state.selected_light_types)]

    # --- Data Display ---
    if filtered_df.empty:
        st.info("No plants match your current filters. Try adjusting your selections.")
    else:
        # Sort plants for consistent display
        if st.session_state.sort_order == "Alphabetical (A-Z)":
            filtered_df = filtered_df.sort_values(by='Common Name', ascending=True)
        elif st.session_state.sort_order == "Alphabetical (Z-A)":
            filtered_df = filtered_df.sort_values(by='Common Name', ascending=False)
        elif st.session_state.sort_order == "Reverse Chronological":
            # For reverse chronological, sort by the end date of the primary activity (e.g., Sow End, Cut End, Plant End, Division End)
            # Find the primary activity type for the current file
            primary_activity_type = list(COLUMN_MAPPINGS[st.session_state.selected_file_type].keys())[0]
            primary_end_col_num = COLUMN_MAPPINGS[st.session_state.selected_file_type][primary_activity_type][1] + '_Num'
            if primary_end_col_num in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by=primary_end_col_num, ascending=False)
            else:
                st.warning(f"Cannot sort by '{primary_end_col_num}' as the column is missing. Sorting by Common Name.")
                filtered_df = filtered_df.sort_values(by='Common Name', ascending=True)


        plant_names_sorted = filtered_df['Common Name'].tolist()

        # --- Create Gantt Chart ---
        fig = go.Figure()
        current_year = date.today().year # Use current year for date calculations

        bar_height = 0.3 # Height of each activity bar
        row_spacing = 1 # Space between plants
        bar_offset_primary = 0.35 # Offset for primary activity
        bar_offset_plant_out = 0 # Offset for plant out activity
        bar_offset_flower = -0.35 # Offset for flower activity

        # Define consistent colors for activities across all file types
        ACTIVITY_COLORS = {
            'Sow': 'blue',
            'Cut': 'darkblue',
            'Plant': 'purple',
            'Division': 'darkgreen',
            'Plant Out': 'orange',
            'Flower': 'red'
        }

        # Define a sort order for legend items to keep it consistent
        LEGEND_SORT_ORDER = {
            'Sow': 1,
            'Cut': 2,
            'Plant': 3,
            'Division': 4,
            'Plant Out': 5,
            'Flower': 6
        }

        all_traces = []

        # Iterate through the sorted plant names
        for i, plant_name in enumerate(plant_names_sorted):
            plant_data = filtered_df[filtered_df['Common Name'] == plant_name].iloc[0]
            y_position = i * row_spacing

            # Determine number of active activities for vertical spacing adjustment
            num_activities = 0
            if st.session_state.filter_primary_activities:
                primary_activity_type = list(COLUMN_MAPPINGS[st.session_state.selected_file_type].keys())[0]
                start_col, end_col = COLUMN_MAPPINGS[st.session_state.selected_file_type][primary_activity_type]
                if start_col + '_Num' in plant_data and end_col + '_Num' in plant_data and plant_data[start_col + '_Num'] > 0 and plant_data[end_col + '_Num'] > 0:
                    num_activities += 1
            if st.session_state.filter_plant_out_activity and 'Plant Out' in COLUMN_MAPPINGS[st.session_state.selected_file_type]:
                start_col, end_col = COLUMN_MAPPINGS[st.session_state.selected_file_type]['Plant Out']
                if start_col + '_Num' in plant_data and end_col + '_Num' in plant_data and plant_data[start_col + '_Num'] > 0 and plant_data[end_col + '_Num'] > 0:
                    num_activities += 1
            if st.session_state.filter_flower_activity and 'Flower' in COLUMN_MAPPINGS[st.session_state.selected_file_type]:
                start_col, end_col = COLUMN_MAPPINGS[st.session_state.selected_file_type]['Flower']
                if start_col + '_Num' in plant_data and end_col + '_Num' in plant_data and plant_data[start_col + '_Num'] > 0 and plant_data[end_col + '_Num'] > 0:
                    num_activities += 1

            # Adjust y_position based on number of activities to center the group
            # Not necessary if fixed offsets are used consistently.
            # y_base = y_position - (num_activities -1) * bar_height / 2 if num_activities > 0 else y_position

            # Display Plant Details in a sidebar or expander
            with st.expander(f"Details for {plant_name}"):
                details_config = PLANT_DETAILS_MAPPING.get(st.session_state.selected_file_type, [])
                if details_config:
                    st.markdown('<p class="no-margin-p"><b>Key Details:</b></p>', unsafe_allow_html=True)
                    for detail in details_config:
                        label = detail['label']
                        cols = detail['cols']
                        unit = detail['unit']
                        display_value = []
                        valid_data_found = False

                        if detail['type'] == 'range':
                            val_min = plant_data.get(cols[0])
                            val_max = plant_data.get(cols[1])
                            if pd.notna(val_min) and pd.notna(val_max):
                                display_value.append(f"{val_min}-{val_max}{unit}")
                                valid_data_found = True
                        elif detail['type'] == 'single':
                            val = plant_data.get(cols[0])
                            if pd.notna(val) and val != '':
                                display_value.append(f"{val}{unit}")
                                valid_data_found = True

                        if valid_data_found:
                            st.markdown(f'<p class="no-margin-p detail-item"><strong>{label}:</strong> {", ".join(display_value)}</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="no-margin-p">No specific details configured for this plant type.</p>', unsafe_allow_html=True)

            # Add activities to the chart
            for activity_key, (start_col_name, end_col_name) in COLUMN_MAPPINGS[st.session_state.selected_file_type].items():
                start_col_num = start_col_name + '_Num'
                end_col_num = end_col_name + '_Num'

                plot_activity = False
                if activity_key in ['Sow', 'Cut', 'Plant', 'Division'] and st.session_state.filter_primary_activities:
                    plot_activity = True
                elif activity_key == 'Plant Out' and st.session_state.filter_plant_out_activity:
                    plot_activity = True
                elif activity_key == 'Flower' and st.session_state.filter_flower_activity:
                    plot_activity = True

                if plot_activity and start_col_num in plant_data and end_col_num in plant_data:
                    start_month_num = plant_data[start_col_num]
                    end_month_num = plant_data[end_col_num]

                    if start_month_num > 0 and end_month_num > 0:
                        # Convert month numbers to day of year for plotting
                        start_day = month_num_to_day_of_year(start_month_num)
                        end_day = month_num_to_day_of_year(end_month_num)

                        # Handle activities that span across year end (e.g., Oct-Mar)
                        if start_month_num > end_month_num:
                            # Part 1: From start month to end of year
                            all_traces.append((
                                activity_key,
                                go.Bar(
                                    y=[y_position + (bar_offset_primary if activity_key in ['Sow', 'Cut', 'Plant', 'Division'] else (bar_offset_plant_out if activity_key == 'Plant Out' else bar_offset_flower))],
                                    x=[366 - start_day], # Duration to end of year
                                    base=[start_day],
                                    orientation='h',
                                    marker=dict(color=ACTIVITY_COLORS.get(activity_key, 'grey')),
                                    name=activity_key,
                                    hovertemplate=f"<b>{plant_name}</b><br>{activity_key}: %{{base}} - %{{x}}<extra></extra>", # CORRECTED HERE
                                    showlegend=True # Will be handled by sorting later
                                )
                            ))
                            # Part 2: From beginning of year to end month
                            all_traces.append((
                                activity_key,
                                go.Bar(
                                    y=[y_position + (bar_offset_primary if activity_key in ['Sow', 'Cut', 'Plant', 'Division'] else (bar_offset_plant_out if activity_key == 'Plant Out' else bar_offset_flower))],
                                    x=[end_day], # Duration from start of year
                                    base=[1], # Start from day 1
                                    orientation='h',
                                    marker=dict(color=ACTIVITY_COLORS.get(activity_key, 'grey')),
                                    name=activity_key,
                                    hovertemplate=f"<b>{plant_name}</b><br>{activity_key}: %{{base}} - %{{x}}<extra></extra>", # CORRECTED HERE
                                    showlegend=True # Will be handled by sorting later
                                )
                            ))
                        else:
                            # Standard duration within the same year
                            all_traces.append((
                                activity_key,
                                go.Bar(
                                    y=[y_position + (bar_offset_primary if activity_key in ['Sow', 'Cut', 'Plant', 'Division'] else (bar_offset_plant_out if activity_key == 'Plant Out' else bar_offset_flower))],
                                    x=[end_day - start_day],
                                    base=[start_day],
                                    orientation='h',
                                    marker=dict(color=ACTIVITY_COLORS.get(activity_key, 'grey')),
                                    name=activity_key,
                                    hovertemplate=f"<b>{plant_name}</b><br>{activity_key}: %{{base}} - %{{x}}<extra></extra>", # CORRECTED HERE
                                    showlegend=True # Will be handled by sorting later
                                )
                            ))

        # Sort traces for consistent legend order
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
        # Simplified total_y_span calculation for robustness
        total_y_span = (len(plant_names_sorted) * row_spacing) + 1 # A simple sum of row spacings + buffer


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
