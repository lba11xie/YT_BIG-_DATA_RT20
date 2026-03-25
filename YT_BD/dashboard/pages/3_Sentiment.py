# ============================================================
#  Dashboard Page 3: Sentiment Analysis
# ============================================================
import sys
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db_connector import get_engine

st.set_page_config(page_title="Sentiment | YT BigData", page_icon="💬", layout="wide")

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
.comment-pos { background:#0d2b1f; border-left:4px solid #34d399; padding:10px 14px; border-radius:8px; margin-bottom:8px; color:#a7f3d0; }
.comment-neg { background:#2b0d0d; border-left:4px solid #f87171; padding:10px 14px; border-radius:8px; margin-bottom:8px; color:#fca5a5; }
.comment-neu { background:#1a1a3e; border-left:4px solid #818cf8; padding:10px 14px; border-radius:8px; margin-bottom:8px; color:#c7d2fe; }
</style>""", unsafe_allow_html=True)

st.markdown("# 💬 Sentiment Analysis")
st.markdown("Powered by **TextBlob NLP** via **Apache Spark UDF** ⚡")
st.markdown("---")

@st.cache_data(ttl=300)
def load_sentiment():
    engine = get_engine()
    with engine.connect() as conn:
        sentiments = pd.read_sql(
            "SELECT sentiment, COUNT(*) as cnt, AVG(polarity) as avg_polarity FROM processed_comments GROUP BY sentiment",
            conn)
        by_video = pd.read_sql(
            """SELECT v.title, AVG(c.polarity) as avg_polarity, COUNT(c.comment_id) as total_comments,
                      SUM(CASE WHEN c.sentiment='Positive' THEN 1 ELSE 0 END) as positive_count,
                      SUM(CASE WHEN c.sentiment='Negative' THEN 1 ELSE 0 END) as negative_count
               FROM processed_comments c JOIN processed_videos v ON c.video_id = v.video_id
               GROUP BY v.title ORDER BY avg_polarity DESC LIMIT 20""", conn)
        sample_comments = pd.read_sql(
            "SELECT comment_text, sentiment, polarity, author_name FROM processed_comments ORDER BY RAND() LIMIT 30",
            conn)
    return sentiments, by_video, sample_comments

try:
    sentiments, by_video, sample_comments = load_sentiment()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-header">🥧 Sentiment Split</div>', unsafe_allow_html=True)
        if not sentiments.empty:
            color_map = {"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#818cf8"}
            fig_donut = go.Figure(data=[go.Pie(
                labels=sentiments["sentiment"],
                values=sentiments["cnt"],
                hole=0.55,
                marker_colors=[color_map.get(s, "#888") for s in sentiments["sentiment"]],
                textfont=dict(color="#ffffff", size=13)
            )])
            fig_donut.update_layout(
                plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                font=dict(color="#e0e0ff", family="Inter"),
                height=350, margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(font=dict(color="#a78bfa")),
                annotations=[dict(text="Sentiment", x=0.5, y=0.5, font_size=16,
                                  font_color="#a78bfa", showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            # Sentiment stats
            for _, row in sentiments.iterrows():
                emoji = "🟢" if row["sentiment"] == "Positive" else ("🔴" if row["sentiment"] == "Negative" else "🔵")
                st.markdown(f"{emoji} **{row['sentiment']}**: {int(row['cnt']):,} comments (avg polarity: {row['avg_polarity']:.3f})")

    with col2:
        st.markdown('<div class="section-header">📊 Video Sentiment Ranking</div>', unsafe_allow_html=True)
        if not by_video.empty:
            by_video["short_title"] = by_video["title"].str[:40]
            fig_bar = px.bar(
                by_video.head(15), x="avg_polarity", y="short_title", orientation="h",
                color="avg_polarity",
                color_continuous_scale=["#f87171", "#818cf8", "#34d399"],
                range_color=[-1, 1],
                template="plotly_dark",
                labels={"avg_polarity": "Avg Polarity", "short_title": "Video"}
            )
            fig_bar.add_vline(x=0, line_width=2, line_color="#a78bfa", line_dash="dash")
            fig_bar.update_layout(
                plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                font=dict(color="#e0e0ff", family="Inter"),
                yaxis=dict(autorange="reversed"),
                height=400, margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Sample Comments
    st.markdown('<div class="section-header">📝 Sample Comments by Sentiment</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🟢 Positive", "🔴 Negative", "🔵 Neutral"])

    def show_comments(tab, sentiment_filter, css_class):
        with tab:
            subset = sample_comments[sample_comments["sentiment"] == sentiment_filter].head(8)
            if subset.empty:
                st.info("No comments found.")
            for _, row in subset.iterrows():
                st.markdown(f'<div class="{css_class}"><b>{row["author_name"]}</b> (polarity: {row["polarity"]:.2f})<br>{row["comment_text"][:200]}</div>',
                            unsafe_allow_html=True)

    show_comments(tab1, "Positive", "comment-pos")
    show_comments(tab2, "Negative", "comment-neg")
    show_comments(tab3, "Neutral",  "comment-neu")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure MySQL is running and the pipeline has been executed.")
en executed.")


