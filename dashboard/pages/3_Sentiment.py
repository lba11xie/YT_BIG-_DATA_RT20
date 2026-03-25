import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db_connector import get_engine
from theme import inject_css, render_theme_toggle, get_plotly_theme, get_theme_colors, COLOR_SEQ

st.set_page_config(page_title="Sentiment | YT BigData", page_icon="", layout="wide")
inject_css()

st.markdown('<div class="hero"><div class="hero-title">Sentiment</div><div class="hero-sub">NLP Analysis of Comments</div></div>', unsafe_allow_html=True)
render_theme_toggle()

engine = get_engine()
df = pd.read_sql("""SELECT v.title as short_title, c.sentiment, c.polarity, c.subjectivity 
                    FROM processed_comments c JOIN processed_videos v ON c.video_id = v.video_id LIMIT 5000""", engine)

if df.empty:
    st.warning("No data found."); st.stop()

df["short_title"] = df["short_title"].apply(lambda x: str(x)[:40] + "...")

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="sh"><span> Comment Sentiment Breakdown</span></div>', unsafe_allow_html=True)
    sentiments = df.groupby("sentiment").agg(cnt=("sentiment","count"), avg_polarity=("polarity","mean")).reset_index()
    fig_donut = px.pie(sentiments, values="cnt", names="sentiment", hole=0.5, color="sentiment", 
                       color_discrete_map={"Positive":"#00E676", "Negative":"#FF1744", "Neutral":"#FFD600"})
    fig_donut.update_layout(height=360, legend=dict(font=dict()), annotations=[dict(text="Sentiment", x=0.5, y=0.5, font_size=16, showarrow=False)], **get_plotly_theme())
    fig_donut.update_traces(marker=dict(line=dict(color=get_plotly_theme().get("font",{}).get("color","#000"), width=3)))
    st.plotly_chart(fig_donut, use_container_width=True, theme=None)
    
    color_map = {"Positive":"#00E676", "Negative":"#FF1744", "Neutral":"#FFD600"}
    for _, row in sentiments.iterrows():
        c = color_map.get(row["sentiment"],"#888")
        total = sentiments["cnt"].sum()
        pct = row['cnt'] / total * 100
        _tc = get_theme_colors()
        st.markdown(f'''<div style="background:{_tc['bg_card']};border:1px solid {c};border-left:4px solid {c};padding:10px 14px;margin-bottom:8px;">
            <span style="color:{c};font-weight:900">{row['sentiment']}</span>
            <span style="color:{_tc['text']};font-size:0.88rem;margin-left:8px">{int(row['cnt']):,} comments ({pct:.1f}%)</span><br>
            <span style="color:{_tc['text_muted']};font-size:0.8rem">Avg polarity: {row['avg_polarity']:.3f}</span>
        </div>''', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="sh"><span> Average Polarity by Video</span></div>', unsafe_allow_html=True)
    by_video = df.groupby("short_title")["polarity"].mean().reset_index().sort_values("polarity", ascending=False).rename(columns={"polarity":"avg_polarity"})
    fig_bar = px.bar(by_video.head(15), x="avg_polarity", y="short_title", orientation="h", color="avg_polarity")
    fig_bar.add_vline(x=0, line_width=2, line_color=get_plotly_theme().get("font",{}).get("color","#000"), line_dash="dash")
    fig_bar.update_layout(height=420, yaxis=dict(autorange="reversed"), coloraxis_colorbar=dict(title="Polarity", tickfont=dict()), coloraxis=dict(colorscale=["#ef4444","#818cf8","#10b981"], cmin=-1, cmax=1), xaxis_title="Avg Polarity", yaxis_title="", **get_plotly_theme())
    fig_bar.update_traces(marker_line_width=0)
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

st.markdown('<div class="sh"><span> Polarity vs Subjectivity</span></div>', unsafe_allow_html=True)
fig_scatter = px.scatter(df, x="polarity", y="subjectivity", color="sentiment", color_discrete_map={"Positive":"#00E676", "Negative":"#FF1744", "Neutral":"#FFD600"}, opacity=0.6)
fig_scatter.update_layout(height=400, xaxis_title="Polarity", yaxis_title="Subjectivity", **get_plotly_theme())
fig_scatter.add_vline(x=0, line_width=1, line_color=get_plotly_theme().get("font",{}).get("color","#000"), line_dash="dash")
st.plotly_chart(fig_scatter, use_container_width=True, theme=None)
