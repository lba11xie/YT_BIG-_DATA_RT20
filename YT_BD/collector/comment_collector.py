# ============================================================
#  Collector: comment_collector.py
#  Fetches top comments for each collected video
# ============================================================
import os, sys, json, csv, time, datetime
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

def get_youtube_client():
    return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

def fetch_comments_for_video(youtube, video_id, max_comments=20):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_comments, 100),
            order="relevance"
        )
        response = request.execute()

        for item in response.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id"   : item["id"],
                "video_id"     : video_id,
                "author_name"  : top.get("authorDisplayName", ""),
                "comment_text" : top.get("textDisplay", "")[:1000],
                "like_count"   : int(top.get("likeCount", 0)),
                "published_at" : top.get("publishedAt", ""),
                "fetched_at"   : datetime.datetime.now().isoformat()
            })
    except HttpError as e:
        error_reason = str(e)
        if "commentsDisabled" in error_reason:
            print(f"  [SKIP] Comments disabled for video: {video_id}")
        else:
            print(f"  [ERROR] {video_id}: {e}")
    return comments

def fetch_all_comments(video_ids, max_per_video=20):
    all_comments = []
    print(f"[INFO] Fetching comments for {len(video_ids)} videos...")
    youtube = get_youtube_client()

    for i, vid_id in enumerate(video_ids):
        print(f"  [{i+1}/{len(video_ids)}] Fetching comments for: {vid_id}")
        comments = fetch_comments_for_video(youtube, vid_id, max_per_video)
        all_comments.extend(comments)
        time.sleep(0.3)

    print(f"[SUCCESS] Total comments fetched: {len(all_comments)}")
    return all_comments

def save_comments(comments):
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    json_path = os.path.join(config.RAW_DATA_DIR, "comments.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    if comments:
        csv_path = config.COMMENTS_CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=comments[0].keys())
            writer.writeheader()
            writer.writerows(comments)
        print(f"[SAVED] Comments → {csv_path}")
    return comments

if __name__ == "__main__":
    # Load video IDs from previously fetched videos
    json_path = os.path.join(config.RAW_DATA_DIR, "videos.json")
    if not os.path.exists(json_path):
        print("[ERROR] Run youtube_collector.py first!")
        sys.exit(1)
    with open(json_path, encoding="utf-8") as f:
        videos = json.load(f)
    video_ids = [v["video_id"] for v in videos]
    comments = fetch_all_comments(video_ids, config.COMMENTS_PER_VIDEO)
    save_comments(comments)


