# app.py

import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

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

st.title("Baby Care Beliefs & Behaviours Survey")

# --- Automated Participant Info ---
st.subheader("Participant Information")
name = st.text_input("Name", key="participant_name")
code = st.text_input("Code", key="participant_code")
survey_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # auto timestamp

responses = {}

# --- Render form dynamically from md file ---
for category, qs in questions.items():
    with st.expander(category, expanded=True):  # collapsible sections
        for q in qs:
            choice = st.selectbox(q, options, key=q)
            responses[q] = option_map[choice]  # store numeric value

# --- Convert responses to horizontal DataFrame ---
row_data = {"Name": name, "Code": code, "DateTime": survey_datetime}
row_data.update(responses)  # add all questions as columns

df = pd.DataFrame([row_data])  # single row per submission

st.subheader("Your Responses (Numeric Codes)")
st.dataframe(df)

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
