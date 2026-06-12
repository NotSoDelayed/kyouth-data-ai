import logging
import sys
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from typing import cast
from pathlib import Path


def extract_html(file_path: Path, part: EmailMessage, suppress_err: bool = False) -> str | None:
    file_name = file_path.name
    if part.get_content_type() == "text/html":
        content_html = part.get_content()
        logging.info(f"✅ Extracted: {file_name}")
        return content_html
    if not suppress_err:
        logging.error(f"⚠️ No HTML content found in: {file_name}")
    return None

def export_html(html: str, file_name: str, output_dir: Path):
    output_file = output_dir / file_name
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html, encoding="utf-8")
    except OSError as err:
        logging.error(f"⚠️ Unable to export to {output_file.name} | Reason: {err}")

def ingest_all_mhtml(input_path: str, output_path: str):
    print("🥉 Bronze: Ingesting HTML to MHTML")
    input_dir = Path(input_path)
    output_dir = Path(output_path)
    if not (input_dir.exists() or input_dir.is_dir()):
        print(f"Input directory '{input_dir.name}' not found.")
        sys.exit(1)

    count_total = 0
    count_fail = 0
    count_success = 0
    for file_path in input_dir.glob("*.mhtml"):
        count_total += 1
        try:
            with open(file_path, "rb") as file:
                raw = cast(EmailMessage, BytesParser(policy=policy.default).parse(file))
        except ValueError as err:
            count_fail += 1
            logging.error(f"Failed to process: {file_path} | Reason: {err}")
            continue

        if raw.is_multipart():
            html = None
            for part in raw.walk():
                html = extract_html(file_path, part, True)
                if html is not None:
                    export_html(html, f"{file_path.stem}.html", output_dir)
                    count_success += 1
                    break
            if html is None:
                count_fail += 1
                logging.error(f"⚠️ No HTML content found in: {file_path.stem}")
        else:
            html = extract_html(file_path, raw)
            if html is not None:
                export_html(html, f"{file_path.stem}.html", output_dir)
                count_success += 1
            else:
                count_fail += 1

    if count_total == 0:
        print("No source was extracted.")
        sys.exit(0)
    print("📊 Bronze Summary:")
    print(f"Total: {count_total} | Extracted: {count_success} | Failed: {count_fail}")
