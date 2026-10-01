import time
import uuid
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="ML Reasoning Assessment", page_icon="🧠", layout="wide")
DURATION_MIN = 75

QUESTIONS = {
    "q1": {"answer": "B", "answer_text": "The split may be unstable and overfit a tiny sample", "points": 5},
    "q2": {"answer": "C", "answer_text": "Increase min_samples_leaf", "points": 5},
    "q3": {"answer": 0.48, "answer_text": "0.48", "tol": 0.01, "points": 5},
    "q4": {"answer": "B", "answer_text": "It trades some training fit for a simpler tree", "points": 5},
    "q5": {"answer": -2.0, "answer_text": "-2.0", "tol": 0.01, "points": 5},
    "q6": {"answer": 2.0, "answer_text": "2.0", "tol": 0.01, "points": 5},
    "q7": {"answer": "B", "answer_text": "Makes XGBoost more conservative about creating low-Hessian child nodes", "points": 5},
    "q8": {"answer": "C", "answer_text": "Each new tree is fitted to improve the current ensemble objective", "points": 5},
    "q9": {"answer": "C", "answer_text": "Accuracy alone is nearly meaningless here; inspect class-sensitive metrics and the confusion matrix", "points": 5},
    "q10": {"answer": "B", "answer_text": "Train on earlier periods and validate on a later unseen period", "points": 5},
}

QUESTION_LABELS = {
    "q1": "Q1 — Split behaviour",
    "q2": "Q2 — Regularisation",
    "q3": "Q3 — Gini calculation",
    "q4": "Q4 — Pruning",
    "q5": "Q6 — XGBoost leaf value",
    "q6": "Q7 — XGBoost split gain",
    "q7": "Q8 — min_child_weight",
    "q8": "Q9 — Sequential boosting",
    "q9": "Q11 — Imbalanced classification",
    "q10": "Q12 — Validation design",
}


def init_state():
    defaults = {"started": False, "submitted": False, "failed": False, "fail_reason": "", "start_time": None, "candidate": "", "exam_id": uuid.uuid4().hex}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def grade_question(key):
    spec = QUESTIONS[key]
    value = st.session_state.get(key)
    if "tol" in spec:
        try:
            correct = abs(float(value) - spec["answer"]) <= spec["tol"]
        except (TypeError, ValueError):
            correct = False
    else:
        correct = isinstance(value, str) and value.startswith(spec["answer"] + " ")
    return correct, spec["points"] if correct else 0


def objective_score():
    score, detail = 0, {}
    for key in QUESTIONS:
        correct, earned = grade_question(key)
        score += earned
        detail[key] = {"correct": correct, "earned": earned}
    return score, detail


def text_answer(key, label, height=150):
    return st.text_area(label, key=key, height=height)


def display_answer(value):
    if value is None or value == "":
        return "No answer"
    return str(value)


def candidate_report():
    score, detail = objective_score()
    lines = [f"Candidate: {st.session_state.candidate}", f"Objective score: {score}/50", "", "OBJECTIVE ANSWER KEY"]
    for key, spec in QUESTIONS.items():
        lines.append(f"{QUESTION_LABELS[key]}: candidate={display_answer(st.session_state.get(key))} | correct={spec['answer']} — {spec['answer_text']} | marks={detail[key]['earned']}/{spec['points']}")
    lines.append("\nWRITTEN RESPONSES — MANUAL REVIEW\n")
    for key in ["r1", "r2", "r3", "r4", "r5"]:
        lines.append(f"{key.upper()}:\n{st.session_state.get(key, '')}\n")
    return "\n".join(lines)


init_state()
st.title("Advanced Machine Learning Reasoning Assessment")
st.caption("Decision Trees • XGBoost • General ML Thinking • Applied Problem Solving")

if not st.session_state.started:
    st.info("This assessment tests reasoning, not recall. Explain assumptions where needed. A calculator and rough work are allowed; external assistance is not.")
    st.warning("Assessment integrity rule: after starting, switching to another browser tab or hiding this tab ends the attempt and records a fail. Keep this tab active until submission.")
    candidate = st.text_input("Candidate name")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duration", f"{DURATION_MIN} min")
    c2.metric("Total marks", "100")
    c3.metric("Reasoning / written", "50 marks")
    if st.button("Start assessment", type="primary", disabled=not candidate.strip()):
        st.session_state.candidate = candidate.strip()
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

exam_key = "ml_integrity_" + st.session_state.exam_id
js = f"""
(() => {{
  const key = '{exam_key}';
  if (!window.__mlAssessmentIntegrityInstalled) {{
    window.__mlAssessmentIntegrityInstalled = true;
    document.addEventListener('visibilitychange', () => {{
      if (document.hidden) localStorage.setItem(key, 'TAB_SWITCH');
    }});
  }}
  return localStorage.getItem(key) || 'OK';
}})()
"""
violation = streamlit_js_eval(js_expressions=js, key="integrity_monitor")
st_autorefresh(interval=1000, limit=None, key="integrity_refresh")

if violation == "TAB_SWITCH" and not st.session_state.submitted:
    st.session_state.failed = True
    st.session_state.fail_reason = "Browser tab/window was hidden during the assessment."

elapsed = int(time.time() - st.session_state.start_time)
remaining = max(0, DURATION_MIN * 60 - elapsed)
mins, secs = divmod(remaining, 60)
if remaining == 0 and not st.session_state.submitted:
    st.session_state.failed = True
    st.session_state.fail_reason = "Assessment time expired before submission."

if st.session_state.failed:
    st.error("Assessment failed")
    st.write(f"**Candidate:** {st.session_state.candidate}")
    st.write(st.session_state.fail_reason)
    st.info("This attempt is locked. Contact the evaluator if the failure was caused by a browser or system event outside your control.")
    st.stop()

with st.sidebar:
    st.header("Assessment")
    st.write(f"**Candidate:** {st.session_state.candidate}")
    st.metric("Time remaining", f"{mins:02d}:{secs:02d}")
    st.progress(min(1.0, elapsed / (DURATION_MIN * 60)))
    st.caption("Do not change browser tabs until you submit.")

if st.session_state.submitted:
    score, detail = objective_score()
    st.success("Assessment submitted successfully.")
    st.header("Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Objective score", f"{score}/50")
    c2.metric("Objective percentage", f"{score * 2:.0f}%")
    c3.metric("Written assessment", "Pending /50")
    st.caption("The objective portion is scored automatically. Written reasoning requires evaluator review before a final score out of 100 can be assigned.")

    st.subheader("Objective answer key")
    rows = []
    for key, spec in QUESTIONS.items():
        result = detail[key]
        rows.append({
            "Question": QUESTION_LABELS[key],
            "Your answer": display_answer(st.session_state.get(key)),
            "Correct answer": f"{spec['answer']} — {spec['answer_text']}" if "tol" not in spec else spec["answer_text"],
            "Result": "Correct" if result["correct"] else "Incorrect",
            "Marks": f"{result['earned']}/{spec['points']}",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("Written responses")
    st.info("These questions are not auto-scored. They remain pending manual evaluation.")
    written = [
        ("Q5 — Tree reasoning", "r1"),
        ("Q10 — Gradient/Hessian reasoning", "r2"),
        ("Q13 — Leakage diagnosis", "r3"),
        ("Q14 — Metric choice", "r4"),
        ("Q15 — Applied ML case", "r5"),
    ]
    for label, key in written:
        with st.expander(label):
            st.write(st.session_state.get(key, "") or "No response")

    report = st.session_state.get("evaluator_report") or candidate_report()
    st.download_button("Download results and answer key", report, file_name=f"{st.session_state.candidate.replace(' ', '_')}_ml_assessment_results.txt", mime="text/plain")
    st.stop()

st.header("Section A — Decision Trees")
st.caption("25 marks • Go beyond definitions.")
st.markdown("**Q1 — Split behaviour (5 marks)**  \nA binary classifier has a continuous feature `income`. One candidate split produces two almost pure child nodes, but one child contains only 3 of 10,000 observations. Which is the strongest concern?")
st.radio("Choose one", ["A — Gini cannot be used on continuous features", "B — The split may be unstable and overfit a tiny sample", "C — Pure nodes always imply leakage", "D — Decision trees require balanced child nodes"], key="q1")
st.markdown("**Q2 — Regularisation (5 marks)**  \nTraining accuracy is 99.8%, validation accuracy is 78%. Which change most directly constrains overly specific leaves?")
st.radio("Choose one", ["A — Increase max_depth", "B — Decrease min_samples_leaf", "C — Increase min_samples_leaf", "D — Remove all categorical features"], key="q2")
st.markdown("**Q3 — Gini calculation (5 marks)**  \nA node contains 60 positives and 40 negatives. Enter its Gini impurity.")
st.number_input("Gini impurity", min_value=0.0, max_value=1.0, step=0.01, key="q3")
st.markdown("**Q4 — Pruning (5 marks)**  \nWhy can cost-complexity pruning improve generalisation?")
st.radio("Choose one", ["A — It guarantees every leaf has equal observations", "B — It trades some training fit for a simpler tree", "C — It converts the tree into an ensemble", "D — It removes the need for validation"], key="q4")
st.markdown("**Q5 — Tree reasoning (5 marks, evaluator review)**")
text_answer("r1", "A feature `customer_id` produces extremely large impurity reduction and dominates the first few levels of a tree. Explain what you would investigate before celebrating the result.")

st.divider()
st.header("Section B — XGBoost Under the Hood")
st.caption("30 marks • Show that you understand what boosting is optimising.")
st.markdown("**Q6 — Leaf value (5 marks)**  \nFor one candidate leaf, sum of gradients G = 8, sum of Hessians H = 3, and λ = 1. Using `w* = -G / (H + λ)`, calculate the optimal leaf weight.")
st.number_input("Optimal leaf weight", step=0.1, key="q5")
st.markdown("**Q7 — Split gain (5 marks)**  \nIgnoring γ, use `Gain = 1/2 [GL²/(HL+λ) + GR²/(HR+λ) - G²/(H+λ)]`. Let GL=6, HL=2, GR=2, HR=1, λ=1. Calculate gain.")
st.number_input("Split gain", step=0.1, key="q6")
st.markdown("**Q8 — min_child_weight (5 marks)**  \nWhat does increasing `min_child_weight` generally do?")
st.radio("Choose one", ["A — Forces every tree to use fewer input columns", "B — Makes XGBoost more conservative about creating low-Hessian child nodes", "C — Directly increases learning rate", "D — Converts boosting into bagging"], key="q7")
st.markdown("**Q9 — Sequential boosting (5 marks)**  \nWhy aren't boosted trees trained independently like random-forest trees?")
st.radio("Choose one", ["A — Independent trees cannot split continuous variables", "B — XGBoost requires one tree per feature", "C — Each new tree is fitted to improve the current ensemble objective", "D — Independent trees cannot calculate Gini impurity"], key="q8")
st.markdown("**Q10 — Gradient/Hessian reasoning (10 marks, evaluator review)**")
text_answer("r2", "In your own words, explain what the gradient and Hessian are doing in XGBoost. Why is second-order information useful? Avoid simply expanding the formula.")

st.divider()
st.header("Section C — General ML Thinking")
st.caption("20 marks • Diagnose before prescribing.")
st.markdown("**Q11 — Imbalanced classification (5 marks)**  \nA fraud model has 99% accuracy. Fraud prevalence is 0.5%. What should you conclude first?")
st.radio("Choose one", ["A — The model is production ready", "B — Accuracy proves the classes are separable", "C — Accuracy alone is nearly meaningless here; inspect class-sensitive metrics and the confusion matrix", "D — Immediately oversample to 50/50"], key="q9")
st.markdown("**Q12 — Validation design (5 marks)**  \nYou predict customer purchases next month using two years of weekly history. Which validation design is usually most defensible?")
st.radio("Choose one", ["A — Randomly split individual rows regardless of time", "B — Train on earlier periods and validate on a later unseen period", "C — Train and validate on the same households and dates", "D — Select the split that gives the highest validation score"], key="q10")
st.markdown("**Q13 — Leakage diagnosis (5 marks, evaluator review)**")
text_answer("r3", "Your AUC jumps from 0.72 to 0.97 after adding a feature called `days_since_last_purchase`. The target is purchase in the next 30 days. What questions do you ask before accepting the improvement?")
st.markdown("**Q14 — Metric choice (5 marks, evaluator review)**")
text_answer("r4", "A retention team can contact only 5% of customers. Explain which evaluation metrics you would prioritise and why. There is no single required metric; justify your choice.")

st.divider()
st.header("Section D — Applied ML Case")
st.caption("25 marks • Treat this like a real project, not a textbook question.")
st.markdown("""
**Case**

A retailer wants to predict which households will make a purchase in the **next 30 days**. You have **18 months** of transactions, browsing behaviour, demographics and marketing interactions. Only **8%** of household-month observations are positive. Marketing will use the model to select customers for a campaign.

Your first model achieves ROC-AUC 0.88 on a random train/test split.

Then you discover:
- households appear repeatedly across months;
- one feature is `future_campaign_response_flag`;
- purchase behaviour changed materially during the most recent quarter;
- the business can contact only 10% of households.
""")
text_answer("r5", "Q15 — Design the solution end-to-end (25 marks). Discuss target construction, observation/anchor dates, leakage, splitting strategy, features, model choice, imbalance, evaluation, business thresholding, and what you would monitor after deployment.", height=350)

st.divider()
st.warning("Submission is final. Review your answers before submitting.")
confirm = st.checkbox("I have reviewed my answers and want to submit.")
if st.button("Submit assessment", type="primary", disabled=not confirm):
    st.session_state["objective_result"] = objective_score()[0]
    st.session_state["evaluator_report"] = candidate_report()
    st.session_state.submitted = True
    st.rerun()
