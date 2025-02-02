import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Branding
AUTHOR_NAME = "Jaideep"
DASHBOARD_TITLE = f"GDP Dashboard by {AUTHOR_NAME}"

# Set the page title and favicon
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="🌍",
)

# ----------------------------------------------------------------------------- 
# Load GDP Data

@st.cache_data
def load_gdp_data():
    """Loads GDP data from a CSV file and processes it for analysis."""
    
    # Path to dataset
    DATA_FILENAME = Path(__file__).parent / 'data/gdp_data.csv'
    
    # Read the CSV file
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    # Define year range
    MIN_YEAR, MAX_YEAR = 1960, 2022

    # Reshape data: Pivot year columns into 'Year' and 'GDP'
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(year) for year in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert 'Year' to integer for better filtering
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

# Load the GDP data
gdp_df = load_gdp_data()

# -----------------------------------------------------------------------------
# Dashboard Header

st.title(DASHBOARD_TITLE)
st.markdown("""
Explore global GDP trends using data from the [World Bank Open Data](https://data.worldbank.org/).  
This dashboard provides insights into GDP growth across different countries from 1960 to 2022.  
Built with Streamlit by **Jaideep**.
""")

# -----------------------------------------------------------------------------
# User Input: Year Range & Country Selection

# Define year range
min_year, max_year = gdp_df['Year'].min(), gdp_df['Year'].max()

# Year range selection
from_year, to_year = st.slider(
    "Select the Year Range",
    min_value=min_year,
    max_value=max_year,
    value=[min_year, max_year]
)

# Country selection
countries = gdp_df['Country Code'].unique()
selected_countries = st.multiselect(
    "Select Countries",
    options=countries,
    default=['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']
)

# Warning if no country is selected
if not selected_countries:
    st.warning("Please select at least one country.")

# -----------------------------------------------------------------------------
# Filtered Data

filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# -----------------------------------------------------------------------------
# GDP Over Time - Line Chart

st.header("GDP Trends Over Time")
st.line_chart(
    filtered_gdp_df,
    x="Year",
    y="GDP",
    color="Country Code",
)

# -----------------------------------------------------------------------------
# GDP Comparison in Selected Years

st.header(f"GDP Comparison: {from_year} vs {to_year}")

# Fetch data for selected years
first_year_data = gdp_df[gdp_df['Year'] == from_year]
last_year_data = gdp_df[gdp_df['Year'] == to_year]

# Display GDP metrics for selected countries
cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year_data[first_year_data['Country Code'] == country]['GDP'].iat[0] / 1e9
        last_gdp = last_year_data[last_year_data['Country Code'] == country]['GDP'].iat[0] / 1e9

        # Calculate GDP growth
        if math.isnan(first_gdp):
            growth = "N/A"
            delta_color = "off"
        else:
            growth = f"{last_gdp / first_gdp:.2f}x"
            delta_color = "normal"

        # Display metric
        st.metric(
            label=f"{country} GDP",
            value=f"{last_gdp:,.0f}B USD",
            delta=growth,
            delta_color=delta_color
        )

# -----------------------------------------------------------------------------
# Footer

st.markdown("---")
st.markdown(f"**Developed by {AUTHOR_NAME}** | Powered by Streamlit")
