import sys
import os
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root directory to sys.path to enable imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.envs.satellite_env import UnifiedSatelliteEnv
from src.controllers.rule_based import RuleBasedController

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Autonomous Satellite Simulation Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for metric cards and badges
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border: 1px solid #2e364f;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        color: #8b9bb4;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
    }
    .metric-delta {
        font-size: 12px;
        font-weight: 500;
        margin-top: 4px;
    }
    .badge-safe { background-color: #1b4d3e; color: #52c41a; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-standard { background-color: #1890ff22; color: #1890ff; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-payload { background-color: #722ed122; color: #b37feb; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-burn-idle { background-color: #434343; color: #d9d9d9; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-burn-pulse { background-color: #fa8c1622; color: #ffa940; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-burn-major { background-color: #f5222d22; color: #ff4d4f; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.title("🛰️ Mission Controls")
st.sidebar.markdown("Configure small-satellite parameters and execute mission simulation.")

initial_alt = st.sidebar.slider(
    "Initial Altitude (km)",
    min_value=390.0,
    max_value=405.0,
    value=396.5,
    step=0.1,
    help="Target orbit altitude is 400.0 km. Values < 398.0 km trigger station-keeping burns."
)

initial_soc_pct = st.sidebar.slider(
    "Initial Battery SOC (%)",
    min_value=20,
    max_value=100,
    value=75,
    step=1,
    help="Battery state-of-charge percentage at mission initialization."
)

num_steps = st.sidebar.slider(
    "Simulation Duration (Steps / Min)",
    min_value=20,
    max_value=200,
    value=100,
    step=5,
    help="Number of 1-minute simulation control steps (~100 steps = 1.6 orbits)."
)

# ==============================================================================
# SIMULATION EXECUTION & DATA CACHING
# ==============================================================================
@st.cache_data(show_spinner=False)
def simulate_mission(alt, soc_pct, steps):
    env = UnifiedSatelliteEnv()
    controller = RuleBasedController()

    initial_soc = soc_pct / 100.0
    env.reset(initial_altitude=alt, initial_soc=initial_soc, initial_propellant=1.5, start_time=0.0)

    trajectory = []
    for step_idx in range(1, steps + 1):
        time_before = env.time
        alt_before = env.altitude
        soc_before = env.soc
        prop_before = env.propellant

        action_idx = controller.select_action(env)
        power_mode, burn_duration = env.action_table[action_idx]

        next_state, reward, done, telem = env.step(action_idx)

        trajectory.append({
            'step': step_idx,
            'time_s': time_before,
            'time_min': time_before / 60.0,
            'alt_km': env.altitude,
            'alt_before_km': alt_before,
            'soc_pct': env.soc * 100.0,
            'soc_before_pct': soc_before * 100.0,
            'propellant_g': env.propellant * 1000.0,
            'fuel_burned_g': (1.5 - env.propellant) * 1000.0,
            'power_mode': power_mode,
            'burn_duration_s': burn_duration,
            'reward': reward,
            'telemetry': telem,
            'done': done,
            'action_idx': action_idx
        })
        if done:
            break

    return trajectory

trajectory = simulate_mission(initial_alt, initial_soc_pct, num_steps)
max_available_steps = len(trajectory)

st.sidebar.markdown("---")
st.sidebar.subheader("⏯️ Mission Playback Scrubber")
selected_step = st.sidebar.slider(
    "Select Mission Step",
    min_value=1,
    max_value=max_available_steps,
    value=max_available_steps,
    step=1,
    help="Move step-by-step to inspect telemetry and decision logic at any point in the mission."
)

curr_data = trajectory[selected_step - 1]
telem = curr_data['telemetry']

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.title("🛰️ Multi-Objective Autonomous Satellite Operations Dashboard")
st.markdown(
    "Real-time visual monitoring, orbital mechanics tracking, energy balance analysis, "
    "and decision inspection for LEO small-satellite station-keeping."
)
st.markdown("---")

# ==============================================================================
# TOP METRIC CARDS (ROW OF 5 CARDS)
# ==============================================================================
c1, c2, c3, c4, c5 = st.columns(5)

# Card 1: Altitude
curr_alt = curr_data['alt_km']
alt_delta = curr_alt - 400.0
c1.metric(
    label="Orbital Altitude",
    value=f"{curr_alt:.2f} km",
    delta=f"{alt_delta:+.2f} km vs Target (400.0 km)",
    delta_color="normal" if abs(alt_delta) <= 2.0 else "inverse"
)

# Card 2: Battery SOC
curr_soc = curr_data['soc_pct']
soc_delta = telem['delta_soc'] * 100.0
c2.metric(
    label="Battery SOC",
    value=f"{curr_soc:.1f}%",
    delta=f"{soc_delta:+.2f}% / step",
    delta_color="normal" if curr_soc >= 20.0 else "inverse"
)

# Card 3: Propellant Remaining
fuel_rem = curr_data['propellant_g']
fuel_burned = curr_data['fuel_burned_g']
c3.metric(
    label="Propellant Fuel",
    value=f"{fuel_rem:.1f} g",
    delta=f"-{fuel_burned:.1f} g Total Burned",
    delta_color="inverse"
)

# Card 4: Electrical Power Mode
mode_names = {0: "Safe Mode (2W)", 1: "Standard (5W)", 2: "Payload (12W)"}
mode_colors = {0: "#52c41a", 1: "#1890ff", 2: "#b37feb"}
power_mode_val = curr_data['power_mode']
c4.metric(
    label="Electrical Power Mode",
    value=mode_names[power_mode_val],
    delta=f"{telem['P_bus']:.1f} W Total Bus Load"
)

# Card 5: Thruster Status
burn_dur = curr_data['burn_duration_s']
if burn_dur == 0.0:
    thruster_status = "Idle (0s)"
elif burn_dur == 2.0:
    thruster_status = "Short Pulse (2s)"
else:
    thruster_status = "Long Pulse (10s)"

c5.metric(
    label="Thruster Firing State",
    value=thruster_status,
    delta=f"{telem['m_used_g']:.2f} g Burned in Step" if burn_dur > 0 else "0.00 g Burned",
    delta_color="inverse" if burn_dur > 0 else "off"
)

st.markdown("---")

# ==============================================================================
# MAIN VISUAL 1: 2D ORBIT SCHEMATIC & ILLUMINATION VIEW
# ==============================================================================
st.subheader("🌐 2D Orbital Geometry & Lighting Condition")

# Calculate orbital phase and satellite 2D coordinates
orbit_period = 92.5 * 60.0
curr_time = curr_data['time_s']
orbit_phase = (curr_time % orbit_period) / orbit_period
theta = orbit_phase * 2.0 * np.pi

# 2D schematic radii
r_earth = 1.0
r_orbit = 1.6
sat_x = r_orbit * np.cos(theta)
sat_y = r_orbit * np.sin(theta)

fig_orbit = go.Figure()

# 1. Earth circle
earth_theta = np.linspace(0, 2 * np.pi, 200)
fig_orbit.add_trace(go.Scatter(
    x=r_earth * np.cos(earth_theta),
    y=r_earth * np.sin(earth_theta),
    fill="toself",
    fillcolor="rgba(30, 144, 255, 0.4)",
    line=dict(color="#1e90ff", width=2),
    name="Earth (LEO)",
    hoverinfo="text",
    text="Earth (LEO - 6378 km)"
))

# 2. Eclipse Shadow Wedge (First 35% of orbit: phase 0.0 to 0.35)
shadow_angles = np.linspace(0, 0.35 * 2 * np.pi, 100)
shadow_x = np.concatenate([[0], r_orbit * 1.3 * np.cos(shadow_angles), [0]])
shadow_y = np.concatenate([[0], r_orbit * 1.3 * np.sin(shadow_angles), [0]])

fig_orbit.add_trace(go.Scatter(
    x=shadow_x,
    y=shadow_y,
    fill="toself",
    fillcolor="rgba(50, 50, 60, 0.55)",
    line=dict(color="rgba(100, 100, 100, 0.5)", width=1, dash="dash"),
    name="Earth Shadow / Eclipse Zone (35% Orbit)"
))

# 3. Orbit Track Circle
fig_orbit.add_trace(go.Scatter(
    x=r_orbit * np.cos(earth_theta),
    y=r_orbit * np.sin(earth_theta),
    mode="lines",
    line=dict(color="#8b9bb4", width=1.5, dash="dot"),
    name="Orbital Trajectory Track"
))

# 4. Sun Rays Arrows (Right Side)
for y_pos in [-1.5, -0.8, 0.0, 0.8, 1.5]:
    fig_orbit.add_annotation(
        x=1.8, y=y_pos,
        ax=2.4, ay=y_pos,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor="#ffc069"
    )

fig_orbit.add_annotation(
    x=2.5, y=0.0,
    text="<b>INCOMING SUNLIGHT</b> ☀️",
    showarrow=False,
    font=dict(color="#ffc069", size=12),
    textangle=-90
)

# 5. Satellite Position Marker
in_sun = telem['in_sun'] == 1.0
sat_color = "#52c41a" if in_sun else "#ff4d4f"
sat_symbol = "diamond"

fig_orbit.add_trace(go.Scatter(
    x=[sat_x],
    y=[sat_y],
    mode="markers+text",
    marker=dict(size=18, color=sat_color, symbol=sat_symbol, line=dict(color="#ffffff", width=2)),
    text=["<b>SAT</b>"],
    textposition="top center",
    name="Satellite Position"
))

fig_orbit.update_layout(
    xaxis=dict(range=[-2.8, 2.8], showgrid=False, zeroline=False, visible=False),
    yaxis=dict(range=[-2.2, 2.2], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
    margin=dict(l=20, r=20, t=30, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=360,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
)

col_vis1, col_vis2 = st.columns([2, 1])
with col_vis1:
    st.plotly_chart(fig_orbit, use_container_width=True)

with col_vis2:
    st.markdown("#### 💡 Lighting & Illumination Status")
    if in_sun:
        st.success("☀️ **DIRECT SUNLIGHT RECOVERY**\n\nSolar Arrays Generating **8.0 W** maximum power.")
    else:
        st.error("🌙 **EARTH SHADOW / ECLIPSE**\n\nZero Solar Generation (**0.0 W**). Battery discharging.")

    st.markdown(f"**Orbital Phase:** `{orbit_phase * 100.0:.1f}%` of orbit completed")
    st.markdown(f"**Mission Elapsed Time:** `{curr_data['time_min']:.1f} mins` (`{curr_data['time_s']:.0f} s`)")
    st.markdown(f"**Discrete State Index:** `State #{curr_data['telemetry'] and curr_data['action_idx']}` (Bin: s={curr_data['step']})")

st.markdown("---")

# ==============================================================================
# MAIN VISUAL 2: SYNCHRONIZED TELEMETRY GRAPHS
# ==============================================================================
st.subheader("📈 Synchronized Telemetry & Performance Dynamics")

times_min = [d['time_min'] for d in trajectory]
alts = [d['alt_km'] for d in trajectory]
socs = [d['soc_pct'] for d in trajectory]
p_gens = [d['telemetry']['P_gen'] for d in trajectory]
p_buses = [d['telemetry']['P_bus'] for d in trajectory]
burns = [d['burn_duration_s'] for d in trajectory]

# Chart 1: Altitude Tracking
fig_alt = go.Figure()

# Deadband tolerance band (398 to 402 km)
fig_alt.add_hrect(
    y0=398.0, y1=402.0,
    fillcolor="rgba(82, 196, 26, 0.12)",
    line_width=0,
    annotation_text="Station-Keeping Tolerance Band (398 - 402 km)",
    annotation_position="top left"
)

# Target altitude line
fig_alt.add_hline(
    y=400.0,
    line=dict(color="#52c41a", width=2, dash="dash"),
    annotation_text="Target 400.0 km"
)

# Altitude trajectory line
fig_alt.add_trace(go.Scatter(
    x=times_min,
    y=alts,
    mode="lines",
    line=dict(color="#1890ff", width=2.5),
    name="Altitude (km)"
))

# Firing markers (2s and 10s burns)
burn_2s_x = [times_min[i] for i in range(len(burns)) if burns[i] == 2.0]
burn_2s_y = [alts[i] for i in range(len(burns)) if burns[i] == 2.0]
burn_10s_x = [times_min[i] for i in range(len(burns)) if burns[i] == 10.0]
burn_10s_y = [alts[i] for i in range(len(burns)) if burns[i] == 10.0]

if burn_2s_x:
    fig_alt.add_trace(go.Scatter(
        x=burn_2s_x, y=burn_2s_y,
        mode="markers",
        marker=dict(color="#fa8c16", size=10, symbol="triangle-up"),
        name="Short Burn (2.0s)"
    ))

if burn_10s_x:
    fig_alt.add_trace(go.Scatter(
        x=burn_10s_x, y=burn_10s_y,
        mode="markers",
        marker=dict(color="#f5222d", size=12, symbol="star"),
        name="Long Burn (10.0s)"
    ))

# Vertical scrubber line
fig_alt.add_vline(
    x=curr_data['time_min'],
    line=dict(color="#ffffff", width=1.5, dash="dot")
)

fig_alt.update_layout(
    title="Orbital Altitude Tracking & Station-Keeping Burns",
    xaxis_title="Mission Elapsed Time (minutes)",
    yaxis_title="Altitude (km)",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(30,34,45,0.6)",
    height=320,
    margin=dict(l=40, r=40, t=40, b=40)
)

st.plotly_chart(fig_alt, use_container_width=True)

# Chart 2: Power Generation & Battery SOC Dynamics
fig_power = make_subplots(specs=[[{"secondary_y": True}]])

# 20% Critical Battery Threshold Line
fig_power.add_hline(
    y=20.0,
    line=dict(color="#ff4d4f", width=2, dash="dash"),
    annotation_text="20% Critical SOC Safety Limit",
    secondary_y=False
)

# Battery SOC Line
fig_power.add_trace(
    go.Scatter(
        x=times_min, y=socs,
        mode="lines",
        line=dict(color="#13c2c2", width=2.5),
        name="Battery SOC (%)"
    ),
    secondary_y=False
)

# Solar Generation Area
fig_power.add_trace(
    go.Scatter(
        x=times_min, y=p_gens,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(82, 196, 26, 0.25)",
        line=dict(color="#52c41a", width=1.5),
        name="Solar Generation P_gen (W)"
    ),
    secondary_y=True
)

# Bus Demand Line
fig_power.add_trace(
    go.Scatter(
        x=times_min, y=p_buses,
        mode="lines",
        line=dict(color="#faad14", width=2, dash="dot"),
        name="Bus Demand P_bus (W)"
    ),
    secondary_y=True
)

# Vertical scrubber line
fig_power.add_vline(
    x=curr_data['time_min'],
    line=dict(color="#ffffff", width=1.5, dash="dot")
)

fig_power.update_layout(
    title="Electrical Power Balance & Battery State of Charge (SOC)",
    xaxis_title="Mission Elapsed Time (minutes)",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(30,34,45,0.6)",
    height=320,
    margin=dict(l=40, r=40, t=40, b=40)
)
fig_power.update_yaxes(title_text="Battery SOC (%)", range=[0, 105], secondary_y=False)
fig_power.update_yaxes(title_text="Power (Watts)", range=[0, 15], secondary_y=True)

st.plotly_chart(fig_power, use_container_width=True)

st.markdown("---")

# ==============================================================================
# RULE DECISION INSPECTION ("WHY DID THE SATELLITE DO THAT?")
# ==============================================================================
st.subheader("🔍 Decision Inspector: Rule Logic & Multi-Objective Reward Analysis")
st.markdown(f"Inspecting deterministic heuristic controller logic at **Step #{curr_data['step']}** (Time: `{curr_data['time_min']:.1f} mins`):")

col_dec1, col_dec2, col_dec3 = st.columns(3)

# 1. Power Logic Explanation
with col_dec1:
    st.markdown("### ⚡ Power Mode Decision")
    soc_val = curr_data['soc_before_pct']
    if soc_val < 30.0:
        power_reason = f"**SOC is {soc_val:.1f}% (< 30.0%)** → Forced **Safe Mode (2.0 W)** to prioritize battery recovery."
        st.error(power_reason)
    elif in_sun:
        power_reason = f"**SOC is {soc_val:.1f}% (≥ 30.0%)** and spacecraft is in **Sunlight** → Activated **High Payload Mode (12.0 W)**."
        st.success(power_reason)
    else:
        power_reason = f"**SOC is {soc_val:.1f}% (≥ 30.0%)** but spacecraft is in **Eclipse** → Maintained **Standard Mode (5.0 W)** to conserve energy."
        st.info(power_reason)

# 2. Propulsion Logic Explanation
with col_dec2:
    st.markdown("### 🚀 Propulsion Decision")
    alt_val = curr_data['alt_before_km']
    if soc_val <= 25.0:
        prop_reason = f"**SOC is {soc_val:.1f}% (≤ 25.0%)** → **Safety Interlock Engaged**: Thruster burn inhibited (0.0 s)."
        st.error(prop_reason)
    elif alt_val < 392.0:
        prop_reason = f"**Altitude is {alt_val:.2f} km (< 392.0 km)** → Triggered **Major Recovery Burn (10.0 s)**."
        st.warning(prop_reason)
    elif 392.0 <= alt_val < 398.0:
        prop_reason = f"**Altitude is {alt_val:.2f} km (< 398.0 km deadband)** → Triggered **Proportional Corrective Burn (2.0 s)**."
        st.warning(prop_reason)
    else:
        prop_reason = f"**Altitude is {alt_val:.2f} km (≥ 398.0 km deadband)** → **Idle (0.0 s)**. Station-keeping satisfied."
        st.success(prop_reason)

# 3. Multi-Objective Cost Breakdown
with col_dec3:
    st.markdown("### 🎯 Multi-Objective Cost Breakdown")
    m_used_kg = telem['m_used_g'] / 1000.0
    norm_orbit_err = abs(curr_alt - 400.0) / 2.0
    norm_fuel_used = m_used_kg / (0.00045 * 10.0)
    norm_power_bus = telem['P_bus'] / 12.67
    batt_pen = telem['batt_penalty']

    c_orbit = 0.4 * norm_orbit_err
    c_fuel = 0.3 * norm_fuel_used
    c_power = 0.1 * norm_power_bus
    c_batt = 0.2 * batt_pen
    total_cost = c_orbit + c_fuel + c_power + c_batt

    st.markdown(f"**Step Total Cost:** `{total_cost:.4f}` (Reward: `{curr_data['reward']:.4f}`)")
    st.markdown(f"- Orbit Error Penalty (40%): `{c_orbit:.4f}`")
    st.markdown(f"- Fuel Mass Penalty (30%): `{c_fuel:.4f}`")
    st.markdown(f"- Bus Power Penalty (10%): `{c_power:.4f}`")
    st.markdown(f"- Battery Risk Penalty (20%): `{c_batt:.4f}`")
