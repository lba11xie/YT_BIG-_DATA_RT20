# ============================================================
#  Dashboard: app.py
#  Main Streamlit entry point — multi-page dark-themed app
# ============================================================
import sys
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import streamlit as st
import pandas as pd
from db.db_connector import get_engine
import config

# ---- Page Config ----
st.set_page_config(
    page_title="📊 YT Big Data Dashboard",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS (Dark Premium Theme) ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #141428 60%, #0d0d1f 100%); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a3e 0%, #12122b 100%) !important;
    border-right: 1px solid #333;
}
[data-testid="stSidebar"] * { color: #e0e0ff !important; }

/* Metric Cards */
.metric-card {
    background: linear-gradient(145deg, #1e1e4a, #252555);
    border: 1px solid #3a3a7a;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
    animation: fadeIn 0.5s ease;
}
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(99,102,241,0.3); }
.metric-value { font-size: 2.2rem; font-weight: 800; color: #a78bfa; margin: 8px 0; }
.metric-label { font-size: 0.85rem; color: #8888cc; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }

/* Section Headers */
.section-header {
    font-size: 1.4rem; font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 20px 0 10px 0; padding-bottom: 6px;
    border-bottom: 2px solid #2d2d7a;
}

/* Tables */
.stDataFrame { border-radius: 12px !important; }

@keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## 📺 YT Analytics")
    st.markdown("**Big Data Dashboard**")
    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    st.markdown("Use the **Pages** list above the sidebar ↑ to navigate between pages.")
    st.markdown("---")
    st.markdown(f"🌍 Region: **{config.REGION_CODE}**")
    st.markdown("⚙️ Powered by **Pandas + TextBlob**")
    st.markdown("🗄️ Stored in **MySQL**")
    st.markdown("📊 Dashboard: **Streamlit + Plotly**")


# ---- Load Dashboard Stats ----
@st.cache_data(ttl=300)
def load_stats():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            vid_count  = pd.read_sql("SELECT COUNT(*) AS cnt FROM processed_videos",   conn).iloc[0]["cnt"]
            comm_count = pd.read_sql("SELECT COUNT(*) AS cnt FROM processed_comments",  conn).iloc[0]["cnt"]
            top_chan   = pd.read_sql(
                "SELECT channel_name, COUNT(*) AS c FROM processed_videos GROUP BY channel_name ORDER BY c DESC LIMIT 1",
                conn
            ).iloc[0]["channel_name"]
            avg_views  = pd.read_sql("SELECT ROUND(AVG(view_count)) AS avg FROM processed_videos", conn).iloc[0]["avg"]
        return int(vid_count), int(comm_count), top_chan, int(avg_views)
    except Exception as e:
        return 0, 0, "N/A", 0

# ---- HOME PAGE ----
st.markdown("# 📺 YouTube Big Data Analytics")
st.markdown("### Real-Time Trending Video Intelligence — India Region 🇮🇳")
st.markdown("---")

vid_count, comm_count, top_chan, avg_views = load_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Videos</div>
        <div class="metric-value">{vid_count:,}</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Comments</div>
        <div class="metric-value">{comm_count:,}</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Top Channel</div>
        <div class="metric-value" style="font-size:1.1rem">{top_chan}</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Avg Views</div>
        <div class="metric-value">{avg_views:,}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---- Architecture Diagram ----
st.markdown('<div class="section-header">🏗️ Data Pipeline Architecture</div>', unsafe_allow_html=True)
st.markdown("""
```
YouTube API v3
     ↓
📥 Collector (Python)
     ↓
🗄️ MySQL Raw Storage  ←→  📁 CSV / JSON Files
     ↓
⚡ Apache Spark Processing
   ├── Data Cleaning & Deduplication
   ├── Engagement Score Calculation
   └── TextBlob Sentiment Analysis
     ↓
🗄️ MySQL Processed Tables
     ↓
📊 Streamlit Dashboard (This App!)
```
""")

st.markdown('<div class="section-header">📋 Recent Trending Videos</div>', unsafe_allow_html=True)
try:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT title, channel_name, category_name, view_count, like_count, engagement_score "
            "FROM processed_videos ORDER BY view_count DESC LIMIT 10",
            conn
        )
    df["view_count"] = df["view_count"].apply(lambda x: f"{int(x):,}")
    df["like_count"] = df["like_count"].apply(lambda x: f"{int(x):,}")
    df["engagement_score"] = df["engagement_score"].apply(lambda x: f"{x:.2f}%")
    df.columns = ["Title", "Channel", "Category", "Views", "Likes", "Engagement"]
    st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.info("💡 Run the pipeline first to populate data. Use: `python run_pipeline.py`")
    st.error(f"DB Error: {e}")


