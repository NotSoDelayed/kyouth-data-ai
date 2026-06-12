import logging
import sys
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

def run_bronze():
    ingest_all_mhtml("data/0_source", "data/1_silver")

def run_silver():
    process_all_html("data/1_silver", "data/2_bronze")

def run_gold():
    pass

def run_profiler():
    pass

COMMANDS = {
    "ingest": run_bronze,
    "process": run_silver
}

def print_usage():
    print("Usage: uv run main.py [optional: task]")
    print("")
    print("task:")
    print("> help -- show this help page")
    print("> ingest -- ingest MHTML to HTML")
    print("> process -- process ETL on HTML to JSON")

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg not in COMMANDS:
            exit_code = 0
            if arg != "help":
                exit_code = 1
                print(f"Unknown argument: {arg}")
            print_usage()
            sys.exit(exit_code)
        COMMANDS[arg]()
        sys.exit(0)
    run_bronze()
    print("")
    run_silver()
    print("")
    run_gold()
    print("")
    run_profiler()

if __name__ == "__main__":
    main()
