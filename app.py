import streamlit as st
import pandas as pd
import plotly.express as px
import time

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
    st.image('https://www.leftovercurrency.com/app/uploads/2018/10/1000-sri-lankan-rupees-banknote-sri-lanka-dancers-series-obverse-2.jpg', width=200)
    st.title("🌏 Navigation")
    page = st.radio("Go to", ["Home", "Dashboard"])

# --- Home Page ---
if page == "Home":
    st.title("🏠 Welcome to the Sri Lanka Poverty Dashboard")
    st.markdown("---")
    st.subheader("📚 About Poverty in Sri Lanka")
    st.write("""
    Sri Lanka has made significant progress in reducing poverty over the past decades. 
    However, economic challenges, inflation, and regional disparities continue to affect vulnerable populations.
    
    This dashboard helps to explore key indicators such as income distribution, poverty headcount ratios, 
    and inequality metrics over time to better understand the situation and track improvements.

    **Key Data Sources:**  
    - Humanitarian Data Exchange (HDX)  
    - National Statistics Office of Sri Lanka

    **Developed by Razaqa Aliskar | Module: 5DATA004W | 2025**
    """)
    st.markdown("---")

# --- Dashboard Page (KPIs + Visuals) ---
elif page == "Dashboard":
    st.title("📊 Sri Lanka Poverty Indicators Dashboard")
    st.markdown("Explore poverty trends, income inequality, and gaps over time for Sri Lanka.")

    # --- Sidebar Filters ---
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    year_range = st.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

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

    # --- Tabs for Visuals ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trend", "📊 Growth", "🏆 Ranking", "📈 Headcount Trend", "🔗 Correlation"])

    with tab1:
        st.subheader("Trend of Selected Indicators")

    # Filter strictly for selected year range again
    trend_df = filtered_df[
        (filtered_df['Year'] >= year_range[0]) &
        (filtered_df['Year'] <= year_range[1])
    ]

    if not trend_df.empty:
        fig_trend = px.line(
            trend_df,
            x="Year",
            y="Value",
            color="Indicator Name",
            markers=True,
            title=f"Trend Analysis ({year_range[0]} - {year_range[1]})",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No Indicator Selected within the selected year range.")


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
        st.subheader("🏆 Indicator Ranking Over Selected Years")

        ranking_df = df[
            (df['Year'] >= year_range[0]) & 
            (df['Year'] <= year_range[1])
        ]

        selected_year = st.selectbox(
            "Select a Year for Ranking:",
            options=sorted(ranking_df['Year'].unique()),
            index=0
        )

        year_ranking_df = ranking_df[ranking_df['Year'] == selected_year]

        if not year_ranking_df.empty:
            fig_rank = px.bar(
                year_ranking_df.sort_values('Value', ascending=False),
                x="Value",
                y="Indicator Name",
                orientation='h',
                title=f"Indicator Ranking ({selected_year})",
                color="Value",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_rank, use_container_width=True)
        else:
            st.warning("No ranking data available for the selected year.")

    with tab4:
        st.subheader("🧩 Poverty Headcount Trend ")

        headcount_df = df[
            (df['Indicator Name'].str.contains('poverty headcount', case=False)) &
            (df['Year'] >= year_range[0]) &
            (df['Year'] <= year_range[1])
        ]

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
    "<center>Developed by <b>Razaqa Aliskar</b> | Module: 5DATA004W | 📅 2025 | Source: <b>HDX</b> </center>",
    unsafe_allow_html=True
)
