# ============================================================
#  Spark: sentiment_analysis.py
#  TextBlob sentiment scoring on comments via Spark UDF
# ============================================================
import sys, os, datetime
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

os.environ["PYSPARK_PYTHON"]        = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, DoubleType, StructType, StructField
import config

# Sentiment UDFs using TextBlob
def get_polarity(text):
    try:
        from textblob import TextBlob
        return float(TextBlob(str(text)).sentiment.polarity)
    except:
        return 0.0

def get_subjectivity(text):
    try:
        from textblob import TextBlob
        return float(TextBlob(str(text)).sentiment.subjectivity)
    except:
        return 0.0

def get_sentiment_label(polarity):
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def analyze_comments(spark):
    print("[SPARK] Reading comments from CSV...")
    df = spark.read.csv(config.COMMENTS_CSV, header=True, inferSchema=True)
    print(f"[SPARK] Loaded {df.count()} comments")

    df = df.dropDuplicates(["comment_id"])
    df = df.fillna({"comment_text": "", "author_name": "Anonymous", "like_count": 0})

    # Register UDFs
    polarity_udf     = F.udf(get_polarity, DoubleType())
    subjectivity_udf = F.udf(get_subjectivity, DoubleType())

    df = (df
          .withColumn("polarity",     polarity_udf(F.col("comment_text")))
          .withColumn("subjectivity", subjectivity_udf(F.col("comment_text")))
    )

    # Label sentiment
    df = df.withColumn(
        "sentiment",
        F.when(F.col("polarity") > 0.1, "Positive")
         .when(F.col("polarity") < -0.1, "Negative")
         .otherwise("Neutral")
    )
    df = df.withColumn("processed_at", F.lit(datetime.datetime.now().isoformat()))

    df = df.select(
        "comment_id", "video_id", "author_name", "comment_text",
        "like_count", "sentiment", "polarity", "subjectivity", "processed_at"
    )

    print(f"[SPARK] Sentiment analysis done on {df.count()} comments")
    print("[SPARK] Sentiment distribution:")
    df.groupBy("sentiment").count().show()
    return df

if __name__ == "__main__":
    spark = (SparkSession.builder
             .appName("YT_Sentiment")
             .master(config.SPARK_MASTER)
             .config("spark.driver.memory", "2g")
             .getOrCreate())
    df = analyze_comments(spark)
    out_path = os.path.join(config.PROCESSED_DATA_DIR, "processed_comments")
    df.write.csv(out_path, header=True, mode="overwrite")
    print(f"[SAVED] → {out_path}")
    spark.stop()


