import streamlit as st
import pandas as pd
import plotly.express as px
import time
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Setup ---
st.set_page_config(page_title="Sri Lanka Poverty Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    time.sleep(1)
    return pd.read_csv('poverty_lka_cleaned.csv')

with st.spinner('Loading data...'):
    df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.image('https://www.shutterstock.com/image-vector/vector-obverse-high-polygonal-pixel-600nw-2456917051.jpg', width=200)
    st.title("🌏 Dashboard Settings")

    st.markdown("---")

    # Year Filter ONLY
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    year_range = st.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )



# --- Main Page ---
st.title("📊 Sri Lanka Poverty Indicators Dashboard")
st.markdown("Explore poverty trends, income inequality, and gaps over time for Sri Lanka.")

# --- Filter Section ---
with st.container():
    st.header("🔎 Filter Options (Main Dashboard)")

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

    if st.button("🔄 Reset Indicators"):
        income_share_choice = default_selection
        st.rerun()

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

with col2:
    poverty_headcount = df[
        (df['Year'] == latest_year) & 
        (df['Indicator Name'].str.contains('poverty headcount', case=False))
    ]
    if not poverty_headcount.empty:
        headcount_value = poverty_headcount['Value'].mean()
        st.metric(
            label="Poverty Headcount (%)",
            value=f"{headcount_value:.2f}%"
        )
    else:
        st.metric(label="Poverty Headcount", value="N/A")

with col3:
    gini_index = df[
        (df['Year'] == latest_year) & 
        (df['Indicator Name'].str.contains('gini', case=False))
    ]
    if not gini_index.empty:
        gini_value = gini_index['Value'].mean()
        st.metric(
            label="Gini Index",
            value=f"{gini_value:.2f}"
        )
    else:
        st.metric(label="Gini Index", value="N/A")

# --- Tabs for Charts ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trend", "📊 Growth", "🏆 Ranking", "📈 Headcount Trend", "🔗 Correlation"])

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
            rank_df.sort_values('Value', ascending=True),
            x="Value",
            y="Indicator Name",
            orientation='h',
            title=f"Indicator Ranking ({latest_year})",
            color="Value",
            color_continuous_scale="Viridis",
            hover_data=["Indicator Name", "Value"]
        )
        fig_rank.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Value",
            yaxis_title="Indicator",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_rank, use_container_width=True)
    else:
        st.warning("No ranking data available.")

with tab4:
    st.subheader("🧩 Poverty Headcount Trend ")

    # Filter headcount indicators directly (NOT relying on main multiselect)
    headcount_df = df[
        (df['Indicator Name'].str.contains('poverty headcount', case=False)) &
        (df['Year'] >= year_range[0]) &
        (df['Year'] <= year_range[1])
    ]

    # Let user pick which headcount indicators to show (new multiselect)
    headcount_options = headcount_df['Indicator Name'].unique()

    selected_headcount = st.multiselect(
        "Select Poverty Headcount Indicator(s):",
        options=headcount_options,
        default=headcount_options.tolist()
    )

    headcount_filtered_df = headcount_df[
        headcount_df['Indicator Name'].isin(selected_headcount)
    ]

    if not headcount_filtered_df.empty:
        fig_headcount = px.line(
            headcount_filtered_df,
            x="Year",
            y="Value",
            color="Indicator Name",
            markers=True,
            title="Poverty Headcount Trend (User Selected)",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        st.plotly_chart(fig_headcount, use_container_width=True)
    else:
        st.info("⚠️ No headcount data available for your selection.")



with tab5:
    st.subheader("Correlation Matrix (Interactive)")

    # Prepare Pivot Table for Selected Data
    corr_filtered_df = df[
        (df['Year'] >= year_range[0]) &
        (df['Year'] <= year_range[1]) &
        (df['Indicator Name'].isin(income_share_choice))
    ]

    pivot_corr = corr_filtered_df.pivot_table(
        values='Value', index='Year', columns='Indicator Name'
    )

    corr_matrix = pivot_corr.corr()

    if not corr_matrix.empty:
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlation Matrix Between Selected Indicators"
        )
        fig_corr.update_layout(
            width=800,
            height=600,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough data to generate correlation matrix.")

    

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center>Developed by <b>Razaqa Aliskar</b> | Module: 5DATA004W | 📅 2025</center>",
    unsafe_allow_html=True
)
