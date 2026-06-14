# Week 1: Data Input & Processing Component

## Project Description

This project executes an ETL pipeline from job listings by processing MHTML files to a SQLite based structured dataset, and generates a data quality profile report.


## Setup Instructions

### Prerequisites
- [Git](https://git-scm.com/install)
- [uv](https://docs.astral.sh/uv/getting-started/installation)


1. Clone the repo
2. Add MHTML files into `<repo directory>/week_1/data/0_source`
3. `cd` into `<repo directory>/week_1` with your terminal
4. Run `uv sync` to set up project packages
5. Activate virtual environment with:
    - macOS / Linux: `source .venv/bin/activate`
    - Windows:
    ```powershell
    cd .venv/bin
    activate.bat
    ```
6. Run the base command `uv run main.py` to get started.


## Usage

Base command: `uv run main.py [optional: args]`

args:
- help: prints the help page
- ingest: ingests MHTML files to raw HTML
- process: process ETL on HTML to JSON
- load: loads processed JSON into DB
- profile: prints data quality report from the DB
- all: executes the whole pipeline
- nuke: nukes all generated files by the program


## Technical Reflections

### Day 1: The Extractor (Medallion & Lakehouses)

- **What We Did:** Setup folder-based Medallion Architecture `(0_source to 3_gold)`. Extracted raw `.mhtml` files to `1_bronze/`.
- **Industry Context:** Modern data platforms often use ***Data Lakes*** to store raw files before transforming them into structured, query-ready data in a ***Data Warehouse**.*
- **Reflection:**
    - Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
      - In case of DB corruption, it can be regenerated/recovered from the raw HTML files for a fresh DB
      - Allows future scalability to the DB such as adding new fields for future datas

### Day 2: Treatment Plant (ETL vs ELT & Scale)

- **What We Did:** Clean HTML `(transform into 2_silver/)` before database load `(load into 3_gold/)` (ETL).
- **Industry Context:** Cloud platforms ***(Snowflake/BigQuery)*** often store raw data first then transform later ***(ELT)***. Enterprise systems use ***Apache Spark*** to process large amounts of data in parallel instead of one file at a time.
- **Reflection:** Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
  - Datas are cheap to store and transform into structured data only on user demand. Processing files sequentially may stress the computing power and slows down the pipeline execution as each step relies on the previous generated dataset where one failure can stop the entire pipeline.

### Day 3: The Blueprint & The Vault (Storage & Contracts)

- **What We Did:** Used SQLite as Gold “warehouse” layer. Enforced basic data integrity via idempotency during load.
- **Industry Context:** Production systems often separate databases used for day-to-day application operations ***(OLTP)*** from databases optimized for analytics and reporting ***(OLAP)***. Strict Data Contracts help ensure incomplete or corrupted data does not break dashboards, analytics, or downstream systems.
- **Reflection:** What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting `nulls` into DB? How does `INSERT OR IGNORE` help prevent duplicate records?
  - Failing early prevents breaking the next pipeline where it assumed the data is ready to be processed. `INSERT OR IGNORE` inserts a record into DB if the value of field `source_id` doesn't exist, and skips ahead if already exist, preventing duplicated records to exist.

### Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

- **What We Did:** `main.py` acts as manual orchestrator, `all` command finalizes sequence
- **Industry Context:** Real-world pipelines usually use orchestration tools like ***Airflow***, which automate execution, retries, scheduling, and dependency management.
- **Reflection:** What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?
  - If processor.py crashes halfway, data is high likelihood to be incomplete and corrupt. Automated orchestration tools solve this by allowing task retry on the failed task once the error is resolved, which are more reliable than manual scripts as the execution order is already defined.
