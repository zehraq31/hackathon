#!/usr/bin/env python3
"""FinOps Intelligence & Mainframe Modernisation Executive Dashboard
Innovation Forum × R1X Hackathon — Challenge 03: Beyond the Mainframe

Interactive Streamlit Application powered by DuckDB OLAP engine for high-speed
parquet analytics, executive insight discovery, and FinOps scenario modelling.
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinOps Intelligence — Beyond the Mainframe",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS / STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main container background */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 34, 56, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.1rem 1.15rem;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
        min-height: 135px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.35);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--card-accent, linear-gradient(90deg, #6366f1, #8b5cf6));
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        line-height: 1.15;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .metric-delta {
        font-size: 0.78rem;
        margin-top: 0.45rem;
        font-weight: 500;
        line-height: 1.35;
    }
    .delta-badge-red {
        color: #f87171;
        background: rgba(239, 68, 68, 0.12);
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        display: inline-block;
    }
    .delta-badge-amber {
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.12);
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        display: inline-block;
    }
    .delta-badge-green {
        color: #34d399;
        background: rgba(16, 185, 129, 0.12);
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        display: inline-block;
    }
    .delta-badge-blue {
        color: #60a5fa;
        background: rgba(59, 130, 246, 0.12);
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        display: inline-block;
    }

    /* Section Highlights */
    .callout-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #6366f1;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }

    .pill {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .pill-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .pill-purple { background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
    .pill-green { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .pill-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .pill-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

    /* Clean Streamlit tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 0.86rem;
        padding: 0.55rem 0.85rem;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(99, 102, 241, 0.15) !important;
        border-bottom: 2px solid #6366f1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER (DUCKDB + CACHING)
# ─────────────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = REPO_ROOT / "sample" / "data" / "c03-beyond-the-mainframe" / "gold"

@st.cache_resource(show_spinner="Connecting to DuckDB OLAP Engine...")
def init_duckdb():
    con = duckdb.connect()
    cost_file = GOLD_DIR / "workload_cost_daily.parquet"
    chargeback_file = GOLD_DIR / "chargeback_allocation.parquet"
    carbon_file = GOLD_DIR / "carbon_by_workload.parquet"

    if not cost_file.exists():
        st.error(
            f"Parquet dataset not found at `{cost_file}`. Please build the dataset via `python build/build.py build --challenge c03-beyond-the-mainframe --version v1 --out sample/data/c03-beyond-the-mainframe`."
        )
        st.stop()

    con.execute(f"CREATE OR REPLACE VIEW cost AS SELECT * FROM read_parquet('{cost_file}');")
    if chargeback_file.exists():
        con.execute(f"CREATE OR REPLACE VIEW chargeback AS SELECT * FROM read_parquet('{chargeback_file}');")
    if carbon_file.exists():
        con.execute(f"CREATE OR REPLACE VIEW carbon AS SELECT * FROM read_parquet('{carbon_file}');")

    return con

con = init_duckdb()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONTROLS & FILTERS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Innovation Forum × R1X")
    st.markdown("**Challenge 03 — Beyond the Mainframe**")
    st.markdown("<span class='pill pill-purple'>Release: v2026-10-26 (Pinned)</span> <span class='pill pill-blue'>DuckDB Engine</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Global Filters")

    # Platform Filter
    platforms = con.execute("SELECT DISTINCT platform FROM cost ORDER BY platform").df()["platform"].tolist()
    selected_platforms = st.multiselect("Platforms", options=platforms, default=platforms)

    # Environment Filter
    environments = con.execute("SELECT DISTINCT environment FROM cost ORDER BY environment").df()["environment"].tolist()
    selected_envs = st.multiselect("Environments", options=environments, default=environments)

    # Business Units Filter
    bus = con.execute("SELECT DISTINCT business_unit FROM cost ORDER BY business_unit").df()["business_unit"].tolist()
    selected_bus = st.multiselect("Business Units (BU)", options=bus, default=[])

    # Date Range
    date_bounds = con.execute("SELECT min(usage_date) as min_d, max(usage_date) as max_d FROM cost").df().iloc[0]
    min_date = date_bounds["min_d"].date() if hasattr(date_bounds["min_d"], "date") else pd.to_datetime(date_bounds["min_d"]).date()
    max_date = date_bounds["max_d"].date() if hasattr(date_bounds["max_d"], "date") else pd.to_datetime(date_bounds["max_d"]).date()

    selected_date_range = st.date_input(
        "Usage Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("---")
    presentation_mode = st.toggle("🎤 Executive Presentation Mode", value=True, help="Toggle pitch-deck bullets and key takeaways")

    st.markdown("---")
    st.caption("Data Contract: Seeded Synthetic FinOps Estate (CC0-1.0). Reconciles exactly to chargeback roll-up.")

# Prepare SQL filter clause
where_conditions = []
if selected_platforms:
    plat_str = "','".join(selected_platforms)
    where_conditions.append(f"cost.platform IN ('{plat_str}')")
if selected_envs:
    env_str = "','".join(selected_envs)
    where_conditions.append(f"cost.environment IN ('{env_str}')")
if selected_bus:
    bu_str = "','".join(selected_bus)
    where_conditions.append(f"cost.business_unit IN ('{bu_str}')")

if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    where_conditions.append(f"cost.usage_date >= '{start_d}' AND cost.usage_date <= '{end_d}'")

where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

# ─────────────────────────────────────────────────────────────────────────────
# TOP KPI BANNER (EXECUTIVE OVERVIEW)
# ─────────────────────────────────────────────────────────────────────────────
estate_kpis = con.execute(f"""
    SELECT
        round(sum(cost.cost_gbp), 2) AS total_spend,
        count(DISTINCT cost.workload_id) AS total_workloads,
        round(sum(CASE WHEN cost.platform = 'mainframe' THEN cost.cost_gbp ELSE 0 END), 2) AS mainframe_spend,
        round(100.0 * sum(CASE WHEN cost.platform = 'mainframe' THEN cost.cost_gbp ELSE 0 END) / NULLIF(sum(cost.cost_gbp), 0), 1) AS mainframe_pct,
        round(sum(CASE WHEN cost.business_unit = 'UNALLOCATED' THEN cost.cost_gbp ELSE 0 END), 2) AS unallocated_spend,
        round(100.0 * sum(CASE WHEN cost.business_unit = 'UNALLOCATED' THEN cost.cost_gbp ELSE 0 END) / NULLIF(sum(cost.cost_gbp), 0), 1) AS unallocated_pct,
        round(sum(CASE WHEN cost.platform = 'mainframe' THEN cost.cost_gbp ELSE 0 END) / NULLIF(sum(CASE WHEN cost.platform = 'mainframe' THEN cost.vcpu_hours ELSE 0 END), 0), 4) AS mainframe_prov_unit_cost,
        round(sum(CASE WHEN cost.platform = 'cloud' THEN cost.cost_gbp ELSE 0 END) / NULLIF(sum(CASE WHEN cost.platform = 'cloud' THEN cost.vcpu_hours ELSE 0 END), 0), 4) AS cloud_prov_unit_cost,
        round(avg(CASE WHEN cost.platform = 'mainframe' THEN cost.utilisation_pct ELSE NULL END), 1) AS mf_mean_util,
        round(avg(CASE WHEN cost.platform = 'cloud' THEN cost.utilisation_pct ELSE NULL END), 1) AS cloud_mean_util,
        round(sum(CASE WHEN cost.environment != 'production' THEN cost.cost_gbp ELSE 0 END), 2) AS nonprod_spend,
        round(100.0 * sum(CASE WHEN cost.environment != 'production' THEN cost.cost_gbp ELSE 0 END) / NULLIF(sum(cost.cost_gbp), 0), 1) AS nonprod_pct
    FROM cost
    {where_clause}
""").df().iloc[0]

# Calculate effective used-hour cost
mf_prov = float(estate_kpis["mainframe_prov_unit_cost"]) if estate_kpis["mainframe_prov_unit_cost"] else 0.4932
cloud_prov = float(estate_kpis["cloud_prov_unit_cost"]) if estate_kpis["cloud_prov_unit_cost"] else 0.0682
mf_util = (float(estate_kpis["mf_mean_util"]) / 100.0) if estate_kpis["mf_mean_util"] else 0.695
cloud_util = (float(estate_kpis["cloud_mean_util"]) / 100.0) if estate_kpis["cloud_mean_util"] else 0.212

mf_used_cost = (mf_prov / mf_util) if mf_util > 0 else 0.71
cloud_used_cost = (cloud_prov / cloud_util) if cloud_util > 0 else 0.32
effective_gap_ratio = (mf_used_cost / cloud_used_cost) if cloud_used_cost > 0 else 2.2
raw_prov_ratio = (mf_prov / cloud_prov) if cloud_prov > 0 else 7.2

# Compute Idle Waste (< 5% utilisation)
waste_kpi = con.execute(f"""
    SELECT
        count(DISTINCT workload_id) AS idle_wl_count,
        coalesce(round(sum(annual_cost), 2), 0.0) AS wasted_spend
    FROM (
        SELECT cost.workload_id, sum(cost.cost_gbp) AS annual_cost
        FROM cost
        {where_clause}
        GROUP BY cost.workload_id
        HAVING avg(cost.utilisation_pct) < 5.0
    ) sub
""").df().iloc[0]

st.markdown("<h1 style='margin-bottom:0px;'>FinOps Intelligence & Mainframe Modernisation</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:1.02rem; margin-top:2px;'>Executive Evidence & Modernisation Roadmap · Challenge 03: Beyond the Mainframe</p>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #3b82f6, #60a5fa);">
        <div class="metric-label">Total Estate Spend</div>
        <div class="metric-value">£{estate_kpis['total_spend']/1e6:.1f}M</div>
        <div class="metric-delta"><span class="delta-badge-blue">{int(estate_kpis['total_workloads']):,} Workloads</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #8b5cf6, #c084fc);">
        <div class="metric-label">Mainframe Core</div>
        <div class="metric-value">£{estate_kpis['mainframe_spend']/1e6:.2f}M</div>
        <div class="metric-delta"><span class="delta-badge-purple" style="color:#c084fc; background:rgba(192,132,252,0.12); padding:0.15rem 0.45rem; border-radius:9999px;">{estate_kpis['mainframe_pct']}% of spend · Live Core</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #f59e0b, #fbbf24);">
        <div class="metric-label">Untagged Spend</div>
        <div class="metric-value">£{estate_kpis['unallocated_spend']/1e6:.2f}M</div>
        <div class="metric-delta"><span class="delta-badge-amber">{estate_kpis['unallocated_pct']}% of total (#1 BU)</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #ef4444, #f87171);">
        <div class="metric-label">Idle Waste (&lt;5% Util)</div>
        <div class="metric-value">£{waste_kpi['wasted_spend']/1e6:.2f}M</div>
        <div class="metric-delta"><span class="delta-badge-red">{int(waste_kpi['idle_wl_count']):,} Zombie Workloads</span></div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #ec4899, #f472b6);">
        <div class="metric-label">Non-Prod Sprawl</div>
        <div class="metric-value">£{estate_kpis['nonprod_spend']/1e6:.2f}M</div>
        <div class="metric-delta"><span class="delta-badge-amber">{estate_kpis['nonprod_pct']}% (Dev, Staging & Test)</span></div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-card" style="--card-accent: linear-gradient(90deg, #10b981, #34d399);">
        <div class="metric-label">Effective Compute Gap</div>
        <div class="metric-value">{effective_gap_ratio:.1f}x</div>
        <div class="metric-delta"><span class="delta-badge-green">Used: £{mf_used_cost:.2f} vs £{cloud_used_cost:.2f}/hr</span></div>
    </div>
    """, unsafe_allow_html=True)

# Problem 3 visible note on vCPU conversion & MIPS
st.markdown(
    """
    <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 0.55rem 0.95rem; margin: 0.75rem 0 1rem 0; font-size: 0.82rem; color: #cbd5e1; line-height: 1.45;">
        <strong>ℹ️ Compute Metric &amp; MIPS Conversion Note:</strong> Mainframe compute is measured in MIPS-equivalent vCPU-hours (1 MIPS-equivalent capacity unit normalised to 1 standard vCPU-hour per the challenge data contract). Raw provisioned rate is 7.2x (£0.49 vs £0.068), but adjusting for real-world utilisation (70% on mainframe vs 21% in cloud) reveals an effective cost gap of ~2.2x (£0.71 vs £0.32 per used hour).
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# TABS NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Executive Briefing & Live Mainframe Core",
    "⚖️ Finding 1: Unit Economics & The Utilisation Gap",
    "🏷️ Finding 2: Untagged Spend (UNALLOCATED)",
    "🧟 Finding 3: Idle Waste Hunter",
    "🧪 Finding 4: Non-Prod Sprawl (£7.6M)",
    "🎛️ What-If ROI Simulator",
    "🌱 Method Demonstration: Carbon Footprint",
    "💻 Live DuckDB SQL Console",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: EXECUTIVE BRIEFING (PITCH DECK)
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    if presentation_mode:
        st.markdown(
            """
            <div class="callout-box">
                <h4 style="margin:0 0 6px 0; color:#818cf8;">🎙️ Pitch Deck Narrative — 3 Key Facts Every Sponsor Leader Must Know</h4>
                <ul style="margin:0; padding-left: 20px; color:#cbd5e1; font-size:0.92rem; line-height:1.65;">
                    <li><strong>Legacy is a live, high-stakes cost base:</strong> Mainframe accounts for <strong>£13.15M (85.8%)</strong> of total enterprise spend, running tier-1 core banking (CICS, IMS, Db2, Sysplex) with consistent ~86% monthly share and quarter-end batch surges.</li>
                    <li><strong>The gap is smaller than it looks (2.2x, not 7.2x):</strong> Mainframe costs 7.2x more per provisioned vCPU-hour (£0.49 vs £0.068), but runs at <strong>70% utilisation</strong> vs only <strong>21% in cloud</strong>. Adjusting for usage narrows the gap to <strong>~2.2x (£0.71 vs £0.32 per used hour)</strong>. Cloud is still roughly 2x cheaper, but naive lift-and-shift will replicate cloud idle and erode the savings.</li>
                    <li><strong>£1.16M untagged & £1.43M pure idle waste:</strong> <code>UNALLOCATED</code> is the #1 cost centre in the enterprise (7.6% of spend), while 132 near-idle workloads (&lt;5% util) run 24/7/365 with zero business justification.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 12-Month Live Mainframe Spend Trend Chart (Problem 4 requirement)
    st.subheader("Mainframe 12-Month Live Trend & Share (High-Stakes Core Estate)")
    monthly_trend = con.execute("""
        SELECT
            strftime(usage_date, '%Y-%m') AS month,
            round(sum(CASE WHEN platform = 'mainframe' THEN cost_gbp ELSE 0 END), 2) AS mainframe_spend,
            round(sum(CASE WHEN platform = 'distributed' THEN cost_gbp ELSE 0 END), 2) AS distributed_spend,
            round(sum(CASE WHEN platform = 'cloud' THEN cost_gbp ELSE 0 END), 2) AS cloud_spend,
            round(sum(cost_gbp), 2) AS total_spend,
            round(100.0 * sum(CASE WHEN platform = 'mainframe' THEN cost_gbp ELSE 0 END) / sum(cost_gbp), 1) AS mainframe_share_pct
        FROM cost
        GROUP BY 1
        ORDER BY 1
    """).df()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        name="Mainframe (£)",
        x=monthly_trend["month"],
        y=monthly_trend["mainframe_spend"],
        marker_color="#8b5cf6",
        yaxis="y"
    ))
    fig_trend.add_trace(go.Bar(
        name="Distributed (£)",
        x=monthly_trend["month"],
        y=monthly_trend["distributed_spend"],
        marker_color="#06b6d4",
        yaxis="y"
    ))
    fig_trend.add_trace(go.Bar(
        name="Cloud (£)",
        x=monthly_trend["month"],
        y=monthly_trend["cloud_spend"],
        marker_color="#10b981",
        yaxis="y"
    ))
    fig_trend.add_trace(go.Scatter(
        name="Mainframe Share (%)",
        x=monthly_trend["month"],
        y=monthly_trend["mainframe_share_pct"],
        mode="lines+markers",
        marker=dict(color="#f59e0b", size=7),
        line=dict(color="#f59e0b", width=2.5, dash="dot"),
        yaxis="y2"
    ))
    fig_trend.update_layout(
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Monthly Spend (GBP)"),
        yaxis2=dict(title="Mainframe Share (%)", overlaying="y", side="right", range=[75, 100]),
        height=330
    )
    st.plotly_chart(fig_trend, width="stretch")

    col_deck_l, col_deck_r = st.columns([1.2, 1])

    with col_deck_l:
        st.subheader("Platform Spend vs. Volume Share")
        plat_summary = con.execute(f"""
            SELECT
                platform,
                round(sum(cost_gbp), 2) AS cost_gbp,
                round(100.0 * sum(cost_gbp) / sum(sum(cost_gbp)) OVER (), 1) AS spend_share_pct,
                round(sum(vcpu_hours), 0) AS vcpu_hours,
                round(100.0 * sum(vcpu_hours) / sum(sum(vcpu_hours)) OVER (), 1) AS compute_share_pct,
                round(avg(utilisation_pct), 1) AS mean_util_pct,
                round(sum(cost_gbp) / sum(vcpu_hours), 4) AS unit_cost
            FROM cost
            {where_clause}
            GROUP BY 1
            ORDER BY cost_gbp DESC
        """).df()

        fig_plat = go.Figure()
        fig_plat.add_trace(go.Bar(
            name="Spend Share (%)",
            x=plat_summary["platform"].str.capitalize(),
            y=plat_summary["spend_share_pct"],
            marker_color="#6366f1",
            text=[f"£{c/1e6:.2f}M ({p}%)" for c, p in zip(plat_summary["cost_gbp"], plat_summary["spend_share_pct"])],
            textposition="auto"
        ))
        fig_plat.add_trace(go.Bar(
            name="Compute Volume Share (%)",
            x=plat_summary["platform"].str.capitalize(),
            y=plat_summary["compute_share_pct"],
            marker_color="#06b6d4",
            text=[f"{v/1e6:.1f}M hrs ({p}%)" for v, p in zip(plat_summary["vcpu_hours"], plat_summary["compute_share_pct"])],
            textposition="auto"
        ))
        fig_plat.update_layout(
            barmode="group",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="% of Estate Total",
            height=320
        )
        st.plotly_chart(fig_plat, width="stretch")

    with col_deck_r:
        st.subheader("Where Does the Money Go? (By BU)")
        bu_top = con.execute(f"""
            SELECT
                business_unit,
                round(sum(cost_gbp), 2) AS cost_gbp
            FROM cost
            {where_clause}
            GROUP BY 1
            ORDER BY cost_gbp DESC
            LIMIT 10
        """).df()

        colors = ["#f59e0b" if bu == "UNALLOCATED" else "#3b82f6" for bu in bu_top["business_unit"]]
        fig_bu = go.Figure(go.Bar(
            x=bu_top["cost_gbp"],
            y=bu_top["business_unit"],
            orientation="h",
            marker_color=colors,
            text=[f"£{v/1e3:,.0f}k" for v in bu_top["cost_gbp"]],
            textposition="outside"
        ))
        fig_bu.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=40, t=30, b=20),
            yaxis=dict(autorange="reversed"),
            xaxis_title="Annual Spend (GBP)",
            height=320
        )
        st.plotly_chart(fig_bu, width="stretch")

    st.markdown("---")
    st.subheader("Actionable Modernisation Roadmap (FinOps 3-Phase Plan)")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #10b981;">
            <span class="pill pill-green">Phase 1: 0–30 Days (Quick Wins)</span>
            <h4 style="margin: 0.6rem 0 0.3rem 0; color:#ffffff;">Stop the Bleeding</h4>
            <p style="color:#94a3b8; font-size:0.88rem; line-height:1.5;">
                • Decommission top 20 zero-work mainframe workloads (<2.7% util): <strong>Save £1.18M</strong><br>
                • Enforce tagging gate on CI/CD pipelines to remediate 61 UNALLOCATED services.<br>
                • <strong>Target Recovery:</strong> £1.18M annual savings, 100% allocation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #6366f1;">
            <span class="pill pill-purple">Phase 2: 30–90 Days (Governance)</span>
            <h4 style="margin: 0.6rem 0 0.3rem 0; color:#ffffff;">Non-Prod Optimisation</h4>
            <p style="color:#94a3b8; font-size:0.88rem; line-height:1.5;">
                • Non-prod consumes 50% (£7.62M). Auto-park dev/test cloud workloads off-hours (nights & weekends).<br>
                • Rationalise redundant mainframe dev/test LPARs (£6.65M spend).<br>
                • <strong>Target Recovery:</strong> £1.35M annual savings.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #f59e0b;">
            <span class="pill pill-amber">Phase 3: 90–365 Days (Architecture)</span>
            <h4 style="margin: 0.6rem 0 0.3rem 0; color:#ffffff;">Rightsized Modernisation</h4>
            <p style="color:#94a3b8; font-size:0.88rem; line-height:1.5;">
                • Migrate batch workloads to cloud with auto-scaling to avoid inheriting 79% cloud idle.<br>
                • Capture the real 2.2x compute advantage via containerisation and autoscaling.<br>
                • <strong>Target Recovery:</strong> £2.5M+ net recurring savings.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: FINDING 1 — UNIT ECONOMICS & THE UTILISATION GAP (Problem 2 & 3 fix)
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Finding 1: The Gap is Smaller Than It Looks (Unit Economics & Utilisation)")
    st.markdown(
        """
        Comparing total spend by platform tells you where the money is; cost per compute unit tells you whether it is well spent.
        However, looking only at provisioned hourly rates without adjusting for real-world utilisation leads to flawed conclusions.
        """
    )

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #8b5cf6;">
            <div class="metric-label">Mainframe Economics</div>
            <div class="metric-value">£0.71 <span style="font-size:0.85rem; font-weight:normal; color:#94a3b8;">/ used vCPU-hr</span></div>
            <div class="metric-delta">
                Provisioned: <strong>£0.4932 / hr</strong><br>
                Mean Utilisation: <strong>69.5%</strong> (high, flat, predictable)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #06b6d4;">
            <div class="metric-label">Distributed Economics</div>
            <div class="metric-value">£0.25 <span style="font-size:0.85rem; font-weight:normal; color:#94a3b8;">/ used vCPU-hr</span></div>
            <div class="metric-delta">
                Provisioned: <strong>£0.0907 / hr</strong><br>
                Mean Utilisation: <strong>36.3%</strong> (on-prem VMs & servers)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown("""
        <div class="metric-card" style="--card-accent: #10b981;">
            <div class="metric-label">Cloud Economics</div>
            <div class="metric-value">£0.32 <span style="font-size:0.85rem; font-weight:normal; color:#94a3b8;">/ used vCPU-hr</span></div>
            <div class="metric-delta">
                Provisioned: <strong>£0.0682 / hr</strong><br>
                Mean Utilisation: <strong>21.2%</strong> (78.8% idle waste!)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_pdx_l, col_pdx_r = st.columns([1.1, 1])

    with col_pdx_l:
        st.markdown("##### Unit Cost vs. Utilisation by Service")
        service_economics = con.execute("""
            SELECT
                service,
                platform,
                round(sum(cost_gbp), 2) AS cost_gbp,
                round(sum(cost_gbp) / sum(vcpu_hours), 4) AS cost_per_vcpu_hr,
                round(avg(utilisation_pct), 1) AS mean_utilisation_pct,
                count(DISTINCT workload_id) AS workload_count
            FROM cost
            GROUP BY 1, 2
        """).df()

        fig_scatter = px.scatter(
            service_economics,
            x="mean_utilisation_pct",
            y="cost_per_vcpu_hr",
            color="platform",
            size="cost_gbp",
            hover_name="service",
            hover_data={"workload_count": True, "cost_gbp": ":£,.0f", "cost_per_vcpu_hr": ":£.4f"},
            labels={"mean_utilisation_pct": "Mean Utilisation (%)", "cost_per_vcpu_hr": "Provisioned Rate (£/vCPU-hr)"},
            color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
            template="plotly_dark",
            height=370
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_scatter, width="stretch")

    with col_pdx_r:
        st.markdown("""
        <div class="callout-box" style="border-left-color: #3b82f6; margin-top:0.4rem;">
            <h4 style="color:#60a5fa; margin:0 0 6px 0;">⚖️ The Gap is Smaller Than It Looks (2.2x, Not 7.2x)</h4>
            <p style="color:#cbd5e1; font-size:0.9rem; line-height:1.65; margin:0;">
                On paper, mainframe looks <strong>7.2x more expensive</strong> per provisioned vCPU-hour (£0.493 vs £0.068).<br><br>
                However, adjust for real-world usage:
                <br>• <strong>Mainframe:</strong> £0.4932 ÷ 0.695 = <strong>£0.71 per used hour</strong>
                <br>• <strong>Cloud:</strong> £0.0682 ÷ 0.212 = <strong>£0.32 per used hour</strong><br><br>
                <strong>The True Takeaway:</strong> Cloud is still roughly <strong>2x cheaper per used hour</strong> (£0.32 vs £0.71). Migrating to cloud is definitely not a mistake—the cost advantage is real.
                However, the gap is much narrower than raw hourly rates suggest: a naive lift-and-shift that copies over-provisioned capacity into cloud inherits cloud's 79% idle rate, capturing only a fraction of the savings.
                To capture the full economic potential, migrations must rightsize compute and use auto-scaling.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: FINDING 2 — UNTAGGED SPEND (UNALLOCATED)
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Finding 2: The Spend Nobody Owns (Untagged & Unallocated)")
    st.markdown(
        """
        The first question in any chargeback exercise is not *how much*, it is *whose*.
        Untagged workloads represent real cash with no designated owner, creating zero incentive to optimize.
        In this estate, **`UNALLOCATED` is the #1 cost centre at £1,159,419.25 (7.6% of all spend)** across 61 workloads.
        """
    )

    col_u1, col_u2 = st.columns([1.1, 1])

    with col_u1:
        st.markdown("##### Untagged Spend by Service & Platform")
        unallocated_services = con.execute("""
            SELECT
                platform,
                service,
                count(DISTINCT workload_id) AS workloads,
                round(sum(cost_gbp), 2) AS cost_gbp,
                round(avg(utilisation_pct), 1) AS avg_utilisation_pct
            FROM cost
            WHERE business_unit = 'UNALLOCATED'
            GROUP BY 1, 2
            ORDER BY cost_gbp DESC
        """).df()

        fig_unalloc = px.bar(
            unallocated_services.head(10),
            x="cost_gbp",
            y="service",
            color="platform",
            orientation="h",
            labels={"cost_gbp": "Untagged Cost (£)", "service": "Service"},
            color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
            text="cost_gbp",
            template="plotly_dark"
        )
        fig_unalloc.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
        fig_unalloc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=40, t=10, b=10),
            yaxis=dict(autorange="reversed"),
            height=370
        )
        st.plotly_chart(fig_unalloc, width="stretch")

    with col_u2:
        st.markdown("##### Platform Distribution of Untagged Spend")
        unalloc_plat = con.execute("""
            SELECT
                platform,
                count(DISTINCT workload_id) AS workloads,
                round(sum(cost_gbp), 2) AS cost_gbp,
                round(100.0 * sum(cost_gbp) / (SELECT sum(cost_gbp) FROM cost WHERE business_unit = 'UNALLOCATED'), 1) AS pct
            FROM cost
            WHERE business_unit = 'UNALLOCATED'
            GROUP BY 1
            ORDER BY cost_gbp DESC
        """).df()

        fig_pie = px.pie(
            unalloc_plat,
            names="platform",
            values="cost_gbp",
            color="platform",
            hole=0.45,
            color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
            template="plotly_dark"
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=310
        )
        st.plotly_chart(fig_pie, width="stretch")
        st.markdown(
            "💡 **Finding:** **85.3% (£989k)** of untagged spend resides on the **Mainframe**, led by *Sysplex Coupling (£331k)* and *VSAM Storage (£156k)*. Untagged cloud workloads account for only £39k."
        )

    st.markdown("##### Detailed Register of Untagged Workloads")
    unalloc_workloads = con.execute("""
        SELECT
            workload_id,
            platform,
            service,
            environment,
            region,
            round(sum(cost_gbp), 2) AS annual_cost_gbp,
            round(avg(utilisation_pct), 1) AS mean_util_pct
        FROM cost
        WHERE business_unit = 'UNALLOCATED'
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY annual_cost_gbp DESC
    """).df()

    st.dataframe(
        unalloc_workloads,
        column_config={
            "annual_cost_gbp": st.column_config.NumberColumn("Annual Cost", format="£%.2f"),
            "mean_util_pct": st.column_config.ProgressColumn("Mean Utilisation", min_value=0, max_value=100, format="%.1f%%"),
        },
        width="stretch",
        height=280
    )

    csv_unalloc = unalloc_workloads.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export Untagged Workloads (CSV)", data=csv_unalloc, file_name="unallocated_workloads.csv", mime="text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: FINDING 3 — IDLE WASTE HUNTER
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Finding 3: Zombie & Near-Idle Workload Hunter")
    st.markdown(
        """
        Near-idle workloads cost money and do almost nothing. They are trivial to find once you look,
        and easy to miss entirely if you only ever look at aggregate totals.
        """
    )

    util_threshold = st.slider("Select Utilisation Floor Threshold (%):", min_value=1.0, max_value=15.0, value=5.0, step=0.5)

    idle_summary = con.execute(f"""
        SELECT
            platform,
            count(DISTINCT workload_id) AS idle_workloads,
            round(sum(cost_gbp), 2) AS wasted_cost_gbp,
            round(avg(utilisation_pct), 2) AS mean_utilisation_pct
        FROM (
            SELECT workload_id, platform, sum(cost_gbp) AS cost_gbp, avg(utilisation_pct) AS utilisation_pct
            FROM cost
            GROUP BY 1, 2
            HAVING avg(utilisation_pct) < {util_threshold}
        )
        GROUP BY 1
        ORDER BY wasted_cost_gbp DESC
    """).df()

    col_w_tbl, col_w_chart = st.columns([1, 1.2])

    with col_w_tbl:
        st.markdown(f"##### Waste Breakdown at &lt;{util_threshold}% Utilisation")
        st.dataframe(
            idle_summary,
            column_config={
                "wasted_cost_gbp": st.column_config.NumberColumn("Wasted Cost", format="£%.2f"),
                "mean_utilisation_pct": st.column_config.NumberColumn("Avg Utilisation", format="%.2f%%"),
            },
            width="stretch",
            hide_index=True
        )
        total_wasted = idle_summary["wasted_cost_gbp"].sum() if not idle_summary.empty else 0
        st.markdown(f"🔥 **Total Annual Waste at &lt;{util_threshold}%:** **£{total_wasted:,.2f}**")

    with col_w_chart:
        if not idle_summary.empty:
            fig_waste = px.pie(
                idle_summary,
                names="platform",
                values="wasted_cost_gbp",
                color="platform",
                color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
                hole=0.4,
                template="plotly_dark",
                title=f"Wasted Spend by Platform (&lt;{util_threshold}%)"
            )
            fig_waste.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=30, b=10), height=260)
            st.plotly_chart(fig_waste, width="stretch")

    st.markdown("##### Top 20 Worst Offender Workloads")
    waste_workloads = con.execute(f"""
        SELECT
            workload_id,
            platform,
            business_unit,
            service,
            environment,
            round(sum(cost_gbp), 2) AS annual_cost_gbp,
            round(avg(utilisation_pct), 2) AS mean_utilisation_pct
        FROM cost
        GROUP BY 1, 2, 3, 4, 5
        HAVING avg(utilisation_pct) < {util_threshold}
        ORDER BY annual_cost_gbp DESC
        LIMIT 20
    """).df()

    st.dataframe(
        waste_workloads,
        column_config={
            "annual_cost_gbp": st.column_config.NumberColumn("Annual Cost", format="£%.2f"),
            "mean_utilisation_pct": st.column_config.ProgressColumn("Mean Utilisation", min_value=0, max_value=util_threshold, format="%.2f%%"),
        },
        width="stretch",
        height=320
    )

    csv_waste = waste_workloads.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export Waste Offender Workloads (CSV)", data=csv_waste, file_name="waste_workloads.csv", mime="text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: FINDING 4 — NON-PROD SPRAWL (Problem 5 fix)
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("Finding 4: Non-Production Sprawl & Scheduling Opportunity")
    
    # Problem 5 explicit one-line definition
    st.info("📌 **Definition:** Non-production environments are defined strictly as **Development**, **Staging**, and **Test** workloads (Production workloads are excluded).")

    st.markdown(
        """
        Conventional FinOps reviews look almost exclusively at production systems.
        In this enterprise, **non-production environments consume 49.7% of the total budget (£7.62M)**.
        Even more striking: **£6.65M of non-production spend is hosted on high-cost Mainframe infrastructure.**
        """
    )

    col_env1, col_env2 = st.columns([1, 1.1])

    with col_env1:
        st.markdown("##### Spend Distribution Across Environments")
        env_breakdown = con.execute("""
            SELECT
                environment,
                count(DISTINCT workload_id) AS workloads,
                round(sum(cost_gbp), 2) AS cost_gbp,
                round(100.0 * sum(cost_gbp) / (SELECT sum(cost_gbp) FROM cost), 1) AS share_pct,
                round(avg(utilisation_pct), 1) AS mean_util_pct
            FROM cost
            GROUP BY 1
            ORDER BY cost_gbp DESC
        """).df()

        fig_env = px.bar(
            env_breakdown,
            x="environment",
            y="cost_gbp",
            color="environment",
            text="cost_gbp",
            color_discrete_sequence=["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b"],
            template="plotly_dark"
        )
        fig_env.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
        fig_env.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="Annual Spend (£)",
            height=340
        )
        st.plotly_chart(fig_env, width="stretch")

    with col_env2:
        st.markdown("##### Platform Distribution Within Environments")
        env_plat = con.execute("""
            SELECT
                environment,
                platform,
                round(sum(cost_gbp), 2) AS cost_gbp
            FROM cost
            GROUP BY 1, 2
            ORDER BY environment, cost_gbp DESC
        """).df()

        fig_env_plat = px.bar(
            env_plat,
            x="environment",
            y="cost_gbp",
            color="platform",
            barmode="stack",
            color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
            template="plotly_dark"
        )
        fig_env_plat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="Annual Spend (£)",
            height=340
        )
        st.plotly_chart(fig_env_plat, width="stretch")

    st.markdown("""
    <div class="callout-box" style="border-left-color: #10b981;">
        <h4 style="color:#34d399; margin:0 0 6px 0;">💡 The Auto-Parking / Ephemeral Environment Opportunity</h4>
        <p style="color:#cbd5e1; font-size:0.9rem; line-height:1.6; margin:0;">
            Non-prod workloads are billed 24 hours a day, 7 days a week (168 hours/week).
            Developers and testers typically only require systems during business hours (45 hours/week).<br>
            Implementing automated night and weekend scheduling ("Auto-Parking") on non-prod cloud and distributed workloads can reduce runtime by <strong>~65%</strong>, yielding immediate annual savings of <strong>~£480k</strong> without impacting engineering productivity.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: WHAT-IF ROI SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.subheader("🎛️ Interactive FinOps ROI & Modernisation Simulator")
    st.markdown(
        """
        Model potential interventions in real time to calculate projected annual cost savings,
        budget reduction, and modernised architecture impact.
        """
    )

    col_sim_ctrl, col_sim_res = st.columns([1, 1.2])

    with col_sim_ctrl:
        st.markdown("##### Simulation Parameters")
        waste_elim_pct = st.slider("1. Eliminate Near-Idle Workloads (<5% Util)", 0, 100, 75, 5, help="% of idle waste capacity decommissioned")
        nonprod_park_pct = st.slider("2. Non-Prod Cloud Auto-Parking (Nights/Weekends)", 0, 80, 50, 5, help="% reduction in non-prod cloud hours")
        mf_modernize_pct = st.slider("3. Migrate Mainframe Non-Prod to Cloud", 0, 50, 20, 5, help="% of mainframe non-prod compute migrated")
        cloud_target_util = st.slider("4. Target Cloud Utilisation Post-Migration", 20, 70, 50, 5, help="Achieved cloud utilisation via autoscaling & containers")

    # Calculation logic using realistic 2.2x utilised economics
    baseline_spend = float(estate_kpis["total_spend"])
    idle_waste_total = float(waste_kpi["wasted_spend"])
    waste_savings = (waste_elim_pct / 100.0) * idle_waste_total

    nonprod_cloud_spend = con.execute("""
        SELECT coalesce(sum(cost_gbp), 0) FROM cost WHERE platform = 'cloud' AND environment != 'production'
    """).fetchone()[0]
    parking_savings = (nonprod_park_pct / 100.0) * float(nonprod_cloud_spend)

    mf_nonprod_spend = con.execute("""
        SELECT coalesce(sum(cost_gbp), 0) FROM cost WHERE platform = 'mainframe' AND environment != 'production'
    """).fetchone()[0]
    
    # Mainframe migrated compute replacement
    mf_migrated_cost = (mf_modernize_pct / 100.0) * float(mf_nonprod_spend)
    # Scaled by utilised economics: cloud cost = mf_cost * (cloud_unit / mf_unit) * (baseline_cloud_util / target_util)
    cloud_cost_replacement = mf_migrated_cost * (0.0682 / 0.4932) * (21.2 / cloud_target_util)
    migration_net_savings = max(0.0, mf_migrated_cost - cloud_cost_replacement)

    total_projected_savings = waste_savings + parking_savings + migration_net_savings
    new_spend = max(0.0, baseline_spend - total_projected_savings)
    savings_pct = (total_projected_savings / baseline_spend) * 100.0 if baseline_spend > 0 else 0.0

    with col_sim_res:
        st.markdown("##### Projected Financial Impact")
        st.markdown(f"""
        <div class="metric-card" style="--card-accent: #10b981; margin-bottom: 1rem;">
            <div class="metric-label">Projected Gross Annual Savings</div>
            <div class="metric-value" style="color:#34d399;">£{total_projected_savings:,.0f}</div>
            <div class="metric-delta"><span class="delta-badge-green">{savings_pct:.1f}% reduction in total estate budget</span></div>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Waste Elimination", f"£{waste_savings:,.0f}")
        with col_s2:
            st.metric("Auto-Parking", f"£{parking_savings:,.0f}")
        with col_s3:
            st.metric("Modernisation Net", f"£{migration_net_savings:,.0f}")

    # Waterfall comparison
    fig_wf = go.Figure(go.Waterfall(
        name="Budget Waterfall",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Baseline Budget", "Idle Waste", "Auto-Parking", "Cloud Modernisation", "Optimised Budget"],
        textposition="outside",
        text=[f"£{baseline_spend/1e6:.2f}M", f"-£{waste_savings/1e6:.2f}M", f"-£{parking_savings/1e6:.2f}M", f"-£{migration_net_savings/1e6:.2f}M", f"£{new_spend/1e6:.2f}M"],
        y=[baseline_spend, -waste_savings, -parking_savings, -migration_net_savings, 0],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": "#10b981"}},
        increasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#6366f1"}}
    ))
    fig_wf.update_layout(
        title="Projected Estate Budget Waterfall (£)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    st.plotly_chart(fig_wf, width="stretch")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: METHOD DEMONSTRATION — CARBON (Moved to back per Problem 4)
# ─────────────────────────────────────────────────────────────────────────────
with tab7:
    st.subheader("🌱 Method Demonstration: Carbon Footprint Signals")
    
    st.warning("⚠️ **Data Provenance Caveat (Synthetic Grid Model):** Grid carbon intensity in this challenge is SYNTHETIC (modelled realistically from UK grid diurnal and seasonal dynamics). Treat these results as a methodological demonstration of temporal load-shifting, not a real-world physical or compliance measurement.")

    carbon_metrics = con.execute("""
        SELECT
            c.platform,
            round(sum(c.energy_kwh), 0) AS total_kwh,
            round(sum(c.carbon_kg) / 1000.0, 2) AS total_carbon_tonnes,
            round(avg(c.grid_intensity_gco2_per_kwh), 1) AS avg_grid_intensity,
            round(sum(c.carbon_kg) / sum(t.cost_gbp), 3) AS kg_co2_per_gbp
        FROM carbon c
        JOIN cost t ON c.workload_id = t.workload_id AND c.usage_date = t.usage_date
        GROUP BY 1
        ORDER BY total_carbon_tonnes DESC
    """).df()

    col_c1, col_c2 = st.columns([1, 1.2])

    with col_c1:
        st.markdown("##### Carbon Footprint by Platform")
        st.dataframe(
            carbon_metrics,
            column_config={
                "total_kwh": st.column_config.NumberColumn("Total Energy (kWh)", format="%.0f"),
                "total_carbon_tonnes": st.column_config.NumberColumn("Emissions (Tonnes CO2)", format="%.2f t"),
                "kg_co2_per_gbp": st.column_config.NumberColumn("Carbon Intensity (kg CO2 / £)", format="%.3f"),
            },
            width="stretch",
            hide_index=True
        )

    with col_c2:
        st.markdown("##### Emissions vs. Cost Ratio")
        fig_carbon = px.bar(
            carbon_metrics,
            x="platform",
            y="kg_co2_per_gbp",
            color="platform",
            text="kg_co2_per_gbp",
            color_discrete_map={"mainframe": "#8b5cf6", "distributed": "#06b6d4", "cloud": "#10b981"},
            template="plotly_dark",
            labels={"kg_co2_per_gbp": "kg CO2 / £ Spend"}
        )
        fig_carbon.update_traces(texttemplate="%{text:.3f} kg/£", textposition="outside")
        fig_carbon.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_carbon, width="stretch")

    # Monthly Carbon Trend
    monthly_carbon = con.execute("""
        SELECT
            strftime(usage_date, '%Y-%m') AS month,
            round(sum(carbon_kg) / 1000.0, 2) AS tonnes_co2,
            round(avg(grid_intensity_gco2_per_kwh), 1) AS mean_grid_intensity
        FROM carbon
        GROUP BY 1
        ORDER BY 1
    """).df()

    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(
        name="Tonnes CO2e",
        x=monthly_carbon["month"],
        y=monthly_carbon["tonnes_co2"],
        marker_color="#10b981",
        yaxis="y"
    ))
    fig_time.add_trace(go.Scatter(
        name="Grid Intensity (gCO2/kWh)",
        x=monthly_carbon["month"],
        y=monthly_carbon["mean_grid_intensity"],
        marker_color="#f59e0b",
        yaxis="y2",
        mode="lines+markers"
    ))
    fig_time.update_layout(
        title="Monthly Emissions & Grid Intensity Fluctuations",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Tonnes CO2e"),
        yaxis2=dict(title="Grid Intensity (gCO2/kWh)", overlaying="y", side="right"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320
    )
    st.plotly_chart(fig_time, width="stretch")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: LIVE DUCKDB CONSOLE
# ─────────────────────────────────────────────────────────────────────────────
with tab8:
    st.subheader("💻 Live DuckDB Query Console")
    st.markdown("Run interactive SQL directly against the 419,750-row Parquet views (`cost`, `chargeback`, `carbon`).")

    sample_queries = {
        "1. Spend by Business Unit (Highlighting UNALLOCATED)": """SELECT business_unit,
       round(sum(cost_gbp), 2) AS cost_gbp,
       round(100 * sum(cost_gbp) / sum(sum(cost_gbp)) OVER (), 1) AS pct_of_total
FROM cost
GROUP BY 1
ORDER BY cost_gbp DESC
LIMIT 15;""",

        "2. Unit Economics & Normalisation by Platform": """SELECT platform,
       round(sum(cost_gbp), 0) AS cost_gbp,
       round(sum(vcpu_hours), 0) AS vcpu_hours,
       round(sum(cost_gbp) / sum(vcpu_hours), 4) AS cost_per_vcpu_hour,
       round(avg(utilisation_pct), 1) AS mean_utilisation_pct
FROM cost
GROUP BY 1
ORDER BY cost_per_vcpu_hour DESC;""",

        "3. Near-Idle Waste Workloads (Utilisation < 5%)": """SELECT workload_id, platform, business_unit,
       round(sum(cost_gbp), 2) AS annual_cost_gbp,
       round(avg(utilisation_pct), 1) AS mean_utilisation_pct
FROM cost
GROUP BY 1, 2, 3
HAVING avg(utilisation_pct) < 5
ORDER BY annual_cost_gbp DESC
LIMIT 20;""",

        "4. Grain & Key Uniqueness Check": """SELECT count(*) AS total_rows,
       count(DISTINCT (workload_id, usage_date)) AS unique_keys,
       count(*) - count(DISTINCT (workload_id, usage_date)) AS duplicate_rows
FROM cost;""",

        "5. Environment Spend & Workload Count": """SELECT environment,
       count(DISTINCT workload_id) AS workloads,
       round(sum(cost_gbp), 2) AS cost_gbp,
       round(avg(utilisation_pct), 1) AS avg_util_pct
FROM cost
GROUP BY 1
ORDER BY cost_gbp DESC;""",

        "6. Carbon Emissions by Platform": """SELECT c.platform,
       round(sum(c.energy_kwh), 0) AS energy_kwh,
       round(sum(c.carbon_kg) / 1000.0, 2) AS tonnes_co2,
       round(sum(c.carbon_kg) / sum(t.cost_gbp), 3) AS kg_co2_per_gbp
FROM carbon c
JOIN cost t ON c.workload_id = t.workload_id AND c.usage_date = t.usage_date
GROUP BY 1
ORDER BY tonnes_co2 DESC;"""
    }

    selected_query_name = st.selectbox("Choose a Starter Query (from consumers/duckdb.sql):", list(sample_queries.keys()))
    user_sql = st.text_area("SQL Query Editor:", value=sample_queries[selected_query_name], height=160)

    if st.button("▶ Run Query", type="primary"):
        start_t = time.perf_counter()
        try:
            res_df = con.execute(user_sql).df()
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            st.success(f"⚡ Executed in {elapsed_ms:.1f} ms — Returned {len(res_df):,} row(s)")
            st.dataframe(res_df, width="stretch")

            csv_res = res_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Results as CSV", data=csv_res, file_name="query_results.csv", mime="text/csv")
        except Exception as err:
            st.error(f"SQL Execution Error: {err}")
