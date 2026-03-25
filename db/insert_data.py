# ============================================================
#  DB: insert_data.py
#  Bulk-inserts raw video/comment data into MySQL
# ============================================================
import sys, os, json
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import pandas as pd
from sqlalchemy import text
from db.db_connector import get_engine
import config

def load_json(path):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def insert_videos(videos):
    if not videos:
        print("[WARN] No videos to insert.")
        return
    df = pd.DataFrame(videos)
    # Parse datetime columns
    for col in ["published_at", "fetched_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    engine = get_engine()
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO videos
                    (video_id, title, channel_name, channel_id, published_at,
                     description, category_id, category_name, duration,
                     view_count, like_count, comment_count, thumbnail_url, tags, fetched_at)
                VALUES
                    (:video_id, :title, :channel_name, :channel_id, :published_at,
                     :description, :category_id, :category_name, :duration,
                     :view_count, :like_count, :comment_count, :thumbnail_url, :tags, :fetched_at)
                ON DUPLICATE KEY UPDATE
                    view_count    = VALUES(view_count),
                    like_count    = VALUES(like_count),
                    comment_count = VALUES(comment_count),
                    fetched_at    = VALUES(fetched_at)
            """), row.to_dict())
    print(f"[OK] Inserted/updated {len(df)} videos into MySQL.")

def insert_comments(comments):
    if not comments:
        print("[WARN] No comments to insert.")
        return
    df = pd.DataFrame(comments)
    for col in ["published_at", "fetched_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    engine = get_engine()
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO comments
                    (comment_id, video_id, author_name, comment_text, like_count,
                     published_at, fetched_at)
                VALUES
                    (:comment_id, :video_id, :author_name, :comment_text, :like_count,
                     :published_at, :fetched_at)
                ON DUPLICATE KEY UPDATE
                    like_count = VALUES(like_count)
            """), row.to_dict())
    print(f"[OK] Inserted/updated {len(df)} comments into MySQL.")

def run():
    videos_path   = os.path.join(config.RAW_DATA_DIR, "videos.json")
    comments_path = os.path.join(config.RAW_DATA_DIR, "comments.json")

    print("[INFO] Loading raw data...")
    videos   = load_json(videos_path)
    comments = load_json(comments_path)

    print(f"[INFO] Inserting {len(videos)} videos...")
    insert_videos(videos)
    print(f"[INFO] Inserting {len(comments)} comments...")
    insert_comments(comments)
    print("[DONE] Data insertion complete!")

if __name__ == "__main__":
    run()


