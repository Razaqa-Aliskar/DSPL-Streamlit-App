import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(page_title="Sri Lanka Poverty Dashboard", layout="wide")

# --- Load Data ---
df = pd.read_csv('poverty_lka_cleaned.csv')

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Replace the multiselect for Year with a range slider
min_year = df['Year'].min()
max_year = df['Year'].max()

year_range = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

indicators = st.sidebar.multiselect(
    "Select Indicator(s):",
    options=df['Indicator Name'].unique(),
    default=df['Indicator Name'].unique()
)

# Filtered Data
filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1]) & (df['Indicator Name'].isin(indicators))]

# --- Main Title ---
st.title("📊 Sri Lanka Poverty Indicators Dashboard")
st.markdown("Explore poverty trends, income inequality, and gaps over time for Sri Lanka.")

# --- KPIs Section ---
st.subheader("📌 Key Metrics")

col1, col2, col3 = st.columns(3)

# Latest Year Data
latest_year = df['Year'].max()
latest_data = df[df['Year'] == latest_year]

if not latest_data.empty:
    poverty_headcount = latest_data[latest_data['Indicator Name'].str.contains("Poverty headcount", case=False)]
    poverty_value = poverty_headcount['Value'].mean() if not poverty_headcount.empty else None

    gap_data = latest_data[latest_data['Indicator Name'].str.contains("poverty gap", case=False)]
    gap_value = gap_data['Value'].mean() if not gap_data.empty else None

    inequality_data = latest_data[latest_data['Indicator Name'].str.contains("Income share held by lowest", case=False)]
    inequality_value = inequality_data['Value'].mean() if not inequality_data.empty else None

    col1.metric(label=f"Poverty Headcount ({latest_year})", value=f"{poverty_value:.2f}%" if poverty_value else "N/A")
    col2.metric(label=f"Poverty Gap ({latest_year})", value=f"{gap_value:.2f}%" if gap_value else "N/A")
    col3.metric(label=f"Lowest 20% Income Share ({latest_year})", value=f"{inequality_value:.2f}%" if inequality_value else "N/A")
else:
    st.warning("No data available for the latest year.")

# --- Trend Analysis Section ---
st.subheader("📈 Trend of Poverty Indicators Over Time")

if not filtered_df.empty:
    fig_trend = px.line(
        filtered_df,
        x="Year",
        y="Value",
        color="Indicator Name",
        markers=True,
        title="Trend of Selected Indicators",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.warning("No data for the selected filters.")

# --- Growth Rate Section ---
st.subheader("📈 Year-on-Year Growth/Decline in Indicators")

growth_df = filtered_df.copy()
growth_df['Value Shifted'] = growth_df.groupby('Indicator Name')['Value'].shift(1)
growth_df['Growth Rate (%)'] = ((growth_df['Value'] - growth_df['Value Shifted']) / growth_df['Value Shifted']) * 100

growth_df = growth_df.dropna()

if not growth_df.empty:
    fig_growth = px.bar(
        growth_df,
        x="Year",
        y="Growth Rate (%)",
        color="Indicator Name",
        barmode="group",
        title="Year-on-Year Growth Rate",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_growth, use_container_width=True)
else:
    st.info("Not enough data to compute growth rates.")

# --- Indicator Ranking (Latest Year) ---
st.subheader(f"🏆 Indicator Ranking in {latest_year}")

rank_df = df[df['Year'] == latest_year]

if not rank_df.empty:
    fig_rank = px.bar(
        rank_df.sort_values('Value', ascending=False),
        x="Value",
        y="Indicator Name",
        orientation='h',
        title=f"Ranking of Indicators ({latest_year})",
        color="Value",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_rank, use_container_width=True)
else:
    st.warning("No ranking data available for the latest year.")

# --- Correlation Analysis ---
st.subheader("🔗 Correlation Between Indicators (Advanced)")

pivot_df = df.pivot(index="Year", columns="Indicator Name", values="Value")

if pivot_df.isnull().sum().sum() < 0.5 * pivot_df.size:  # Less than 50% missing
    corr_matrix = pivot_df.corr()

    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="Tealrose",
        title="Correlation Between Indicators"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Too much missing data for correlation matrix.")

# --- Data View Section ---
st.subheader("📄 Explore Filtered Dataset")
st.dataframe(filtered_df)

# Footer
st.markdown("---")
st.markdown("Developed by [Razaqa Aliskar] | Module: 5DATA004W | 📅 2025")
