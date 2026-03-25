# ============================================================
#  Spark: export_results.py
#  Writes processed DataFrames back to MySQL
# ============================================================
import sys, os, pandas as pd, datetime
sys.path.insert(0, r"c:/JELLYFISH/YT_BD/YT_BD")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from sqlalchemy import text
from db.db_connector import get_engine
import config

os.environ["PYSPARK_PYTHON"]        = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

def spark_df_to_mysql(spark_df, table_name):
    """Convert Spark DataFrame to pandas and insert to MySQL."""
    print(f"[EXPORT] Writing {spark_df.count()} rows → MySQL table `{table_name}`...")
    pandas_df = spark_df.toPandas()
    # Parse datetime
    for col in pandas_df.columns:
        if "at" in col.lower():
            pandas_df[col] = pd.to_datetime(pandas_df[col], errors="coerce")

    engine = get_engine()
    pandas_df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=100
    )
    print(f"[OK] Exported {len(pandas_df)} rows to `{table_name}`")

def run_export(processed_videos_df, processed_comments_df):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE processed_videos"))
        conn.execute(text("TRUNCATE TABLE processed_comments"))
    print("[INFO] Cleared old processed data.")
    spark_df_to_mysql(processed_videos_df,   "processed_videos")
    spark_df_to_mysql(processed_comments_df, "processed_comments")
    print("[DONE] Export complete!")

if __name__ == "__main__":
    from spark.spark_processor    import get_spark, process_videos
    from spark.sentiment_analysis import analyze_comments

    spark = get_spark()
    vid_df  = process_videos(spark)
    comm_df = analyze_comments(spark)
    run_export(vid_df, comm_df)
    spark.stop()


