"""Applied ML thinking and implementation assessment — Streamlit entry point."""
import json
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

exam = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))
questions = exam["questions"]
st.set_page_config(page_title="Applied ML Trainee Exam", page_icon="🧠", layout="wide")

st.title(exam["title"])
st.caption(f"Candidate: {exam['candidate']} • 20 applied cases • 40 objective + 60 manually reviewed points")
st.info("Each scenario needs a reasoned decision AND a concrete implementation plan. Include pseudocode or SQL, data grain, metrics, validation, assumptions, and failure modes.")
st.warning("This Streamlit version does not securely proctor browser activity, verify identity or store results on a server. Download the submission before closing.")

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "submitted_at" not in st.session_state:
    st.session_state["submitted_at"] = None

with st.sidebar:
    st.header("Assessment navigation")
    index = st.radio("Case", range(len(questions)), format_func=lambda i: f"{i+1:02d} · {questions[i]['title']}")
    st.caption("Written responses require human review: 0–3 points per case.")

q = questions[index]
st.subheader(f"Case {index+1:02d} · {q['title']}")
st.caption(q["domain"])
st.markdown(q["scenario"])
st.markdown("#### Implementation challenge")
st.write(q["task"])
choice_key, answer_key = f"choice_{index}", f"reason_{index}"
choices = ["Select an answer"] + [f"{chr(65+i)}. {x}" for i,x in enumerate(q["options"])]
st.radio("Part A · Best decision (2 points)", choices, key=choice_key, disabled=st.session_state["submitted"])
st.text_area(
    "Part B · Reasoning and implementation (3 points, manually assessed)",
    key=answer_key, height=260,
    placeholder="Define the objective and data grain; show pseudocode or SQL, metrics, split, assumptions and failure modes...",
    disabled=st.session_state["submitted"],
)

def answers():
    result=[]
    for j,item in enumerate(questions):
        picked=st.session_state.get(f"choice_{j}", choices[0] if j==index else "Select an answer")
        idx=next((k for k,opt in enumerate(item["options"]) if picked==f"{chr(65+k)}. {opt}"), None)
        result.append({"number":j+1,"domain":item["domain"],"title":item["title"],
                       "choice_index":idx,"correct_index":item["answer"],
                       "reasoning":st.session_state.get(f"reason_{j}",""),
                       "objective_points":2 if idx==item["answer"] else 0,
                       "reviewer_rubric":item["rubric"],"explanation":item["explanation"]})
    return result

current=answers()
answered=sum(x["choice_index"] is not None and bool(x["reasoning"].strip()) for x in current)
st.progress(answered/20, text=f"{answered}/20 cases have both a decision and written reasoning")
if not st.session_state["submitted"]:
    st.markdown("### Submit the assessment")
    confirm=st.checkbox("I understand submitting locks my answers and reveals the review guidance.")
    if st.button("Submit assessment",type="primary",disabled=not confirm):
        st.session_state["submitted"]=True
        st.session_state["submitted_at"]=datetime.now(timezone.utc).isoformat()
        st.rerun()
else:
    score=sum(x["objective_points"] for x in current)
    st.success(f"Submitted · Objective score: {score}/40. Written work: awaiting manual review (up to 60 points).")
    payload={"candidate":exam["candidate"],"version":exam["version"],
             "submitted_at":st.session_state["submitted_at"],"objective_score":score,
             "objective_max":40,"written_score":"Pending human review (60 points)",
             "integrity":"Not securely proctored", "responses":current}
    st.download_button("Download submission and rubric (JSON)",
                       json.dumps(payload,indent=2),file_name="ml_exam_geetanjali_submission.json",
                       mime="application/json")
    st.markdown("### Post-submission feedback")
    st.write(f"**Correct decision:** {q['options'][q['answer']]}")
    st.write(q["explanation"])
    st.markdown("**Reviewer rubric: one point per criterion**")
    for criterion in q["rubric"]:
        st.write(f"• {criterion}")
