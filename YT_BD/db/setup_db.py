# ============================================================
#  DB: setup_db.py
#  Creates MySQL database and all tables
# ============================================================
import sys
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

import pymysql
import config

CREATE_DB_SQL = f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

TABLE_VIDEOS = """
CREATE TABLE IF NOT EXISTS `videos` (
    `video_id`      VARCHAR(20)   PRIMARY KEY,
    `title`         VARCHAR(500)  NOT NULL,
    `channel_name`  VARCHAR(255),
    `channel_id`    VARCHAR(100),
    `published_at`  DATETIME,
    `description`   TEXT,
    `category_id`   VARCHAR(10),
    `category_name` VARCHAR(100),
    `duration`      VARCHAR(30),
    `view_count`    BIGINT        DEFAULT 0,
    `like_count`    BIGINT        DEFAULT 0,
    `comment_count` BIGINT        DEFAULT 0,
    `thumbnail_url` VARCHAR(500),
    `tags`          TEXT,
    `fetched_at`    DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLE_COMMENTS = """
CREATE TABLE IF NOT EXISTS `comments` (
    `comment_id`   VARCHAR(100)  PRIMARY KEY,
    `video_id`     VARCHAR(20),
    `author_name`  VARCHAR(255),
    `comment_text` TEXT,
    `like_count`   INT           DEFAULT 0,
    `published_at` DATETIME,
    `fetched_at`   DATETIME,
    INDEX idx_video_id (video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLE_PROCESSED_VIDEOS = """
CREATE TABLE IF NOT EXISTS `processed_videos` (
    `video_id`          VARCHAR(20)  PRIMARY KEY,
    `title`             VARCHAR(500),
    `channel_name`      VARCHAR(255),
    `category_name`     VARCHAR(100),
    `view_count`        BIGINT,
    `like_count`        BIGINT,
    `comment_count`     BIGINT,
    `engagement_score`  DOUBLE,
    `duration_seconds`  INT,
    `thumbnail_url`     VARCHAR(500),
    `published_at`      DATETIME,
    `processed_at`      DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLE_PROCESSED_COMMENTS = """
CREATE TABLE IF NOT EXISTS `processed_comments` (
    `comment_id`      VARCHAR(100) PRIMARY KEY,
    `video_id`        VARCHAR(20),
    `author_name`     VARCHAR(255),
    `comment_text`    TEXT,
    `like_count`      INT,
    `sentiment`       VARCHAR(20),
    `polarity`        DOUBLE,
    `subjectivity`    DOUBLE,
    `processed_at`    DATETIME,
    INDEX idx_video_id (video_id),
    INDEX idx_sentiment (sentiment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def setup_database():
    print("[INFO] Setting up MySQL database...")
    # First connect without DB to create it
    conn = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        charset="utf8mb4"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_DB_SQL)
            print(f"[OK] Database `{config.DB_NAME}` ready.")
        conn.commit()
    finally:
        conn.close()

    # Now connect with DB selected
    conn2 = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset="utf8mb4"
    )
    try:
        with conn2.cursor() as cur:
            for name, sql in [
                ("videos",             TABLE_VIDEOS),
                ("comments",           TABLE_COMMENTS),
                ("processed_videos",   TABLE_PROCESSED_VIDEOS),
                ("processed_comments", TABLE_PROCESSED_COMMENTS),
            ]:
                cur.execute(sql)
                print(f"[OK] Table `{name}` ready.")
        conn2.commit()
    finally:
        conn2.close()

    print("\n[SUCCESS] Database setup complete!")

if __name__ == "__main__":
    setup_database()


