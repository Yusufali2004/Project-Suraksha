import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Project Suraksha Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- Data Loading and Merging ---
# Function to load data to allow caching
@st.cache_data
def load_data():
    attendance_df = pd.read_csv("attendance.csv")
    scores_df = pd.read_csv("scores.csv")
    fees_df = pd.read_csv("fees.csv")

    # Merge the dataframes into one
    student_df = pd.merge(attendance_df, scores_df, on="StudentID")
    student_df = pd.merge(student_df, fees_df, on="StudentID")
    return student_df

student_df = load_data()

# --- Risk Evaluation Engine ---
def calculate_risk(row):
    score_drop = (row['PreviousScore'] - row['RecentScore'])
    fees_due = row['FeesTotal'] - row['FeesPaid']

    # [cite_start]Rule-based logic [cite: 108]
    if row['AttendancePercentage'] < 75 or score_drop > 15 or fees_due > 25000:
        return "High"
    elif row['AttendancePercentage'] < 85 or score_drop > 10 or fees_due > 10000:
        return "Medium"
    else:
        return "Low"

# [cite_start]Apply the risk logic to each student [cite: 108]
student_df['RiskLevel'] = student_df.apply(calculate_risk, axis=1)
student_df['ScoreDrop'] = student_df['PreviousScore'] - student_df['RecentScore']
student_df['FeesDue'] = student_df['FeesTotal'] - student_df['FeesPaid']


# --- Dashboard UI ---
st.title("🛡️ Project Suraksha: Student Success Dashboard")
st.write("An early warning system to identify and support at-risk students.")

# --- Key Metrics ---
high_risk_count = student_df[student_df['RiskLevel'] == 'High'].shape[0]
medium_risk_count = student_df[student_df['RiskLevel'] == 'Medium'].shape[0]
total_students = student_df.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Students", total_students)
col2.metric("High-Risk Students", high_risk_count)
col3.metric("Medium-Risk Students", medium_risk_count)

st.markdown("---")

# --- Interactive Filters ---
st.sidebar.header("Filter Students")
risk_filter = st.sidebar.multiselect(
    "Select Risk Level",
    options=student_df['RiskLevel'].unique(),
    default=student_df['RiskLevel'].unique()
)

filtered_df = student_df[student_df['RiskLevel'].isin(risk_filter)]

# --- Display Data with Color Coding ---
st.subheader("Student Risk Overview")

# Function to apply color based on risk level
def style_risk(row):
    if row.RiskLevel == 'High':
        return ['background-color: #FF7276'] * len(row)
    elif row.RiskLevel == 'Medium':
        return ['background-color: #FFC107'] * len(row)
    else:
        return ['background-color: #82E0AA'] * len(row)

# Apply the styling to the dataframe
st.dataframe(
    filtered_df[['StudentName', 'RiskLevel', 'AttendancePercentage', 'ScoreDrop', 'FeesDue']].style.apply(style_risk, axis=1),
    use_container_width=True
)

# --- Simulate Notification ---
st.subheader("Take Action")
selected_student = st.selectbox("Select a student to notify:", options=filtered_df[filtered_df['RiskLevel']=='High']['StudentName'])

if st.button(f"Send Alert for {selected_student}"):
    st.success(f"✅ Alert successfully sent to the mentor and guardian of {selected_student}!")
    st.info( "This demonstrates the notification functionality. In the full version, this would trigger an actual Email/SMS.")