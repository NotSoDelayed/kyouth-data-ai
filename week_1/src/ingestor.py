import logging
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
        logging.error(f"⚠️ Unable to export to {file_name}: {err}")

def ingest_all_mhtml(input_path: str, output_path: str):
    input_dir = Path(input_path)
    output_dir = Path(output_path)
    for file_path in input_dir.glob("*.mhtml"):
        try:
            with open(file_path, "rb") as file:
                raw = cast(EmailMessage, BytesParser(policy=policy.default).parse(file))
        except ValueError as err:
            logging.error(f"Failed to process: {file_path} | Reason: {err}")
            continue
        if raw.is_multipart():
            for part in raw.walk():
                html = extract_html(file_path, part, True)
                if html is not None:
                    export_html(html, f"{file_path.stem}.html", output_dir)
                    break
        else:
            if not extract_html(file_path, raw):
                continue