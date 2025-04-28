import streamlit as st
import pandas as pd
st.write ("razaqaa")

df = pd.read_csv('poverty_lka_cleaned.csv')

import streamlit as st
import pandas as pd
import altair as alt

# --- Load Your Data ---
# Assuming your data is in a CSV file named 'sri_lanka_data.csv'
# Adjust the filename and path as needed.
try:
    df = pd.read_csv('poverty_lka_cleaned.csv')
except FileNotFoundError:
    st.error("Error: Could not find 'sri_lanka_data.csv'.  Please make sure it's in the same directory.")
    st.stop()  # Halt execution if the data file is missing

# --- Data Preprocessing ---
# Clean and transform your data here if necessary.
# This is crucial to ensure it's in the right format for plotting.
# Example: Convert 'Year' to datetime if needed
if 'Year' in df.columns:
    try:
        df['Year'] = pd.to_datetime(df['Year'], errors='coerce')
        df.dropna(subset=['Year'], inplace=True)  # Remove rows with invalid years
    except KeyError:
        st.error("Error: 'Year' column not found in the dataset.")
        st.stop()

# --- Streamlit App ---
st.title("Sri Lanka Development Indicators Dashboard")

# --- 1. Income Inequality Section ---
st.header("Income Inequality")

# Dropdown for Income Share Percentile (if applicable)
income_share_cols = [col for col in df.columns if "Income share held by" in col]
selected_income_share = None
if income_share_cols:
    selected_income_share = st.selectbox("Select Income Share Percentile", income_share_cols, index=0)  # Default to the first one

# Line Chart for Income Share
if selected_income_share:
    income_share_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(format="%Y")),  # Format Year on the axis
        y=selected_income_share,
        tooltip=['Year', selected_income_share]
    ).properties(
        title=f"Income Share Held by {selected_income_share}"
    ).interactive()
    st.altair_chart(income_share_chart, use_container_width=True)

# Line Chart for Gini Index
if 'Gini index' in df.columns:
    gini_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(format="%Y")),
        y='Gini index',
        tooltip=['Year', 'Gini index']
    ).properties(
        title="Gini Index Over Time"
    ).interactive()
    st.altair_chart(gini_chart, use_container_width=True)


# --- 2. Poverty Section ---
st.header("Poverty")

# Dropdown for Poverty Line
poverty_cols = [col for col in df.columns if "Poverty headcount ratio" in col]
selected_poverty_line = None
if poverty_cols:
    selected_poverty_line = st.selectbox("Select Poverty Line", poverty_cols, index=0)

# Line Chart for Poverty Ratio
if selected_poverty_line:
    poverty_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(format="%Y")),
        y=selected_poverty_line,
        tooltip=['Year', selected_poverty_line]
    ).properties(
        title=f"Poverty Headcount Ratio at {selected_poverty_line}"
    ).interactive()
    st.altair_chart(poverty_chart, use_container_width=True)


# --- 3. Women in Parliament Section ---
st.header("Women in Parliament")

if 'Proportion of seats held by women in national parliaments' in df.columns:
    women_parliament_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(format="%Y")),
        y='Proportion of seats held by women in national parliaments',
        tooltip=['Year', 'Proportion of seats held by women in national parliaments']
    ).properties(
        title="Women's Representation in Parliament"
    ).interactive()
    st.altair_chart(women_parliament_chart, use_container_width=True)


# --- 4. Multidimensional Poverty Section ---
st.header("Multidimensional Poverty")

mpi_cols = [col for col in df.columns if "Multidimensional poverty index" in col]
selected_mpi_indicator = None
if mpi_cols:
    selected_mpi_indicator = st.selectbox("Select MPI Indicator", mpi_cols, index=0)

if selected_mpi_indicator:
    mpi_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(format="%Y")),
        y=selected_mpi_indicator,
        tooltip=['Year', selected_mpi_indicator]
    ).properties(
        title=f"{selected_mpi_indicator} Over Time"
    ).interactive()
    st.altair_chart(mpi_chart, use_container_width=True)


# --- Add a Time Range Slider for Global Filtering ---
if 'Year' in df.columns:
    min_year = df['Year'].min().year
    max_year = df['Year'].max().year
    year_range = st.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))
    df = df[(df['Year'].dt.year >= year_range[0]) & (df['Year'].dt.year <= year_range[1])]


# ---  Key Insights Text  ---
st.header("Key Insights")
st.write("This dashboard provides an overview of key development indicators for Sri Lanka...") #Add your insights here.

# ---  Footer  ---
st.sidebar.header("About")
st.sidebar.info("This Streamlit app visualizes Sri Lankan development indicators.  Data source: [Your Data Source(s) Here]") # Replace with your actual data source(s)