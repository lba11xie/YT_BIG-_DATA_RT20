import streamlit as st
import pandas as pd
import plotly.express as px
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, get_theme_colors, COLOR_SEQ

st.set_page_config(page_title="Overview | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Overview</div><div class="hero-sub">Top Videos & Core Metrics</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()
df = pd.read_sql("SELECT * FROM processed_videos ORDER BY view_count DESC LIMIT 1000", engine)
if df.empty:
    st.warning("No data found.")
    st.stop()
df["short_title"] = df["title"].apply(lambda x: str(x)[:40] + "..." if len(str(x)) > 40 else str(x))

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="sh"><span> Top 10 by Views</span></div>', unsafe_allow_html=True)
    fig = px.bar(
        df.head(10).sort_values("view_count", ascending=True),
        x="view_count", y="short_title", orientation="h",
        color="engagement_score", color_continuous_scale=["#FF1744","#FFD600","#00E676"],
        labels={"view_count":"Views", "short_title":""}
    )
    fig.update_layout(
        height=420, coloraxis_colorbar=dict(title="Eng%", tickfont=dict()),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"), yaxis=dict(autorange="reversed", gridcolor="rgba(255,255,255,0.04)"),
        **get_plotly_theme()
    )
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True, theme=None)

with c2:
    st.markdown('<div class="sh"><span> Engagement vs Views</span></div>', unsafe_allow_html=True)
    fig2 = px.scatter(
        df, x="view_count", y="like_count", color="category_name",
        color_discrete_sequence=COLOR_SEQ, labels={"view_count":"Views","like_count":"Likes"}
    )
    fig2.update_layout(height=420, legend=dict(font=dict(size=10)), **get_plotly_theme())
    fig2.update_traces(marker=dict(line=dict(width=0)))
    st.plotly_chart(fig2, use_container_width=True, theme=None)

st.markdown('<div class="sh"><span> Video Details — Top 10</span></div>', unsafe_allow_html=True)
for i, (_, row) in enumerate(df.head(10).iterrows()):
    _tc = get_theme_colors()
    accent_colors = ["#FFD600","#00E676","#FF1744","#00B0FF","#D500F9","#FF9100"]
    accent = accent_colors[i % len(accent_colors)]
    cols = st.columns([1, 5])
    with cols[0]:
        if row.get("thumbnail_url"): st.image(row["thumbnail_url"], width=150)
    with cols[1]:
        st.markdown(f"""<div class="vid-card" style="border-left:4px solid {accent}">
            <b style="color:{_tc['text']};font-size:1.02rem">{row['title']}</b><br>
            <span style="color:{_tc['text_muted']}">{row['channel_name']}</span><br><br>
            <span class="stat"> <b>{int(row['view_count']):,}</b> views</span>
            <span class="stat"> <b>{int(row['like_count']):,}</b> likes</span>
            <span class="stat"> <b>{int(row['comment_count']):,}</b> comments</span>
            <span class="stat"> <b>{row['engagement_score']:.2f}%</b> eng</span>
        </div>""", unsafe_allow_html=True)
