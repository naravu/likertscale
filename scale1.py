# app.py

import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Load questions from existing Markdown file ---
def load_questions(md_file="baby_assessment.md"):
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

st.title("Baby Care Beliefs & Behaviours Survey")

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

st.subheader("Your Responses (Numeric Codes)")
st.dataframe(df)

# --- Google Sheets Integration ---
def append_to_google_sheet(dataframe, sheet_name="BabyCareSurveyResponses"):
    # Define scope
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # Authenticate using service account
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # Open sheet
    sheet = client.open(sheet_name).sheet1

    # Append row
    sheet.append_row(dataframe.iloc[0].tolist())

# --- Submit Button ---
if st.button("Submit Responses"):
    if name and code:
        append_to_google_sheet(df)
        st.success("Responses submitted and saved to Google Sheet!")
    else:
        st.error("Please enter Name and Code before submitting.")

# --- Download buttons ---
csv_buffer = BytesIO()
df.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, sheet_name="Responses", engine="openpyxl")
excel_buffer.seek(0)

st.download_button(
    label="Download responses as CSV",
    data=csv_buffer,
    file_name="responses.csv",
    mime="text/csv"
)

st.download_button(
    label="Download responses as Excel",
    data=excel_buffer,
    file_name="responses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
