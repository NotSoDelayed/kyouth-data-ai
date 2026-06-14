import logging
import shutil
import sys
from pathlib import Path

from src.ingestor import ingest_all_mhtml
from src.loader import load_all_jsons
from src.processor import process_all_html
from src.profiler import run_data_profile


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_bronze():
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)

def run_silver():
    process_all_html(BRONZE_DIR, SILVER_DIR)

def run_gold():
    load_all_jsons(SILVER_DIR, GOLD_DIR/DB_NAME)

def run_profiler():
    run_data_profile(GOLD_DIR/DB_NAME)

def nuke():
    nuked = False
    for path_str in SILVER_DIR, BRONZE_DIR, GOLD_DIR:
        path = Path(path_str)
        if not path.exists():
            print(f"{path} doesn't exist. Skipping...")
            continue
        shutil.rmtree(path)
        nuked = True
        print(f"Nuked: {path}")
    if not nuked:
        print("Nothing was nuked.")
        sys.exit(1)

def print_usage():
    print("Usage: uv run main.py [ingest|process|load|profile|all|help]")
    print("")
    print("task:")
    print("> help -- show this help page")
    print("> all -- executes the whole pipeline")
    print("> nuke -- nukes all generated files")
    print("> ingest -- ingest MHTML to HTML")
    print("> process -- process ETL on HTML to JSON")

def run_pipeline():
    run_bronze()
    print("")
    run_silver()
    print("")
    run_gold()
    print("")
    run_profiler()

COMMANDS = {
    "ingest": run_bronze,
    "process": run_silver,
    "load": run_gold,
    "profile": run_profiler,
    "all": run_pipeline,
    "nuke": nuke,
    "help": print_usage
}

def main():
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    if arg is None:
        print_usage()
        sys.exit(1)
    if arg not in COMMANDS:
        print_usage()
        sys.exit(1)
    COMMANDS[arg]()

if __name__ == "__main__":
    main()
