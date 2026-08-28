import pandas as pd

from country_lookup import (
    iso_to_country,
    get_zone,
    get_disaster_category,
)

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = "ifrc_document_index_2022_onward.csv"
OUTPUT_FILE = "report_metadata.csv"


# ============================================================
# LOAD REPORT INDEX
# ============================================================

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} reports from {INPUT_FILE}")


# ============================================================
# KEEP REPORTS WE ARE PROCESSING
# ============================================================

# We want:
# 1. DREF reports missing from the structured DREF JSON
# 2. Emergency Appeal / Other reports
#
# If your report_category values are slightly different,
# this section can be adjusted after looking at the CSV.

wanted_categories = [
    "DREF (Missing from JSON)",
    "Emergency Appeal / Other",
]

df = df[
    df["report_category"].isin(wanted_categories)
].copy()

print(f"Reports selected for processing: {len(df)}")


# ============================================================
# COUNTRY
# ============================================================

df["Country"] = df["iso"].apply(
    iso_to_country
)


# ============================================================
# ZONE
# ============================================================

df["Zone"] = df["Country"].apply(
    get_zone
)


# ============================================================
# START DATE
# ============================================================

df["Start Date"] = pd.to_datetime(
    df["event_start_date"],
    errors="coerce"
).dt.strftime("%Y-%m-%d")


# ============================================================
# YEAR
# ============================================================

start_dates = pd.to_datetime(
    df["Start Date"],
    errors="coerce"
)

df["Year"] = start_dates.dt.year


# ============================================================
# END DATE
# ============================================================

# End date will come from the report itself through Gemini.
#
# Therefore, do NOT try to infer it from the API.
#
# This column is included here so that the final metadata
# structure is ready for flatten_markdown.py.

df["End Date"] = None


# ============================================================
# OPERATION DURATION
# ============================================================

# This will also be calculated later using:
#
# Start Date + End Date
#
# once End Date has been extracted by Gemini.

df["Operation Duration"] = None


# ============================================================
# DISASTER TYPE
# ============================================================

def parse_disaster_type(event_name):

    if pd.isna(event_name):
        return None

    text = str(event_name).strip()

    # Example:
    #
    # COG: Epidemic - 07-2025 - CHOLERA EPIDEMIC
    #
    # becomes:
    #
    # Epidemic - 07-2025 - CHOLERA EPIDEMIC

    if ":" in text:
        text = text.split(":", 1)[1].strip()

    # Take the first section before " - "
    #
    # Epidemic - 07-2025 - CHOLERA EPIDEMIC
    #
    # becomes:
    #
    # Epidemic

    if " - " in text:
        text = text.split(" - ", 1)[0].strip()

    return text


df["Disaster Type"] = df["event_name"].apply(
    parse_disaster_type
)


# ============================================================
# DISASTER CATEGORY
# ============================================================

df["Disaster Category"] = (
    df["Disaster Type"]
    .apply(get_disaster_category)
)


# ============================================================
# APPEAL CODE
# ============================================================

df["Appeal Code"] = df["appeal_code"]


# ============================================================
# RENAME EXISTING METADATA
# ============================================================

df["ISO"] = df["iso"]

df["Document Type"] = df["document_type"]

df["Document Name"] = df["document_name"]

df["Report Category"] = df["report_category"]

df["Filename"] = df["filename"]


# ============================================================
# KEEP ONLY THE COLUMNS WE NEED
# ============================================================

metadata_columns = [

    "Appeal Code",

    "Country",
    "Zone",
    "ISO",

    "Start Date",
    "End Date",
    "Operation Duration",
    "Year",

    "Disaster Type",
    "Disaster Category",

    "Document Type",
    "Document Name",
    "Report Category",
    "Filename",
]


df = df[metadata_columns]


# ============================================================
# CHECK FOR UNKNOWN COUNTRIES / ZONES
# ============================================================

unknown_countries = df[
    df["Country"].isna()
].copy()

unknown_zones = df[
    df["Zone"] == "Unknown"
].copy()


if len(unknown_countries) > 0:

    print(
        f"\nWARNING: {len(unknown_countries)} "
        "reports have an unknown country."
    )

    print(
        unknown_countries[
            ["Appeal Code", "ISO"]
        ].to_string(index=False)
    )


if len(unknown_zones) > 0:

    print(
        f"\nWARNING: {len(unknown_zones)} "
        "reports have an unknown zone."
    )

    print(
        unknown_zones[
            ["Appeal Code", "Country"]
        ].to_string(index=False)
    )


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n----------------------------------------")
print("Report metadata created successfully")
print("----------------------------------------")

print(f"Input:  {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")
print(f"Reports: {len(df)}")

print("\nColumns:")
for column in df.columns:
    print(f"  - {column}")

print("\nFirst 5 reports:")
print(df.head().to_string(index=False))