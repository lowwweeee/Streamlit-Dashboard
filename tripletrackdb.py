import streamlit as st
import plotly.express as px
import pandas as pd
import io

st.set_page_config(page_title="Triple Track Garage - Hot Wheels",
                   page_icon="🚗", layout="wide")

# Title
st.title("🚗 Triple Track Garage - Hot Wheels Sales Dashboard")
st.markdown("""
<style>
    div.block-container {
        padding-top: 2rem;
    }
    h1, h2, h3, h4 {
        font-family: Arial, sans-serif;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ---- Download Template Button ----
template_data = {
    "Order Date": ["2023-01-15", "2023-02-10"],
    "Buyer Name": ["John Doe", "Jane Smith"],
    "Location": ["Manila", "Cebu"],
    "Class": ["Sports Car", "Truck"],
    "Price": [250.00, 300.00],
    "Quantity": [2, 1],
    "Cost": [150.00, 200.00]
}
template_df = pd.DataFrame(template_data)

# Save to Excel in memory
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    template_df.to_excel(writer, index=False, sheet_name="Template")
buffer.seek(0)

st.download_button(
    label="⬇️ Download Excel Template",
    data=buffer,
    file_name="sales_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---- File uploader ----
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Use openpyxl engine for modern Excel files
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success("File uploaded successfully!")
        st.write(df.head())  # show preview
    except Exception as e:
        st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload an Excel file to proceed.")

    # Ensure numeric columns
    df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')
    df["Cost"] = pd.to_numeric(df["Cost"], errors='coerce')

    # Calculate Amount Collected and Profit
    df["Amount Collected"] = df["Price"] * df["Quantity"]
    df["Profit"] = (df["Price"] - df["Cost"]) * df["Quantity"]

    # Sidebar filters
    st.sidebar.header("🔎 Filters")
    location = st.sidebar.multiselect(
        "Select Location", df["Location"].unique())
    car_class = st.sidebar.multiselect("Select Class", df["Class"].unique())

    filtered_df = df.copy()
    if location:
        filtered_df = filtered_df[filtered_df["Location"].isin(location)]
    if car_class:
        filtered_df = filtered_df[filtered_df["Class"].isin(car_class)]

    # KPI Section
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales",
                f"₱{filtered_df['Amount Collected'].sum():,.2f}")
    col2.metric("Total Quantity Sold", f"{int(filtered_df['Quantity'].sum())}")
    col3.metric("Unique Buyers", f"{int(filtered_df['Buyer Name'].nunique())}")
    col4.metric("Total Profit", f"₱{filtered_df['Profit'].sum():,.2f}")

    # Charts
    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader("Class-wise Sales & Profit")
        summary_class = filtered_df.groupby(
            "Class")[['Amount Collected', 'Profit']].sum().reset_index()
        fig1 = px.bar(summary_class, x="Class", y=["Amount Collected", "Profit"], text_auto=True,
                      barmode='group', template="simple_white")
        st.plotly_chart(fig1, use_container_width=True)

    with chart2:
        st.subheader("Location-wise Sales & Profit")
        summary_location = filtered_df.groupby(
            "Location")[['Amount Collected', 'Profit']].sum().reset_index()
        fig2 = px.bar(summary_location, x="Location", y=["Amount Collected", "Profit"], text_auto=True,
                      barmode='group', template="simple_white")
        st.plotly_chart(fig2, use_container_width=True)

    # Time Series
    st.subheader("📈 Sales & Profit Over Time")
    filtered_df["Order Date"] = pd.to_datetime(
        filtered_df["Order Date"], errors='coerce')
    time_series = filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M"))[
        ['Amount Collected', 'Profit']].sum().reset_index()
    time_series["Order Date"] = time_series["Order Date"].astype(str)
    fig3 = px.line(time_series, x="Order Date", y=[
                   "Amount Collected", "Profit"], markers=True, template="simple_white")
    st.plotly_chart(fig3, use_container_width=True)

    # Detailed Data
    st.subheader("📋 Sales Records")
    st.write(filtered_df.style.background_gradient(cmap="Blues"))

else:
    st.info("Please upload a CSV or Excel file to view the dashboard.")
