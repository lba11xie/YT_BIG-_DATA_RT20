import streamlit as st
import pandas as pd
import plotly.express as px
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, COLOR_SEQ

st.set_page_config(page_title="Categories | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Categories</div><div class="hero-sub">Distribution & Performance</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()
df = pd.read_sql("SELECT category_name, COUNT(*) as video_count, SUM(view_count) as total_views, AVG(engagement_score) as avg_eng, SUM(comment_count) as total_comments FROM processed_videos GROUP BY category_name", engine)
if df.empty:
    st.warning("No data found."); st.stop()

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="sh"><span> Video Count by Category</span></div>', unsafe_allow_html=True)
    fig1 = px.pie(df, values="video_count", names="category_name", hole=0.4, color_discrete_sequence=COLOR_SEQ)
    fig1.update_layout(height=420, legend=dict(font=dict()), **get_plotly_theme())
    fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color=get_plotly_theme().get("font",{}).get("color","#000"), width=2)))
    st.plotly_chart(fig1, use_container_width=True, theme=None)
with c2:
    st.markdown('<div class="sh"><span> Total Views by Category</span></div>', unsafe_allow_html=True)
    fig2 = px.bar(df.sort_values("total_views", ascending=True), x="total_views", y="category_name", orientation="h", color="avg_eng", color_continuous_scale=["#FF1744","#FFD600","#00E676"], labels={"total_views":"Total Views","category_name":""})
    fig2.update_layout(height=420, coloraxis_colorbar=dict(title="Avg Eng%", tickfont=dict()), **get_plotly_theme())
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True, theme=None)

st.markdown('<div class="sh"><span> Category Detailed Metrics</span></div>', unsafe_allow_html=True)
st.dataframe(df.sort_values("video_count", ascending=False), use_container_width=True, hide_index=True)
