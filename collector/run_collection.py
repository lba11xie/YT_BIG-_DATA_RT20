# ============================================================
#  Collector: run_collection.py
#  Master script: runs video + comment collection
# ============================================================
import sys
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

from collector.youtube_collector import get_youtube_client, fetch_trending_videos, save_videos
from collector.comment_collector import fetch_all_comments, save_comments
import config

def run():
    print("=" * 60)
    print("  STEP 1: Collecting YouTube Trending Videos")
    print("=" * 60)
    youtube = get_youtube_client()
    videos  = fetch_trending_videos(youtube, config.REGION_CODE, config.TOTAL_VIDEOS_TO_FETCH)
    save_videos(videos)

    print("\n" + "=" * 60)
    print("  STEP 2: Collecting Comments")
    print("=" * 60)
    video_ids = [v["video_id"] for v in videos]
    comments  = fetch_all_comments(video_ids, config.COMMENTS_PER_VIDEO)
    save_comments(comments)

    print("\n[DONE] Collection complete!")
    print(f"  Videos   : {len(videos)}")
    print(f"  Comments : {len(comments)}")
    return videos, comments

if __name__ == "__main__":
    run()
