import streamlit as st
import pandas as pd
import re
from sqlalchemy import text
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_theme_colors

st.set_page_config(page_title="Keyword Search | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Comment Search</div><div class="hero-sub">Find Keywords & Sentiments</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()

def highlight(txt, keywords):
    for k in keywords:
        if k.strip():
            txt = re.sub(f"(?i)({re.escape(k.strip())})", r'<span class="hl">\1</span>', txt)
    return txt

st.markdown('<div class="sh"><span> Search Filters</span></div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
query = c1.text_input("Enter keyword(s) to search comments...", key="q")
sentiment_filter = c2.selectbox("Sentiment", ["All", "Positive", "Negative", "Neutral"])

if query:
    q_str = f"%{query}%"
    sql = """
    SELECT c.comment_text, c.author_name, c.sentiment, c.polarity, v.title as video_title
    FROM processed_comments c JOIN processed_videos v ON c.video_id = v.video_id 
    WHERE c.comment_text LIKE :q
    """
    if sentiment_filter != "All":
        sql += " AND c.sentiment = :s"
    
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params={"q":q_str, "s":sentiment_filter})
        
    if df.empty:
        st.warning("No comments matched your search.")
    else:
        st.markdown(f'<div class="sh"><span> Results ({len(df)})</span></div>', unsafe_allow_html=True)
        s_color = {"Positive":"#00E676", "Negative":"#FF1744", "Neutral":"#FFD600"}
        keywords = query.split()
        for _, row in df.head(50).iterrows():
            text_hl = highlight(str(row.get("comment_text",""))[:300], keywords)
            sent = row.get("sentiment","Neutral")
            color = s_color.get(sent,"#FFD600")
            polar = float(row.get("polarity",0))
            bar_w = int((polar+1)/2*100)
            _tc_s = get_theme_colors()
            st.markdown(f'''<div class="res-card" style="border-left:8px solid {color}">
                <span style="font-size:0.85rem; font-weight:700; text-transform:uppercase;color:{_tc_s['text_muted']}"> {str(row.get('video_title',''))[:60]}</span><br>
                <b style="font-size:1.1rem; text-transform:uppercase;color:{_tc_s['text']}">{row.get('author_name','')}</b>
                <span style="color:{color}; margin-left:8px; font-weight:900; text-transform:uppercase;">● {sent}</span>
                <span style="font-size:0.85rem; font-weight:700;color:{_tc_s['text_muted']}"> (polarity: {polar:+.2f})</span><br><br>
                <span style="font-weight:500; font-size:0.95rem;color:{_tc_s['text']}">{text_hl}</span><br><br>
                <div style="height:8px; background:{_tc_s['bg_card']}; border:1px solid {_tc_s['border']};">
                    <div style="height:100%; width:{bar_w}%; background:{color}; border-right:2px solid {_tc_s['bg']};"></div>
                </div>
            </div>''', unsafe_allow_html=True)
else:
    st.info("Enter a keyword to start searching through YouTube comments.")
