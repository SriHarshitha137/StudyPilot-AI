"""StudyPilot AI Streamlit dashboard."""
from __future__ import annotations

import os
from datetime import date
from io import StringIO

import pandas as pd
import streamlit as st

from ibm_granite import IBMGraniteAgent
from mock_granite import MockGraniteAgent
from utils import days_until, load_student_data, parse_subjects, save_student_data

st.set_page_config(page_title="StudyPilot AI", page_icon="🎓", layout="wide")
st.markdown("""<style>
.stApp { background: #f6f9ff; }
[data-testid="stSidebar"] { background: #083b8a; }
[data-testid="stSidebar"] * { color: #ffffff; }
.hero { background: linear-gradient(115deg,#083b8a,#1677d2); padding: 1.7rem 2rem; border-radius: 18px; color:white; margin-bottom:1rem; }
</style>""", unsafe_allow_html=True)


def engine():
    """Use offline mock by default; Granite is opt-in via AI_ENGINE."""
    return IBMGraniteAgent() if os.getenv("AI_ENGINE", "mock").lower() == "granite" else MockGraniteAgent()


def export_plan(profile, plan):
    output = StringIO()
    output.write("StudyPilot AI Study Plan for " + profile["student_name"] + "\n")
    output.write("Exam date: " + profile["exam_date"] + " | Target: " + str(profile["target_percentage"]) + "%\n\n")
    for item in plan:
        output.write(item["day"] + " — " + item["focus"] + " (" + item["hours"] + ")\n" + item["task"] + "\n\n")
    return output.getvalue()


if "profile" not in st.session_state:
    st.session_state.profile = load_student_data()
for key in ("plan", "revision", "tasks"):
    if key not in st.session_state:
        st.session_state[key] = []

profile = st.session_state.profile
with st.sidebar:
    st.title("🎓 StudyPilot AI")
    st.caption("Your personal study co-pilot")
    profile["student_name"] = st.text_input("Student Name", profile["student_name"])
    profile["semester"] = st.text_input("Semester", profile["semester"])
    profile["exam_date"] = str(st.date_input("Exam Date", date.fromisoformat(profile["exam_date"])))
    profile["subjects"] = parse_subjects(st.text_area("Subjects (comma separated)", ", ".join(profile["subjects"])))
    profile["weak_subjects"] = parse_subjects(st.text_area("Weak Subjects (comma separated)", ", ".join(profile["weak_subjects"])))
    profile["daily_study_hours"] = st.slider("Daily Study Hours", 1, 12, int(profile["daily_study_hours"]))
    profile["target_percentage"] = st.slider("Target Percentage", 40, 100, int(profile["target_percentage"]))
    ai = engine()
    if st.button("Generate Study Plan", use_container_width=True):
        st.session_state.plan = ai.generate_study_plan(profile)
    if st.button("Generate Revision Plan", use_container_width=True):
        st.session_state.revision = ai.generate_revision_plan(profile)
    if st.button("Generate Daily Tasks", use_container_width=True):
        st.session_state.tasks = ai.generate_daily_tasks(profile)
    if st.button("Generate Motivation", use_container_width=True):
        st.session_state.motivation = ai.generate_motivation(profile)
    if st.button("Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

save_student_data(profile)
ai = engine()
motivation = st.session_state.get("motivation") or ai.generate_motivation(profile)
priorities = ai.generate_subject_priority(profile)
if not st.session_state.tasks:
    st.session_state.tasks = ai.generate_daily_tasks(profile)
if not st.session_state.plan:
    st.session_state.plan = ai.generate_study_plan(profile)
if not st.session_state.revision:
    st.session_state.revision = ai.generate_revision_plan(profile)

st.markdown('<div class="hero"><h1>Welcome back, ' + profile["student_name"] + ' 👋</h1><p>Plan with purpose. Build momentum for ' + str(profile["target_percentage"]) + '%.</p></div>', unsafe_allow_html=True)
days = days_until(profile["exam_date"])
top = priorities[0] if priorities else {"subject": "—", "score": 0}
a, b, c, d = st.columns(4)
a.metric("Exam Countdown", str(days) + " days")
b.metric("Daily Study Hours", str(profile["daily_study_hours"]) + " hrs")
c.metric("Completion", str(profile.get("completion_percentage", 0)) + "%")
d.metric("Top Priority", str(top["subject"]))

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Today's Tasks")
    st.dataframe(pd.DataFrame(st.session_state.tasks), use_container_width=True, hide_index=True)
    st.subheader("Weekly Planner")
    st.dataframe(pd.DataFrame(st.session_state.plan), use_container_width=True, hide_index=True)
with right:
    st.subheader("Subject Priority")
    priority_frame = pd.DataFrame(priorities)
    st.bar_chart(priority_frame.set_index("subject")["score"])
    st.dataframe(priority_frame, use_container_width=True, hide_index=True)
    st.subheader("Study Analytics")
    st.progress(int(profile.get("completion_percentage", 0)))
    st.caption("Weak subjects: " + (", ".join(profile["weak_subjects"]) or "None selected"))
    st.caption("Priority score: " + str(top["score"]) + "/100")
    st.info("🍅 Pomodoro recommendation: complete " + str(max(2, profile["daily_study_hours"] * 2)) + " focused 25-minute sessions today.")
    st.success("“" + motivation["quote"] + "”\n\nTip: " + motivation["tip"])

st.subheader("Revision Planner")
st.dataframe(pd.DataFrame(st.session_state.revision), use_container_width=True, hide_index=True)
st.download_button("Export Study Plan (TXT)", data=export_plan(profile, st.session_state.plan), file_name="studypilot_study_plan.txt", mime="text/plain")
st.caption("Engine: IBM Granite" if os.getenv("AI_ENGINE", "mock").lower() == "granite" else "Engine: MockGraniteAgent (offline default)")

