# ============================================================
#  Dashboard Page 4: Word Cloud
# ============================================================
import sys
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io, re
from db.db_connector import get_engine

st.set_page_config(page_title="Word Cloud | YT BigData", page_icon="☁️", layout="wide")

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

st.markdown("# ☁️ Comment Word Cloud")
st.markdown("Most frequent words from **all YouTube comments** in the dataset")
st.markdown("---")

EXTRA_STOPWORDS = {"video", "like", "subscribe", "channel", "youtube", "watch",
                   "please", "know", "one", "will", "good", "great", "also",
                   "comment", "really", "just", "much", "many"}

@st.cache_data(ttl=300)
def load_comments():
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT comment_text, sentiment FROM processed_comments", conn
        )
    return df

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def make_wordcloud(text_series, bg_color="#0f0f1a", colormap="plasma"):
    all_text = " ".join(text_series.dropna().apply(clean_text))
    stopwords = STOPWORDS | EXTRA_STOPWORDS
    wc = WordCloud(
        width=900, height=500,
        background_color=bg_color,
        colormap=colormap,
        stopwords=stopwords,
        max_words=150,
        collocations=False,
        prefer_horizontal=0.7
    ).generate(all_text)
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(bg_color)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=bg_color)
    plt.close(fig)
    buf.seek(0)
    return buf, wc

def get_top_words(text_series, n=20):
    from collections import Counter
    stopwords = STOPWORDS | EXTRA_STOPWORDS
    all_words = []
    for text in text_series.dropna():
        cleaned = clean_text(text)
        words = [w for w in cleaned.split() if len(w) > 3 and w not in stopwords]
        all_words.extend(words)
    counter = Counter(all_words)
    return pd.DataFrame(counter.most_common(n), columns=["word", "count"])

try:
    df = load_comments()

    if df.empty:
        st.info("No data yet. Run `python run_pipeline.py` to collect data.")
        st.stop()

    # Sidebar filter
    sentiment_filter = st.sidebar.selectbox(
        "Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"]
    )
    colormap_choice = st.sidebar.selectbox(
        "Color Theme", ["plasma", "viridis", "cool", "hot", "rainbow"]
    )

    if sentiment_filter != "All":
        filtered = df[df["sentiment"] == sentiment_filter]["comment_text"]
    else:
        filtered = df["comment_text"]

    st.markdown(f'<div class="section-header">☁️ Word Cloud — {sentiment_filter} Comments ({len(filtered):,} total)</div>', unsafe_allow_html=True)

    with st.spinner("Generating word cloud..."):
        wc_buf, wc_obj = make_wordcloud(filtered, colormap=colormap_choice)
    st.image(wc_buf, use_column_width=True)

    # Top words bar chart
    st.markdown('<div class="section-header">📊 Top 20 Most Frequent Words</div>', unsafe_allow_html=True)
    top_words = get_top_words(filtered, 20)
    fig = px.bar(
        top_words, x="count", y="word", orientation="h",
        color="count", color_continuous_scale="Viridis",
        template="plotly_dark",
        labels={"count": "Frequency", "word": "Word"}
    )
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font=dict(color="#e0e0ff", family="Inter"),
        yaxis=dict(autorange="reversed"),
        height=500, margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure MySQL is running and the pipeline has been executed.")


