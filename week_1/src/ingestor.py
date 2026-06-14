import logging
import sys
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path
from typing import cast


def extract_html(file_path: Path, part: EmailMessage, suppress_err: bool = False) -> str | None:
    file_name = file_path.name
    if part.get_content_type() == "text/html":
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset() or "utf-8"
        content_html = payload.decode(charset, errors="replace")
        logging.info(f"✅ Extracted: {file_name}")
        return content_html
    if not suppress_err:
        logging.warning(f"⚠️ No HTML content found in: {file_name}")
    return None

def export_html(html: str, file_name: str, output_dir: Path):
    output_file = output_dir / file_name
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html, encoding="utf-8")
    except OSError as err:
        logging.error(f"⚠️ Unable to export to {output_file.name} | Reason: {err}")

def ingest_all_mhtml(input_path: Path, output_path: Path):
    print("🥉 Bronze: Ingesting HTML to MHTML")
    if not (input_path.exists() or input_path.is_dir()):
        print(f"Input directory '{input_path.name}' not found.")
        sys.exit(1)

    count_total = 0
    count_fail = 0
    count_success = 0
    for file_path in input_path.glob("*.mhtml"):
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
                    export_html(html, f"{file_path.stem}.html", output_path)
                    count_success += 1
                    break
            if html is None:
                count_fail += 1
                logging.warning(f"⚠️ No HTML content found in: {file_path.stem}")
        else:
            html = extract_html(file_path, raw)
            if html is not None:
                export_html(html, f"{file_path.stem}.html", output_path)
                count_success += 1
            else:
                count_fail += 1

    print("\n📊 Bronze Summary:")
    print(f"Total: {count_total} | Extracted: {count_success} | Failed: {count_fail}")
