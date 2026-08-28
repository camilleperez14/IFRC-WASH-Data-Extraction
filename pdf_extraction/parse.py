from pathlib import Path
import signal

from docling.document_converter import DocumentConverter

PDF_FOLDER = Path("pdfs")
OUTPUT_FOLDER = Path("markdown")

OUTPUT_FOLDER.mkdir(exist_ok=True)

pdf_files = list(PDF_FOLDER.rglob("*.pdf"))

print(f"Found {len(pdf_files)} PDFs to parse.\n")

converted = 0
failed = 0
skipped = 0

failed_files = []


class Timeout(Exception):
    pass


def handler(signum, frame):
    raise Timeout("Parsing timed out")


signal.signal(signal.SIGALRM, handler)


for i, pdf_path in enumerate(pdf_files, start=1):

    converter = DocumentConverter()

    relative = pdf_path.parent.relative_to(PDF_FOLDER)
    output_dir = OUTPUT_FOLDER / relative
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / (pdf_path.stem + ".md")

    if md_path.exists():
        skipped += 1
        print(f"[{i}/{len(pdf_files)}] Skipping {pdf_path.name}")
        continue

    print(f"[{i}/{len(pdf_files)}] Parsing {pdf_path.name}...")

    try:

        signal.alarm(300)  # 5 minute timeout

        result = converter.convert(str(pdf_path))

        signal.alarm(0)

        markdown = result.document.export_to_markdown()

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        converted += 1

        print("    ✓ Done")

    except Exception as e:

        signal.alarm(0)

        failed += 1

        failed_files.append({
            "filename": pdf_path.name,
            "error": str(e)
        })

        print("    ✗ Failed")
        print(f"      {e}")

print("\n--------------------------------")
print(f"Converted : {converted}")
print(f"Skipped   : {skipped}")
print(f"Failed    : {failed}")
print(f"Output    : {OUTPUT_FOLDER}")

if failed_files:
    import pandas as pd

    pd.DataFrame(failed_files).to_csv(
        "parsing_failures.csv",
        index=False
    )

    print("\nSaved parsing_failures.csv")
