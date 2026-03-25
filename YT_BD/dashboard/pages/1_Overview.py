# ============================================================
#  Dashboard Page 1: Overview - Top Trending Videos
# ============================================================
import sys
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db_connector import get_engine

st.set_page_config(page_title="Top Videos | YT BigData", page_icon="📊", layout="wide")

# Custom CSS (matching home theme)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #141428 60%, #0d0d1f 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a3e,#12122b) !important; border-right:1px solid #333; }
[data-testid="stSidebar"] * { color: #e0e0ff !important; }
.section-header { font-size:1.4rem; font-weight:700; background:linear-gradient(90deg,#a78bfa,#60a5fa);
-webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:20px 0 10px 0;
padding-bottom:6px; border-bottom:2px solid #2d2d7a; }
.video-card { background: linear-gradient(145deg,#1e1e4a,#252555); border:1px solid #3a3a7a;
border-radius:16px; padding:16px; margin-bottom:12px; transition:all 0.3s; }
.video-card:hover { transform:translateY(-3px); box-shadow:0 8px 32px rgba(99,102,241,0.3); }
</style>""", unsafe_allow_html=True)

st.markdown("# 📊 Top Trending Videos")
st.markdown("---")

@st.cache_data(ttl=300)
def load_videos():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(
            """SELECT video_id, title, channel_name, category_name,
                      view_count, like_count, comment_count, engagement_score,
                      thumbnail_url, published_at
               FROM processed_videos
               ORDER BY view_count DESC LIMIT 50""", conn
        )

try:
    df = load_videos()

    if df.empty:
        st.info("No data yet. Run `python run_pipeline.py` to collect data.")
        st.stop()

    # ---- Top 10 by Views Bar Chart ----
    st.markdown('<div class="section-header">🏆 Top 10 Videos by Views</div>', unsafe_allow_html=True)
    top10 = df.head(10).copy()
    top10["short_title"] = top10["title"].str[:35] + "..."
    fig = px.bar(
        top10, x="view_count", y="short_title", orientation="h",
        color="engagement_score", color_continuous_scale="Viridis",
        labels={"view_count": "Views", "short_title": "Video"},
        template="plotly_dark"
    )
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font=dict(color="#e0e0ff", family="Inter"),
        yaxis=dict(autorange="reversed"),
        height=450, margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_colorbar=dict(title="Engagement%", tickfont=dict(color="#a78bfa"))
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Scatter: Views vs. Likes ----
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">💎 Views vs Likes</div>', unsafe_allow_html=True)
        fig2 = px.scatter(
            df, x="view_count", y="like_count",
            hover_name="title", color="category_name",
            size="comment_count", template="plotly_dark",
            labels={"view_count": "Views", "like_count": "Likes"},
            size_max=30
        )
        fig2.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font=dict(color="#e0e0ff", family="Inter"),
            height=380, margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(font=dict(color="#a78bfa"))
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">⚡ Top by Engagement Score</div>', unsafe_allow_html=True)
        top_eng = df.nlargest(10, "engagement_score")[["title", "channel_name", "engagement_score"]].copy()
        top_eng["title_s"] = top_eng["title"].str[:30]
        fig3 = px.bar(
            top_eng, x="engagement_score", y="title_s", orientation="h",
            color="engagement_score", color_continuous_scale="Plasma",
            template="plotly_dark",
            labels={"engagement_score": "Score%", "title_s": "Video"}
        )
        fig3.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font=dict(color="#e0e0ff", family="Inter"),
            yaxis=dict(autorange="reversed"),
            height=380, margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ---- Video Cards ----
    st.markdown('<div class="section-header">🎬 Video Details (Top 10)</div>', unsafe_allow_html=True)
    for _, row in df.head(10).iterrows():
        cols = st.columns([1, 4])
        with cols[0]:
            if row.get("thumbnail_url"):
                st.image(row["thumbnail_url"], width=160)
        with cols[1]:
            st.markdown(f"""<div class="video-card">
                <b style="color:#a78bfa;font-size:1.05rem">{row['title']}</b><br>
                <span style="color:#60a5fa">📺 {row['channel_name']}</span> &nbsp;|&nbsp;
                <span style="color:#34d399">#{row['category_name']}</span><br>
                <span style="color:#e0e0ff">👁 {int(row['view_count']):,} views &nbsp;
                ❤️ {int(row['like_count']):,} likes &nbsp;
                💬 {int(row['comment_count']):,} comments &nbsp;
                ⚡ {row['engagement_score']:.2f}% engagement</span>
            </div>""", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure MySQL is running and the pipeline has been executed.")


