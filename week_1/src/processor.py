import json
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError


class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


def process_all_html(input_path: Path, output_path: Path):
    print("🥈 Silver: Transforming HTML to JSON")
    if not input_path.exists() or not input_path.is_dir():
        print(f"Input directory '{input_path}' not found.")
        sys.exit(1)

    total = 0
    count_processed = 0
    count_skipped = 0
    output_path.mkdir(parents=True, exist_ok=True)
    html_files = sorted([f for f in input_path.iterdir() if f.suffix == ".html"])
    for file in html_files:
        total += 1
        try:
            with open(file, "r", encoding="utf-8") as json_file:
                soup = BeautifulSoup(json_file.read(), "html.parser")
            og_url_tag = soup.find("meta", attrs={"property": "og:url"})
            og_url = ""
            if og_url_tag:
                og_url = og_url_tag.get("content", "").strip()
            source_id = ""
            if og_url:
                source_id = og_url.rstrip("/").split("/")[-1]

            job_title = ""
            company = ""
            description = ""
            title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
            if title_tag:
                job_title = title_tag.get_text(separator=" ", strip=True)
            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            if company_tag:
                company = company_tag.get_text(separator=" ", strip=True)
            desc_tag = soup.find(attrs={"data-automation": "jobAdDetails"})
            if desc_tag:
                description = desc_tag.get_text(separator=" ", strip=True)
                description = "\n".join(description.split("\n"))
            if not source_id:
                count_skipped += 1
                logging.warning(f"⚠️ Missing source_id in: {file.name}")
                continue
            if not job_title:
                count_skipped += 1
                logging.warning(f"⚠️ Missing job_title in: {file.name}")
                continue
            if not company:
                count_skipped += 1
                logging.warning(f"⚠️ Missing company in: {file.name}")
                continue
            if not description:
                count_skipped += 1
                logging.warning(f"⚠️ Missing description in: {file.name}")
                continue

            listing = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description
            )

            output_file = output_path / (file.stem + ".json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(listing.model_dump(), json_file, indent=4, ensure_ascii=False)
            count_processed += 1
            logging.info(f"✅ Processed: {file.name}")
        except ValidationError:
            count_skipped += 1
            logging.warning(f"⚠️ Validation failed in: {file.name}")
        except ValueError:
            count_skipped += 1
            logging.warning(f"⚠️ Skipped: {file.name}")

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {count_processed} | Skipped: {count_skipped}")
