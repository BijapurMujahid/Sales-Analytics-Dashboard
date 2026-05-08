import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Setting
st.set_page_config(page_title="Sales Intelligence Pro", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_sales_data.csv')
    
    # --- ERROR FIXING START ---
    # 1. Khali (NaN) records ko 'Unknown' se bhar dena
    df['Party_Name'] = df['Party_Name'].fillna('Unknown')
    df['Make'] = df['Make'].fillna('General')
    
    # 2. Sabko String (Text) mein badalna taaki sorting error na aaye
    df['Party_Name'] = df['Party_Name'].astype(str)
    df['Make'] = df['Make'].astype(str)
    # --- ERROR FIXING END ---

    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Your Data")
    
    # Party Filter (Ab error nahi aayega)
    parties_list = sorted(df['Party_Name'].unique())
    selected_party = st.sidebar.selectbox("Select Party (Customer)", ["All"] + parties_list)

    # Brand Filter
    makes_list = sorted(df['Make'].unique())
    selected_make = st.sidebar.selectbox("Select Brand (Make)", ["All"] + makes_list)

    # Filtering Logic
    filtered_df = df.copy()
    if selected_party != "All":
        filtered_df = filtered_df[filtered_df['Party_Name'] == selected_party]
    if selected_make != "All":
        filtered_df = filtered_df[filtered_df['Make'] == selected_make]

    # --- MAIN DASHBOARD ---
    st.title("📊 Professional Sales Insights")
    st.divider()

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"₹{filtered_df['Total_Amount'].sum():,.2f}")
    with col2:
        st.metric("Orders Count", len(filtered_df))
    with col3:
        st.metric("Unique Items", filtered_df['Product_Name'].nunique())
    with col4:
        st.metric("Avg Bill Value", f"₹{filtered_df['Total_Amount'].mean():,.0f}" if len(filtered_df)>0 else "0")

    # Charts
    c1, c2 = st.columns([6, 4])
    with c1:
        # Daily Trend
        trend = filtered_df.groupby('Date')['Total_Amount'].sum().reset_index()
        fig_line = px.line(trend, x='Date', y='Total_Amount', title="Sales Trend", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    with c2:
        # Top Products
        top_p = filtered_df.groupby('Product_Name')['Total_Amount'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_bar = px.bar(top_p, x='Total_Amount', y='Product_Name', orientation='h', title="Top 10 Products", color='Total_Amount')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Deep Detail Table
    st.subheader("📝 Deep Transactional Details")
    st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Something went wrong: {e}")