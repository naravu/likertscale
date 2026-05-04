# app.py

import streamlit as st
import pandas as pd
import re
from datetime import datetime
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Load questions from existing Markdown file ---
def load_questions(md_file="scale.md"):
    questions = {}
    current_category = None
    with open(md_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):  # category heading
                current_category = line.replace("#", "").strip()
                questions[current_category] = []
            elif re.match(r"^\d+\.", line):  # numbered question
                q_text = line.split(".", 1)[1].strip()
                if current_category:
                    questions[current_category].append(q_text)
    return questions

questions = load_questions()

# Mapping of options to numeric codes
option_map = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Agree": 3,
    "Strongly Agree": 4
}
options = list(option_map.keys())

st.title("Baby Care Survey")

# --- Participant Info ---
st.subheader("Participant Information")
name = st.text_input("Name", key="participant_name")
code = st.text_input("Code", key="participant_code")
survey_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # auto timestamp

responses = {}

# --- Render form dynamically ---
for category, qs in questions.items():
    with st.expander(category, expanded=True):
        for q in qs:
            choice = st.selectbox(q, options, key=q)
            responses[q] = option_map[choice]

# --- Convert responses to horizontal DataFrame ---
row_data = {"Name": name, "Code": code, "DateTime": survey_datetime}
row_data.update(responses)
df = pd.DataFrame([row_data])

st.subheader("Responses (Numeric Codes)")
st.dataframe(df)

# --- Google Sheets Integration using Streamlit Secrets ---
def append_to_google_sheet(dataframe, sheet_name="likertscale", worksheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # Load credentials from Streamlit Secrets
    service_account_info = st.secrets["service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    # Open sheet and worksheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)

    # If sheet is empty, add header row first
    if len(sheet.get_all_values()) == 0:
        header = list(dataframe.columns.astype(str))
        sheet.append_row(header)

    # Convert all values to strings to avoid int64 serialization errors
    row_values = dataframe.iloc[0].astype(str).tolist()

    # Append row
    sheet.append_row(row_values)

# --- Custom CSS for smaller buttons ---
st.markdown("""
    <style>
    div.stButton > button, div.stDownloadButton > button {
        padding: 0.4em 0.8em;
        font-size: 0.85em;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Place buttons in a single row ---
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("✅ Submit"):
        if name and code:
            append_to_google_sheet(df, sheet_name="likertscale", worksheet_name="Sheet1")
            st.success("Responses submitted and saved to Google Sheet!")
        else:
            st.error("Please enter Name and Code before submitting.")

csv_buffer = BytesIO()
df.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, sheet_name="Responses", engine="openpyxl")
excel_buffer.seek(0)

with col2:
    st.download_button(
        label="📄 CSV",
        data=csv_buffer,
        file_name="responses.csv",
        mime="text/csv"
    )

with col3:
    st.download_button(
        label="📊 Excel",
        data=excel_buffer,
        file_name="responses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
