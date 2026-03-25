import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, get_theme_colors, COLOR_SEQ

st.set_page_config(page_title="Trending | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Trending</div><div class="hero-sub">Momentum & Viral Videos</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()
df = pd.read_sql("SELECT * FROM processed_videos ORDER BY view_count DESC LIMIT 200", engine)
if df.empty:
    st.warning("No data found."); st.stop()

_tc = get_theme_colors()

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown('<div class="sh"><span> Viral Videos Right Now</span></div>', unsafe_allow_html=True)
    fig_bar = px.bar(df.head(15).sort_values("view_count", ascending=True), x="view_count", y="title", orientation="h", color="engagement_score", color_continuous_scale=["#FFD600","#00E676","#FF1744"])
    fig_bar.update_layout(height=500, coloraxis_colorbar=dict(title="Eng%"), **get_plotly_theme())
    fig_bar.update_traces(marker_line_width=0)
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

with c2:
    st.markdown('<div class="sh"><span> Category Momentum</span></div>', unsafe_allow_html=True)
    cat_df = df.groupby("category_name")["view_count"].sum().reset_index().sort_values("view_count", ascending=False)
    for i, row in cat_df.head(6).iterrows():
        pct = (row["view_count"] / cat_df["view_count"].sum()) * 100
        st.markdown(f'''
        <div class="mom" style="border-color:{_tc["border"]}; background:{_tc["bg_card"]}">
            <div class="mom-name" style="color:{_tc["text"]}">{row["category_name"]}</div>
            <div style="height:10px; background:{_tc["bg"]}; border:1px solid {_tc["border"]};">
                <div class="mom-bar" style="width:{int(pct)}%"></div>
            </div>
            <div style="font-size:0.8rem; text-align:right; margin-top:4px; color:{_tc["text_muted"]}"><b>{int(row["view_count"]):,}</b> views</div>
        </div>
        ''', unsafe_allow_html=True)

st.markdown('<div class="sh"><span> Channel Comparison (Radar)</span></div>', unsafe_allow_html=True)
top_channels = df.groupby("channel_name")[["view_count", "like_count", "comment_count", "engagement_score"]].mean().reset_index()
top_channels = top_channels.sort_values("view_count", ascending=False).head(4)
categories = ['Views', 'Likes', 'Comments', 'Engagement']

# Radar Chart Logic: Normalize metrics for display
radar_df = top_channels.copy()
for col in ['view_count', 'like_count', 'comment_count', 'engagement_score']:
    max_val = radar_df[col].max()
    if max_val > 0:
        radar_df[col] = radar_df[col] / max_val

fig_radar = go.Figure()
colors = ["#FFD600", "#00E676", "#00B0FF", "#D500F9"]
for i, row in radar_df.iterrows():
    vals = [row["view_count"], row["like_count"], row["comment_count"], row["engagement_score"]]
    fig_radar.add_trace(go.Scatterpolar(
        r=vals, theta=categories, fill='toself', name=str(row["channel_name"])[:15],
        marker=dict(color=colors[i%len(colors)])
    ))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, showticklabels=False, gridcolor="rgba(128,128,128,0.2)"),
        angularaxis=dict(gridcolor="rgba(128,128,128,0.2)")
    ), 
    height=450, 
    **get_plotly_theme()
)
st.plotly_chart(fig_radar, use_container_width=True, theme=None)
