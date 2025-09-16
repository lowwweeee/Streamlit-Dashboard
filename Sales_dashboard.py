import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# -------------------------------
# Custom CSS for Styling
# -------------------------------
st.markdown("""
    <style>
        .main { background-color: #F8F9FA; }
        h1, h2, h3 { color: #2C3E50; }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------
st.title("📊 Sales Performance Dashboard")
st.markdown("### Interactive view of sales, profits, and products")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload a Sales CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Convert dates
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(
            df["Order Date"], dayfirst=True, errors="coerce")

    # -------------------------------
    # Sidebar Filters
    # -------------------------------
    st.sidebar.header("🔍 Filters")

    if "Order Date" in df.columns:
        years = df["Order Date"].dt.year.unique()
        selected_year = st.sidebar.selectbox("Select Year", sorted(years))
        df = df[df["Order Date"].dt.year == selected_year]

    if "Region" in df.columns:
        regions = df["Region"].unique().tolist()
        selected_regions = st.sidebar.multiselect(
            "Select Region(s)", regions, default=regions)
        df = df[df["Region"].isin(selected_regions)]

    # -------------------------------
    # Tabs
    # -------------------------------
    tab1, tab2, tab3 = st.tabs(["📌 Overview", "📈 Trends", "🏆 Products"])

    # ---- Overview Tab ----
    with tab1:
        st.markdown("### 📌 Key Metrics")
        total_sales = df["Sales"].sum()
        total_profit = df["Profit"].sum()
        total_quantity = df["Quantity"].sum()
        profit_margin = (total_profit / total_sales) * \
            100 if total_sales != 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"<div class='metric-card'><h3>💰 Sales</h3><h2>${total_sales:,.0f}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"<div class='metric-card'><h3>📈 Profit</h3><h2>${total_profit:,.0f}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"<div class='metric-card'><h3>📊 Margin</h3><h2>{profit_margin:.2f}%</h2></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(
                f"<div class='metric-card'><h3>📦 Quantity</h3><h2>{total_quantity:,}</h2></div>", unsafe_allow_html=True)

    # ---- Trends Tab ----
    with tab2:
        st.markdown("### 📈 Sales & Profit Trends")
        col1, col2 = st.columns(2)

        if "Order Date" in df.columns:
            sales_trend = df.groupby(
                df["Order Date"].dt.to_period("M")).sum(numeric_only=True)
            sales_trend.index = sales_trend.index.to_timestamp()

            fig_sales = px.line(
                sales_trend, x=sales_trend.index, y="Sales",
                title="💰 Sales Over Time", markers=True, template="plotly_white"
            )
            col1.plotly_chart(fig_sales, use_container_width=True)

            if "Profit" in df.columns:
                fig_profit = px.line(
                    sales_trend, x=sales_trend.index, y="Profit",
                    title="📈 Profit Over Time", markers=True, template="plotly_white"
                )
                col2.plotly_chart(fig_profit, use_container_width=True)

        if "Category" in df.columns:
            sales_category = df.groupby(
                "Category")["Sales"].sum().reset_index()
            fig_cat = px.bar(
                sales_category, x="Category", y="Sales",
                title="📂 Sales by Category", text_auto=True,
                color="Category", template="plotly_white"
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        if "Region" in df.columns:
            sales_region = df.groupby("Region")["Sales"].sum().reset_index()
            fig_region = px.bar(
                sales_region, x="Region", y="Sales",
                title="🌍 Sales by Region", text_auto=True,
                color="Region", template="plotly_white"
            )
            st.plotly_chart(fig_region, use_container_width=True)

    # ---- Products Tab ----
    with tab3:
        st.markdown("### 🏆 Top Products by Sales")
        if "Product Name" in df.columns:
            top_products = df.groupby("Product Name")[["Sales", "Profit", "Quantity"]] \
                             .sum().sort_values(by="Sales", ascending=False).head(10)

            st.dataframe(top_products.style.background_gradient(cmap="Blues"))

else:
    st.info("👆 Upload your sales file to explore insights.")
