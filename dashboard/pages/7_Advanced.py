import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, get_theme_colors, COLOR_SEQ

st.set_page_config(page_title="Advanced Analytics | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Advanced</div><div class="hero-sub">Correlations & Distributions</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()
df = pd.read_sql("SELECT * FROM processed_videos Limit 1000", engine)
cdf = pd.read_sql("SELECT * FROM processed_comments Limit 5000", engine)

if df.empty:
    st.warning("No data found."); st.stop()

st.markdown('<div class="sh"><span> Metric Correlations</span></div>', unsafe_allow_html=True)
cols = ["view_count","like_count","comment_count","engagement_score","duration_seconds"]
corr = df[cols].corr()
fig_heat = go.Figure(data=go.Heatmap(
    z=corr.values, x=cols, y=cols, colorscale=[[0,"#7c3aed"],[0.5,"#06b6d4"],[1,"#10b981"]], zmin=-1, zmax=1,
    text=corr.values.round(2), texttemplate="%{text}", textfont=dict(size=13), hovertemplate="%{y} vs %{x}: %{z}<extra></extra>"
))
fig_heat.update_layout(height=400, **get_plotly_theme())
st.plotly_chart(fig_heat, use_container_width=True, theme=None)

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="sh"><span> Engagement Distribution</span></div>', unsafe_allow_html=True)
    fig_hist = px.histogram(df, x="engagement_score", nbins=40, color_discrete_sequence=["#FFD600"])
    fig_hist.update_layout(height=340, bargap=0.05, **get_plotly_theme())
    fig_hist.update_traces(marker_line_color=get_plotly_theme().get("font",{}).get("color","#000"),marker_line_width=0.8)
    st.plotly_chart(fig_hist, use_container_width=True, theme=None)

with c2:
    st.markdown('<div class="sh"><span> Views vs Duration</span></div>', unsafe_allow_html=True)
    fig_dur = px.scatter(df, x="duration_seconds", y="view_count", color="category_name", color_discrete_sequence=COLOR_SEQ)
    fig_dur.update_layout(height=340, legend=dict(font=dict(size=9)), **get_plotly_theme())
    fig_dur.update_traces(marker=dict(size=7, line=dict(width=0)))
    st.plotly_chart(fig_dur, use_container_width=True, theme=None)

st.markdown('<div class="sh"><span> Time Series (Views)</span></div>', unsafe_allow_html=True)
df["date"] = pd.to_datetime(df["published_at"]).dt.date
ts = df.groupby("date")["view_count"].sum().reset_index()
fig_ts = px.area(ts, x="date", y="view_count", color_discrete_sequence=["#FFD600"])
fig_ts.update_traces(fillcolor="rgba(255,214,0,0.15)", line_color="#FFD600")
fig_ts.update_layout(height=340, **get_plotly_theme())
st.plotly_chart(fig_ts, use_container_width=True, theme=None)

if not cdf.empty:
    st.markdown('<div class="sh"><span> Comment Polarity & Subjectivity</span></div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        fig_pol = px.histogram(cdf, x="polarity", nbins=40, color_discrete_sequence=["#38bdf8"])
        fig_pol.add_vline(x=0, line_color=get_plotly_theme().get("font",{}).get("color","#000"), line_dash="dash", line_width=2)
        fig_pol.update_layout(height=300, bargap=0.06, title=dict(text="Polarity Distribution",font=dict()), **get_plotly_theme())
        st.plotly_chart(fig_pol, use_container_width=True, theme=None)
    with sc2:
        fig_sub = px.histogram(cdf, x="subjectivity", nbins=40, color_discrete_sequence=["#f43f5e"])
        fig_sub.update_layout(height=300, bargap=0.06, title=dict(text="Subjectivity Distribution",font=dict()), **get_plotly_theme())
        st.plotly_chart(fig_sub, use_container_width=True, theme=None)

# ── Download CSV Data ──────────────────────────────────────────────────────────
st.markdown('<div class="sh"><span>⬇ Download CSV Data</span></div>', unsafe_allow_html=True)
dl1, dl2 = st.columns(2)
with dl1:
    st.download_button(
        label="📥 Download Videos CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="processed_videos.csv",
        mime="text/csv",
        use_container_width=True,
    )
with dl2:
    if not cdf.empty:
        st.download_button(
            label="📥 Download Comments CSV",
            data=cdf.to_csv(index=False).encode("utf-8"),
            file_name="processed_comments.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No comments data available.")
