import logging
import sys
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

def run_bronze():
    ingest_all_mhtml("data/0_source", "data/1_silver")

def run_silver():
    process_all_html("data/1_silver", "data/2_bronze")

def run_gold():
    load_all_jsons("data/2_bronze", "data/3_gold/jobs.db")

def run_profiler():
    pass

def print_usage():
    print("Usage: uv run main.py [ingest|process|load|profile|all|help]")
    print("")
    print("task:")
    print("> help -- show this help page")
    print("> all -- executes the whole pipeline")
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
    "all": run_pipeline,
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
