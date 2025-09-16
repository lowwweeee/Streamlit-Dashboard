import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Triple Track Garage",
                   page_icon="🚗", layout="wide")

# === Custom CSS for Hot Wheels theme ===
st.markdown("""
    <style>
    body { font-family: 'Poppins', sans-serif; background-color: #0D0D0D; }
    .block-container h1 { color: #FF4500; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: #FF4500; font-size: 26px; font-weight: bold; }
    h2, h3, h4 { color: #007BFF; }
    .stDownloadButton>button { background-color: #FF4500; color: white; border-radius: 8px; font-weight: bold; }
    .stDownloadButton>button:hover { background-color: #E03E00; color: white; }
    </style>
""", unsafe_allow_html=True)

# === Logo + Title ===
st.image("hotwheels_logo.jpg", width=120)  # Optional
st.title("🔥 Triple Track Garage Sales Dashboard 🚗")

# === File Uploader ===
fl = st.file_uploader("📂 Upload your sales file", type=["csv", "xlsx", "xls"])
if fl is not None:
    if fl.name.endswith(".csv"):
        df = pd.read_csv(fl)
    else:
        df = pd.read_excel(fl)

    # Ensure numeric fields
    df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')
    df["Cost"] = pd.to_numeric(df["Cost"], errors='coerce')
    df["Amount Collected"] = df["Price"] * df["Quantity"]
    df["Profit"] = (df["Price"] - df["Cost"]) * df["Quantity"]

    # === KPIs ===
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Sales", f"₱{df['Amount Collected'].sum():,.2f}")
    col2.metric("📦 Quantity Sold", f"{df['Quantity'].sum()}")
    col3.metric("👥 Unique Buyers", f"{df['Buyer Name'].nunique()}")
    col4.metric("📈 Total Profit", f"₱{df['Profit'].sum():,.2f}")

    # === Tabs for navigation ===
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "📂 Raw Data"])

    with tab1:
        st.subheader("Sales by Class")
        fig = px.bar(df.groupby("Class")["Amount Collected"].sum().reset_index(),
                     x="Class", y="Amount Collected", color="Class")
        fig.update_layout(template="plotly_dark",
                          plot_bgcolor="#0D0D0D", paper_bgcolor="#0D0D0D")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Sales Over Time")
        if "Order Date" in df.columns:
            df["Order Date"] = pd.to_datetime(
                df["Order Date"], errors="coerce")
            line_df = df.groupby(df["Order Date"].dt.to_period("M"))[
                "Amount Collected"].sum().reset_index()
            line_df["Order Date"] = line_df["Order Date"].astype(str)
            fig2 = px.line(line_df, x="Order Date", y="Amount Collected")
            fig2.update_layout(template="plotly_dark",
                               plot_bgcolor="#0D0D0D", paper_bgcolor="#0D0D0D")
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("📂 Sales Records")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv,
                           file_name="sales_data.csv", mime="text/csv")

else:
    st.info("👆 Upload an Excel or CSV file to begin.")
