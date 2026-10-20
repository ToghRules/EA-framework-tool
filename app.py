"""
EA Framework Decision-Support System
Interactive tool for evaluating and comparing Enterprise Architecture frameworks
using the Weighted Sum Model (WSM).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from data import EA_FRAMEWORKS, DEFAULT_CRITERIA
from evaluation import EvaluationEngine
from database import (
    init_db, save_scenario, load_scenarios, delete_scenario,
    save_eval_result, load_eval_history, delete_eval_result
)
from auth import show_auth_page
from datetime import datetime


init_db()


st.set_page_config(
    page_title="EA Framework Selector",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.main { background-color: #0f1117; }

.stApp { background-color: #0f1117; color: #e8e8e8; }

.metric-card {
    background: linear-gradient(135deg, #1a1d27 0%, #13151f 100%);
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 0.4rem 0;
}

.winner-card {
    background: linear-gradient(135deg, #1a2744 0%, #0f1628 100%);
    border: 1px solid #3b5bdb;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
}

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6c7599;
    border-bottom: 1px solid #2a2d3e;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.stSlider > div > div > div > div {
    background-color: #3b5bdb !important;
}

div[data-testid="stMetric"] {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    padding: 0.8rem 1rem;
}

.framework-badge {
    display: inline-block;
    background: #1e2235;
    border: 1px solid #3b5bdb;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    color: #7b9eff;
    font-family: 'Space Mono', monospace;
}

.stButton > button {
    background: #3b5bdb;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
}

.stButton > button:hover {
    background: #4c6ef5;
    border: none;
}

[data-testid="stSidebar"] {
    background-color: #0d0f18;
    border-right: 1px solid #1e2235;
}

.stCheckbox > label { color: #c8cdd8; }
.stSelectbox > label { color: #c8cdd8; }

.rank-1 { color: #ffd700; font-weight: 700; }
.rank-2 { color: #c0c0c0; font-weight: 600; }
.rank-3 { color: #cd7f32; font-weight: 600; }

.scenario-tag {
    background: #1a2744;
    border: 1px solid #3b5bdb44;
    border-radius: 6px;
    padding: 0.15rem 0.5rem;
    font-size: 0.75rem;
    color: #7b9eff;
    margin-right: 0.3rem;
}
</style>
""", unsafe_allow_html=True)



if "user" not in st.session_state or st.session_state.user is None:
    show_auth_page()
    st.stop()


_user    = st.session_state.user
_user_id = _user["id"]


def init_session():
    if "criteria_weights" not in st.session_state:
        st.session_state.criteria_weights = {c: DEFAULT_CRITERIA[c]["default_weight"] for c in DEFAULT_CRITERIA}
    if "selected_frameworks" not in st.session_state:
        st.session_state.selected_frameworks = list(EA_FRAMEWORKS.keys())
    if "scenarios" not in st.session_state:
        
        db_scenarios = load_scenarios(_user_id)
        st.session_state.scenarios = {
            s["name"]: {"weights": s["weights"], "frameworks": s["frameworks"], "id": s["id"]}
            for s in db_scenarios
        }
    if "custom_criteria" not in st.session_state:
        st.session_state.custom_criteria = {}

init_session()


with st.sidebar:
    st.markdown("# 🏛️ EA Selector")
    st.markdown(
        f"<p style='color:#6c7599; font-size:0.8rem; font-family:Space Mono'>v1.0 · WSM Engine</p>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"<div style='background:#1a1d27; border:1px solid #2a2d3e; border-radius:8px; "
        f"padding:0.6rem 0.8rem; margin-bottom:0.5rem;'>"
        f"<span style='color:#6c7599; font-size:0.7rem; font-family:Space Mono'>LOGGED IN AS</span><br>"
        f"<span style='color:#7b9eff; font-size:0.9rem'>{_user['username']}</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    if st.button("🚪 Logout", use_container_width=True):
        for key in ["user", "scenarios", "criteria_weights", "selected_frameworks", "custom_criteria"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.divider()

    st.markdown("<div class='section-header'>Frameworks</div>", unsafe_allow_html=True)
    selected = []
    for fw in EA_FRAMEWORKS:
        checked = st.checkbox(
            fw,
            value=(fw in st.session_state.selected_frameworks),
            key=f"fw_{fw}"
        )
        if checked:
            selected.append(fw)
    st.session_state.selected_frameworks = selected

    st.divider()
    st.markdown("<div class='section-header'>Criteria Weights</div>", unsafe_allow_html=True)
    st.caption("Drag sliders — scores auto-normalize to 100%")

    total_weight = 0
    for crit, meta in DEFAULT_CRITERIA.items():
        w = st.slider(
            meta["label"],
            min_value=0,
            max_value=10,
            value=st.session_state.criteria_weights.get(crit, meta["default_weight"]),
            key=f"w_{crit}",
            help=meta["description"]
        )
        st.session_state.criteria_weights[crit] = w
        total_weight += w

    weight_sum = sum(st.session_state.criteria_weights.values())
    if weight_sum == 0:
        st.warning("⚠️ All weights are 0")
    else:
        st.progress(min(1.0, weight_sum / 50), text=f"Total weight: {weight_sum}")

    st.divider()
    st.markdown("<div class='section-header'>Scenarios</div>", unsafe_allow_html=True)
    scenario_name = st.text_input("Save current as scenario", placeholder="e.g. Gov-focused")
    if st.button("💾 Save Scenario") and scenario_name:
        ok, msg = save_scenario(
            _user_id, scenario_name,
            list(st.session_state.selected_frameworks),
            dict(st.session_state.criteria_weights)
        )
        if ok:
            
            db_scenarios = load_scenarios(_user_id)
            st.session_state.scenarios = {
                s["name"]: {"weights": s["weights"], "frameworks": s["frameworks"], "id": s["id"]}
                for s in db_scenarios
            }
            st.success(msg)
        else:
            st.error(msg)


st.markdown("# EA Framework Decision-Support System")
st.markdown("<p style='color:#6c7599'>Evaluate and compare Enterprise Architecture frameworks using weighted multi-criteria analysis.</p>", unsafe_allow_html=True)

if len(st.session_state.selected_frameworks) < 2:
    st.warning("Please select at least 2 frameworks from the sidebar to compare.")
    st.stop()


engine = EvaluationEngine(
    frameworks=st.session_state.selected_frameworks,
    criteria=DEFAULT_CRITERIA,
    weights=st.session_state.criteria_weights
)
results = engine.evaluate()


st.divider()
cols = st.columns(len(st.session_state.selected_frameworks))
sorted_results = sorted(results.items(), key=lambda x: x[1]["final_score"], reverse=True)

for i, (fw, data) in enumerate(sorted_results):
    with cols[i]:
        rank_emoji = ["🥇", "🥈", "🥉", "4️⃣"][min(i, 3)]
        st.metric(
            label=f"{rank_emoji} {fw}",
            value=f"{data['final_score']:.1f} / 100",
            delta=f"Rank #{i+1}"
        )

st.divider()


save_col, label_col = st.columns([1, 3])
with save_col:
    session_label = label_col.text_input(
        "Session label (optional)",
        placeholder="e.g. Hospital project — Phase 1",
        label_visibility="collapsed"
    )
with label_col:
    if st.button("💾 Save this evaluation to history"):
        label = session_label.strip() or f"Evaluation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ok, msg = save_eval_result(_user_id, label, results,
                                   st.session_state.criteria_weights,
                                   st.session_state.selected_frameworks)
        st.success(msg) if ok else st.error(msg)

st.divider()


tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Rankings", "🕸️ Radar Chart", "📋 Criteria Breakdown", "🔄 Scenario Analysis", "🕓 History"])

with tab1:
    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        st.markdown("<div class='section-header'>Final WSM Scores</div>", unsafe_allow_html=True)
        fw_names = [x[0] for x in sorted_results]
        fw_scores = [x[1]["final_score"] for x in sorted_results]
        colors = ["#3b5bdb", "#4c6ef5", "#748ffc", "#91a7ff"][:len(fw_names)]

        fig_bar = go.Figure(go.Bar(
            x=fw_names,
            y=fw_scores,
            marker=dict(
                color=colors,
                line=dict(color="#1e2235", width=1)
            ),
            text=[f"{s:.1f}" for s in fw_scores],
            textposition="outside",
            textfont=dict(color="#e8e8e8", family="Space Mono"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="#0f1117",
            plot_bgcolor="#0f1117",
            font=dict(color="#c8cdd8", family="DM Sans"),
            yaxis=dict(range=[0, 110], gridcolor="#1e2235", tickfont=dict(color="#6c7599")),
            xaxis=dict(tickfont=dict(color="#c8cdd8", size=13)),
            margin=dict(t=20, b=20, l=10, r=10),
            height=320,
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.markdown("<div class='section-header'>Score Table</div>", unsafe_allow_html=True)
        table_data = []
        for rank, (fw, data) in enumerate(sorted_results, 1):
            table_data.append({
                "Rank": rank,
                "Framework": fw,
                "Score": f"{data['final_score']:.2f}",
            })
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, hide_index=True, use_container_width=True,
                     column_config={"Score": st.column_config.ProgressColumn("Score", max_value=100, format="%.2f")})

        st.markdown("<div class='section-header' style='margin-top:1rem'>Winner Analysis</div>", unsafe_allow_html=True)
        winner = sorted_results[0][0]
        winner_score = sorted_results[0][1]["final_score"]
        winner_strengths = sorted_results[0][1]["top_criteria"]
        st.markdown(f"""
        <div class='winner-card'>
            <div style='font-family:Space Mono; color:#7b9eff; font-size:0.7rem; letter-spacing:0.1em'>TOP RECOMMENDATION</div>
            <div style='font-size:2rem; font-weight:700; margin:0.3rem 0'>{winner}</div>
            <div style='color:#7b9eff; font-size:1.1rem'>{winner_score:.1f} / 100</div>
            <div style='color:#6c7599; font-size:0.8rem; margin-top:0.5rem'>
                Strengths: {', '.join(winner_strengths[:3])}
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-header'>Multi-Criteria Radar Comparison</div>", unsafe_allow_html=True)

    criteria_labels = [DEFAULT_CRITERIA[c]["label"] for c in DEFAULT_CRITERIA]
    
    palette = [
        ("#3b5bdb", "rgba(59,91,219,0.15)"),
        ("#f03e3e", "rgba(240,62,62,0.15)"),
        ("#2f9e44", "rgba(47,158,68,0.15)"),
        ("#e67700", "rgba(230,119,0,0.15)"),
        ("#ae3ec9", "rgba(174,62,201,0.15)"),
    ]

    fig_radar = go.Figure()
    for i, fw in enumerate(st.session_state.selected_frameworks):
        raw_scores = [results[fw]["raw_scores"][c] for c in DEFAULT_CRITERIA]
        line_color, fill_color = palette[i % len(palette)]
        fig_radar.add_trace(go.Scatterpolar(
            r=raw_scores + [raw_scores[0]],
            theta=criteria_labels + [criteria_labels[0]],
            fill='toself',
            name=fw,
            line=dict(color=line_color, width=2),
            fillcolor=fill_color,
            opacity=0.85,
        ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#13151f",
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color="#6c7599", size=9), gridcolor="#2a2d3e"),
            angularaxis=dict(tickfont=dict(color="#c8cdd8", size=11), gridcolor="#2a2d3e"),
        ),
        paper_bgcolor="#0f1117",
        font=dict(color="#c8cdd8"),
        legend=dict(bgcolor="#1a1d27", bordercolor="#2a2d3e", borderwidth=1),
        height=500,
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    st.markdown("<div class='section-header'>Per-Criterion Weighted Contribution</div>", unsafe_allow_html=True)

    
    criteria_list = list(DEFAULT_CRITERIA.keys())
    palette_crit = px.colors.qualitative.Bold

    fig_stack = go.Figure()
    for ci, crit in enumerate(criteria_list):
        contributions = []
        for fw in st.session_state.selected_frameworks:
            contributions.append(results[fw]["weighted_scores"][crit])
        fig_stack.add_trace(go.Bar(
            name=DEFAULT_CRITERIA[crit]["label"],
            x=st.session_state.selected_frameworks,
            y=contributions,
            marker_color=palette_crit[ci % len(palette_crit)],
        ))

    fig_stack.update_layout(
        barmode="stack",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(color="#c8cdd8", family="DM Sans"),
        legend=dict(bgcolor="#1a1d27", bordercolor="#2a2d3e", font=dict(size=11)),
        yaxis=dict(gridcolor="#1e2235", tickfont=dict(color="#6c7599")),
        xaxis=dict(tickfont=dict(color="#c8cdd8", size=13)),
        height=380,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    
    st.markdown("<div class='section-header'>Raw Scores Matrix</div>", unsafe_allow_html=True)
    matrix = {}
    for fw in st.session_state.selected_frameworks:
        matrix[fw] = {DEFAULT_CRITERIA[c]["label"]: results[fw]["raw_scores"][c] for c in DEFAULT_CRITERIA}
    df_matrix = pd.DataFrame(matrix).T
    st.dataframe(df_matrix.round(1), use_container_width=True)

with tab4:
    st.markdown("<div class='section-header'>What-If Scenario Comparison</div>", unsafe_allow_html=True)

    if not st.session_state.scenarios:
        st.info("💡 Save scenarios using the sidebar to compare them here. Try saving: a governance-focused scenario and a usability-focused one.")
    else:
        scenario_names = list(st.session_state.scenarios.keys())
        selected_scenarios = st.multiselect("Select scenarios to compare", scenario_names, default=scenario_names[:min(3, len(scenario_names))])

        if selected_scenarios:
            scenario_data = []
            for sname in selected_scenarios:
                sc = st.session_state.scenarios[sname]
                sc_engine = EvaluationEngine(
                    frameworks=sc["frameworks"],
                    criteria=DEFAULT_CRITERIA,
                    weights=sc["weights"]
                )
                sc_results = sc_engine.evaluate()
                for fw, data in sc_results.items():
                    scenario_data.append({"Scenario": sname, "Framework": fw, "Score": data["final_score"]})

            df_scenario = pd.DataFrame(scenario_data)
            fig_sc = px.bar(
                df_scenario, x="Framework", y="Score", color="Scenario",
                barmode="group",
                color_discrete_sequence=["#3b5bdb", "#f03e3e", "#2f9e44", "#e67700"],
            )
            fig_sc.update_layout(
                paper_bgcolor="#0f1117",
                plot_bgcolor="#0f1117",
                font=dict(color="#c8cdd8"),
                legend=dict(bgcolor="#1a1d27", bordercolor="#2a2d3e"),
                yaxis=dict(range=[0, 110], gridcolor="#1e2235"),
                height=380,
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig_sc, use_container_width=True)

            st.dataframe(df_scenario.pivot_table(index="Framework", columns="Scenario", values="Score").round(2),
                         use_container_width=True)

with tab5:
    st.markdown("<div class='section-header'>Evaluation History</div>", unsafe_allow_html=True)
    history = load_eval_history(_user_id)

    if not history:
        st.info("💡 No evaluations saved yet. Run an evaluation above and click **Save this evaluation to history**.")
    else:
        st.caption(f"{len(history)} record(s) stored for your account.")

        for record in history:
            with st.expander(f"🗂️ {record['session_label']}  —  {record['created_at']}  |  Winner: **{record['winner']}** ({record['winner_score']:.1f}/100)"):
                col_res, col_w = st.columns([2, 1])

                with col_res:
                    st.markdown("**Scores**")
                    rows = [
                        {"Framework": fw, "Score": f"{d['final_score']:.2f}", "Top Criteria": ", ".join(d["top_criteria"])}
                        for fw, d in sorted(record["results_json"].items(), key=lambda x: -x[1]["final_score"])
                    ]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

                with col_w:
                    st.markdown("**Weights used**")
                    w_df = pd.DataFrame(
                        [{"Criterion": DEFAULT_CRITERIA[k]["label"], "Weight": v}
                         for k, v in record["weights_snapshot"].items()]
                    )
                    st.dataframe(w_df, hide_index=True, use_container_width=True)

                if st.button(f"🗑️ Delete", key=f"del_hist_{record['id']}"):
                    ok, msg = delete_eval_result(_user_id, record["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
st.divider()
st.markdown(
    "<p style='text-align:center; color:#3a3f55; font-family:Space Mono; font-size:0.7rem'>"
    "EA Decision-Support System · WSM Engine · Master's Thesis Prototype"
    "</p>",
    unsafe_allow_html=True
)
