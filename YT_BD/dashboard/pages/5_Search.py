# ============================================================
#  Dashboard Page 5: AI-Powered Search Engine (Advanced)
#  Gemini NL → SQL, semantic search, smart insights, auto-suggestions
# ============================================================
import sys
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

import streamlit as st
import pandas as pd
import json
import re
from sqlalchemy import text
from db.db_connector import get_engine
import google.generativeai as genai # type: ignore

# ─── Gemini Config ────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyA-3uFLIi9CynCge2OFJy9Ok78_ieOlrS8"
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL   = "gemini-2.0-flash"

st.set_page_config(page_title="AI Search | YT BigData", page_icon="🔍", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #141428 60%, #0d0d1f 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a3e,#12122b) !important; border-right:1px solid #333; }
[data-testid="stSidebar"] * { color: #e0e0ff !important; }

/* Hero Search */
.search-hero {
  text-align:center; padding:32px 16px 16px 16px;
}
.search-hero h1 {
  font-size:2.4rem; font-weight:800;
  background:linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  margin-bottom:4px;
}
.search-hero p { color:#6666aa; font-size:1rem; margin:0; }

/* Search bar glow */
.stTextInput input {
  background:#1a1a3e !important; color:#e0e0ff !important;
  border:2px solid #3a3a7a !important; border-radius:14px !important;
  font-size:1.1rem !important; padding:14px 18px !important;
  transition:all 0.3s !important;
}
.stTextInput input:focus {
  border-color:#a78bfa !important; box-shadow:0 0 20px rgba(167,139,250,0.3) !important;
}

/* AI badge */
.ai-badge {
  display:inline-flex; align-items:center; gap:6px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  color:#fff; border-radius:20px; padding:4px 14px; font-size:0.82rem;
  font-weight:600; margin-bottom:12px;
}

/* Section header */
.section-header {
  font-size:1.2rem; font-weight:700;
  background:linear-gradient(90deg,#a78bfa,#60a5fa);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  margin:16px 0 10px 0; padding-bottom:5px; border-bottom:2px solid #2d2d7a;
}

/* Result cards */
.result-card {
  background:linear-gradient(145deg,#1e1e4a,#252555);
  border:1px solid #3a3a7a; border-radius:14px;
  padding:14px 18px; margin-bottom:10px; transition:all 0.3s;
}
.result-card:hover { transform:translateY(-3px); box-shadow:0 6px 24px rgba(99,102,241,0.3); }
.tag-pill {
  display:inline-block; background:#2d2d7a; color:#a78bfa;
  border-radius:20px; padding:2px 10px; font-size:0.78rem; margin:2px;
}
.stat-badge { display:inline-block; color:#60a5fa; margin-right:12px; font-size:0.88rem; }
.highlight { background:#3a3a00; color:#fde68a; border-radius:3px; padding:0 3px; }

/* AI Insight box */
.insight-box {
  background:linear-gradient(145deg,#1a1a40,#1f1f50);
  border:1px solid #5b21b6; border-left:4px solid #a78bfa;
  border-radius:14px; padding:18px 22px; margin:16px 0;
  color:#e0e0ff; line-height:1.7; font-size:0.95rem;
}
.insight-box b { color:#a78bfa; }

/* Intent chip */
.intent-chip {
  display:inline-block; background:#1a2a4a; color:#60a5fa;
  border:1px solid #2a5a9a; border-radius:20px;
  padding:3px 12px; font-size:0.8rem; margin-right:6px;
}

/* Suggestion chips */
.sugg-chip {
  display:inline-block; background:#1e1e4a; color:#a78bfa;
  border:1px solid #3a3a7a; border-radius:20px;
  padding:5px 14px; font-size:0.82rem; margin:4px 4px 4px 0;
  cursor:pointer; transition:all 0.2s;
}
.sugg-chip:hover { background:#2a2a6e; transform:translateY(-1px); }

.no-result { text-align:center; color:#6666aa; padding:40px; font-size:1.1rem; }
.mode-tag {
  display:inline-block; font-size:0.75rem; font-weight:700; letter-spacing:0.05em;
  padding:2px 8px; border-radius:6px; margin-left:8px; vertical-align:middle;
}
.mode-ai   { background:#312e81; color:#a78bfa; }
.mode-kw   { background:#1a3a2a; color:#34d399; }
</style>""", unsafe_allow_html=True)

# ─── Engine ───────────────────────────────────────────────────
engine = get_engine()

# ─── Session State ────────────────────────────────────────────
if "ai_search_history" not in st.session_state:
    st.session_state.ai_search_history = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "trigger_query" not in st.session_state:
    st.session_state.trigger_query = ""

# ─── Data Schema Helper ───────────────────────────────────────
DB_SCHEMA = """
Tables available:
1. processed_videos (video_id, title, channel_name, category_name, view_count, like_count,
   comment_count, engagement_score, duration_seconds, thumbnail_url, published_at, processed_at)
2. processed_comments (comment_id, video_id, author_name, comment_text, like_count,
   sentiment, polarity, subjectivity, processed_at)

Columns meaning:
- engagement_score: (likes+comments)/views*100 — higher = more engaging
- sentiment: 'Positive', 'Neutral', or 'Negative'
- polarity: -1.0 (very negative) to 1.0 (very positive)
"""

# ─── Gemini Functions ─────────────────────────────────────────
def gemini_nl_to_sql(user_query: str, actual_categories: list) -> dict:
    """Use Gemini to convert natural language to SQL + extract intent."""
    cat_list_str = ", ".join([f"'{c}'" for c in actual_categories])
    prompt = f"""You are an advanced SQL expert for a YouTube analytics database.

{DB_SCHEMA}

IMPORTANT - The EXACT category_name values in the database are: {cat_list_str}
Always use these exact strings when filtering by category.

User's natural language query: "{user_query}"

Your job:
1. Detect the INTENT: one of [video_search, comment_search, both, analytics, trend]
2. Generate a safe MySQL SELECT query. For videos: SELECT video_id, title, channel_name, category_name, view_count, like_count, comment_count, engagement_score, thumbnail_url FROM processed_videos
3. Identify keywords for text highlighting
4. Write a short search_description (1 line)

RULES:
- Always use LIMIT (max 20 for videos, max 25 for comments)
- Use LIKE '%word%' for partial text matches on title/channel_name/comment_text
- Use = for exact category matches (use exact values from the list above)
- Avoid DROP, DELETE, UPDATE, INSERT, TRUNCATE, tags column
- For "most viewed" / "top" / "popular" → ORDER BY view_count DESC
- For "most liked" / "most likes" → ORDER BY like_count DESC
- For "best engagement" → ORDER BY engagement_score DESC
- For "gaming" → WHERE category_name = 'Gaming'
- For "music" → WHERE category_name = 'Music'
- For "entertainment" → WHERE category_name = 'Entertainment'
- For "positive comments" → WHERE sentiment = 'Positive'
- If no specific filter, just ORDER BY the relevant metric
- Return ONLY valid JSON, no markdown, no code blocks

Return JSON:
{{
  "intent": "video_search|comment_search|both|analytics|trend",
  "video_sql": "SELECT video_id, title, channel_name, category_name, view_count, like_count, comment_count, engagement_score, thumbnail_url FROM processed_videos WHERE ... ORDER BY ... LIMIT 20",
  "comment_sql": "SELECT pc.comment_text, pc.author_name, pc.sentiment, pc.polarity, pc.like_count, pv.title AS video_title FROM processed_comments pc JOIN processed_videos pv ON pc.video_id=pv.video_id WHERE ... ORDER BY pc.like_count DESC LIMIT 25",
  "keywords": ["word1", "word2"],
  "search_description": "Searching for ...",
  "skip_videos": false,
  "skip_comments": false
}}

If intent is only about comments, set skip_videos=true and video_sql=null.
If intent is only about videos, set skip_comments=true.
"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp  = model.generate_content(prompt)
        raw   = resp.text.strip()
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        return json.loads(raw)
    except Exception as e:
        # Fallback: keyword search
        kw = user_query.split()[0] if user_query.split() else user_query
        return {
            "intent": "both",
            "video_sql": f"SELECT video_id, title, channel_name, category_name, view_count, like_count, comment_count, engagement_score, thumbnail_url FROM processed_videos WHERE title LIKE '%{user_query}%' OR channel_name LIKE '%{user_query}%' ORDER BY view_count DESC LIMIT 20",
            "comment_sql": f"SELECT pc.comment_text, pc.author_name, pc.sentiment, pc.polarity, pc.like_count, pv.title AS video_title FROM processed_comments pc JOIN processed_videos pv ON pc.video_id=pv.video_id WHERE pc.comment_text LIKE '%{user_query}%' ORDER BY pc.like_count DESC LIMIT 25",
            "keywords": user_query.split(),
            "search_description": f"Keyword search for '{user_query}'",
            "skip_videos": False,
            "skip_comments": False
        }

@st.cache_data(ttl=60)
def gemini_insights(user_query: str, video_count: int, comment_count: int,
                    top_titles: list, top_cats: list, sentiments: dict) -> str:
    """Generate smart insights about the search results."""
    prompt = f"""You are a YouTube data analyst. A user searched for: "{user_query}"

Results found:
- Videos: {video_count}
- Comments: {comment_count}
- Top video titles: {top_titles[:3]}
- Categories found: {top_cats}
- Comment sentiments: {sentiments}

Write 3-4 bullet point insights (each 1-2 lines) about what these results mean.
Use **bold** for key numbers/names. Be specific, data-driven, and interesting.
Start with "🔍 **AI Insights for '{user_query}':**" then the bullets.
Keep it under 120 words total. No fluff."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp  = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        err = str(e)
        if "quota" in err.lower():
            return f"🔍 Found **{video_count} videos** and **{comment_count} comments** matching your search. _(AI insights unavailable — quota limit reached)_"
        return f"🔍 Found **{video_count} videos** and **{comment_count} comments** for your search."

@st.cache_data(ttl=300)
def gemini_suggestions(context: str) -> list:
    """Generate smart search suggestions based on the database."""
    prompt = f"""Based on this YouTube trending data context: {context}

Generate 8 interesting, varied natural-language search queries a user might type.
Mix different intents: top videos, sentiment, categories, channels, engagement, comments.
Return ONLY a JSON array of 8 strings. No markdown, no explanation.
Example: ["Which gaming videos got the most engagement?", "Show positive comments about music"]"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp  = model.generate_content(prompt)
        raw   = resp.text.strip()
        raw   = re.sub(r"```json\s*|```\s*", "", raw)
        return json.loads(raw)
    except:
        return [
            "Top 10 most viewed videos",
            "Music videos sorted by likes",
            "Show positive comments",
            "Which channel has the most trending videos?",
            "Gaming videos with highest engagement",
            "Entertainment videos sorted by comments",
            "Videos with over 10 million views",
            "Negative comments in Film & Animation"
        ]

def highlight_text(text: str, keywords: list) -> str:
    """Highlight keywords in text."""
    for kw in keywords:
        if kw and len(kw) > 2:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            text = pattern.sub(f'<span class="highlight">{kw}</span>', text)
    return text

def run_sql_safe(sql_query: str, params: dict = None):
    """Run SQL safely, returning empty DataFrame on error."""
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(sql_query), conn, params=params)
    except Exception as e:
        st.error(f"SQL Error: {str(e)[:200]}")
        return pd.DataFrame()

# ─── Load context for suggestions ────────────────────────────
@st.cache_data(ttl=600)
def load_quick_context():
    try:
        cats = pd.read_sql("SELECT category_name, COUNT(*) c FROM processed_videos GROUP BY category_name ORDER BY c DESC LIMIT 5", engine)
        top  = pd.read_sql("SELECT title FROM processed_videos ORDER BY view_count DESC LIMIT 3", engine)
        return f"Categories: {cats['category_name'].tolist()}, Top videos: {top['title'].tolist()}"
    except:
        return "YouTube trending videos in India, Music/Gaming/Entertainment categories"

# ─── UI: Hero Header ─────────────────────────────────────────
st.markdown("""
<div class="search-hero">
  <h1>🔍 AI-Powered Search</h1>
  <p>Natural language search across your YouTube trending data — powered by <b>Google Gemini</b></p>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center"><span class="ai-badge">✨ Gemini AI Active</span></div>', unsafe_allow_html=True)

# ─── Main Search Bar ─────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    default_val = st.session_state.trigger_query or ""
    query = st.text_input(
        "Search Query", placeholder="Try: 'Show me top gaming videos' or 'Positive comments about cricket'...",
        label_visibility="collapsed", key="main_search_query", value=default_val
    )
with col_btn:
    search_btn = st.button("🔍 Search", type="primary", width='stretch')

# Reset trigger
st.session_state.trigger_query = ""

# ─── Sidebar: History & Filters ──────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Search Mode")
    search_mode = st.radio("Search Mode", ["🤖 AI Natural Language", "⌨️ Keyword Only"], index=0, label_visibility="collapsed")

    st.markdown("### ⚙️ Filters")
    try:
        cats = pd.read_sql("SELECT DISTINCT category_name FROM processed_videos ORDER BY category_name", engine)
        cat_list = ["All"] + cats["category_name"].tolist()
    except:
        cat_list = ["All"]
    category_filter  = st.selectbox("Category", cat_list)
    sentiment_filter = st.selectbox("Comment Sentiment", ["All", "Positive", "Neutral", "Negative"])
    sort_by          = st.selectbox("Sort Videos By", ["Views ↓", "Likes ↓", "Engagement ↓", "Comments ↓"])
    max_results      = st.slider("Max Video Results", 5, 20, 10)

    st.markdown("### 📜 Recent Searches")
    if st.session_state.ai_search_history:
        for h in reversed(st.session_state.ai_search_history[-5:]):
            if st.button(f"↩ {h[:35]}...", key=f"hist_{h[:20]}", width='stretch'):
                st.session_state.trigger_query = h
                st.rerun()
    else:
        st.caption("No recent searches yet")

    if st.button("🗑️ Clear History", width='stretch'):
        st.session_state.ai_search_history = []
        st.rerun()

sort_map = {"Views ↓": "view_count", "Likes ↓": "like_count",
            "Engagement ↓": "engagement_score", "Comments ↓": "comment_count"}

# ─── Smart Suggestions (shown when idle) ─────────────────────
if not query and not search_btn:
    st.markdown('<div class="section-header">💡 Try Asking...</div>', unsafe_allow_html=True)
    ctx = load_quick_context()
    suggestions = gemini_suggestions(ctx)
    # Show as clickable chips in a grid
    s_cols = st.columns(2)
    for i, s in enumerate(suggestions):
        with s_cols[i % 2]:
            if st.button(f"🔎 {s}", key=f"sugg_{i}", width='stretch'):
                st.session_state.trigger_query = s
                st.rerun()

    # Popular categories quick browse
    st.markdown('<div class="section-header">🔥 Browse by Category</div>', unsafe_allow_html=True)
    try:
        top_cats = pd.read_sql(
            "SELECT category_name, COUNT(*) AS c, AVG(engagement_score) AS avg_eng FROM processed_videos GROUP BY category_name ORDER BY c DESC LIMIT 8",
            engine)
        c_cols = st.columns(4)
        emojis = ["🎵","🎮","😂","🏏","📰","🎬","📚","🍳","⚡","🌍"]
        for i, (_, row) in enumerate(top_cats.iterrows()):
            with c_cols[i % 4]:
                if st.button(f"{emojis[i%len(emojis)]} {row['category_name']}\n{row['c']} videos",
                             key=f"cat_{i}", width='stretch'):
                    st.session_state.trigger_query = f"Show {row['category_name']} videos sorted by views"
                    st.rerun()
    except:
        pass

# ─── Search Execution ─────────────────────────────────────────
elif query or search_btn:
    q = query.strip()
    if not q:
        st.warning("⚠️ Please enter a search query.")
    else:
        # Save to history
        if q not in st.session_state.ai_search_history:
            st.session_state.ai_search_history.append(q)

        use_ai = "AI" in search_mode

        # Load actual category names for Gemini context
        try:
            actual_cats = pd.read_sql("SELECT DISTINCT category_name FROM processed_videos ORDER BY category_name", engine)["category_name"].tolist()
        except:
            actual_cats = ["Music", "Gaming", "Entertainment", "Film & Animation", "People & Blogs"]

        if use_ai:
            with st.spinner("🤖 Gemini is understanding your query..."):
                result = gemini_nl_to_sql(q, actual_cats)

            intent      = result.get("intent", "both")
            keywords    = result.get("keywords", q.split())
            description = result.get("search_description", f"Searching for '{q}'")
            skip_vids   = result.get("skip_videos", False)
            skip_cmts   = result.get("skip_comments", False)
            video_sql   = result.get("video_sql")
            comment_sql = result.get("comment_sql")

            # Apply sidebar filters on top of AI-generated SQL
            if video_sql and category_filter != "All":
                # Inject category filter if not already in query
                if "category_name" not in video_sql.lower():
                    video_sql = video_sql.replace(
                        "ORDER BY", f"AND category_name = '{category_filter}' ORDER BY"
                    )
            # Limit override
            video_sql = re.sub(r"LIMIT \d+", f"LIMIT {max_results}", video_sql or "")

        else:
            # Keyword-only mode
            keywords    = [q]
            description = f"Keyword search for '{q}'"
            skip_vids   = False
            skip_cmts   = False
            sort_col    = sort_map.get(sort_by, "view_count")
            cat_clause  = f"AND category_name = '{category_filter}'" if category_filter != "All" else ""
            sent_clause = f"AND sentiment = '{sentiment_filter}'" if sentiment_filter != "All" else ""
            video_sql   = f"""SELECT video_id, title, channel_name, category_name,
                               view_count, like_count, comment_count, engagement_score, thumbnail_url
                               FROM processed_videos
                               WHERE (title LIKE '%{q}%' OR channel_name LIKE '%{q}%')
                               {cat_clause} ORDER BY {sort_col} DESC LIMIT {max_results}"""
            comment_sql = f"""SELECT pc.comment_text, pc.author_name, pc.sentiment, pc.polarity, pc.like_count,
                               pv.title AS video_title FROM processed_comments pc
                               JOIN processed_videos pv ON pc.video_id=pv.video_id
                               WHERE pc.comment_text LIKE '%{q}%' {sent_clause}
                               ORDER BY pc.like_count DESC LIMIT 25"""

        # ── Header ──
        mode_tag = '<span class="mode-tag mode-ai">AI</span>' if use_ai else '<span class="mode-tag mode-kw">KEYWORD</span>'
        st.markdown(f'<div class="section-header">Results {mode_tag}: &ldquo;{q}&rdquo;</div>', unsafe_allow_html=True)
        if use_ai:
            st.markdown(f'<span class="intent-chip">Intent: {intent}</span> <span style="color:#666;font-size:0.85rem">{description}</span>', unsafe_allow_html=True)

        # ── Run queries ──
        vdf = run_sql_safe(video_sql) if not skip_vids and video_sql else pd.DataFrame()
        cdf = run_sql_safe(comment_sql) if not skip_cmts and comment_sql else pd.DataFrame()

        # ── Fallback: if AI SQL returned 0 videos, retry with keyword LIKE search ──
        if use_ai and not skip_vids and vdf.empty:
            sort_col_fb = sort_map.get(sort_by, "view_count")
            cat_clause_fb = f"AND category_name = '{category_filter}'" if category_filter != "All" else ""
            fallback_sql = f"""SELECT video_id, title, channel_name, category_name,
                view_count, like_count, comment_count, engagement_score, thumbnail_url
                FROM processed_videos
                WHERE (title LIKE '%{q}%' OR channel_name LIKE '%{q}%'
                    OR category_name LIKE '%{q}%')
                {cat_clause_fb} ORDER BY {sort_col_fb} DESC LIMIT {max_results}"""
            vdf = run_sql_safe(fallback_sql)
            if not vdf.empty:
                st.info("💡 AI query returned no rows — showing keyword fallback results.")

        if use_ai and not skip_cmts and cdf.empty:
            sent_fb = f"AND sentiment = '{sentiment_filter}'" if sentiment_filter != "All" else ""
            fallback_cmt = f"""SELECT pc.comment_text, pc.author_name, pc.sentiment, pc.polarity, pc.like_count,
                pv.title AS video_title FROM processed_comments pc
                JOIN processed_videos pv ON pc.video_id=pv.video_id
                WHERE pc.comment_text LIKE '%{q}%' {sent_fb}
                ORDER BY pc.like_count DESC LIMIT 25"""
            cdf = run_sql_safe(fallback_cmt)

        # ── AI Insights ──
        if use_ai and (not vdf.empty or not cdf.empty):
            with st.spinner("✨ Generating AI insights..."):
                top_titles = vdf["title"].tolist() if not vdf.empty else []
                top_cats   = vdf["category_name"].unique().tolist() if not vdf.empty and "category_name" in vdf.columns else []
                sent_dist  = cdf["sentiment"].value_counts().to_dict() if not cdf.empty and "sentiment" in cdf.columns else {}
                insight    = gemini_insights(q, len(vdf), len(cdf), top_titles, top_cats, sent_dist)
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

        # ── Stats bar ──
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📹 Videos Found", len(vdf))
        m2.metric("💬 Comments Found", len(cdf))
        if not vdf.empty and "view_count" in vdf.columns:
            m3.metric("👁 Total Views", f"{int(vdf['view_count'].sum()):,}")
        if not vdf.empty and "engagement_score" in vdf.columns:
            m4.metric("⚡ Avg Engagement", f"{vdf['engagement_score'].mean():.2f}%")

        st.markdown("---")

        # ── Video Results ──
        if not skip_vids:
            st.markdown(f"#### 🎬 Videos ({len(vdf)} found)")
            if vdf.empty:
                st.markdown('<div class="no-result">😔 No videos found. Try rephrasing your search.</div>', unsafe_allow_html=True)
            else:
                sent_color = {"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#818cf8"}
                for _, row in vdf.iterrows():
                    title_hl = highlight_text(str(row.get("title", "")), keywords)
                    chan_hl  = highlight_text(str(row.get("channel_name", "")), keywords)
                    cat      = row.get("category_name", "")
                    cols     = st.columns([1, 4])
                    with cols[0]:
                        if row.get("thumbnail_url"):
                            st.image(row["thumbnail_url"], width=140)
                    with cols[1]:
                        yt_link = f"https://www.youtube.com/watch?v={row.get('video_id','')}"
                        st.markdown(f"""<div class="result-card">
                            <b style="color:#a78bfa;font-size:1.02rem">{title_hl}</b><br>
                            <span style="color:#60a5fa">📺 {chan_hl}</span>
                            &nbsp;<span class="tag-pill">#{cat}</span><br><br>
                            <span class="stat-badge">👁 {int(row.get('view_count',0)):,}</span>
                            <span class="stat-badge">❤️ {int(row.get('like_count',0)):,}</span>
                            <span class="stat-badge">💬 {int(row.get('comment_count',0)):,}</span>
                            <span class="stat-badge">⚡ {float(row.get('engagement_score',0)):.2f}%</span>
                            <br><a href="{yt_link}" target="_blank" style="color:#818cf8;font-size:0.82rem;text-decoration:none">▶ Open on YouTube</a>
                        </div>""", unsafe_allow_html=True)

        # ── Comment Results ──
        if not skip_cmts:
            st.markdown(f"#### 💬 Comments ({len(cdf)} found)")
            if cdf.empty:
                st.markdown('<div class="no-result">😔 No comments matched your query.</div>', unsafe_allow_html=True)
            else:
                sent_color = {"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#818cf8"}
                for _, row in cdf.iterrows():
                    text_hl = highlight_text(str(row.get("comment_text", ""))[:300], keywords)
                    sent    = row.get("sentiment", "Neutral")
                    color   = sent_color.get(sent, "#818cf8")
                    polar   = float(row.get("polarity", 0))
                    bar_w   = int((polar + 1) / 2 * 100)
                    st.markdown(f"""<div class="result-card" style="border-left:4px solid {color}">
                        <span style="color:#999;font-size:0.82rem">📺 {str(row.get('video_title',''))[:60]}</span><br>
                        <b style="color:#e0e0ff">{row.get('author_name','')}</b>
                        <span style="color:{color};margin-left:8px">● {sent}</span>
                        <span style="color:#888;font-size:0.8rem"> (polarity: {polar:+.2f})</span>
                        <br><br>
                        <span style="color:#ccccee">{text_hl}</span><br><br>
                        <div style="height:4px;background:#2d2d7a;border-radius:4px;overflow:hidden">
                          <div style="height:100%;width:{bar_w}%;background:linear-gradient(90deg,#f87171,#818cf8,#34d399);border-radius:4px"></div>
                        </div>
                        <span style="color:#555;font-size:0.75rem">Sentiment polarity bar</span>
                    </div>""", unsafe_allow_html=True)

        # ── Related Searches ──
        if use_ai:
            st.markdown('<div class="section-header">🔗 Related Searches</div>', unsafe_allow_html=True)
            related_prompt = f'Give 4 related search queries similar to "{q}" for YouTube analytics. Return ONLY a JSON array of 4 strings.'
            try:
                model   = genai.GenerativeModel(GEMINI_MODEL)
                r_resp  = model.generate_content(related_prompt)
                r_raw   = re.sub(r"```json\s*|```\s*", "", r_resp.text.strip())
                related = json.loads(r_raw)
                r_cols  = st.columns(4)
                for i, rel in enumerate(related[:4]):
                    with r_cols[i % 4]:
                        if st.button(f"🔍 {rel[:40]}", key=f"rel_{i}", width='stretch'):
                            st.session_state.trigger_query = rel
                            st.rerun()
            except:
                pass


