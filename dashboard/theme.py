import streamlit as st

# Brutalist Yellow and Black Non-Gradient Scale Theme
COMMON_CSS_DARK = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@700;900&family=JetBrains+Mono:wght@700;900&display=swap');

html, body, [class*="css"], .stApp { 
    font-family: 'Google Sans', 'Inter', system-ui, sans-serif !important; 
    background-color: #000000 !important; 
    color: #FFFFFF !important; 
}
.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown li, .stMarkdown span, label, .stWidgetLabel { color: #FFFFFF !important; }
.stCheckbox label span, .stRadio label span, .stSelectbox label span, [data-testid="stRadio"] label *, [data-testid="stCheckbox"] label *, [data-testid="stSelectbox"] label * { color: #FFFFFF !important; }
.lb-rank, .stat, .hero-sub { color: #FFFFFF !important; }

/* Base App Background */
.stApp { background-color: #000000 !important; }

/* Sidebar */
[data-testid="stSidebar"] { 
    background-color: #0A0A0A !important; 
    border-right: 2px solid #FFD600 !important; 
}
[data-testid="stSidebar"] * { color: #CCCCCC !important; }
[data-testid="stSidebarNav"] span { 
    font-size: 0.85rem !important; 
    text-transform: uppercase !important; 
    letter-spacing: 0.8px; 
    font-weight: 900; 
    color: #FFFFFF !important;
}
[data-testid="stSidebarNav"] a {
    border-radius: 0px !important;
    border: 2px solid transparent !important;
    transition: all 0.2s !important;
    padding-left: 12px !important;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #111111 !important;
    border-color: #FFD600 !important;
    transform: translateX(4px) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #FFD600 !important;
    border-color: #FFD600 !important;
    box-shadow: 4px 4px 0px rgba(255, 214, 0, 0.3) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] * {
    color: #000000 !important;
}

/* Buttons */
div[data-testid="stButton"] button, [data-testid="baseButton-secondary"] { background: #FFFFFF !important; border: 2px solid #FFD600 !important; border-radius: 0px !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
div[data-testid="stButton"] button *, [data-testid="baseButton-secondary"] * { color: #000000 !important; font-weight: 900 !important; text-transform: uppercase; }
div[data-testid="stButton"] button:hover, div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus, [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-secondary"]:active, [data-testid="baseButton-secondary"]:focus { background: #FFD600 !important; border-color: #FFD600 !important; transform: translateY(-4px) scale(1.02) !important; box-shadow: 6px 6px 0px rgba(255, 214, 0, 0.3) !important; outline: none !important; }
div[data-testid="stButton"] button:hover *, div[data-testid="stButton"] button:active *, div[data-testid="stButton"] button:focus *, [data-testid="baseButton-secondary"]:hover *, [data-testid="baseButton-secondary"]:active *, [data-testid="baseButton-secondary"]:focus * { color: #000000 !important; }

/* Metrics */
[data-testid="metric-container"] { 
    background: #111111 !important; 
    border: 2px solid #333333 !important; 
    border-radius: 0px !important; 
    padding: 16px 20px !important; 
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px) !important;
    background: #FFD600 !important;
    border-color: #FFD600 !important;
    box-shadow: 6px 6px 0px rgba(255, 214, 0, 0.4) !important;
}
[data-testid="metric-container"]:hover * { color: #000000 !important; }
[data-testid="stMetricValue"] { 
    color: #FFD600 !important; 
    font-family: 'JetBrains Mono', monospace !important; 
    font-weight: 900 !important; 
    font-size: 1.8rem !important;
}

/* DataFrames */
.stDataFrame { 
    border-radius: 0px !important; 
    border: 2px solid #333333 !important; 
    font-size: 0.85rem !important;
}

/* Inputs & Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 2px solid #333333 !important; padding: 0 !important; gap: 24px !important; }
.stTabs [data-baseweb="tab"] * { color: #CCCCCC !important; font-weight: 900 !important; text-transform: uppercase; }
.stTabs [data-baseweb="tab"] { border-radius: 0 !important; padding: 10px 0 !important; border: none !important; }
.stTabs [aria-selected="true"] * { color: #FFD600 !important; }
.stTabs [aria-selected="true"] { border-bottom: 4px solid #FFD600 !important; background: transparent !important; }
.stTextInput input, .stSelectbox > div > div { background: #111111 !important; border: 2px solid #333333 !important; color: #FFFFFF !important; border-radius: 0px !important; font-weight: 700 !important; }
.stTextInput input:focus, .stSelectbox > div > div:focus { border-color: #FFD600 !important; box-shadow: 4px 4px 0px rgba(255, 214, 0, 0.2) !important; }

/* Custom UI Components */
@keyframes antigravFade { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes badgeFloat { 0%, 100% { transform: translateY(0); box-shadow: 2px 2px 0px #000000; } 50% { transform: translateY(-4px); box-shadow: 4px 4px 0px rgba(255,214,0,0.4); } }
@keyframes pulseGlow { 0% { box-shadow: 4px 4px 0px rgba(255, 214, 0, 0.2); } 100% { box-shadow: 8px 8px 0px rgba(255, 214, 0, 0.4); } }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }
@keyframes slideIn { 0% { transform: translateX(-30px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }
@keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

.hero { 
    background: #000000; 
    border: 4px solid #FFD600; 
    border-radius: 0px; 
    padding: 40px; 
    margin-bottom: 32px; 
    text-align: center; 
    animation: antigravFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards, pulseGlow 4s alternate infinite;
    box-shadow: 8px 8px 0px rgba(255,214,0,0.2);
}
.hero-title { 
    font-size: 2.8rem; 
    font-weight: 900; 
    color: #FFD600; 
    margin: 0 0 12px 0; 
    letter-spacing: -0.5px;
    text-transform: uppercase;
}
.hero-sub { color: #CCCCCC; font-size: 1.1rem; margin: 0; font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.badge { display: inline-block; border: 2px solid #FFD600; background: #000000; color: #FFD600; border-radius: 0px; padding: 4px 10px; font-size: 0.75rem; margin-right: 8px; font-weight: 900; text-transform: uppercase; animation: badgeFloat 4s ease-in-out infinite; box-shadow: 2px 2px 0px #000000; }
.badge:nth-child(even) { animation-delay: 1s; }
.badge:nth-child(3n) { animation-delay: 2s; }
.badge-live { background: #FFD600 !important; color: #000000 !important; }
.badge-live * { color: #000000 !important; }
.live-dot { display: inline-block; width: 6px; height: 6px; background: #000000 !important; border-radius: 0px; animation: blink 1.5s infinite; margin-right: 4px; vertical-align: middle; }

.sh { font-size: 1.35rem; font-weight: 900; color: #FFD600; border-bottom: 4px solid #333333; padding-bottom: 12px; margin: 32px 0 20px 0; animation: slideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; text-transform: uppercase; letter-spacing: 1px; }
.sh span { color: #FFD600 !important; }

/* KPI Cards */
.kpi { border-radius: 0px; padding: 24px; text-align: left; background: #000000; border: 2px solid #FFD600; box-shadow: 4px 4px 0px rgba(255,214,0,0.2); margin-bottom: 16px; transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s, border-color 0.3s; animation: antigravFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards, badgeFloat 6s ease-in-out infinite; }
.kpi:hover { background: #FFD600 !important; border-color: #FFD600 !important; box-shadow: 8px 8px 0px rgba(255, 214, 0, 0.4) !important; animation-play-state: paused !important; }
.kpi:hover * { color: #000000 !important; }
.kpi-val { font-size: 2rem; font-weight: 900; color: #FFD600; margin: 8px 0; font-family: 'JetBrains Mono', monospace; }
.kpi-label { font-size: 0.85rem; font-weight: 900; color: #FFFFFF; text-transform: uppercase; letter-spacing: 1px; }

/* Cards & Lists */
.card, .res-card, .vid-card { background: #000000; border: 2px solid #333333; border-radius: 0px; padding: 20px; margin-bottom: 16px; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); animation: antigravFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; box-shadow: 4px 4px 0px rgba(0,0,0,0.5); }
.card:hover, .res-card:hover, .vid-card:hover { background: #FFD600 !important; border-color: #FFD600 !important; box-shadow: 8px 8px 0px rgba(255, 214, 0, 0.4) !important; }
.card:hover *, .res-card:hover *, .vid-card:hover * { color: #000000 !important; border-color: #000000 !important; }
.card:hover .tag, .res-card:hover .tag { background: #000000 !important; color: #FFD600 !important; }
.tag { display: inline-block; padding: 2px 8px; font-size: 0.75rem; border-radius: 0px; background: #111111; border: 1px solid #333333; color: #CCCCCC; margin-right: 6px; text-transform: uppercase; font-weight: 900; }
.stat { color: #AAAAAA !important; font-size: 0.85rem; margin-right: 16px; text-transform: uppercase; font-weight: 700; }
.stat b { color: #FFD600 !important; font-family: 'JetBrains Mono', monospace; font-weight: 900; }
.hl { font-weight: 900; background: #FFD600 !important; color: #000000 !important; padding: 0 4px; border-radius: 0px; }
.hl * { color: #000000 !important; }

/* Components */
.ticker { background: #000000; border: 2px solid #333333; border-left: 6px solid #FFD600; border-radius: 0px; padding: 14px 24px; margin-bottom: 24px; box-shadow: 4px 4px 0px rgba(0,0,0,0.5); }
.ticker-scroll { display: inline-flex; gap: 48px; animation: tickerScroll 20s linear infinite; }
.ticker-scroll:hover { animation-play-state: paused; }
.ticker-item { white-space: nowrap; font-size: 0.85rem; color: #FFFFFF !important; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
.ticker-lbl { color: #888888 !important; text-transform: uppercase; font-weight: 900; }
.ticker-val { font-weight: 900; color: #000000 !important; background: #FFD600 !important; padding: 0 6px; }
.ticker-val * { color: #000000 !important; }

.lb { display: flex; align-items: center; gap: 16px; background: #111111; border: 2px solid #333333; border-radius: 0px; padding: 14px; margin-bottom: 10px; transition: all 0.2s; }
.lb:hover { border-color: #FFD600; transform: translateX(4px); box-shadow: -4px 4px 0px rgba(255,214,0,0.2); }
.lb-rank { font-size: 1rem; font-weight: 900; width: 30px; color: #666666; font-family: 'JetBrains Mono', monospace; }
.lb-name { flex: 1; color: #FFFFFF; font-weight: 900; font-size: 0.95rem; text-transform: uppercase; }
.lb-bg { flex: 2; background: #222222; border-radius: 0px; height: 12px; overflow: hidden; border: 1px solid #444444; }
.lb-fill { height: 100%; background: #FFD600; border-radius: 0px; border-right: 2px solid #000000; }
.lb-val { font-size: 0.85rem; font-weight: 900; color: #FFD600; width: 60px; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* Comments */
.cmt { border-radius: 0px; padding: 16px; margin-bottom: 12px; border: 2px solid #333333; background: #111111; box-shadow: 2px 2px 0px rgba(0,0,0,0.5); }
.cmt-pos { border-left: 6px solid #00E676; }
.cmt-neg { border-left: 6px solid #FF1744; }
.cmt-neu { border-left: 6px solid #FFD600; }

/* Misc */
.insight { background: #000000; border: 2px solid #333333; border-left: 6px solid #FFD600; padding: 16px 20px; color: #FFFFFF; font-size: 0.95rem; margin: 16px 0; border-radius: 0px; font-family: 'JetBrains Mono', monospace; box-shadow: 4px 4px 0px rgba(0,0,0,0.5); font-weight: 700; text-transform: uppercase; }
.mom { border: 2px solid #333333; background: #111111; border-radius: 0px; padding: 16px; margin-bottom: 10px; box-shadow: 2px 2px 0px rgba(0,0,0,0.5); transition: border-color 0.2s; }
.mom:hover { border-color: #FFD600; }
.mom-name { color: #FFFFFF; font-weight: 900; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; }
.mom-bar { height: 100%; background: #FFD600; border-radius: 0px; border-right: 2px solid #000000; }

/* GLOBAL SMOOTHING & HOVERS (DARK) */
.kpi:hover, .card:hover, .res-card:hover, .vid-card:hover, div[data-testid="stButton"] button:hover, [data-testid="baseButton-secondary"]:hover, [data-testid="metric-container"]:hover { transform: translateY(-8px) scale(1.02) !important; }
.kpi:hover *, .card:hover *, .res-card:hover *, .vid-card:hover *, [data-testid="metric-container"]:hover * { color: #000000 !important; border-color: #000000 !important; }
* { transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.6s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.4s ease, background-color 0.4s ease !important; }
/* FORCE BLACK TEXT INSIDE YELLOW SPANS (Overrides .stMarkdown span) */
.stMarkdown .badge-live, .stMarkdown .badge-live *,
.stMarkdown .hl, .stMarkdown .hl *,
.stMarkdown .ticker-val, .stMarkdown .ticker-val * {
    color: #000000 !important;
}

/* FIX PLOTLY TOOLTIPS (Disable CSS transitions on SVG elements calculating positions via JS) */
.js-plotly-plot * {
    transition: none !important;
}
</style>
"""

COMMON_CSS_LIGHT = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@700;900&family=JetBrains+Mono:wght@700;900&display=swap');

html, body, [class*="css"], .stApp { 
    font-family: 'Google Sans', 'Inter', system-ui, sans-serif !important; 
    background-color: #FFFFFF !important; 
    color: #000000 !important; 
}
.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown li, .stWidgetLabel { color: #000000 !important; }
.stCheckbox label span, .stRadio label span, .stSelectbox label span, .stMarkdown span, label, [data-testid="stRadio"] label *, [data-testid="stCheckbox"] label *, [data-testid="stSelectbox"] label * { color: #000000 !important; }
.lb-rank, .stat, .hero-sub, .ticker-lbl { color: #000000 !important; }

/* Base App Background */
.stApp { background-color: #FFFFFF !important; }

/* Sidebar */
[data-testid="stSidebar"] { 
    background-color: #F0F0F0 !important; 
    border-right: 4px solid #000000 !important; 
}
[data-testid="stSidebar"] * { color: #000000 !important; }
[data-testid="stSidebarNav"] span { 
    font-size: 0.82rem !important; 
    text-transform: uppercase !important; 
    letter-spacing: 0.8px; 
    font-weight: 900; 
    color: #000000 !important;
}
[data-testid="stSidebarNav"] a {
    border-radius: 0px !important;
    border: 2px solid transparent !important;
    transition: all 0.2s !important;
    padding-left: 12px !important;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #FFFFFF !important;
    border-color: #000000 !important;
    transform: translateX(4px) !important;
    box-shadow: 4px 4px 0px #FFD600 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #FFD600 !important;
    border-color: #000000 !important;
    box-shadow: 4px 4px 0px #000000 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] * {
    color: #000000 !important;
}

/* Buttons */
div[data-testid="stButton"] button, [data-testid="baseButton-secondary"] { background: #FFFFFF !important; border: 2px solid #000000 !important; border-radius: 0px !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 4px 4px 0px rgba(0,0,0,0.1) !important; }
div[data-testid="stButton"] button *, [data-testid="baseButton-secondary"] * { color: #000000 !important; font-weight: 900 !important; text-transform: uppercase; }
div[data-testid="stButton"] button:hover, div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus, [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-secondary"]:active, [data-testid="baseButton-secondary"]:focus { 
    background: #FFD600 !important; 
    border-color: #000000 !important; 
    transform: translateY(-4px) !important;
    box-shadow: 6px 6px 0px #FFD600 !important;
    outline: none !important;
}
div[data-testid="stButton"] button:hover *, div[data-testid="stButton"] button:active *, div[data-testid="stButton"] button:focus *, [data-testid="baseButton-secondary"]:hover *, [data-testid="baseButton-secondary"]:active *, [data-testid="baseButton-secondary"]:focus * { color: #000000 !important; }

/* Metrics */
[data-testid="metric-container"] { background: #FFFFFF !important; border: 3px solid #000000 !important; border-radius: 0px !important; padding: 16px 20px !important; transition: transform 0.3s ease, box-shadow 0.3s ease !important; box-shadow: 4px 4px 0px #000000 !important; }
[data-testid="metric-container"]:hover { transform: translateY(-4px) !important; background: #FFD600 !important; border-color: #000000 !important; box-shadow: 8px 8px 0px #000000 !important; }
[data-testid="metric-container"]:hover * { color: #000000 !important; }
[data-testid="stMetricValue"] { color: #000000 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important; font-size: 1.8rem !important; }

/* DataFrames */
.stDataFrame { border-radius: 0px !important; border: 3px solid #000000 !important; font-size: 0.85rem !important; box-shadow: 4px 4px 0px #000000 !important; }

/* Inputs & Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 3px solid #000000 !important; padding: 0 !important; gap: 24px !important; }
.stTabs [data-baseweb="tab"] * { color: #333333 !important; font-weight: 900 !important; text-transform: uppercase; }
.stTabs [data-baseweb="tab"] { border-radius: 0 !important; padding: 10px 0 !important; border: none !important; }
.stTabs [aria-selected="true"] * { color: #000000 !important; }
.stTabs [aria-selected="true"] { border-bottom: 5px solid #FFD600 !important; background: transparent !important; }
.stTextInput input, .stSelectbox > div > div { background: #FFFFFF !important; border: 3px solid #000000 !important; color: #000000 !important; border-radius: 0px !important; font-weight: 900 !important; box-shadow: 4px 4px 0px #000000 !important; }
.stTextInput input:focus, .stSelectbox > div > div:focus { border-color: #000000 !important; box-shadow: 6px 6px 0px #FFD600 !important; }

/* Custom UI Components */
@keyframes antigravFade { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes badgeFloat { 0%, 100% { transform: translateY(0); box-shadow: 2px 2px 0px #000; } 50% { transform: translateY(-4px); box-shadow: 4px 4px 0px #000; } }
@keyframes pulseGlowLight { 0% { box-shadow: 4px 4px 0px rgba(0,0,0,1); } 100% { box-shadow: 8px 8px 0px #FFD600; } }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }
@keyframes slideIn { 0% { transform: translateX(-30px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }
@keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

.hero { background: #FFFFFF; border: 5px solid #000000; border-radius: 0px; padding: 40px; margin-bottom: 32px; text-align: center; animation: antigravFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards, pulseGlowLight 4s alternate infinite; box-shadow: 8px 8px 0px #000000; }
.hero-title { font-size: 2.8rem; font-weight: 900; color: #000000; margin: 0 0 12px 0; letter-spacing: -0.5px; text-transform: uppercase; }
.hero-sub { color: #000000; font-size: 1.1rem; margin: 0; font-family: 'JetBrains Mono', monospace; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; }
.badge { display: inline-block; border: 3px solid #000000; background: #FFFFFF; color: #000000; border-radius: 0px; padding: 4px 10px; font-size: 0.75rem; margin-right: 8px; font-weight: 900; text-transform: uppercase; animation: badgeFloat 4s ease-in-out infinite; box-shadow: 2px 2px 0px #000000; }
.badge:nth-child(even) { animation-delay: 1s; }
.badge:nth-child(3n) { animation-delay: 2s; }
.badge-live { background: #FFD600 !important; color: #000000 !important; border-color: #000000 !important; }
.badge-live * { color: #000000 !important; }
.live-dot { display: inline-block; width: 6px; height: 6px; background: #000000 !important; border-radius: 0px; animation: blink 1.5s infinite; margin-right: 4px; vertical-align: middle; }

.sh { font-size: 1.35rem; font-weight: 900; color: #000000; border-bottom: 4px solid #000000; padding-bottom: 12px; margin: 32px 0 20px 0; animation: slideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; text-transform: uppercase; letter-spacing: 1px; }
.sh span { color: #000000 !important; }

/* KPI Cards */
.kpi { border-radius: 0px; padding: 24px; text-align: left; background: #FFFFFF; border: 3px solid #000000; box-shadow: 4px 4px 0px #000000; margin-bottom: 16px; transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s, border-color 0.3s; animation: antigravFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards, badgeFloat 6s ease-in-out infinite; }
.kpi:hover { background: #FFD600 !important; border-color: #000000 !important; box-shadow: 8px 8px 0px #000000 !important; animation-play-state: paused !important; }
.kpi:hover * { color: #000000 !important; }
.kpi-val { font-size: 2rem; font-weight: 900; color: #000000; margin: 8px 0; font-family: 'JetBrains Mono', monospace; }
.kpi-label { font-size: 0.85rem; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 1px; }

/* Cards & Lists */
.card, .res-card, .vid-card { background: #FFFFFF; border: 3px solid #000000; box-shadow: 4px 4px 0px #000000; border-radius: 0px; padding: 20px; margin-bottom: 16px; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); animation: antigravFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.card:hover, .res-card:hover, .vid-card:hover { background: #FFD600 !important; border-color: #000000 !important; box-shadow: 8px 8px 0px #000000 !important; }
.card:hover *, .res-card:hover *, .vid-card:hover * { color: #000000 !important; border-color: #000000 !important; }
.card:hover .tag, .res-card:hover .tag { background: #000000 !important; color: #FFD600 !important; }
.tag { display: inline-block; padding: 2px 8px; font-size: 0.75rem; border-radius: 0px; background: #E0E0E0; border: 1px solid #000000; color: #000000; margin-right: 6px; font-weight: 900; text-transform: uppercase; }
.stat { color: #000000; font-size: 0.85rem; margin-right: 16px; text-transform: uppercase; font-weight: 700; }
.stat b { color: #000000; font-family: 'JetBrains Mono', monospace; font-weight: 900; }
.hl { font-weight: 900; background: #FFD600 !important; color: #000000 !important; padding: 0 4px; border-radius: 0px; border: 1px solid #000000; }
.hl * { color: #000000 !important; }

/* Components */
.ticker { background: #FFFFFF; border: 3px solid #000000; border-left: 8px solid #FFD600; border-radius: 0px; padding: 14px 24px; margin-bottom: 24px; box-shadow: 4px 4px 0px #000000; }
.ticker-scroll { display: inline-flex; gap: 48px; animation: tickerScroll 20s linear infinite; }
.ticker-scroll:hover { animation-play-state: paused; }
.ticker-item { white-space: nowrap; font-size: 0.85rem; color: #000000; font-family: 'JetBrains Mono', monospace; font-weight: 900; }
.ticker-lbl { color: #000000; text-transform: uppercase; }
.ticker-val { font-weight: 900; color: #000000 !important; background: #FFD600 !important; padding: 0 6px; border: 1px solid #000000; }
.ticker-val * { color: #000000 !important; }

.lb { display: flex; align-items: center; gap: 16px; background: #FFFFFF; border: 3px solid #000000; border-radius: 0px; padding: 14px; margin-bottom: 10px; box-shadow: 2px 2px 0px #000000; transition: all 0.2s; }
.lb:hover { border-color: #000000; transform: translateX(4px); box-shadow: -4px 4px 0px #FFD600; }
.lb-rank { font-size: 1rem; font-weight: 900; width: 30px; color: #000000; font-family: 'JetBrains Mono', monospace; }
.lb-name { flex: 1; color: #000000; font-weight: 900; font-size: 0.95rem; text-transform: uppercase; }
.lb-bg { flex: 2; background: #E0E0E0; border-radius: 0px; height: 12px; overflow: hidden; border: 1px solid #000000; }
.lb-fill { height: 100%; background: #FFD600; border-radius: 0px; border-right: 2px solid #000000; }
.lb-val { font-size: 0.85rem; font-weight: 900; color: #000000; width: 60px; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* Comments */
.cmt { border-radius: 0px; padding: 16px; margin-bottom: 12px; border: 3px solid #000000; background: #FFFFFF; box-shadow: 2px 2px 0px #000000; }
.cmt-pos { border-left: 8px solid #00E676; }
.cmt-neg { border-left: 8px solid #FF1744; }
.cmt-neu { border-left: 8px solid #FFD600; }

/* Misc */
.insight { background: #FFFFFF; border: 3px solid #000000; border-left: 8px solid #FFD600; padding: 16px 20px; color: #000000; font-size: 0.95rem; margin: 16px 0; border-radius: 0px; font-family: 'JetBrains Mono', monospace; box-shadow: 4px 4px 0px #000000; font-weight: 900; text-transform: uppercase; }
.mom { border: 3px solid #000000; background: #FFFFFF; border-radius: 0px; padding: 16px; margin-bottom: 10px; box-shadow: 2px 2px 0px #000000; transition: border-color 0.2s; }
.mom:hover { border-color: #000000; box-shadow: 4px 4px 0px #FFD600; }
.mom-name { color: #000000; font-weight: 900; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; }
.mom-bar { height: 100%; background: #FFD600; border-radius: 0px; border-right: 2px solid #000000; }

/* GLOBAL SMOOTHING (LIGHT) */
.kpi:hover, .card:hover, .res-card:hover, .vid-card:hover, div[data-testid="stButton"] button:hover, [data-testid="baseButton-secondary"]:hover, [data-testid="metric-container"]:hover { transform: translateY(-8px) scale(1.02) !important; }
.kpi:hover *, .card:hover *, .res-card:hover *, .vid-card:hover *, [data-testid="metric-container"]:hover * { color: #000000 !important; border-color: #000000 !important; }
* { transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.6s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.4s ease, background-color 0.4s ease !important; }
/* FORCE BLACK TEXT INSIDE YELLOW SPANS (Overrides .stMarkdown span) */
.stMarkdown .badge-live, .stMarkdown .badge-live *,
.stMarkdown .hl, .stMarkdown .hl *,
.stMarkdown .ticker-val, .stMarkdown .ticker-val * {
    color: #000000 !important;
}

/* FIX PLOTLY TOOLTIPS (Disable CSS transitions on SVG elements calculating positions via JS) */
.js-plotly-plot * {
    transition: none !important;
}
</style>
"""

PLOTLY_THEME_DARK = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#FFFFFF", "family": "Google Sans"},
    "margin": {"l": 10, "r": 10, "t": 36, "b": 10},
}
PLOTLY_THEME_LIGHT = {
    "template": "plotly_white",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#000000", "family": "Google Sans"},
    "margin": {"l": 10, "r": 10, "t": 36, "b": 10},
}

# Strict High Contrast Brutalist Colors
COLOR_SEQ = ["#FFD600", "#00E676", "#FF1744", "#00B0FF", "#D500F9", "#FF9100", "#FFFFFF"]

GRAD = {
    "purple_cyan":  ["#FFD600", "#FFD600"],
    "cyan_pink":    ["#000000", "#000000"],
    "pink_orange":  ["#FFD600", "#FFD600"],
    "green_cyan":   ["#0A0A0A", "#0A0A0A"],
    "orange_yellow":["#FFD600", "#000000"],
    "full":         ["#FFD600", "#000000", "#FFD600", "#000000"],
}

def get_plotly_theme():
    """Return a fresh Plotly layout dict matching the current theme session state."""
    theme = st.session_state.get("theme", "Dark")
    if theme == "Dark":
        return dict(PLOTLY_THEME_DARK)
    return dict(PLOTLY_THEME_LIGHT)

# Backwards-compat mutable dict — updated by inject_css()
PLOTLY_THEME = {}

def inject_css():
    theme = st.session_state.get("theme", "Dark")
    if theme == "Dark":
        st.markdown(COMMON_CSS_DARK, unsafe_allow_html=True)
        PLOTLY_THEME.clear()
        PLOTLY_THEME.update(PLOTLY_THEME_DARK)
    else:
        st.markdown(COMMON_CSS_LIGHT, unsafe_allow_html=True)
        PLOTLY_THEME.clear()
        PLOTLY_THEME.update(PLOTLY_THEME_LIGHT)

def render_theme_toggle():
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Theme")
    with col2:
        new_theme = st.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, label_visibility="collapsed")
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

def get_theme_colors():
    """Return a dict of key theme-aware CSS colors for use in inline styles."""
    is_dark = st.session_state.get("theme", "Dark") == "Dark"
    return {
        "bg":        "#000000" if is_dark else "#FFFFFF",
        "bg_card":   "#111111" if is_dark else "#F5F5F5",
        "text":      "#FFFFFF" if is_dark else "#000000",
        "text_muted":"#CCCCCC" if is_dark else "#333333",
        "accent":    "#FFD600",
        "border":    "#333333" if is_dark else "#000000",
        "shadow":    "rgba(255,214,0,0.2)" if is_dark else "#000000",
    }
