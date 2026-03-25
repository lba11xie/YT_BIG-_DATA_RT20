import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io, re
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, get_theme_colors, COLOR_SEQ
import plotly.express as px

st.set_page_config(page_title="Word Cloud | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Keyword Cloud</div><div class="hero-sub">Title Themes & Frequent Terms</div></div>', unsafe_allow_html=True)
render_theme_toggle()

EXTRA_STOP = {"video", "new", "official", "music", "trailer", "song", "lyric", "video)", "(official"}
def clean_text(t):
    return re.sub(r'[^a-z0-9\s]', '', str(t).lower())

def make_wordcloud(text_series, colormap="plasma"):
    all_text = " ".join(text_series.dropna().apply(clean_text))
    if not all_text.strip(): return None, None
    _tc = get_theme_colors()
    bg_color = _tc["bg"]
    wc = WordCloud(width=1100, height=520, background_color=bg_color, colormap=colormap, stopwords=STOPWORDS | EXTRA_STOP, max_words=160, collocations=False, prefer_horizontal=0.75).generate(all_text)
    fig, ax = plt.subplots(figsize=(12, 5.5))
    fig.patch.set_facecolor(bg_color)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=bg_color)
    plt.close(fig)
    buf.seek(0)
    return buf, wc

engine = get_engine()
df = pd.read_sql("SELECT title, category_name FROM processed_videos", engine)

if df.empty:
    st.warning("No data found."); st.stop()

st.markdown('<div class="sh"><span> Global Title Word Cloud</span></div>', unsafe_allow_html=True)
buf, wc = make_wordcloud(df["title"])
if buf:
    st.image(buf, use_container_width=True)

st.markdown('<div class="sh"><span> Top Words Frequency</span></div>', unsafe_allow_html=True)
if wc:
    freq = wc.words_
    fdf = pd.DataFrame(list(freq.items()), columns=["Word", "Score"]).sort_values("Score", ascending=False).head(20)
    fig = px.bar(fdf, x="Score", y="Word", orientation="h", color="Score", color_continuous_scale=["#FFD600","#00E676","#00B0FF"])
    fig.update_layout(yaxis=dict(autorange="reversed"), height=520, showlegend=False, xaxis_title="Frequency", yaxis_title="", **get_plotly_theme())
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True, theme=None)
