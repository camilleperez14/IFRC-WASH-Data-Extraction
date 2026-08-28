import os
import time
import requests
import pandas as pd

# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_CSV = "reports_needing_extraction.csv"
BASE_FOLDER = "pdfs"

os.makedirs(BASE_FOLDER, exist_ok=True)

# --------------------------------------------------
# Load report list
# --------------------------------------------------

df = pd.read_csv(INPUT_CSV)

print(f"Found {len(df)} reports to download.\n")

downloaded = 0
skipped = 0
failed = 0

headers = {
    "User-Agent": "Mozilla/5.0"
}

# --------------------------------------------------
# Download PDFs
# --------------------------------------------------

for _, row in df.iterrows():

    pdf_url = row["pdf_url"]
    filename = row["filename"]
    category = row["report_category"]

    # Choose destination folder
    if category == "DREF (Missing from JSON)":
        folder = os.path.join(BASE_FOLDER, "missing_drefs")
    else:
        folder = os.path.join(BASE_FOLDER, "non_dref_final_reports")

    os.makedirs(folder, exist_ok=True)

    output_path = os.path.join(folder, filename)

    # Skip if already downloaded
    if os.path.exists(output_path):
        skipped += 1
        continue

    try:
        response = requests.get(
            pdf_url,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        downloaded += 1
        print(f"Downloaded: {filename}")

    except Exception as e:
        failed += 1
        print(f"Failed: {filename}")
        print(e)

    time.sleep(0.2)

# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n----------------------------")
print(f"Downloaded : {downloaded}")
print(f"Skipped    : {skipped}")
print(f"Failed     : {failed}")