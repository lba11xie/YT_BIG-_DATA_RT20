# pandas_processor.py
# ============================================================
#  Pandas-based Big Data processor (no JVM needed)
#  Computes: engagement score, duration parsing, TextBlob sentiment
#  Writes processed results straight into MySQL
# ============================================================
import sys, os, re, datetime
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import pandas as pd
from textblob import TextBlob
from sqlalchemy import text as sql_text
from db.db_connector import get_engine
import config

print("=" * 60)
print("  ⚡ Pandas Big-Data Processor")
print("=" * 60)

def parse_duration(dur):
    """ISO 8601 duration → seconds."""
    if not dur or pd.isna(dur):
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", str(dur))
    if not m: return 0
    return int(m.group(1) or 0)*3600 + int(m.group(2) or 0)*60 + int(m.group(3) or 0)

def sentiment_label(polarity):
    if polarity > 0.1:  return "Positive"
    if polarity < -0.1: return "Negative"
    return "Neutral"

# ---- STEP 1: Process Videos ----
print("\n[STEP 1] Loading & processing videos...")
vdf = pd.read_csv(config.VIDEOS_CSV)
print(f"  Loaded {len(vdf)} rows from CSV")

vdf = vdf.drop_duplicates(subset=["video_id"])
vdf["view_count"]    = pd.to_numeric(vdf["view_count"],    errors="coerce").fillna(0)
vdf["like_count"]    = pd.to_numeric(vdf["like_count"],    errors="coerce").fillna(0)
vdf["comment_count"] = pd.to_numeric(vdf["comment_count"], errors="coerce").fillna(0)
vdf["title"]         = vdf["title"].fillna("Unknown")
vdf["channel_name"]  = vdf["channel_name"].fillna("Unknown")
vdf["category_name"] = vdf["category_name"].fillna("Unknown")
vdf["tags"]          = vdf["tags"].fillna("")

vdf["duration_seconds"] = vdf["duration"].apply(parse_duration)
vdf["engagement_score"] = vdf.apply(
    lambda r: (r["like_count"] + r["comment_count"]) / r["view_count"] * 100
    if r["view_count"] > 0 else 0.0, axis=1
)
vdf["processed_at"] = datetime.datetime.now()
vdf["published_at"] = pd.to_datetime(vdf["published_at"], errors="coerce")

vid_out = vdf[[
    "video_id", "title", "channel_name", "category_name",
    "view_count", "like_count", "comment_count",
    "engagement_score", "duration_seconds",
    "thumbnail_url", "published_at", "processed_at"
]]
print(f"  ✅ Processed {len(vid_out)} videos (deduped, scored)")

# ---- STEP 2: Sentiment Analysis on Comments ----
print("\n[STEP 2] Loading & analyzing comment sentiment...")
cdf = pd.read_csv(config.COMMENTS_CSV)
print(f"  Loaded {len(cdf)} rows from CSV")

cdf = cdf.drop_duplicates(subset=["comment_id"])
cdf["comment_text"] = cdf["comment_text"].fillna("").astype(str)
cdf["author_name"]  = cdf["author_name"].fillna("Anonymous")
cdf["like_count"]   = pd.to_numeric(cdf["like_count"], errors="coerce").fillna(0)
cdf["published_at"] = pd.to_datetime(cdf["published_at"], errors="coerce")

total = len(cdf)
print(f"  Running TextBlob on {total} comments...")
polarities     = []
subjectivities = []
for i, text in enumerate(cdf["comment_text"]):
    if i % 500 == 0:
        print(f"    → {i}/{total} comments analyzed...")
    blob = TextBlob(str(text))
    polarities.append(blob.sentiment.polarity)
    subjectivities.append(blob.sentiment.subjectivity)

cdf["polarity"]     = polarities
cdf["subjectivity"] = subjectivities
cdf["sentiment"]    = cdf["polarity"].apply(sentiment_label)
cdf["processed_at"] = datetime.datetime.now()

comm_out = cdf[[
    "comment_id", "video_id", "author_name", "comment_text",
    "like_count", "sentiment", "polarity", "subjectivity", "processed_at"
]]

# Print distribution
dist = cdf["sentiment"].value_counts()
print(f"\n  📊 Sentiment Distribution:")
for label, count in dist.items():
    pct = count / total * 100
    print(f"     {label:10s}: {count:4d}  ({pct:.1f}%)")
print(f"  ✅ Processed {len(comm_out)} comments")

# ---- STEP 3: Export to MySQL ----
print("\n[STEP 3] Exporting to MySQL...")
engine = get_engine()
with engine.begin() as conn:
    conn.execute(sql_text("TRUNCATE TABLE processed_videos"))
    conn.execute(sql_text("TRUNCATE TABLE processed_comments"))
print("  Cleared old processed tables.")

vid_out.to_sql("processed_videos",    engine, if_exists="append", index=False, chunksize=200, method="multi")
print(f"  ✅ Exported {len(vid_out)} processed videos → MySQL")
comm_out.to_sql("processed_comments", engine, if_exists="append", index=False, chunksize=300, method="multi")
print(f"  ✅ Exported {len(comm_out)} processed comments → MySQL")

# ---- STEP 4: Save processed CSVs locally too ----
os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
vid_out.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "processed_videos.csv"),   index=False)
comm_out.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "processed_comments.csv"), index=False)

print("\n" + "=" * 60)
print("  ✅ All processing complete!")
print(f"  Videos  processed: {len(vid_out)}")
print(f"  Comments processed: {len(comm_out)}")
print("=" * 60)


