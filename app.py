import random
import streamlit as st

st.set_page_config(page_title="RL Lab", page_icon="🎯", layout="wide")

st.title("Reinforcement Learning Lab")
st.caption("Learn RL by watching an agent learn a policy from rewards.")

# -----------------------------
# Environment
# -----------------------------
N_STATES = 7
START = 3
GOAL = 6
TRAP = 0
ACTIONS = ["LEFT", "RIGHT"]


def step(state, action):
    """Simple 1-D environment."""
    if action == "LEFT":
        next_state = max(TRAP, state - 1)
    else:
        next_state = min(GOAL, state + 1)

    if next_state == GOAL:
        return next_state, 10.0, True
    if next_state == TRAP:
        return next_state, -10.0, True
    return next_state, -0.1, False


def fresh_q():
    return {s: {a: 0.0 for a in ACTIONS} for s in range(N_STATES)}


def greedy_action(q, state):
    left = q[state]["LEFT"]
    right = q[state]["RIGHT"]
    if left == right:
        return random.choice(ACTIONS)
    return "LEFT" if left > right else "RIGHT"


def train(q, episodes, alpha, gamma, epsilon):
    rewards = []
    for _ in range(episodes):
        state = START
        total_reward = 0.0

        for _ in range(50):
            if random.random() < epsilon:
                action = random.choice(ACTIONS)
            else:
                action = greedy_action(q, state)

            next_state, reward, done = step(state, action)
            best_next = max(q[next_state].values())

            # Q-learning update:
            # Q(s,a) <- Q(s,a) + alpha * [r + gamma max Q(s',a') - Q(s,a)]
            td_target = reward if done else reward + gamma * best_next
            q[state][action] += alpha * (td_target - q[state][action])

            state = next_state
            total_reward += reward
            if done:
                break

        rewards.append(total_reward)
    return rewards


if "q" not in st.session_state:
    st.session_state.q = fresh_q()
if "history" not in st.session_state:
    st.session_state.history = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = START
if "episode_reward" not in st.session_state:
    st.session_state.episode_reward = 0.0

# -----------------------------
# Controls
# -----------------------------
st.sidebar.header("Q-Learning Controls")
alpha = st.sidebar.slider("Learning rate (alpha)", 0.01, 1.0, 0.20, 0.01)
gamma = st.sidebar.slider("Discount factor (gamma)", 0.0, 1.0, 0.95, 0.01)
epsilon = st.sidebar.slider("Exploration (epsilon)", 0.0, 1.0, 0.20, 0.01)
episodes = st.sidebar.slider("Training episodes", 10, 5000, 500, 10)

col1, col2 = st.sidebar.columns(2)
if col1.button("Train", use_container_width=True):
    new_rewards = train(st.session_state.q, episodes, alpha, gamma, epsilon)
    st.session_state.history.extend(new_rewards)
    st.session_state.agent_state = START
    st.session_state.episode_reward = 0.0

if col2.button("Reset", use_container_width=True):
    st.session_state.q = fresh_q()
    st.session_state.history = []
    st.session_state.agent_state = START
    st.session_state.episode_reward = 0.0

# -----------------------------
# Environment view
# -----------------------------
st.subheader("1. Environment")
st.write("The agent starts in the middle. Reach the goal for **+10**. Hit the trap for **-10**. Every ordinary move costs **-0.1**.")

cells = []
for s in range(N_STATES):
    if s == TRAP:
        label = "💀 TRAP"
    elif s == GOAL:
        label = "🏆 GOAL"
    elif s == st.session_state.agent_state:
        label = "🤖 AGENT"
    else:
        label = f"State {s}"
    cells.append(label)

cols = st.columns(N_STATES)
for i, label in enumerate(cells):
    cols[i].metric(f"S{i}", label)

# Manual interaction makes state/action/reward concrete.
st.write("**Take an action manually**")
a, b, c = st.columns([1, 1, 3])
manual_action = None
if a.button("← LEFT", use_container_width=True):
    manual_action = "LEFT"
if b.button("RIGHT →", use_container_width=True):
    manual_action = "RIGHT"

if manual_action:
    old_state = st.session_state.agent_state
    if old_state in (TRAP, GOAL):
        old_state = START
        st.session_state.agent_state = START
        st.session_state.episode_reward = 0.0

    new_state, reward, done = step(old_state, manual_action)
    st.session_state.agent_state = new_state
    st.session_state.episode_reward += reward
    c.info(f"s={old_state}  →  a={manual_action}  →  r={reward:+.1f}  →  s'={new_state}")
    if done:
        c.success(f"Episode finished. Return = {st.session_state.episode_reward:+.1f}. Click an action to restart.")

# -----------------------------
# Q table / policy
# -----------------------------
st.divider()
st.subheader("2. What the agent learns")

rows = []
for s in range(N_STATES):
    if s in (TRAP, GOAL):
        policy = "terminal"
    else:
        l = st.session_state.q[s]["LEFT"]
        r = st.session_state.q[s]["RIGHT"]
        policy = "← LEFT" if l > r else "RIGHT →" if r > l else "?"
    rows.append({
        "State": s,
        "Q(LEFT)": round(st.session_state.q[s]["LEFT"], 3),
        "Q(RIGHT)": round(st.session_state.q[s]["RIGHT"], 3),
        "Greedy policy": policy,
    })

st.dataframe(rows, use_container_width=True, hide_index=True)

st.latex(r"Q(s,a) \leftarrow Q(s,a) + \alpha [r + \gamma \max_{a'}Q(s',a') - Q(s,a)]")
st.write("The bracketed term is the **TD error**: the difference between what the agent currently believes and the improved target produced by the reward plus the best estimated future value.")

# -----------------------------
# Training results
# -----------------------------
st.divider()
st.subheader("3. Training")

if st.session_state.history:
    rewards = st.session_state.history
    block = max(1, len(rewards) // 100)
    smoothed = []
    for i in range(0, len(rewards), block):
        chunk = rewards[i:i + block]
        smoothed.append(sum(chunk) / len(chunk))

    st.line_chart(smoothed, y_label="Average episode return", x_label="Training progression")
    m1, m2, m3 = st.columns(3)
    m1.metric("Episodes trained", len(rewards))
    m2.metric("Recent avg return", f"{sum(rewards[-100:]) / min(100, len(rewards)):.2f}")
    m3.metric("Best return", f"{max(rewards):.2f}")
else:
    st.info("Press **Train** in the sidebar. Start with the defaults and watch the Q-values propagate backward from the goal.")

# -----------------------------
# Concept map
# -----------------------------
st.divider()
st.subheader("4. Map the code to RL language")
st.markdown("""
| RL concept | In this lab |
|---|---|
| **Agent** | The robot |
| **Environment** | Seven-state line |
| **State (s)** | Agent's current position |
| **Action (a)** | LEFT or RIGHT |
| **Reward (r)** | +10 goal, -10 trap, -0.1 step |
| **Policy (π)** | Rule for choosing LEFT/RIGHT |
| **Q(s,a)** | Expected discounted return from an action |
| **α** | How aggressively new experience changes Q |
| **γ** | How much future reward matters |
| **ε** | Probability of exploring instead of exploiting |
""")

st.caption("Repository: shashank14581/ml_test • Q-learning implemented from scratch — no RL library.")
