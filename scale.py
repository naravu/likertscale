# app.py

import streamlit as st
import pandas as pd
import re
from io import BytesIO

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

responses = {}

# --- Render form dynamically from md file ---
for category, qs in questions.items():
    with st.expander(category, expanded=True):  # collapsible sections
        for q in qs:
            choice = st.selectbox(q, options, key=q)
            responses[q] = option_map[choice]  # store numeric value

# --- Convert responses to DataFrame ---
df = pd.DataFrame(list(responses.items()), columns=["Question", "Response (Numeric)"])

st.subheader("Your Responses (Numeric Codes)")
st.dataframe(df)

# --- Download buttons ---
csv = df.to_csv(index=False).encode("utf-8")

# Excel export (in-memory)
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, sheet_name="Responses", engine="openpyxl")
excel_buffer.seek(0)

st.download_button(
    label="Download responses as CSV",
    data=csv,
    file_name="responses.csv",
    mime="text/csv"
)

st.download_button(
    label="Download responses as Excel",
    data=excel_buffer,
    file_name="responses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
