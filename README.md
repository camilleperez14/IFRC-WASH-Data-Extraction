# IFRC-WASH-Data-Extraction
Python pipeline for extracting and analyzing WASH information from IFRC DREF reports.

## Overview

This project extracts and organizes WASH (Water, Sanitation, and Hygiene) information from IFRC DREF final reports.

The goal is to create a structured dataset that combines information from:

* IFRC DREF structured JSON data
* WASH indicators
* Narrative descriptions within DREF final reports
* Financial report PDFs
* LLM-assisted extraction of WASH activities and beneficiary information

The resulting dataset can be used to analyze WASH activities, people reached, expenditure, and reporting patterns across DREF operations.

## Repository Structure

```text
IFRC-WASH-Data-Extraction/
│
├── README.md
├── requirements.txt
│
├── src/
│   └── dref_extraction.py
│
├── data/
│   └── [input data]
│
├── outputs/
│   └── [generated outputs]
│
└── llm_cache/
    └── [cached LLM responses]
```

Additional scripts can be added to the `src/` folder as the project develops.

---

## Main Script

### `dref_extraction.py`

This is the primary DREF extraction script.

The script:

1. Loads the DREF JSON export.
2. Assigns each operation to an IFRC zone.
3. Categorizes operations by disaster type.
4. Identifies WASH interventions.
5. Extracts WASH information from structured indicators.
6. Uses Gemini to extract additional information from narrative text.
7. Combines indicator-based and narrative-based results.
8. Estimates people reached for certain infrastructure using predefined people-per-unit assumptions.
9. Extracts financial information from financial-report PDFs.
10. Identifies potential reporting issues using automated flags.
11. Produces a summary CSV and a manual-review CSV.

---

## Requirements

The project uses Python 3.12.

The current external Python dependencies are:

```text
pdfplumber==0.11.10
requests==2.34.2
urllib3==2.7.0
google-genai==2.10.0
```

Install the dependencies with:

```bash
pip3 install -r requirements.txt
```

---

## API Key

The extraction script uses the Google Gemini API to analyze narrative text.

The API key should **not** be written directly into the Python script or committed to GitHub.

The script expects the key to be available as an environment variable:

```text
GEMINI_API_KEY
```

Set the environment variable in Terminal before running the script.

For example:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Do not add the actual API key to this repository.

---

## Input Data

The current DREF extraction script expects the DREF structured data JSON file to be available in the working directory.

The current filename expected by the script is:

```text
dref_final_report_export_11062026.json
```

The script loads this file and processes each DREF operation.

The input records provide information such as:

* Country
* Operation start date
* Operation end date
* Disaster type
* Appeal code
* Number of people assisted
* Planned interventions
* WASH indicators
* Financial report information

---

## WASH Extraction

The script focuses on three WASH sectors:

### Water

The extraction includes:

* Wells
* Boreholes
* Pumps
* Water points
* Tanks
* Water treatment plants
* Chlorine tablets

### Sanitation

The extraction includes:

* Community latrines
* Family latrines

### Hygiene

The extraction includes:

* Hygiene promotion
* Hygiene kits
* Cleaning kits
* Dignity kits
* MHM kits

The script uses both predefined keyword matching and LLM-assisted narrative extraction.

---

## Indicator Extraction

WASH indicators are searched using predefined keywords.

Indicators may report either:

* Number of people
* Number of households/families
* Number of infrastructure items

When an indicator reports households or families, the current script converts this to people using:

```text
households × 5
```

This assumption should be documented and reconsidered if the methodology changes.

---

## LLM Extraction

The script sends WASH narrative text and WASH indicators to Gemini.

The narrative text includes:

* Description
* Narrative description of achievements
* Lessons learned
* Challenges

The LLM is instructed to identify WASH activities, quantities, beneficiary numbers, evidence, confidence, and disagreements between indicators and narrative information.

The extraction is restricted to predefined WASH categories rather than allowing the model to create new intervention types.

### LLM caching

LLM results are cached locally in:

```text
llm_cache/
```

The cache is keyed using the appeal code and prompt version.

This prevents the script from repeatedly calling Gemini for the same operation when the cached result already exists.

The current prompt version is:

```text
v6
```

If the prompt is changed substantially, the prompt version should also be updated so that previous cached results are not incorrectly reused.

---

## Combining Results

The script combines information from the LLM and structured indicators.

For infrastructure counts:

1. LLM count is used when available.
2. Otherwise, the indicator count is used.

For people helped:

1. LLM-reported people helped is preferred.
2. Otherwise, indicator-based people helped is used.
3. If neither is available, predefined people-per-unit estimates may be applied.
4. If no estimate is available, the result is zero.

The script also records evidence, confidence, source, and extraction method.

---

## People-Per-Unit Estimates

For certain infrastructure types, the script uses predefined assumptions to estimate the number of people served when the report provides infrastructure counts but does not provide a beneficiary count.

Current assumptions include:

| Infrastructure        | People per unit |
| --------------------- | --------------: |
| Well                  |             400 |
| Borehole              |             500 |
| Pump                  |             500 |
| Water point           |             500 |
| Water treatment plant |           2,000 |
| Community latrine     |              20 |
| Family latrine        |               5 |

These are **estimates rather than reported beneficiary numbers** and should be treated differently from directly reported figures.

---

## Water Beneficiary Overlap

The script attempts to determine whether beneficiaries of different water interventions overlap.

Possible values are:

* `same`
* `different`
* `unknown`

If beneficiaries appear to be the same population, the script uses the maximum rather than adding the beneficiary counts together.

If beneficiaries appear to be different populations, the counts are summed.

If overlap is unknown, the script uses the maximum as a conservative estimate.

---

## Financial Extraction

The script identifies the financial report associated with each DREF operation and extracts financial information from the PDF.

The current extraction includes:

* Grand total budget
* Grand total expenditure
* Planned operations budget
* Planned operations expenditure
* WASH planned operations budget
* WASH planned operations expenditure
* WASH relief items, construction, and supplies budget
* WASH relief items, construction, and supplies expenditure

The financial PDF is downloaded and processed using `pdfplumber`.

---

## Outputs

### `dref_summary.csv`

This is the main output file.

It contains operation-level information including:

* Country
* Zone
* Dates
* Disaster type/category
* Appeal code
* Total people assisted
* Financial information
* WASH target and actual beneficiaries
* Water, sanitation, and hygiene beneficiaries
* Infrastructure counts
* People reached by intervention
* Evidence
* Confidence
* LLM notes
* Review flags
* Water beneficiary overlap

### `manual_review.csv`

This file contains operations that triggered one or more automated review flags.

It includes:

* Appeal code
* Country
* Flags requiring review

---

## Automated Review Flags

The script currently identifies several potential reporting issues, including:

* WASH activity but no WASH expenditure
* WASH expenditure but no WASH activity
* No WASH activities reported
* Missing financial report
* Indicator/narrative disagreement
* WASH expenditure but no WASH beneficiaries extracted
* Chlorine tablets reported but beneficiaries unknown

These flags are intended to identify records for **manual review**, not automatically determine that the underlying report is incorrect.

---

## Running the Script

Once Python, the required packages, the input JSON, and the Gemini API key are configured, run:

```bash
python3 src/dref_extraction.py
```

The script will process the DREF records and create:

```text
dref_summary.csv
manual_review.csv
```

The terminal will also display progress as reports are processed.

---

## Important Notes

### API usage

The script uses Gemini for narrative extraction. Running the script on new records can therefore generate API usage.

The local LLM cache is intended to reduce unnecessary repeated calls.

### Manual review

LLM extraction and automated rules should not be treated as perfect. Records identified by the review flags should be checked against the original DREF report when accuracy is important.

### Estimates

Some beneficiary numbers are calculated rather than directly reported. These should be distinguished from reported values in downstream analysis.

### Input changes

If the structure or field names of the DREF JSON export change, parts of the extraction script may need to be updated.

### Financial reports

Financial extraction depends on the structure of the PDF tables. Changes in PDF formatting may cause the financial extraction to fail or require modification.

---

## Future Development

Potential future work includes:

* Adding additional extraction scripts
* Incorporating IFRC Appeal reports
* Improving validation of beneficiary numbers
* Improving financial-report extraction
* Expanding WASH intervention categories
* Improving handling of ambiguous indicators
* Adding automated quality-control checks
* Separating the extraction pipeline into modular scripts
* Developing a more reproducible configuration for input/output paths

---

## Handover Documentation

A more detailed internship handover document should accompany this README.

The handover document should explain:

* Background and purpose of the project
* How the project was developed
* Detailed methodology
* Extraction logic and assumptions
* Important decisions made during development
* Known issues and limitations
* Examples of problematic reports
* How results were validated
* Remaining work
* Recommended next steps
* Any additional scripts or analyses developed during the internship

The README is intended to provide the technical starting point; the handover document provides the broader project context and institutional knowledge.
