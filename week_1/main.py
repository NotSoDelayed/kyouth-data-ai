import logging
import sys
from src.ingestor import ingest_all_mhtml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

def run_bronze():
    ingest_all_mhtml("data/0_source", "data/1_silver")

def run_silver():
    print("silver")

def run_gold():
    print("gold")

def run_profiler():
    print("profiler")

COMMANDS = {
    "ingest": run_bronze
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
    run_silver()
    run_gold()
    run_profiler()

if __name__ == "__main__":
    main()
