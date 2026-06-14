import sys
import sqlite3
from sqlite3 import Cursor
from pathlib import Path
from typing import Any


def query_simple_values(cursor: Cursor) -> Any:
    cursor.execute(
        """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN job_title = '' THEN 1 ELSE 0 END) AS empty_job_title,
                SUM(CASE WHEN company = '' THEN 1 ELSE 0 END) AS empty_company,
                SUM(CASE WHEN description = '' THEN 1 ELSE 0 END) AS empty_job_desc
            FROM jobs
        """
    )
    return cursor.fetchone()

def query_desc_len_avg(cursor: Cursor) -> int:
    cursor.execute(
        """
            SELECT
                AVG(LENGTH(description))
            FROM jobs
            WHERE description != '';
        """
    )
    return int(cursor.fetchone()[0])

def query_longest_desc(cursor: Cursor) -> Any:
    cursor.execute(
        """
        SELECT
            source_id,
            job_title AS job_title,
            LENGTH(description) AS desc_len
        FROM jobs
        ORDER BY desc_len DESC
        LIMIT 1;
        """
    )
    return cursor.fetchone()

def query_shortest_desc(cursor: Cursor) -> Any:
    cursor.execute(
        """
        SELECT
            source_id,
            job_title AS job_title,
            LENGTH(description) AS desc_len
        FROM jobs
        ORDER BY desc_len ASC
        LIMIT 1;
        """
    )
    return cursor.fetchone()

def run_data_profile(db_path_str: str):
    db_path = Path(db_path_str)
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    simple = query_simple_values(cursor)
    desc_length_avg = query_desc_len_avg(cursor)
    desc_length_longest = query_longest_desc(cursor)
    desc_length_shortest = query_shortest_desc(cursor)
    print("--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {simple["total"]}")
    print(f"❓ Missing Values -> job_title: {simple["empty_job_title"]}, company: {simple["empty_company"]}, description: {simple["empty_job_desc"]}")
    print(f"📝 Avg Description Length: {desc_length_avg} chars")
    print(f"⚠️ Shortest Description: {desc_length_shortest["desc_len"]} chars")
    print(f"   ↳ source_id: {desc_length_shortest["source_id"]} | job_title: {desc_length_shortest["job_title"]}")
    print(f"🚨 Longest Description: {desc_length_longest["desc_len"]} chars")
    print(f"   ↳ source_id: {desc_length_longest["source_id"]} | job_title: {desc_length_longest["job_title"]}")
