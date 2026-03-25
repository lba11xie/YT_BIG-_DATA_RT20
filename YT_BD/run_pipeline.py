# ============================================================
#  run_pipeline.py — One-click full Big Data pipeline
# ============================================================
import sys, os, time, subprocess
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   🚀  YouTube Big Data Analytics Pipeline               ║
║   Region: India (IN) | Powered by PySpark               ║
╚══════════════════════════════════════════════════════════╝
"""

def step(msg):
    print(f"\n{'='*60}")
    print(f"  ▶  {msg}")
    print(f"{'='*60}")

def run():
    print(BANNER)

    # STEP 1: Setup MySQL DB
    step("STEP 1/5 — Database Setup")
    from db.setup_db import setup_database
    setup_database()

    # STEP 2: Collect YouTube data
    step("STEP 2/5 — Collecting YouTube Data")
    from collector.run_collection import run as collect_run
    videos, comments = collect_run()

    # STEP 3: Insert to MySQL
    step("STEP 3/5 — Inserting Raw Data to MySQL")
    from db.insert_data import run as insert_run
    insert_run()

    # STEP 4: PySpark processing
    step("STEP 4/5 — Processing with Apache Spark")
    import os
    os.environ["PYSPARK_PYTHON"]        = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    from spark.spark_processor    import get_spark, process_videos
    from spark.sentiment_analysis import analyze_comments
    from spark.export_results     import run_export

    spark = get_spark()
    print("[SPARK] Processing videos...")
    vid_df  = process_videos(spark)
    print("[SPARK] Analyzing comment sentiment...")
    comm_df = analyze_comments(spark)
    run_export(vid_df, comm_df)
    spark.stop()
    print("[SPARK] All Spark jobs completed!")

    # STEP 5: Launch Dashboard
    step("STEP 5/5 — Launching Streamlit Dashboard")
    print("\n[INFO] Opening dashboard at → http://localhost:8501")
    print("[INFO] Press Ctrl+C to stop the dashboard.\n")
    time.sleep(1)
    dashboard_path = r"c:\JELLYFISH\YT_BD\YT_BD\dashboard\app.py"
    os.system(f'streamlit run "{dashboard_path}"')

if __name__ == "__main__":
    run()


