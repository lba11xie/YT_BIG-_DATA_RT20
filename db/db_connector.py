# ============================================================
#  DB: db_connector.py
#  MySQL connection utilities
# ============================================================
import sys
sys.path.insert(0, r"c:\JELLYFISH\YT_BD\YT_BD")

import pymysql
from sqlalchemy import create_engine, text
import config

def get_connection():
    """Raw PyMySQL connection."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_engine():
    """SQLAlchemy engine for pandas/spark compatibility."""
    return create_engine(config.DB_URL, echo=False)

def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally return results."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            conn.commit()
    finally:
        conn.close()

def test_connection():
    try:
        conn = get_connection()
        conn.close()
        print("[OK] MySQL connection successful!")
        return True
    except Exception as e:
        print(f"[ERROR] MySQL connection failed: {e}")
        return False


