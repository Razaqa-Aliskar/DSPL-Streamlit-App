import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- Page Setup ---
st.set_page_config(page_title="Sri Lanka Poverty Dashboard", layout="wide")

# --- Custom CSS for Background and Styling ---
page_bg_img = '''
<style>
.stApp {
background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
url("https://images.unsplash.com/photo-1601764762628-4d33e2f13251");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
color: white;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    time.sleep(1)  # To show spinner effect
    return pd.read_csv('poverty_lka_cleaned.csv')

with st.spinner('Loading data...'):
    df = load_data()

# --- Title ---
st.title("📊 Sri Lanka Poverty Indicators Dashboard")
st.markdown("Explore poverty trends, income inequality, and gaps over time for Sri Lanka.")

# --- Filter Section ---
with st.container():
    st.header("🔎 Filter Options")

    col1, col2 = st.columns([1,2])

    with col1:
        min_year = int(df['Year'].min())
        max_year = int(df['Year'].max())
        year_range = st.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )

    with col2:
        income_options = df['Indicator Name'].dropna().unique()
        default_indicator = "Income share held by lowest 20%"

        if default_indicator in income_options:
            default_selection = [default_indicator]
        else:
            default_selection = [income_options[0]]

        income_share_choice = st.multiselect(
            "Select KPI Indicator(s):",
            options=income_options,
            default=default_selection
        )

    # Reset button
    if st.button("🔄 Reset Filters"):
        year_range = (min_year, max_year)
        income_share_choice = default_selection

# --- Filtered Data ---
filtered_df = df[
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1]) & 
    (df['Indicator Name'].isin(income_share_choice))
]

# --- KPI Section ---
st.subheader("📌 Key Metrics")

latest_year = df['Year'].max()

col1, col2, col3 = st.columns(3)

# First KPI - selected income indicators
with col1:
    if income_share_choice:
        for indicator in income_share_choice:
            latest_data = df[
                (df['Year'] == latest_year) &
                (df['Indicator Name'] == indicator)
            ]
            if not latest_data.empty:
                indicator_value = latest_data['Value'].mean()
                st.metric(
                    label=f"{indicator} ({latest_year})",
                    value=f"{indicator_value:.2f}%"
                )
            else:
                st.metric(label=f"{indicator} ({latest_year})", value="N/A")
    else:
        st.metric(label="No Indicator Selected", value="N/A")

# Second KPI - poverty headcount
with col2:
    poverty_headcount = df[(df['Year'] == latest_year) & (df['Indicator Name'].str.contains('poverty headcount', case=False))]
    if not poverty_headcount.empty:
        headcount_value = poverty_headcount['Value'].mean()
        st.metric(
            label="Poverty Headcount (%)",
            value=f"{headcount_value:.2f}%"
        )
    else:
        st.metric(label="Poverty Headcount", value="N/A")

# Third KPI - gini index
with col3:
    gini_index = df[(df['Year'] == latest_year) & (df['Indicator Name'].str.contains('gini', case=False))]
    if not gini_index.empty:
        gini_value = gini_index['Value'].mean()
        st.metric(
            label="Gini Index",
            value=f"{gini_value:.2f}"
        )
    else:
        st.metric(label="Gini Index", value="N/A")

# --- Tabs for Charts ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend", "📊 Growth", "🏆 Ranking", "🔗 Correlation"])

with tab1:
    st.subheader("Trend of Selected Indicators")
    if not filtered_df.empty:
        fig_trend = px.line(
            filtered_df,
            x="Year",
            y="Value",
            color="Indicator Name",
            markers=True,
            title="Trend Analysis",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No data for the selected filters.")

with tab2:
    st.subheader("Year-on-Year Growth")
    growth_df = filtered_df.copy()
    growth_df['Previous Value'] = growth_df.groupby('Indicator Name')['Value'].shift(1)
    growth_df['Growth Rate (%)'] = ((growth_df['Value'] - growth_df['Previous Value']) / growth_df['Previous Value']) * 100
    growth_df = growth_df.dropna()

    if not growth_df.empty:
        fig_growth = px.bar(
            growth_df,
            x="Year",
            y="Growth Rate (%)",
            color="Indicator Name",
            barmode="group",
            title="Yearly Growth/Decline",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("Not enough data to calculate growth.")

with tab3:
    st.subheader(f"Ranking in {latest_year}")
    rank_df = df[df['Year'] == latest_year]

    if not rank_df.empty:
        fig_rank = px.bar(
            rank_df.sort_values('Value', ascending=False),
            x="Value",
            y="Indicator Name",
            orientation='h',
            title=f"Indicator Ranking ({latest_year})",
            color="Value",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_rank, use_container_width=True)
    else:
        st.warning("No ranking data available.")

with tab4:
    st.subheader("Correlation Analysis")
    pivot_df = df.pivot(index="Year", columns="Indicator Name", values="Value")

    if pivot_df.isnull().sum().sum() < 0.5 * pivot_df.size:
        corr_matrix = pivot_df.corr()

        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="Tealrose",
            title="Correlation Between Indicators"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough data to compute correlation.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center>Developed by <b>Razaqa Aliskar</b> | Module: 5DATA004W | 📅 2025</center>",
    unsafe_allow_html=True
)

