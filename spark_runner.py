# spark_runner.py  — Runs all Spark processing jobs
# Handles Windows path-with-spaces issue for PYSPARK_PYTHON
import sys, os, re, datetime

# Resolve short 8.3 path so Spark can handle "GROW MORE" space in path
def get_short_path(long_path):
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(500)
        ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, 500)
        return buf.value if buf.value else long_path
    except:
        return long_path

PYTHON_SHORT = get_short_path(sys.executable)
print(f"[INFO] Python short path: {PYTHON_SHORT}")

os.environ["PYSPARK_PYTHON"]        = PYTHON_SHORT
os.environ["PYSPARK_DRIVER_PYTHON"] = PYTHON_SHORT
os.environ["PYTHONIOENCODING"]      = "utf-8"

sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")
import config

# ---- Duration parser (ISO 8601 → seconds) ----
def _parse_duration(dur):
    if not dur:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", str(dur))
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mi * 60 + s

# ---- TextBlob sentiment UDFs ----
def _get_polarity(text):
    try:
        from textblob import TextBlob
        return float(TextBlob(str(text)).sentiment.polarity)
    except:
        return 0.0

def _get_subjectivity(text):
    try:
        from textblob import TextBlob
        return float(TextBlob(str(text)).sentiment.subjectivity)
    except:
        return 0.0

# ---- Main Spark runner ----
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType

spark = (SparkSession.builder
         .appName(config.SPARK_APP_NAME)
         .master(config.SPARK_MASTER)
         .config("spark.driver.memory", "2g")
         .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
         .config("spark.pyspark.python",        PYTHON_SHORT)
         .config("spark.pyspark.driver.python", PYTHON_SHORT)
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# ======== STEP 1: Process Videos ========
print("\n[SPARK] Step 1: Processing videos from CSV...")
vdf = spark.read.csv(config.VIDEOS_CSV, header=True, inferSchema=True)
vdf = vdf.dropDuplicates(["video_id"])
vdf = vdf.fillna({
    "view_count": 0, "like_count": 0, "comment_count": 0,
    "title": "Unknown", "channel_name": "Unknown",
    "category_name": "Unknown", "tags": "", "description": ""
})
vdf = (vdf
       .withColumn("view_count",    F.col("view_count").cast(DoubleType()))
       .withColumn("like_count",    F.col("like_count").cast(DoubleType()))
       .withColumn("comment_count", F.col("comment_count").cast(DoubleType())))

dur_udf = F.udf(_parse_duration, IntegerType())
vdf = vdf.withColumn("duration_seconds", dur_udf(F.col("duration")))

vdf = vdf.withColumn("engagement_score",
      F.when(F.col("view_count") > 0,
             (F.col("like_count") + F.col("comment_count")) / F.col("view_count") * 100)
       .otherwise(0.0))
vdf = vdf.withColumn("processed_at", F.lit(datetime.datetime.now().isoformat()))

vdf = vdf.select(
    "video_id", "title", "channel_name", "category_name",
    "view_count", "like_count", "comment_count",
    "engagement_score", "duration_seconds",
    "thumbnail_url", "published_at", "processed_at"
)
vid_count = vdf.count()
print(f"[SPARK] Videos processed: {vid_count}")

# ======== STEP 2: Sentiment Analysis on Comments ========
print("\n[SPARK] Step 2: Sentiment analysis on comments...")
cdf = spark.read.csv(config.COMMENTS_CSV, header=True, inferSchema=True)
cdf = cdf.dropDuplicates(["comment_id"])
cdf = cdf.fillna({"comment_text": "", "author_name": "Anonymous", "like_count": 0})

pol_udf = F.udf(_get_polarity, DoubleType())
sub_udf = F.udf(_get_subjectivity, DoubleType())
cdf = (cdf
       .withColumn("polarity",     pol_udf(F.col("comment_text")))
       .withColumn("subjectivity", sub_udf(F.col("comment_text"))))
cdf = cdf.withColumn("sentiment",
      F.when(F.col("polarity") > 0.1, "Positive")
       .when(F.col("polarity") < -0.1, "Negative")
       .otherwise("Neutral"))
cdf = cdf.withColumn("processed_at", F.lit(datetime.datetime.now().isoformat()))
cdf = cdf.select(
    "comment_id", "video_id", "author_name", "comment_text",
    "like_count", "sentiment", "polarity", "subjectivity", "processed_at"
)
comm_count = cdf.count()
print(f"[SPARK] Comments processed: {comm_count}")
print("[SPARK] Sentiment distribution:")
cdf.groupBy("sentiment").count().show()

# ======== STEP 3: Export to MySQL ========
print("\n[SPARK] Step 3: Exporting processed data to MySQL...")
import pandas as pd
from sqlalchemy import text as sql_text
from db.db_connector import get_engine

engine = get_engine()
with engine.begin() as conn:
    conn.execute(sql_text("TRUNCATE TABLE processed_videos"))
    conn.execute(sql_text("TRUNCATE TABLE processed_comments"))
print("[INFO] Cleared old processed tables.")

# Convert to pandas and write
vid_pd  = vdf.toPandas()
comm_pd = cdf.toPandas()

for col_name in ["published_at", "processed_at"]:
    if col_name in vid_pd.columns:
        vid_pd[col_name] = pd.to_datetime(vid_pd[col_name], errors="coerce")
    if col_name in comm_pd.columns:
        comm_pd[col_name] = pd.to_datetime(comm_pd[col_name], errors="coerce")

vid_pd.to_sql("processed_videos",    engine, if_exists="append", index=False, chunksize=200, method="multi")
print(f"[OK] Exported {len(vid_pd)} processed videos → MySQL")

comm_pd.to_sql("processed_comments", engine, if_exists="append", index=False, chunksize=200, method="multi")
print(f"[OK] Exported {len(comm_pd)} processed comments → MySQL")

spark.stop()
print("\n[DONE] All Spark jobs completed successfully!")


