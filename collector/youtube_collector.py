# ============================================================
#  Collector: youtube_collector.py
#  Fetches trending YouTube videos for region IN
# ============================================================
import os, sys, json, csv, time, datetime
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

def get_youtube_client():
    return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

def fetch_trending_videos(youtube, region_code="IN", max_total=200):
    videos = []
    next_page_token = None
    fetched = 0

    print(f"[INFO] Fetching trending videos for region: {region_code}")
    while fetched < max_total:
        try:
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=min(50, max_total - fetched),
                pageToken=next_page_token
            )
            response = request.execute()
        except HttpError as e:
            print(f"[ERROR] YouTube API error: {e}")
            break

        for item in response.get("items", []):
            snippet    = item.get("snippet", {})
            stats      = item.get("statistics", {})
            content    = item.get("contentDetails", {})
            category   = config.CATEGORY_MAP.get(snippet.get("categoryId", "0"), "Unknown")

            videos.append({
                "video_id"      : item["id"],
                "title"         : snippet.get("title", ""),
                "channel_name"  : snippet.get("channelTitle", ""),
                "channel_id"    : snippet.get("channelId", ""),
                "published_at"  : snippet.get("publishedAt", ""),
                "description"   : snippet.get("description", "")[:500],
                "category_id"   : snippet.get("categoryId", ""),
                "category_name" : category,
                "duration"      : content.get("duration", ""),
                "view_count"    : int(stats.get("viewCount", 0)),
                "like_count"    : int(stats.get("likeCount", 0)),
                "comment_count" : int(stats.get("commentCount", 0)),
                "thumbnail_url" : snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "tags"          : "|".join(snippet.get("tags", [])),
                "fetched_at"    : datetime.datetime.now().isoformat()
            })
            fetched += 1

        next_page_token = response.get("nextPageToken")
        print(f"[INFO] Fetched {fetched} videos so far...")

        if not next_page_token or fetched >= max_total:
            break
        time.sleep(0.5)   # Be nice to the API

    print(f"[SUCCESS] Total videos fetched: {len(videos)}")
    return videos

def save_videos(videos):
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    # Save JSON
    json_path = os.path.join(config.RAW_DATA_DIR, "videos.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    # Save CSV
    if videos:
        csv_path = config.VIDEOS_CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=videos[0].keys())
            writer.writeheader()
            writer.writerows(videos)
        print(f"[SAVED] Videos → {csv_path}")
    return videos

if __name__ == "__main__":
    yt = get_youtube_client()
    videos = fetch_trending_videos(yt, config.REGION_CODE, config.TOTAL_VIDEOS_TO_FETCH)
    save_videos(videos)


