# ============================================================
#  Dashboard: app.py  (Colorful UI Overhaul v2)
# ============================================================
import sys
sys.path.insert(0, r"d:\New_UI\YT_BD")

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from db.db_connector import get_engine
import config
from theme import inject_css, render_theme_toggle

st.set_page_config(
    page_title="YT BIG DATA AUDIT RT 2.0",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    render_theme_toggle()
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <div style="font-size:2.4rem;"></div>
        <div style="font-size:1.2rem;font-weight:900;background:inherit;
            ">YT BIG DATA</div>
        <div style="color:inherit;font-size:0.8rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;">AUDIT RT 2.0</div>
    </div>
    <div style="height:1px;background:inherit,transparent);margin:12px 0;"></div>
    """, unsafe_allow_html=True)

    theme_state = st.session_state.get("theme", "Dark")
    c_bg = "transparent"
    c_title = "#FFD600" if theme_state == "Dark" else "#000000"
    c_time = "#FFD600" if theme_state == "Dark" else "#000000"
    c_date = "#CCCCCC" if theme_state == "Dark" else "#000000"
    c_border = "#FFD600" if theme_state == "Dark" else "#000000"
    c_box = "#000000" if theme_state == "Dark" else "#FFFFFF"
    c_shadow = "rgba(255,214,0,0.2)" if theme_state == "Dark" else "#000000"

    st.markdown(f'<div style="background:{c_box};border:3px solid {c_border};border-radius:0px;padding:12px;margin-bottom:14px;box-shadow:4px 4px 0px {c_shadow};transition:all 0.5s cubic-bezier(0.22,1,0.36,1);">', unsafe_allow_html=True)
    components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@700;900&family=JetBrains+Mono:wght@700;900&display=swap');
        body {{ margin:0; padding:0; overflow:hidden; background:{c_bg}; }}
        .clock-container {{ display:flex; flex-direction:column; justify-content:center; }}
        .title {{ color:{c_title}; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:1px; font-family:'Google Sans',sans-serif; margin-bottom:4px; }}
        .time {{ color:{c_time}; font-size:24px; font-weight:900; letter-spacing:1px; font-family:'JetBrains Mono',monospace; margin-bottom:2px; }}
        .date {{ color:{c_date}; font-size:13px; font-family:'Google Sans',sans-serif; font-weight:700; text-transform:uppercase; }}
        </style>
        <div class="clock-container">
            <div class="title">LIVE CLOCK</div>
            <div class="time" id="rt-clock">--:--:--</div>
            <div class="date" id="rt-date">-- --- ----</div>
        </div>
        <script>
        function updateClock() {{
            const now = new Date();
            document.getElementById('rt-clock').innerText = now.toLocaleTimeString('en-GB', {{hour12:false}});
            document.getElementById('rt-date').innerText = now.toLocaleDateString('en-GB', {{day:'numeric', month:'long', year:'numeric'}});
        }}
        setInterval(updateClock, 1000);
        updateClock();
        </script>
    """, height=70)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("####  Config")
    c_config_bg = "#111111" if theme_state == "Dark" else "#F9F9F9"
    c_config_bd = "#333333" if theme_state == "Dark" else "#000000"
    c_config_text = "#FFFFFF" if theme_state == "Dark" else "#000000"
    
    st.markdown(f"""
    <div style="font-size:0.85rem; color:{c_config_text}; font-weight:700; line-height:1.6; background:{c_config_bg}; padding:12px; border:2px solid {c_config_bd}; border-radius:0px; box-shadow:4px 4px 0px {c_config_bd}; transition:all 0.5s cubic-bezier(0.22,1,0.36,1);">
        • Region: <b style="color:inherit">{config.REGION_CODE}</b><br>
        • Database: <b>{config.DB_NAME}</b><br>
        • Target Videos: <b>{config.TOTAL_VIDEOS_TO_FETCH}</b><br>
        • Comments/Vid: <b>{config.COMMENTS_PER_VIDEO}</b><br>
        • Spark Runtime: <b>{config.SPARK_MASTER}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="height:1px;background:inherit,transparent);margin:12px 0;"></div>
    <div style="color:inherit;font-size:0.78rem;">
         Apache Spark · TextBlob NLP<br>
         MySQL · Plotly
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    if st.button(" Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Load Stats ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stats():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            vid_count   = pd.read_sql("SELECT COUNT(*) AS c FROM processed_videos",  conn).iloc[0]["c"]
            comm_count  = pd.read_sql("SELECT COUNT(*) AS c FROM processed_comments", conn).iloc[0]["c"]
            top_chan    = pd.read_sql("SELECT channel_name,COUNT(*) AS c FROM processed_videos GROUP BY channel_name ORDER BY c DESC LIMIT 1", conn).iloc[0]["channel_name"]
            avg_views   = pd.read_sql("SELECT ROUND(AVG(view_count)) AS v FROM processed_videos", conn).iloc[0]["v"]
            total_views = pd.read_sql("SELECT SUM(view_count) AS v FROM processed_videos", conn).iloc[0]["v"]
            avg_eng     = pd.read_sql("SELECT ROUND(AVG(engagement_score),2) AS e FROM processed_videos", conn).iloc[0]["e"]
        return int(vid_count), int(comm_count), top_chan, int(avg_views), int(total_views), float(avg_eng)
    except:
        return 0, 0, "N/A", 0, 0, 0.0

# ── Hero ──────────────────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div class="hero">
  <div class="hero-title"> YT BIG DATA AUDIT RT 2.0</div>
  <div class="hero-sub">Real-Time Trending Video Intelligence · India Region</div>
  <div class="hero-badges">
    <span class="badge badge-live"><span class="live-dot"></span> LIVE DATA PROCESSING</span>
    <span class="badge"> REAL TIME</span>
    <span class="badge"> DASHBOARD</span>
    <span class="badge badge-india"> India Region</span>
    <span style="color:inherit;font-size:0.8rem;align-self:center;">Updated: {now.strftime('%d %b %Y · %H:%M:%S')}</span>
  </div>
</div>
""", unsafe_allow_html=True)

vid_count, comm_count, top_chan, avg_views, total_views, avg_eng = load_stats()

# ── Ticker ────────────────────────────────────────────────────
tv_str = f"{int(total_views/1e6):.1f}M" if total_views >= 1e6 else f"{total_views:,}"
st.markdown(f"""
<div class="ticker" style="overflow: hidden; white-space: nowrap;">
  <div class="ticker-scroll">
      <span class="ticker-item"><span class="ticker-lbl"> Videos: </span><span class="ticker-val">{vid_count:,}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Comments: </span><span class="ticker-val">{comm_count:,}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Total Views: </span><span class="ticker-val">{tv_str}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Avg Engagement: </span><span class="ticker-val">{avg_eng}%</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Top Channel: </span><span class="ticker-val">{top_chan[:30]}</span></span>
      <!-- Duplicate for seamless scroll -->
      <span class="ticker-item"><span class="ticker-lbl"> Videos: </span><span class="ticker-val">{vid_count:,}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Comments: </span><span class="ticker-val">{comm_count:,}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Total Views: </span><span class="ticker-val">{tv_str}</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Avg Engagement: </span><span class="ticker-val">{avg_eng}%</span></span>
      <span class="ticker-item"><span class="ticker-lbl"> Top Channel: </span><span class="ticker-val">{top_chan[:30]}</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards (6 cols, multicolor) ────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
chan_disp = (top_chan[:12]+"…") if len(top_chan) > 12 else top_chan
tv_disp   = f"{int(total_views/1e6):.1f}M" if total_views>=1e6 else f"{total_views:,}"

kpi_data = [
    (c1, "kpi-purple", "", "Total Videos",   f"{vid_count:,}"),
    (c2, "kpi-cyan",   "", "Comments",        f"{comm_count:,}"),
    (c3, "kpi-pink",   "", "Avg Views",       f"{int(avg_views/1e6):.1f}M" if avg_views>=1e6 else f"{avg_views:,}"),
    (c4, "kpi-orange", "", "Total Views",     tv_disp),
    (c5, "kpi-green",  "", "Avg Engagement",  f"{avg_eng}%"),
    (c6, "kpi-yellow", "", "Top Channel",     chan_disp),
]
for col, cls, icon, label, val in kpi_data:
    with col:
        st.markdown(f"""<div class="kpi {cls}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Nav ─────────────────────────────────────────────────
st.markdown('<div class="sh"><span> Quick Navigation</span></div>', unsafe_allow_html=True)
nav_cols = st.columns(7)
nav_items = [
    ("pages/1_Overview.py", "Overview", "Top trending & charts"),
    ("pages/2_Category_Analysis.py", "Categories", "Category breakdown"),
    ("pages/3_Sentiment.py", "Sentiment", "Comment NLP analysis"),
    ("pages/4_WordCloud.py", "WordCloud", "Title keyword cloud"),
    ("pages/5_Search.py", "Search", "Keyword search"),
    ("pages/7_Advanced.py", "Advanced", "Deep analytics"),
    ("pages/8_Trending.py", "Trending", "Viral score board"),
]
for col, (target_page, title, desc) in zip(nav_cols, nav_items):
    with col:
        if st.button(f"{title}", help=desc, use_container_width=True):
            st.switch_page(target_page)

st.markdown("<br>", unsafe_allow_html=True)



# ── Recent Top Videos Table ───────────────────────────────────
st.markdown('<div class="sh"><span> Top 10 Trending Videos Right Now</span></div>', unsafe_allow_html=True)
try:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT video_id, title, channel_name, category_name, view_count, like_count, engagement_score "
            "FROM processed_videos ORDER BY view_count DESC LIMIT 10", conn)
    df["Link"]            = "https://youtube.com/watch?v=" + df["video_id"].astype(str)
    df["ChannelLink"]     = "https://www.youtube.com/results?search_query=" + df["channel_name"].str.replace(" ", "+")
    df["view_count"]      = df["view_count"].apply(lambda x: f"{int(x):,}")
    df["like_count"]      = df["like_count"].apply(lambda x: f"{int(x):,}")
    df["engagement_score"]= df["engagement_score"].apply(lambda x: f"{x:.2f}%")
    df = df[["title", "channel_name", "ChannelLink", "Link", "category_name", "view_count", "like_count", "engagement_score"]]
    df.columns = ["Title","Channel","Search","Watch","Category","Views","Likes","Engagement"]
    
    st.dataframe(df, use_container_width=True, hide_index=True, column_config={
        "Watch": st.column_config.LinkColumn("Watch", display_text="▶ Play"),
        "Search": st.column_config.LinkColumn("Search", display_text="🔍 Channel")
    })
except Exception as e:
    st.info(" Run `python run_pipeline.py` to populate data.")
    st.error(f"DB Error: {e}")


