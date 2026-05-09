import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pharma Sales Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")
    return df

df = load_data()

# Title
st.title("📊 Pharma Sales Dashboard")
st.markdown("---")

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    parties = ["All"] + sorted(df["Party_Name"].dropna().unique().tolist())
    party = st.selectbox("Party", parties)

with col2:
    makes = ["All"] + sorted(df["Make"].dropna().unique().tolist())
    make = st.selectbox("Make", makes)

with col3:
    products = ["All"] + sorted(df["Item_Description"].dropna().unique().tolist())
    product = st.selectbox("Product", products)

with col4:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    date_range = st.date_input("Date Range", [min_date, max_date])

# Apply filters
filtered = df.copy()
if party != "All":
    filtered = filtered[filtered["Party_Name"] == party]
if make != "All":
    filtered = filtered[filtered["Make"] == make]
if product != "All":
    filtered = filtered[filtered["Item_Description"] == product]
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"] >= pd.Timestamp(date_range[0])) &
        (filtered["Date"] <= pd.Timestamp(date_range[1]))
    ]

st.markdown("---")

# KPI Cards
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"₹{filtered['Amount'].sum():,.0f}")
k2.metric("Total Qty", f"{filtered['Qty'].sum():,.0f}")
k3.metric("Total Bills", filtered["Bill_No"].nunique())
k4.metric("Total Parties", filtered["Party_Name"].nunique())

st.markdown("---")

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Sales by Make")
    make_data = filtered.groupby("Make")["Amount"].sum().reset_index()
    fig1 = px.bar(make_data, x="Make", y="Amount", color="Make")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Top 10 Products")
    prod_data = filtered.groupby("Item_Description")["Amount"].sum().nlargest(10).reset_index()
    fig2 = px.bar(prod_data, x="Amount", y="Item_Description", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Sales by Party")
    party_data = filtered.groupby("Party_Name")["Amount"].sum().nlargest(10).reset_index()
    fig3 = px.pie(party_data, values="Amount", names="Party_Name")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Sales Over Time")
    time_data = filtered.groupby("Date")["Amount"].sum().reset_index()
    fig4 = px.line(time_data, x="Date", y="Amount")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("Raw Data")
st.dataframe(filtered, use_container_width=True)