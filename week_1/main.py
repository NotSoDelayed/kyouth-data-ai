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

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg not in COMMANDS:
            print(f"Unknown argument: {arg}")
            return
        COMMANDS[arg]()
        return
    run_bronze()
    print("")
    run_silver()
    print("")
    run_gold()
    print("")
    run_profiler()

if __name__ == "__main__":
    main()
