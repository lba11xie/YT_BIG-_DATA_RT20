# ============================================================
#  Spark: spark_processor.py
#  Core PySpark processing: clean, transform, engagement score
# ============================================================
import sys, os, re, datetime
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

os.environ["PYSPARK_PYTHON"]        = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType
import config

def get_spark():
    return (
        SparkSession.builder
        .appName(config.SPARK_APP_NAME)
        .master(config.SPARK_MASTER)
        .config("spark.driver.memory", "2g")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )

def parse_duration_udf(duration_str):
    """Convert ISO 8601 duration (PT4M13S) to seconds."""
    if not duration_str:
        return 0
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, str(duration_str))
    if not match:
        return 0
    hours   = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def process_videos(spark):
    print("[SPARK] Reading videos from CSV...")
    df = spark.read.csv(config.VIDEOS_CSV, header=True, inferSchema=True)
    print(f"[SPARK] Loaded {df.count()} videos")

    # Drop duplicates
    df = df.dropDuplicates(["video_id"])

    # Fill nulls
    df = df.fillna({
        "view_count": 0, "like_count": 0, "comment_count": 0,
        "title": "Unknown", "channel_name": "Unknown",
        "category_name": "Unknown", "tags": ""
    })

    # Cast numeric cols
    df = (df
          .withColumn("view_count",    F.col("view_count").cast(DoubleType()))
          .withColumn("like_count",    F.col("like_count").cast(DoubleType()))
          .withColumn("comment_count", F.col("comment_count").cast(DoubleType()))
    )

    # Parse duration to seconds using Spark UDF
    parse_dur = F.udf(parse_duration_udf, IntegerType())
    df = df.withColumn("duration_seconds", parse_dur(F.col("duration")))

    # Engagement score = (likes + comments) / views * 100
    df = df.withColumn(
        "engagement_score",
        F.when(F.col("view_count") > 0,
               (F.col("like_count") + F.col("comment_count")) / F.col("view_count") * 100
        ).otherwise(0.0)
    )

    # Add processed_at timestamp
    df = df.withColumn("processed_at", F.lit(datetime.datetime.now().isoformat()))

    # Select final columns
    df = df.select(
        "video_id", "title", "channel_name", "category_name",
        "view_count", "like_count", "comment_count",
        "engagement_score", "duration_seconds",
        "thumbnail_url", "published_at", "processed_at"
    )

    print(f"[SPARK] Processed {df.count()} videos")
    df.show(5, truncate=True)
    return df

if __name__ == "__main__":
    spark = get_spark()
    df = process_videos(spark)
    # Save locally
    out_path = os.path.join(config.PROCESSED_DATA_DIR, "processed_videos")
    df.write.csv(out_path, header=True, mode="overwrite")
    print(f"[SAVED] Processed videos → {out_path}")
    spark.stop()


