# ============================================================
#  Dashboard Page 2: Category Analysis
# ============================================================
import sys
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db_connector import get_engine

st.set_page_config(page_title="Category Analysis | YT BigData", page_icon="📂", layout="wide")

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
</style>""", unsafe_allow_html=True)

st.markdown("# 📂 Category Analysis")
st.markdown("---")

@st.cache_data(ttl=300)
def load_category_data():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(
            """SELECT category_name, COUNT(*) as video_count,
                      SUM(view_count) as total_views,
                      AVG(view_count) as avg_views,
                      AVG(like_count) as avg_likes,
                      AVG(engagement_score) as avg_engagement,
                      SUM(comment_count) as total_comments
               FROM processed_videos
               GROUP BY category_name
               ORDER BY video_count DESC""", conn
        )

try:
    df = load_category_data()

    if df.empty:
        st.info("No data yet. Run `python run_pipeline.py` to collect data.")
        st.stop()

    col1, col2 = st.columns(2)

    # Pie: Video count per category
    with col1:
        st.markdown('<div class="section-header">🥧 Videos Per Category</div>', unsafe_allow_html=True)
        fig1 = px.pie(
            df, values="video_count", names="category_name",
            hole=0.45, template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig1.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font=dict(color="#e0e0ff", family="Inter"),
            height=400, margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(font=dict(color="#a78bfa", size=10))
        )
        fig1.update_traces(textfont=dict(color="#ffffff"))
        st.plotly_chart(fig1, use_container_width=True)

    # Bar: Avg views per category
    with col2:
        st.markdown('<div class="section-header">📊 Avg Views Per Category</div>', unsafe_allow_html=True)
        df_sorted = df.sort_values("avg_views", ascending=True).tail(15)
        fig2 = px.bar(
            df_sorted, x="avg_views", y="category_name", orientation="h",
            color="avg_engagement", color_continuous_scale="Viridis",
            template="plotly_dark",
            labels={"avg_views": "Avg Views", "category_name": "Category"}
        )
        fig2.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font=dict(color="#e0e0ff", family="Inter"),
            height=400, margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Bubble: Total views vs total comments (bubble = video count)
    st.markdown('<div class="section-header">🌐 Category Bubble Map (Views × Comments × Count)</div>', unsafe_allow_html=True)
    fig3 = px.scatter(
        df, x="total_views", y="total_comments",
        size="video_count", color="avg_engagement",
        hover_name="category_name", template="plotly_dark",
        color_continuous_scale="Turbo", size_max=60,
        labels={"total_views": "Total Views", "total_comments": "Total Comments",
                "avg_engagement": "Avg Engagement%"}
    )
    fig3.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font=dict(color="#e0e0ff", family="Inter"),
        height=420, margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Category Data Table
    st.markdown('<div class="section-header">📋 Category Summary Table</div>', unsafe_allow_html=True)
    display_df = df.copy()
    display_df["avg_views"]      = display_df["avg_views"].apply(lambda x: f"{int(x):,}")
    display_df["total_views"]    = display_df["total_views"].apply(lambda x: f"{int(x):,}")
    display_df["avg_engagement"] = display_df["avg_engagement"].apply(lambda x: f"{x:.2f}%")
    display_df.columns = ["Category", "Videos", "Total Views", "Avg Views", "Avg Likes", "Avg Engagement", "Total Comments"]
    st.dataframe(display_df[["Category", "Videos", "Total Views", "Avg Views", "Avg Engagement"]], 
                 use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure MySQL is running and the pipeline has been executed.")


