import json
import logging
import sqlite3
from pathlib import Path


def load_all_jsons(input_path: Path, db_path: Path):
    print("🥇 Gold: Inserting JSON data into database")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        cursor = db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """)
        db.commit()

        n_total = 0
        n_inserted = 0
        n_skipped = 0
        for file_path in input_path.glob("*.json"):
            n_total += 1
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except OSError as err:
                logging.error(f"Failed to read file {file_path.name} | Reason: {err}")
                n_skipped += 1
                continue
            cursor.execute(
                """
                    INSERT OR IGNORE INTO jobs (source_id, job_title, company, description)
                    VALUES (?, ?, ?, ?)
                """,
                (data["source_id"], data["job_title"], data["company"], data["description"])
            )
            if cursor.rowcount == 1:
                n_inserted += 1
                logging.info(f"✅ Inserted: {file_path.stem}.json")
            else:
                n_skipped += 1
                logging.warning(f"⏭️ Skipped (duplicate): {file_path.stem}.json")
            print(f"  {cursor.rowcount}")
    print("\n📊 Gold Summary:")
    print(f"Total: {n_total} | Inserted: {n_inserted} | Skipped: {n_skipped}")
