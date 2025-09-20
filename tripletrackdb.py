import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Triple Track Garage - Hot Wheels",
                   page_icon="🚗", layout="wide")

# ----------------------------
# Global Styling
# ----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Arial', sans-serif;
    color: #333;
}

div.stDownloadButton > button,
div.stButton > button,
div[data-testid="stFileUploader"] button {
    background-color: #007BFF;
    color: white !important;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    height: 45px;
    width: 100%;
    border: none;
    transition: 0.3s;
}
div.stDownloadButton > button:hover,
div.stButton > button:hover,
div[data-testid="stFileUploader"] button:hover {
    background-color: #0056b3;
    color: #fff !important;
}

div[data-testid="stFileUploader"] section {
    border: 2px dashed #007BFF;
    background-color: #f9f9ff;
    padding: 20px;
    border-radius: 10px;
    transition: 0.3s;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: #0056b3;
    background-color: #eef3ff;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Title
# ----------------------------
st.title("Triple Track Garage - Hot Wheels Sales Dashboard")

# ----------------------------
# Download Template
# ----------------------------
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

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    template_df.to_excel(writer, index=False, sheet_name="Template")
buffer.seek(0)

st.download_button(
    label="Download Excel Template",
    data=buffer,
    file_name="sales_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ----------------------------
# File Upload
# ----------------------------
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success("File uploaded successfully.")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    else:
        # Convert numeric columns
        for col in ["Price", "Quantity", "Cost"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Derived columns
        df["Amount Collected"] = df["Price"] * df["Quantity"]
        df["Profit"] = (df["Price"] - df["Cost"]) * df["Quantity"]

        # ----------------------------
        # Sidebar Filters
        # ----------------------------
        st.sidebar.header("Filters")
        location_filter = st.sidebar.multiselect("Select Location", df["Location"].unique())
        class_filter = st.sidebar.multiselect("Select Class", df["Class"].unique())

        filtered_df = df.copy()
        if location_filter:
            filtered_df = filtered_df[filtered_df["Location"].isin(location_filter)]
        if class_filter:
            filtered_df = filtered_df[filtered_df["Class"].isin(class_filter)]

        # ----------------------------
        # Key Metrics
        # ----------------------------
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", f"₱{filtered_df['Amount Collected'].sum():,.2f}")
        col2.metric("Total Quantity", f"{int(filtered_df['Quantity'].sum())}")
        col3.metric("Unique Buyers", f"{int(filtered_df['Buyer Name'].nunique())}")
        col4.metric("Total Profit", f"₱{filtered_df['Profit'].sum():,.2f}")

        # ----------------------------
        # Charts
        # ----------------------------
        chart1, chart2 = st.columns(2)

        with chart1:
            st.subheader("Sales & Profit by Class")
            summary_class = (
                filtered_df.groupby("Class")[["Amount Collected", "Profit"]]
                .sum()
                .reset_index()
            )
            fig1 = px.bar(summary_class, x="Class",
                          y=["Amount Collected", "Profit"],
                          barmode="group", text_auto=True,
                          template="simple_white")
            st.plotly_chart(fig1, use_container_width=True)

        with chart2:
            st.subheader("Sales & Profit by Location")
            summary_location = (
                filtered_df.groupby("Location")[["Amount Collected", "Profit"]]
                .sum()
                .reset_index()
            )
            fig2 = px.bar(summary_location, x="Location",
                          y=["Amount Collected", "Profit"],
                          barmode="group", text_auto=True,
                          template="simple_white")
            st.plotly_chart(fig2, use_container_width=True)

        # ----------------------------
        # Time Series
        # ----------------------------
        st.subheader("Sales & Profit Over Time")
        filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"], errors="coerce")
        time_series = (
            filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M"))
            [["Amount Collected", "Profit"]]
            .sum()
            .reset_index()
        )
        time_series["Order Date"] = time_series["Order Date"].astype(str)

        fig3 = px.line(time_series, x="Order Date",
                       y=["Amount Collected", "Profit"],
                       markers=True, template="simple_white")
        st.plotly_chart(fig3, use_container_width=True)

        # ----------------------------
        # Detailed Data
        # ----------------------------
        st.subheader("Sales Records")
        st.dataframe(filtered_df.style.background_gradient(cmap="Blues"),
                     use_container_width=True)

else:
    st.info("Please upload an Excel file to view the dashboard.")
