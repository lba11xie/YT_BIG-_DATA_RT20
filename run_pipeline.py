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

    # STEP 4: Pandas processing (fallback from PySpark due to Java version)
    step("STEP 4/5 — Processing with Pandas")
    subprocess.run([sys.executable, "-X", "utf8", "pandas_processor.py"], check=True)
    print("[PANDAS] All processing jobs completed!")

    # STEP 5: Launch Dashboard
    step("STEP 5/5 — Launching Streamlit Dashboard")
    print("\n[INFO] Opening dashboard at → http://localhost:8501")
    print("[INFO] Press Ctrl+C to stop the dashboard.\n")
    time.sleep(1)
    dashboard_path = r"c:\JELLYFISH\YT_BD\YT_BD\dashboard\app.py"
    os.system(f'streamlit run "{dashboard_path}"')

if __name__ == "__main__":
    run()


