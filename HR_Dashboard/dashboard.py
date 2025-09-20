import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- Page Config ---
st.set_page_config(page_title="HR Analytics Dashboard",
                   page_icon="👔", layout="wide")

# --- Branding Colors ---
CORPORATE_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
                    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

# --- Sidebar Upload ---
st.sidebar.header("📂 Upload HR Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

# --- Sample Template Download ---
sample_data = {
    "EmployeeID": [1, 2, 3],
    "Name": ["Alice", "Bob", "Charlie"],
    "Department": ["HR", "IT", "Finance"],
    "Gender": ["F", "M", "M"],
    "Age": [29, 34, 41],
    "Salary": [50000, 60000, 75000],
    "JobLevel": [1, 2, 3],
    "HireDate": ["2019-01-10", "2018-03-15", "2015-07-23"],
    "ExitDate": [None, "2022-05-01", None],
    "EmploymentStatus": ["Active", "Exited", "Active"],
    "PerformanceRating": [3, 4, 5]
}
sample_df = pd.DataFrame(sample_data)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    sample_df.to_excel(writer, index=False, sheet_name="HR_Template")
buffer.seek(0)

st.sidebar.download_button(
    label="📥 Download Excel Template",
    data=buffer,
    file_name="HR_Dashboard_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Load Data ---
if uploaded_file is None:
    st.info("👆 Upload an Excel file to begin. Use the template for reference.")
    st.stop()   # ⛔ Stop here, no charts will be displayed

df = pd.read_excel(uploaded_file)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
departments = st.sidebar.multiselect("Department", options=df["Department"].unique(),
                                     default=df["Department"].unique())
genders = st.sidebar.multiselect("Gender", options=df["Gender"].unique(),
                                 default=df["Gender"].unique())

filtered = df[df["Department"].isin(departments) & df["Gender"].isin(genders)]

# --- KPIs ---
st.title("👔 HR Analytics Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", len(filtered))
col2.metric("Active Employees",
            (filtered["EmploymentStatus"] == "Active").sum())
col3.metric("Exited Employees",
            (filtered["EmploymentStatus"] == "Exited").sum())
col4.metric("Avg. Salary", f"${filtered['Salary'].mean():,.0f}")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["👥 Workforce", "💰 Compensation", "📉 Attrition", "⭐ Performance"])

with tab1:
    st.subheader("Headcount by Department")
    dept = filtered.groupby("Department").size().reset_index(name="Count")
    st.plotly_chart(px.bar(dept, x="Department", y="Count", text="Count", color="Department",
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

    st.subheader("Gender Diversity")
    gender = filtered.groupby("Gender").size().reset_index(name="Count")
    st.plotly_chart(px.pie(gender, names="Gender", values="Count", hole=0.4,
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

    st.subheader("Age Distribution")
    st.plotly_chart(px.histogram(filtered, x="Age", nbins=10, color="Gender", barmode="overlay",
                                 color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

with tab2:
    st.subheader("Salary Distribution by Department")
    st.plotly_chart(px.box(filtered, x="Department", y="Salary", color="Department",
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

    st.subheader("Job Level Distribution")
    job_levels = filtered.groupby("JobLevel").size().reset_index(name="Count")
    st.plotly_chart(px.bar(job_levels, x="JobLevel", y="Count", text="Count", color="JobLevel",
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

with tab3:
    st.subheader("Employment Status (Attrition)")
    attrition = filtered.groupby(
        "EmploymentStatus").size().reset_index(name="Count")
    st.plotly_chart(px.pie(attrition, names="EmploymentStatus", values="Count", hole=0.4,
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

    st.subheader("Hires vs Exits Over Time")
    hires = pd.to_datetime(filtered["HireDate"], errors="coerce").dropna(
    ).dt.to_period("M").value_counts().sort_index()
    exits = pd.to_datetime(filtered["ExitDate"], errors="coerce").dropna(
    ).dt.to_period("M").value_counts().sort_index()
    trend = pd.DataFrame({"Hires": hires, "Exits": exits}).fillna(0)
    trend.index = trend.index.astype(str)
    st.plotly_chart(px.line(trend, x=trend.index, y=["Hires", "Exits"], markers=True,
                            color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)

with tab4:
    st.subheader("Performance Ratings Distribution")
    perf = filtered.groupby(
        "PerformanceRating").size().reset_index(name="Count")
    st.plotly_chart(px.bar(perf, x="PerformanceRating", y="Count", text="Count", color="PerformanceRating",
                           color_discrete_sequence=CORPORATE_COLORS), use_container_width=True)
