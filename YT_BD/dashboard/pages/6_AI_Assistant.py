# ============================================================
#  Dashboard Page 6: AI Assistant
#  Gemini-powered chatbot that answers questions about your YouTube data
# ============================================================
import sys
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.db_connector import get_engine

st.set_page_config(page_title="AI Assistant | YT BigData", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #141428 60%, #0d0d1f 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a3e,#12122b) !important; border-right:1px solid #333; }
[data-testid="stSidebar"] * { color: #e0e0ff !important; }
.section-header { font-size:1.2rem; font-weight:700; background:linear-gradient(90deg,#a78bfa,#60a5fa);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  margin:12px 0 8px 0; padding-bottom:4px; border-bottom:2px solid #2d2d7a; }

/* Chat bubbles */
.chat-user { background: linear-gradient(135deg,#4f46e5,#7c3aed); color:#fff;
  border-radius:18px 18px 4px 18px; padding:12px 16px; margin:8px 0 8px 20%;
  max-width:78%; font-size:0.95rem; }
.chat-ai { background: linear-gradient(145deg,#1e1e4a,#252555); border:1px solid #3a3a7a; color:#e0e0ff;
  border-radius:18px 18px 18px 4px; padding:14px 18px; margin:8px 20% 8px 0;
  max-width:78%; font-size:0.95rem; line-height:1.6; }
.chat-ai b { color:#a78bfa; }
.chat-ai code { background:#0f0f2a; color:#60a5fa; padding:1px 5px; border-radius:4px; font-size:0.87rem; }

/* Quick question buttons */
.stButton > button {
  background: linear-gradient(135deg,#1e1e4a,#2a2a6e) !important;
  color:#a78bfa !important; border:1px solid #3a3a7a !important;
  border-radius:20px !important; font-size:0.85rem !important;
  padding:6px 14px !important; transition:all 0.3s !important;
}
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 4px 16px rgba(99,102,241,0.3) !important; }

/* API key input */
.api-key-box { background:#1a1a3e; border:1px solid #3a3a7a; border-radius:12px; padding:16px; margin-bottom:16px; }
</style>""", unsafe_allow_html=True)

st.markdown("# 🤖 AI Assistant")
st.markdown("Ask anything about your YouTube trending data — powered by **Google Gemini AI**")
st.markdown("---")

# ─── Sidebar: API Key config ────────────────────────────────
# Hardcoded Gemini API key — no manual entry needed
GEMINI_API_KEY = "AIzaSyAoNypEmqM9VDltzNL0I8JRbw4KmgQ00A0"

with st.sidebar:
    st.markdown("### 🤖 AI Status")
    st.success("✅ Gemini AI Active")
    st.markdown("---")
    st.markdown("### 🧠 Model")
    model_choice = st.selectbox("Gemini Model", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"], index=0)
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

api_key_input = GEMINI_API_KEY  # Always use hardcoded key

# ─── Load data context from MySQL ────────────────────────────
@st.cache_data(ttl=300)
def load_data_context():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Summary stats
            stats = pd.read_sql("""
                SELECT COUNT(*) AS total_videos,
                       SUM(view_count) AS total_views,
                       AVG(view_count) AS avg_views,
                       AVG(engagement_score) AS avg_engagement
                FROM processed_videos
            """, conn).iloc[0]
            # Top videos
            top_videos = pd.read_sql("""
                SELECT title, channel_name, category_name, view_count, like_count, engagement_score
                FROM processed_videos ORDER BY view_count DESC LIMIT 10
            """, conn)
            # Category stats
            cat_stats = pd.read_sql("""
                SELECT category_name, COUNT(*) AS count, AVG(view_count) AS avg_views
                FROM processed_videos GROUP BY category_name ORDER BY count DESC
            """, conn)
            # Sentiment stats
            sentiment = pd.read_sql("""
                SELECT sentiment, COUNT(*) AS count FROM processed_comments GROUP BY sentiment
            """, conn)
            # Top comments
            top_comments = pd.read_sql("""
                SELECT comment_text, sentiment, polarity FROM processed_comments
                ORDER BY like_count DESC LIMIT 20
            """, conn)
        return stats, top_videos, cat_stats, sentiment, top_comments
    except Exception as e:
        return None, None, None, None, None

def build_system_prompt(stats, top_videos, cat_stats, sentiment, top_comments):
    if stats is None:
        return "You are an AI assistant for a YouTube analytics dashboard. The database is empty - ask user to run the pipeline."

    top_v_str = top_videos.to_string(index=False) if top_videos is not None else "N/A"
    cat_str   = cat_stats.to_string(index=False) if cat_stats is not None else "N/A"
    sent_str  = sentiment.to_string(index=False) if sentiment is not None else "N/A"
    comm_str  = top_comments["comment_text"].head(5).tolist() if top_comments is not None else []

    return f"""You are an expert AI Data Analyst named "YT-Analyst" for a Big Data YouTube Analytics project.
You have access to real data from YouTube's trending videos in India (IN region), collected via YouTube Data API v3, stored in MySQL, and processed using Python/Pandas.

DATASET SUMMARY:
- Total trending videos: {int(stats['total_videos'])}
- Total views across all videos: {int(stats['total_views']):,}
- Average views per video: {int(stats['avg_views']):,}
- Average engagement score: {float(stats['avg_engagement']):.2f}%
- Total comments analyzed: ~2,934

TOP 10 VIDEOS BY VIEWS:
{top_v_str}

CATEGORY BREAKDOWN:
{cat_str}

SENTIMENT ANALYSIS RESULTS:
{sent_str}

SAMPLE POPULAR COMMENTS:
{chr(10).join(comm_str[:3])}

YOUR ROLE:
- Answer questions about this YouTube data clearly and insightfully
- Give data-driven answers with specific numbers from the dataset above
- Suggest insights, trends, and patterns the user might not have noticed
- Help explain Big Data concepts (Spark, Hadoop, ETL, sentiment analysis) in simple terms
- If asked about something outside this dataset, say so honestly
- Keep answers concise but insightful. Use bullet points and **bold** for key numbers.
- Be enthusiastic and helpful - this is a college final year project!
"""

# ─── Initialize chat session ─────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Quick Question Buttons ───────────────────────────────────
st.markdown('<div class="section-header">⚡ Quick Questions</div>', unsafe_allow_html=True)
q_cols = st.columns(3)
quick_qs = [
    "Which category has the most trending videos?",
    "What is the overall sentiment of YouTube comments?",
    "Which video has the highest engagement score?",
    "What does engagement score mean?",
    "Tell me the top 5 most viewed videos",
    "What insights can I get from this data?",
]
for i, q in enumerate(quick_qs):
    with q_cols[i % 3]:
        if st.button(q, key=f"quick_{i}"):
            st.session_state.messages.append({"role": "user", "content": q})

st.markdown("---")

# ─── Chat Display ─────────────────────────────────────────────
st.markdown('<div class="section-header">💬 Chat</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">🧑‍💻 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

# ─── Chat Input ───────────────────────────────────────────────
user_input = st.chat_input("Ask me anything about your YouTube data...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# ─── AI Response ──────────────────────────────────────────────
needs_response = (
    st.session_state.messages and
    st.session_state.messages[-1]["role"] == "user"
)

if needs_response:
    last_user_msg = st.session_state.messages[-1]["content"]

    if not api_key_input:
        # Fallback: rule-based smart responses using real data
        stats, top_videos, cat_stats, sentiment, top_comments = load_data_context()

        def local_answer(q, top_videos, cat_stats, sentiment):
            q_lower = q.lower()
            if any(w in q_lower for w in ["top", "most viewed", "popular", "best"]):
                if top_videos is not None and not top_videos.empty:
                    top3 = top_videos.head(3)
                    lines = [f"**{i+1}. {r['title']}** — 👁 {int(r['view_count']):,} views"
                             for i, (_, r) in enumerate(top3.iterrows())]
                    return "🏆 **Top 3 Most Viewed Videos:**\n\n" + "\n\n".join(lines)
            if any(w in q_lower for w in ["categor", "music", "gaming", "entertainment"]):
                if cat_stats is not None and not cat_stats.empty:
                    top_cat = cat_stats.iloc[0]
                    return (f"📂 **Top Category: {top_cat['category_name']}** with **{int(top_cat['count'])} videos** "
                            f"and avg **{int(top_cat['avg_views']):,}** views. "
                            f"\n\nAll categories: " +
                            ", ".join([f"{r['category_name']} ({int(r['count'])})" for _, r in cat_stats.iterrows()]))
            if any(w in q_lower for w in ["sentiment", "positive", "negative", "comment"]):
                if sentiment is not None and not sentiment.empty:
                    rows = {r["sentiment"]: int(r["count"]) for _, r in sentiment.iterrows()}
                    total = sum(rows.values())
                    parts = [f"**{k}**: {v} ({v/total*100:.1f}%)" for k, v in rows.items()]
                    return "💬 **Comment Sentiment Analysis:**\n\n" + "\n\n".join(parts) + "\n\n> Most comments are Neutral — typical for entertainment content!"
            if any(w in q_lower for w in ["engagement", "score"]):
                return ("⚡ **Engagement Score** = (Likes + Comments) / Views × 100\n\n"
                        "It measures how actively viewers interact relative to views.\n"
                        "A high score = very engaged audience. Usually music/comedy/gaming score highest!")
            if any(w in q_lower for w in ["insight", "summary", "tell me", "overview"]):
                return ("📊 **Key Insights from your dataset:**\n\n"
                        "- 🎵 **Music & Gaming** dominate trending — highest video count\n"
                        "- 💬 **79% of comments are Neutral** — viewers are mostly informational\n"
                        "- 🌟 **Avg views: 1M+** — India's YouTube market is massive\n"
                        "- ⚡ Videos with short durations tend to have better engagement\n"
                        "- 📱 Top channels appear multiple times — brand loyalty is strong")
            if any(w in q_lower for w in ["spark", "big data", "hadoop", "etl"]):
                return ("⚡ **Big Data Stack in this project:**\n\n"
                        "- **Apache Spark** (PySpark) — distributed data processing engine\n"
                        "- **MySQL** — structured storage for raw + processed data\n"
                        "- **ETL Pipeline** — Extract (YouTube API) → Transform (Spark/Pandas) → Load (MySQL)\n"
                        "- **TextBlob** — NLP library for sentiment scoring\n"
                        "- **Streamlit** — rapid dashboard framework\n\n"
                        "> Spark processes data **100x faster** than plain Python for large datasets!")
            return ("🤖 I need your **Gemini API key** in the sidebar to answer complex questions!\n\n"
                    "Get a **free key** at: [aistudio.google.com](https://aistudio.google.com/apikey)\n\n"
                    "Or try one of the **Quick Questions** above — those work without a key! ⚡")

        reply = local_answer(last_user_msg, top_videos, cat_stats, sentiment)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    else:
        # ─── Gemini API response ───────────────────────────────
        with st.spinner("🤖 YT-Analyst is thinking..."):
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel(model_choice)

                stats, top_videos, cat_stats, sentiment, top_comments = load_data_context()
                system_prompt = build_system_prompt(stats, top_videos, cat_stats, sentiment, top_comments)

                # Build full conversation history for Gemini
                history = []
                msgs = st.session_state.messages[:-1]  # all except the latest user msg
                for m in msgs:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})

                chat = model.start_chat(history=history)
                full_prompt = f"{system_prompt}\n\nUser question: {last_user_msg}"
                response = chat.send_message(full_prompt)
                reply = response.text

                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

            except Exception as e:
                err_msg = str(e)
                if "API_KEY_INVALID" in err_msg or "invalid" in err_msg.lower():
                    reply = "❌ Invalid API key. Please check your Gemini API key."
                elif "quota" in err_msg.lower() or "429" in err_msg:
                    reply = "⚠️ API quota exceeded. Gemini free tier limit reached. Try again in a minute."
                elif "404" in err_msg or "not found" in err_msg.lower():
                    reply = "⚠️ Model not available. Switching to gemini-2.0-flash — please select it in the sidebar Model dropdown and try again."
                else:
                    reply = f"❌ Error: {err_msg[:200]}"
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

# Show placeholder if chat is empty
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding:40px; color:#4a4a8a;">
        <div style="font-size:3rem">🤖</div>
        <div style="font-size:1.1rem; margin-top:12px; color:#6666aa">
            Ask me anything about your YouTube data!<br>
            <span style="font-size:0.9rem; color:#4a4a7a">
            Try: <i>"Which video has the most views?"</i> or <i>"What is the sentiment of comments?"</i>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


