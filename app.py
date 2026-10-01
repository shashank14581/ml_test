import random
import streamlit as st

st.set_page_config(page_title="RL Concepts Builder", page_icon="🎯", layout="wide")

st.title("Reinforcement Learning — Concepts Builder")
st.caption("Build the intuition first: State → Action → Reward → Return → Value → Bellman → Q-Learning")

N_STATES = 7
START = 3
TRAP = 0
GOAL = 6
ACTIONS = ["LEFT", "RIGHT"]


def env_step(state, action):
    nxt = max(TRAP, state - 1) if action == "LEFT" else min(GOAL, state + 1)
    if nxt == GOAL:
        return nxt, 10.0, True
    if nxt == TRAP:
        return nxt, -10.0, True
    return nxt, -0.1, False


def fresh_q():
    return {s: {a: 0.0 for a in ACTIONS} for s in range(N_STATES)}


def greedy(q, state):
    l, r = q[state]["LEFT"], q[state]["RIGHT"]
    if l == r:
        return random.choice(ACTIONS)
    return "LEFT" if l > r else "RIGHT"


def q_train(q, episodes, alpha, gamma, epsilon):
    returns = []
    for _ in range(episodes):
        s = START
        total = 0.0
        for _ in range(50):
            a = random.choice(ACTIONS) if random.random() < epsilon else greedy(q, s)
            ns, reward, done = env_step(s, a)
            next_best = 0.0 if done else max(q[ns].values())
            target = reward + gamma * next_best
            td_error = target - q[s][a]
            q[s][a] += alpha * td_error
            total += reward
            s = ns
            if done:
                break
        returns.append(total)
    return returns


for key, value in {
    "q": fresh_q(),
    "agent_state": START,
    "episode_return": 0.0,
    "history": [],
    "last_transition": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.header("Learning controls")
    gamma = st.slider("γ — Discount factor", 0.0, 1.0, 0.90, 0.01)
    alpha = st.slider("α — Learning rate", 0.01, 1.0, 0.20, 0.01)
    epsilon = st.slider("ε — Exploration rate", 0.0, 1.0, 0.20, 0.01)
    episodes = st.slider("Training episodes", 10, 5000, 500, 10)
    c1, c2 = st.columns(2)
    if c1.button("Train", use_container_width=True):
        st.session_state.history.extend(q_train(st.session_state.q, episodes, alpha, gamma, epsilon))
    if c2.button("Reset", use_container_width=True):
        st.session_state.q = fresh_q()
        st.session_state.agent_state = START
        st.session_state.episode_return = 0.0
        st.session_state.history = []
        st.session_state.last_transition = None
        st.rerun()

concept = st.radio(
    "Choose a concept",
    ["1. RL Basics", "2. Return & Discounting", "3. State Value V(s)", "4. Action Value Q(s,a)", "5. Bellman Equation", "6. Q-Learning", "7. Exploration vs Exploitation"],
    horizontal=True,
)

st.divider()

if concept == "1. RL Basics":
    st.header("1. RL Basics")
    st.markdown("""
**Agent** — the learner / decision maker.  
**Environment** — the world the agent interacts with.  
**State (S)** — current situation of the agent.  
**Action (A)** — decision taken by the agent.  
**Reward (R)** — immediate feedback from the environment.  
**Policy (π)** — rule used by the agent to choose actions.

The basic loop is:

**State → Action → Environment → Reward + Next State → Action → ...**
""")

    st.subheader("Interact with the environment")
    cols = st.columns(N_STATES)
    for s in range(N_STATES):
        if s == TRAP:
            text = "💀 TRAP"
        elif s == GOAL:
            text = "🏆 GOAL"
        elif s == st.session_state.agent_state:
            text = "🤖 AGENT"
        else:
            text = "·"
        cols[s].metric(f"State {s}", text)

    a, b = st.columns(2)
    action = None
    if a.button("← LEFT", use_container_width=True):
        action = "LEFT"
    if b.button("RIGHT →", use_container_width=True):
        action = "RIGHT"
    if action:
        s = st.session_state.agent_state
        if s in (TRAP, GOAL):
            s = START
            st.session_state.episode_return = 0.0
        ns, r, done = env_step(s, action)
        st.session_state.agent_state = ns
        st.session_state.episode_return += r
        st.session_state.last_transition = (s, action, r, ns)
        st.rerun()

    if st.session_state.last_transition:
        s, a0, r, ns = st.session_state.last_transition
        st.info(f"State s={s} → Action a={a0} → Reward r={r:+.1f} → Next state s′={ns}")

elif concept == "2. Return & Discounting":
    st.header("2. Return and Discount Factor γ")
    st.markdown("**Reward is immediate. Return is the total future reward the agent cares about.**")
    st.latex(r"G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2R_{t+3} + \cdots")
    rewards_text = st.text_input("Future rewards (comma separated)", "1, 2, 10")
    try:
        rewards = [float(x.strip()) for x in rewards_text.split(",")]
        parts, total = [], 0.0
        for i, r in enumerate(rewards):
            contribution = (gamma ** i) * r
            total += contribution
            parts.append({"Step": i + 1, "Reward": r, "Discount": round(gamma ** i, 4), "Contribution": round(contribution, 4)})
        st.dataframe(parts, use_container_width=True, hide_index=True)
        st.metric("Discounted return G", f"{total:.4f}")
    except ValueError:
        st.error("Enter numbers separated by commas.")
    st.write("γ close to 0 → short-sighted agent. γ close to 1 → future rewards matter strongly.")

elif concept == "3. State Value V(s)":
    st.header("3. State Value — V(s)")
    st.markdown("**V(s) asks: if I am in this state and continue following policy π, how much future return should I expect?**")
    st.latex(r"V_\pi(s)=\mathbb{E}_\pi[G_t\mid S_t=s]")
    st.write("It gives **one number per state**. It evaluates how good a state is, not which particular action is best.")
    st.info("Near the +10 goal, states should eventually acquire positive value. Near the −10 trap, states should acquire negative value.")

elif concept == "4. Action Value Q(s,a)":
    st.header("4. Action Value — Q(s,a)")
    st.markdown("**Q(s,a) asks: how good is taking action a in state s, followed by good future behaviour?**")
    st.latex(r"Q_\pi(s,a)=\mathbb{E}_\pi[G_t\mid S_t=s,A_t=a]")
    st.write("Unlike V(s), Q distinguishes actions. In our environment every non-terminal state has two values: Q(LEFT) and Q(RIGHT).")
    rows = [{"State": s, "Q(LEFT)": round(st.session_state.q[s]["LEFT"], 3), "Q(RIGHT)": round(st.session_state.q[s]["RIGHT"], 3)} for s in range(N_STATES)]
    st.dataframe(rows, use_container_width=True, hide_index=True)

elif concept == "5. Bellman Equation":
    st.header("5. Bellman Equation")
    st.markdown("The Bellman idea is simple: **value now = immediate reward + discounted value of what comes next.**")
    st.latex(r"V(s)=\mathbb{E}[R_{t+1}+\gamma V(S_{t+1})]")
    st.markdown("For optimal action values:")
    st.latex(r"Q^*(s,a)=\mathbb{E}[R_{t+1}+\gamma\max_{a'}Q^*(S_{t+1},a')]")
    st.subheader("Calculate one Bellman target")
    reward_demo = st.number_input("Immediate reward r", value=-0.1)
    next_q = st.number_input("Best Q-value in next state", value=5.0)
    target = reward_demo + gamma * next_q
    st.latex(r"Target = r + \gamma \max Q(s',a')")
    st.metric("Bellman target", f"{target:.4f}")
    st.write(f"Here: {reward_demo:.2f} + ({gamma:.2f} × {next_q:.2f}) = {target:.4f}")

elif concept == "6. Q-Learning":
    st.header("6. Q-Learning")
    st.markdown("Q-learning repeatedly moves the current Q-value toward the Bellman target.")
    st.latex(r"Q(s,a) \leftarrow Q(s,a)+\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)]")
    st.markdown("The bracketed quantity is the **TD error**:")
    st.latex(r"\delta = \underbrace{r+\gamma\max Q(s',a')}_{Target}-\underbrace{Q(s,a)}_{Current\ estimate}")
    st.write("Use **Train** in the sidebar, then inspect how reward information propagates backward from the goal.")
    rows = []
    for s in range(N_STATES):
        l, r = st.session_state.q[s]["LEFT"], st.session_state.q[s]["RIGHT"]
        policy = "terminal" if s in (TRAP, GOAL) else ("← LEFT" if l > r else "RIGHT →" if r > l else "?")
        rows.append({"State": s, "Q(LEFT)": round(l, 3), "Q(RIGHT)": round(r, 3), "Greedy policy": policy})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if st.session_state.history:
        st.line_chart(st.session_state.history[-500:], y_label="Episode return", x_label="Recent training episode")

else:
    st.header("7. Exploration vs Exploitation")
    st.markdown("""
**Exploitation** — choose the action currently believed to be best.  
**Exploration** — deliberately try another action to learn whether it might be better.

With ε-greedy:
""")
    st.latex(r"A_t=\begin{cases}\text{random action} & \text{with probability }\epsilon\\ \arg\max_a Q(s,a) & \text{with probability }1-\epsilon\end{cases}")
    st.metric("Current exploration probability", f"{epsilon:.0%}")
    st.metric("Current exploitation probability", f"{1-epsilon:.0%}")
    st.write("High ε early → discover alternatives. Lower ε later → use what has been learned.")

st.divider()
st.subheader("Concept ladder")
st.markdown("**Agent + Environment → State/Action/Reward → Return → V(s) → Q(s,a) → Bellman recursion → TD error → Q-learning → Policy**")
st.caption("Repository: shashank14581/ml_test • Interactive tabular RL concepts builder")
