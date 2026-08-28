import requests
import pandas as pd
import time

BASE_URL = "https://goadmin.ifrc.org/api/v2/appeal_document/"

documents = []

url = BASE_URL
page = 1

# --------------------------------------------------
# Download all appeal documents from IFRC GO
# --------------------------------------------------

while url:
    print(f"Downloading page {page}...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    for doc in data["results"]:

        appeal = doc.get("appeal") or {}
        event = appeal.get("event") or {}

        documents.append({
            "appeal_code": appeal.get("code"),
            "appeal_id": appeal.get("id"),
            "event_id": event.get("id"),
            "document_id": doc.get("id"),
            "document_type": doc.get("type"),
            "document_name": doc.get("name"),
            "description": doc.get("description"),
            "created_at": doc.get("created_at"),
            "pdf_url": doc.get("document_url"),
            "iso": doc.get("iso"),
            "country": iso_to_country(doc.get("iso")),
            "event_name": event.get("name"),
            "event_start_date": event.get("start_date"),
            "filename": f"{appeal.get('code')}_{doc.get('id')}.pdf"
        })

    url = data["next"]
    page += 1
    time.sleep(0.2)

# --------------------------------------------------
# Create dataframe
# --------------------------------------------------

df = pd.DataFrame(documents)

print(f"\nDownloaded {len(df)} documents.")

# remove duplicates based on document_id
before = len(df)

df = (
    df.drop_duplicates(subset="document_id")
      .reset_index(drop=True)
)

after = len(df)

print(f"Removed {before - after} duplicate documents.")

# --------------------------------------------------
# Keep operations starting in 2022 or later
# --------------------------------------------------

df["event_start_date"] = pd.to_datetime(
    df["event_start_date"],
    errors="coerce"
)

df["operation_year"] = df["event_start_date"].dt.year

df = df[
    df["operation_year"] >= 2022
].copy()

print(f"Documents from operations starting in 2022 or later: {len(df)}")



# --------------------------------------------------
# Load DREF dataset
# --------------------------------------------------

dref = pd.read_csv("dref_summary.csv")

# Normalize appeal codes

df["appeal_code"] = (
    df["appeal_code"]
      .fillna("")
      .astype(str)
      .str.strip()
      .str.upper()
)

dref["Appeal Code"] = (
    dref["Appeal Code"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
)

dref_codes = set(dref["Appeal Code"])

# --------------------------------------------------
# Identify final reports
# --------------------------------------------------

df["is_final_report"] = (
    df["document_type"]
      .fillna("")
      .str.contains("final report", case=False)
)

# --------------------------------------------------
# Identify reports already covered by DREF JSON
# --------------------------------------------------

df["in_dref_dataset"] = df["appeal_code"].isin(dref_codes)

df["report_category"] = "Other"

df.loc[
    (df["document_type"] == "DREF Operation Final Report") &
    (df["in_dref_dataset"]),
    "report_category"
] = "DREF (JSON)"

df.loc[
    (df["document_type"] == "DREF Operation Final Report") &
    (~df["in_dref_dataset"]),
    "report_category"
] = "DREF (Missing from JSON)"

df.loc[
    (df["is_final_report"]) &
    (df["document_type"] != "DREF Operation Final Report"),
    "report_category"
] = "Emergency Appeal / Other"

# --------------------------------------------------
# Save master index
# --------------------------------------------------

df.to_csv(
    "ifrc_document_index_2022_onward.csv",
    index=False
)

print("Saved ifrc_document_index_2022_onward.csv")

print(df.shape)

print("Unique document IDs:", df["document_id"].nunique())

print("Duplicate document IDs:", df.duplicated(subset="document_id").sum())

# --------------------------------------------------
# Keep only final reports
# --------------------------------------------------

finals = df[df["is_final_report"]].copy()

# --------------------------------------------------
# Split into groups
# --------------------------------------------------

missing_drefs = finals[
    finals["report_category"] == "DREF (Missing from JSON)"
]

emergency_appeals = finals[
    finals["report_category"] == "Emergency Appeal / Other"
]

reports_needing_extraction = pd.concat(
    [missing_drefs, emergency_appeals],
    ignore_index=True
)

reports_needing_extraction = (
    reports_needing_extraction
        .drop_duplicates(subset="document_id")
        .reset_index(drop=True)
)

# --------------------------------------------------
# Save outputs
# --------------------------------------------------

finals.to_csv(
    "all_final_reports.csv",
    index=False
)

missing_drefs.to_csv(
    "missing_drefs_from_json.csv",
    index=False
)

emergency_appeals.to_csv(
    "emergency_appeal_final_reports.csv",
    index=False
)

reports_needing_extraction.to_csv(
    "reports_needing_extraction.csv",
    index=False
)

# --------------------------------------------------
# Check for duplicate final reports
# --------------------------------------------------

duplicate_docs = (
    finals.groupby("document_id")
          .size()
          .sort_values(ascending=False)
)

duplicate_docs = duplicate_docs[duplicate_docs > 1]

if len(duplicate_docs) > 0:
    print("\nDuplicate document IDs:")
    print(duplicate_docs)

# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nSummary")
print("-----------------------------------")
print(f"Total documents: {len(df)}")
print(f"Final reports: {len(finals)}")
print(f"DREFs already in JSON: {len(finals[finals['report_category'] == 'DREF (JSON)'])}")
print(f"Missing DREFs: {len(missing_drefs)}")
print(f"Emergency Appeal final reports: {len(emergency_appeals)}")
print(f"Reports needing extraction: {len(reports_needing_extraction)}")

if len(duplicate_docs) > 0:
    print("\nDocument IDs with multiple final reports:")
    print(duplicate_docs)

print("\nFirst reports needing extraction:\n")

print(
    reports_needing_extraction[
        [
            "appeal_code",
            "document_type",
            "document_name",
            "operation_year"
        ]
    ].head(20)
)

print("\nDocument types needing extraction:\n")

print(
    reports_needing_extraction["document_type"].value_counts()
)