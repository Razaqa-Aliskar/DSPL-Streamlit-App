import streamlit as st
import pandas as pd
st.write ("razaqaa")

df = pd.read_csv('poverty_lka_cleaned.csv')

# Add a title to the dashboard
st.title('Interactive Dashboard')

# Add a subheader
st.subheader('Exploring the Data')

# Display the data
st.write(df)