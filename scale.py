# app.py

import streamlit as st
import pandas as pd
import re

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

options = ["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"]

st.title("Baby Care Beliefs & Behaviours Survey")

responses = {}

# --- Render form dynamically from md file ---
for category, qs in questions.items():
    st.header(category)
    for q in qs:
        choice = st.radio(q, options, key=q)
        responses[q] = choice

# --- Convert responses to DataFrame ---
df = pd.DataFrame(list(responses.items()), columns=["Question", "Response"])

st.subheader("Your Responses")
st.dataframe(df)

# --- Download buttons ---
csv = df.to_csv(index=False).encode("utf-8")

# Excel export (in-memory)
excel_buffer = pd.ExcelWriter("responses.xlsx", engine="xlsxwriter")
df.to_excel(excel_buffer, index=False, sheet_name="Responses")
excel_buffer.close()

with open("responses.xlsx", "rb") as f:
    excel_data = f.read()

st.download_button(
    label="Download responses as CSV",
    data=csv,
    file_name="responses.csv",
    mime="text/csv"
)

st.download_button(
    label="Download responses as Excel",
    data=excel_data,
    file_name="responses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
