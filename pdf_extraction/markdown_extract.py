import json
import time
from pathlib import Path
import os

from google import genai


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MODEL = "gemini-2.5-flash"

MARKDOWN_FOLDER = Path("markdown")
OUTPUT_FOLDER = Path("json")

OUTPUT_FOLDER.mkdir(exist_ok=True)



client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# --------------------------------------------------
# PROMPT
# --------------------------------------------------

PROMPT = """
You are extracting structured WASH information from an IFRC Emergency Appeal or DREF Final Report.

The report has already been converted to Markdown.

Return ONLY valid JSON.

Do NOT wrap your answer in markdown.

Do NOT explain anything.

Extract ONLY information explicitly stated.

If something is not stated, return null.

Return exactly this schema:

{
  "metadata": {

    "country": null,

    "hazard": null,

    "operation_start_date": null,

    "operation_end_date": null

  },
  
  "finance": {

    "number_people_helped": null,

    "total_budget_chf": null,
    "total_expenditure_chf": null,

    "planned_operations_budget_chf": null,
    "planned_operations_expenditure_chf": null,

    "wash_planned_operations_budget_chf": null,
    "wash_planned_operations_expenditure_chf": null,

    "wash_relief_items_budget_chf": null,
    "wash_relief_items_expenditure_chf": null,

    "wash_targeted_people_helped": null,
    "wash_actual_people_helped": null,

    "wash_budget_stated_chf": null
  },

  "beneficiaries": {

    "water_people_reached": null,
    "sanitation_people_reached": null,
    "hygiene_people_reached": null
  },

  "flags": {

    "llm_notes": "",
    "flags": "",
    "water_overlap": null
  },

  "water": [],

  "sanitation": [],

  "hygiene": [],

  "water_infrastructure": [],

  "sanitation_infrastructure": []
}

Every water/sanitation/hygiene item should contain:

{
    "type":"",
    "action":"",
    "count":null,
    "people_helped":null,
    "people_helped_source":"reported",
    "evidence":"",
    "confidence":"high"
}

Confidence must be:

high
medium
low

Return JSON only.
"""

# --------------------------------------------------
# FIND FILES
# --------------------------------------------------

# md_files = sorted(MARKDOWN_FOLDER.rglob("*.md"))
md_files = sorted(MARKDOWN_FOLDER.rglob("*.md"))[:5] 

print(f"Found {len(md_files)} markdown files.\n")

converted = 0
skipped = 0
failed = 0

failures = []

# --------------------------------------------------
# LOOP
# --------------------------------------------------

for i, md_file in enumerate(md_files, start=1):

    relative = md_file.parent.relative_to(MARKDOWN_FOLDER)

    out_dir = OUTPUT_FOLDER / relative

    out_dir.mkdir(parents=True, exist_ok=True)

    json_file = out_dir / (md_file.stem + ".json")

    if json_file.exists():

        skipped += 1

        print(f"[{i}/{len(md_files)}] Skip {md_file.name}")

        continue

    print(f"\n[{i}/{len(md_files)}] {md_file.name}")

    try:

        markdown = md_file.read_text(
            encoding="utf-8"
        )

        start = time.time()

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                PROMPT,
                markdown
            ]
        )

        text = response.text.strip()

        # Remove markdown fences if Gemini adds them

        text = (
            text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(text)

        with open(
            json_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"    Saved: {json_file}")

        elapsed = time.time() - start

        converted += 1

        print(f"    ✓ {elapsed:.1f}s")

    except Exception as e:

        failed += 1

        failures.append({
            "file": md_file.name,
            "error": str(e)
        })

        print(f"    ✗ {e}")

        break

# --------------------------------------------------
# SAVE FAILURES
# --------------------------------------------------

if failures:

    with open(
        "extract_failures.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            failures,
            f,
            indent=2
        )

print("\n----------------------------")

print(f"Converted : {converted}")

print(f"Skipped   : {skipped}")

print(f"Failed    : {failed}")

print("----------------------------")