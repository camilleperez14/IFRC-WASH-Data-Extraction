import csv
import json
import os
import re
from datetime import datetime

import pdfplumber
import requests
import urllib3

from google import genai

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# GEMINI
# -----------------------------
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# -----------------------------
# CACHE
# -----------------------------
CACHE_FOLDER = "llm_cache"

os.makedirs(CACHE_FOLDER, exist_ok=True)

PROMPT_VERSION = "v6"


# -----------------------------
# LOAD DATA
# -----------------------------
with open("dref_final_report_export_11062026.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ======================================================
# HELPER
# ======================================================

def r(results, infra, field):
    return results[infra][field]


# -----------------------------
# MAPPINGS
# -----------------------------
zone_map = {}


zone_map.update({
    #Africa
    "Angola": "Africa",
    "Benin": "Africa",
    "Botswana": "Africa",
    "Burkina Faso": "Africa",
    "Burundi": "Africa",
    "Cabo Verde": "Africa",
    "Cameroon": "Africa",
    "Cape Verde": "Africa",
    "Central African Republic": "Africa",
    "Chad": "Africa",
    "Comoros": "Africa",
    "Republic of the Congo": "Africa",
    "Congo": "Africa",
    "Democratic Republic of Congo": "Africa",
    "Côte d'Ivoire": "Africa",
    "Ivory Coast": "Africa",
    "Equatorial Guinea": "Africa",
    "Eswatini": "Africa",
    "Eswatini, Kingdom of": "Africa",
    "Ethiopia": "Africa",
    "Gabon": "Africa",
    "Gambia": "Africa",
    "Ghana": "Africa",
    "Guinea": "Africa",
    "Guinea-Bissau": "Africa",
    "Kenya": "Africa",
    "Lesotho": "Africa",
    "Liberia": "Africa",
    "Madagascar": "Africa",
    "Malawi": "Africa",
    "Mali": "Africa",
    "Mauritania": "Africa",
    "Mauritius": "Africa",
    "Mozambique": "Africa",
    "Namibia": "Africa",
    "Niger": "Africa",
    "Nigeria": "Africa",
    "Rwanda": "Africa",
    "Sao Tome and Principe": "Africa",
    "Senegal": "Africa",
    "Seychelles": "Africa",
    "Sierra Leone": "Africa",
    "South Africa": "Africa",
    "South Sudan": "Africa",
    "Tanzania": "Africa",
    "Tanzania, United Republic of": "Africa",
    "Togo": "Africa",
    "Tunisia": "Africa",
    "Uganda": "Africa",
    "Zambia": "Africa",
    "Zimbabwe": "Africa",
    # Middle East and North Africa
    "Algeria": "Middle East and North Africa",
    "Bahrain": "Middle East and North Africa",
    "Egypt": "Middle East and North Africa",
    "Iran": "Middle East and North Africa",
    "Iran, Islamic Republic of": "Middle East and North Africa",
    "Iraq": "Middle East and North Africa",
    "Israel": "Middle East and North Africa",
    "Jordan": "Middle East and North Africa",
    "Kuwait": "Middle East and North Africa",
    "Lebanon": "Middle East and North Africa",
    "Libya": "Middle East and North Africa",
    "Morocco": "Middle East and North Africa",
    "Oman": "Middle East and North Africa",
    "Palestine": "Middle East and North Africa",
    "Qatar": "Middle East and North Africa",
    "Saudi Arabia": "Middle East and North Africa",
    "Sudan": "Middle East and North Africa",
    "Syria": "Middle East and North Africa",
    "Syrian Arab Republic": "Middle East and North Africa",
    "Tunisia": "Middle East and North Africa",
    "United Arab Emirates": "Middle East and North Africa",
    "Yemen": "Middle East and North Africa",
    "Djibouti": "Middle East and North Africa",
    "Somalia": "Middle East and North Africa",
    #Europe & Central Asia
    "Albania": "Europe & Central Asia",
    "Andorra": "Europe & Central Asia",
    "Armenia": "Europe & Central Asia",
    "Austria": "Europe & Central Asia",
    "Azerbaijan": "Europe & Central Asia",
    "Belarus": "Europe & Central Asia",
    "Belgium": "Europe & Central Asia",
    "Bosnia and Herzegovina": "Europe & Central Asia",
    "Bulgaria": "Europe & Central Asia",
    "Croatia": "Europe & Central Asia",
    "Cyprus": "Europe & Central Asia",
    "Czech Republic": "Europe & Central Asia",
    "Denmark": "Europe & Central Asia",
    "Estonia": "Europe & Central Asia",
    "Finland": "Europe & Central Asia",
    "France": "Europe & Central Asia",
    "Georgia": "Europe & Central Asia",
    "Germany": "Europe & Central Asia",
    "Greece": "Europe & Central Asia",
    "Hungary": "Europe & Central Asia",
    "Iceland": "Europe & Central Asia",
    "Ireland": "Europe & Central Asia",
    "Italy": "Europe & Central Asia",
    "Kazakhstan": "Europe & Central Asia",
    "Kyrgyzstan": "Europe & Central Asia",
    "Latvia": "Europe & Central Asia",
    "Lithuania": "Europe & Central Asia",
    "Luxembourg": "Europe & Central Asia",
    "Malta": "Europe & Central Asia",
    "Moldova": "Europe & Central Asia",
    "Monaco": "Europe & Central Asia",
    "Montenegro": "Europe & Central Asia",
    "Netherlands": "Europe & Central Asia",
    "North Macedonia": "Europe & Central Asia",
    "Norway": "Europe & Central Asia",
    "Poland": "Europe & Central Asia",
    "Portugal": "Europe & Central Asia",
    "Romania": "Europe & Central Asia",
    "Russia": "Europe & Central Asia",
    "Serbia": "Europe & Central Asia",
    "Slovakia": "Europe & Central Asia",
    "Slovenia": "Europe & Central Asia",
    "Spain": "Europe & Central Asia",
    "Sweden": "Europe & Central Asia",
    "Switzerland": "Europe & Central Asia",
    "Tajikistan": "Europe & Central Asia",
    "Turkey": "Europe & Central Asia",
    "Ukraine": "Europe & Central Asia",
    "United Kingdom": "Europe & Central Asia",
    "Liechtenstein": "Europe & Central Asia",
    "San Marino": "Europe & Central Asia",
    #Asia Pacific
    "Afghanistan": "Asia Pacific",
    "Australia": "Asia Pacific",
    "Bangladesh": "Asia Pacific",
    "Bhutan": "Asia Pacific",
    "Brunei": "Asia Pacific",
    "Cambodia": "Asia Pacific",
    "China": "Asia Pacific",
    "Fiji": "Asia Pacific",
    "India": "Asia Pacific",
    "Indonesia": "Asia Pacific",
    "Japan": "Asia Pacific",
    "Kiribati": "Asia Pacific",
    "Laos": "Asia Pacific",
    "Lao People's Democratic Republic": "Asia Pacific",
    "Malaysia": "Asia Pacific",
    "Maldives": "Asia Pacific",
    "Marshall Islands": "Asia Pacific",
    "Micronesia, Federated States of": "Asia Pacific",
    "Mongolia": "Asia Pacific",
    "Myanmar": "Asia Pacific",
    "Nepal": "Asia Pacific",
    "New Zealand": "Asia Pacific",
    "North Korea": "Asia Pacific",
    "Pakistan": "Asia Pacific",
    "Palau": "Asia Pacific",
    "Papua New Guinea": "Asia Pacific",
    "Philippines": "Asia Pacific",
    "South Korea": "Asia Pacific",
    "Sri Lanka": "Asia Pacific",
    "Thailand": "Asia Pacific",
    "Timor-Leste": "Asia Pacific",
    "Tonga": "Asia Pacific",
    "Tuvalu": "Asia Pacific",
    "Vanuatu": "Asia Pacific",
    "Vietnam": "Asia Pacific",
    "Viet Nam": "Asia Pacific",
    # Americas
    "Antigua and Barbuda": "Americas",
    "Argentina": "Americas",
    "Bahamas": "Americas",
    "Barbados": "Americas",
    "Belize": "Americas",
    "Bolivia": "Americas",
    "Brazil": "Americas",
    "Canada": "Americas",
    "Chile": "Americas",
    "Colombia": "Americas",
    "Costa Rica": "Americas",
    "Cuba": "Americas",
    "Dominica": "Americas",
    "Dominican Republic": "Americas",
    "Ecuador": "Americas",
    "El Salvador": "Americas",
    "Grenada": "Americas",
    "Guatemala": "Americas",
    "Guyana": "Americas",
    "Haiti": "Americas",
    "Honduras": "Americas",
    "Jamaica": "Americas",
    "Mexico": "Americas",
    "Nicaragua": "Americas",
    "Panama": "Americas",
    "Paraguay": "Americas",
    "Peru": "Americas",
    "Saint Kitts and Nevis": "Americas",
    "Saint Lucia": "Americas",
    "Saint Vincent and the Grenadines": "Americas",
    "Suriname": "Americas",
    "Trinidad and Tobago": "Americas",
    "United States": "Americas",
    "Uruguay": "Americas",
    "Venezuela": "Americas"
    })


disaster_map = {
    "Drought": "Climatological",
    "Heat Wave": "Climatological",
    "Cold Wave": "Climatological",


    "Epidemic": "Biological",
    "Pandemic": "Biological",


    "Earthquake": "Geophysical",
    "Tsunami": "Geophysical",
    "Volcanic eruption": "Geophysical",
    "Landslide": "Geophysical",


    "Cyclone": "Meteorological",
    "Storm": "Meteorological",


    "Flood": "Hydrological",
    "Flash Flood": "Hydrological",


    "Wildfire": "Non-technological and man-made",
    "Fire": "Non-technological and man-made",


    "Population movement": "Human-related",
    
    "Complex Emergency": "Complex Emergency",


    "Other": "Other"
    }


# -----------------------------
# PEOPLE PER UNIT
# -----------------------------

PEOPLE_PER_UNIT = {

    # Water
    "well":400,
    "borehole":500,
    "pump":500,
    "tank":500,
    "water_point":500,
    "water_treatment_plant":2000,

    # Sanitation
    "community_latrine":20,
    "family_latrine":5
}

# -----------------------------
# IGNORE
# -----------------------------

EXCLUDE_WORDS = [

    "%",

    "percent",
    "percentage",

    "volunteer",
    "volunteers",

    "training",
    "trainings",

    "liters",
    "litres",

    "bottle",
    "bottles",

    "water delivered",

    "cash",

    "meeting",
    "meetings",

    "assessment",
    "assessments",

    "monitoring"
]

# -----------------------------
# SAFE WATER
# -----------------------------
SAFE_WATER_ACCESS_KEYWORDS = [

    "access to safe water",
    "access to safe drinking water",
    "access to drinking water",
    "access to clean water",
    "access to potable water",
    "access to safe",
    "access to clean",
    "access to potable",


    "households with access to safe drinking water",
    "people with access to safe drinking water",

    "population with access to safe drinking water",

    "beneficiaries with access to safe water"

]
# -----------------------------
# WATER
# -----------------------------

WATER_KEYWORDS = {

    "well":[
        "well",
        "wells"
    ],

    "borehole":[
        "borehole",
        "boreholes",
        "bore hole",
        "bore holes"
    ],

    "pump":[
        "pump",
        "pumps"
    ],

    "water_point":[
        "water point",
        "water points",
        "water source",
        "water sources",
        "water supply point",
        "protected water source",
        "protected drinking water source"
    ],

    "tank":[
        "tank",
        "tanks",
        "water tank",
        "water tanks",
        "storage tank",
        "storage tanks"
    ],

    "water_treatment_plant":[
        "water treatment plant",
        "water treatment plants",
        "water purification plant",
        "water purification plants",
        "purification system",
        "treatment system"
    ],

    "chlorine_tablet":[
        "chlorine tablet",
        "chlorine tablets",
        "water purification tablet",
        "water purification tablets",
        "aquatab",
        "aquatabs"
    ]
}

SANITATION_KEYWORDS = {

    "community_latrine":[

        "latrine",
        "latrines",

        "community latrine",
        "community latrines",

        "communal latrine",
        "communal latrines",

        "pit latrine",
        "pit latrines",

        "toilet",
        "toilets",

        "vip toilet",
        "vip toilets",

        "vip latrine",
        "vip latrines",

        "sanplat",
        "sanplats"
    ],

    "family_latrine":[

        "family latrine",
        "family latrines",

        "household latrine",
        "household latrines",

        "family toilet",
        "family toilets",

        "household toilet",
        "household toilets"
    ]
}

# -----------------------------
# HYGIENE
# -----------------------------

HYGIENE_KEYWORDS = {

    "hygiene_promotion":[

        "hygiene promotion",

        "hygiene awareness",

        "hygiene education",

        "community hygiene",

        "behavior change",

        "behaviour change",

        "risk communication"
    ],

    "hygiene_kit":[
        "hygiene kit",
        "hygiene kits"
    ],

    "cleaning_kit":[
        "cleaning kit",
        "cleaning kits"
    ],

    "dignity_kit":[
        "dignity kit",
        "dignity kits"
    ],

    "mhm_kit":[
        "mhm kit",
        "mhm kits",

        "menstrual hygiene management kit",
        "menstrual hygiene management kits",

        "menstrual hygiene kit",
        "menstrual hygiene kits"
    ]
}

# -----------------------------
# NORMALIZE LLM OUTPUT
# -----------------------------

WATER_NORMALIZE = {
    "well": "well",
    "wells": "well",

    "borehole": "borehole",
    "boreholes": "borehole",

    "pump": "pump",
    "pumps": "pump",

    "tank": "tank",
    "tanks": "tank",

    "water point": "water_point",
    "water points": "water_point",
    "water_point": "water_point",
    "water_points": "water_point",

    "water treatment plant": "water_treatment_plant",
    "water treatment plants": "water_treatment_plant",
    "water_treatment_plant": "water_treatment_plant",
    "water_treatment_plants": "water_treatment_plant",

    "chlorine tablet": "chlorine_tablet",
    "chlorine tablets": "chlorine_tablet",
    "chlorine_tablet": "chlorine_tablet",
}

SANITATION_NORMALIZE = {
    "community latrine": "community_latrine",
    "community latrines": "community_latrine",
    "community_latrine": "community_latrine",
    "community_latrines": "community_latrine",

    "family latrine": "family_latrine",
    "family latrines": "family_latrine",
    "family_latrine": "family_latrine",
    "family_latrines": "family_latrine",

}

HYGIENE_NORMALIZE = {
    "hygiene promotion": "hygiene_promotion",
    "hygiene promotions": "hygiene_promotion",
    "hygiene_promotion": "hygiene_promotion",
    "hygiene_promotions": "hygiene_promotion",

    "hygiene kit": "hygiene_kit",
    "hygiene kits": "hygiene_kit",
    "hygiene_kit": "hygiene_kit",
    "hygiene_kits": "hygiene_kit",

    "cleaning kit": "cleaning_kit",
    "cleaning kits": "cleaning_kit",
    "cleaning_kit": "cleaning_kit",
    "cleaning_kits": "cleaning_kit",

    "dignity kit": "dignity_kit",
    "dignity kits": "dignity_kit",
    "dignity_kit": "dignity_kit",
    "dignity_kits": "dignity_kit",

    "mhm kit": "mhm_kit",
    "mhm kits": "mhm_kit",
    "mhm_kit": "mhm_kit",
    "mhm_kits": "mhm_kit"
}

# -----------------------------
# PEOPLE AND HOUSEHOLD KEYWORDS
# -----------------------------

PEOPLE_WORDS = [

    "people",

    "person",

    "persons",

    "beneficiary",

    "beneficiaries",

    "individual",

    "individuals"
]

HOUSEHOLD_WORDS = [

    "household",
    "households",

    "family",
    "families",

    "hh",
    "hhs"
]

def r(results, infra, field):
    return results[infra][field]

 # -----------------------------
   # FINANCE TABLE HELPERS
   # -----------------------------
def extract_numbers(row):
  
    numbers = []


    for cell in row:
        if not cell:
            continue


        matches = re.findall(
            r'-?\d+(?:[.,]\d{3})*',
            str(cell)
        )


        numbers.extend(matches)


    return numbers


def extract_currency_values(row_text):


    return re.findall(
        r'-?\d+(?:[.,]\d{3})*',
        row_text
    )




def to_number(value):


    if value is None:
        return None


    value = str(value).strip()


    # Remove thousands separators
    value = value.replace(",", "")
    value = value.replace(".", "")


    try:
        return int(value)
    except ValueError:
        return None
    
   # -----------------------------
   # FINANCE TABLE
   # -----------------------------
def extract_financials(pdf_url):


    # grand total
    grand_budget = None
    grand_expenditure = None


    # planned operations total
    po_budget = None
    po_expenditure = None


    # WASH planned operations 
    wash_po_budget = None
    wash_po_expenditure = None


    # WASH relief items, construction, and supplies
    wash_rcs_budget = None
    wash_rcs_expenditure = None 

    try:
        r = requests.get(
                pdf_url,
                timeout=30,
                verify=False
            )
        with open("temp.pdf", "wb") as f:
            f.write(r.content)


        with pdfplumber.open("temp.pdf") as pdf:


            for page_num, page in enumerate(pdf.pages, start=1):


                if page_num > 2:
                    continue
                
                tables = page.extract_tables()


                for table in tables:


                    for row in table:
                        if not row:
                            continue


                        row_text = " ".join(str(x) for x in row if x)


                        if "Grand Total" in row_text:
                            nums = extract_numbers(row)

                            if len(nums) >= 2:
                                grand_budget = nums[0]
                                grand_expenditure = nums[1]




                        if "Planned Operations Total" in row_text or "Area of focus Total" in row_text:
                            nums = extract_numbers(row)


                            if len(nums) > 2:
                                po_budget = nums[0]
                                po_expenditure = nums[1]
                                if po_expenditure == "0":
                                    po_expenditure = None


                            if len(nums) == 2:
                                po_expenditure = nums[0]

                        # WASH planned operations
                        if (
                            ("PO05" in row_text or "AOF5" in row_text)
                            and ("Water, Sanitation" in row_text or "Water, sanitation" in row_text)
                        ):


                            budget_cell = row[1] if len(row) > 1 else ""
                            expenditure_cell = row[2] if len(row) > 2 else ""


                            wash_po_budget = to_number(budget_cell)


                            if expenditure_cell.strip():
                                wash_po_expenditure = to_number(expenditure_cell)
                            else:
                                wash_po_expenditure = 0


                        # WASH relief items, construction, and supplies
                        if (
                            ("Water, Sanitation" in row_text or "Water, sanitation" in row_text)
                            and "CAX" in row_text
                        ):


                            nums = extract_numbers(row)


                            # remove the accidental "AX" matches etc.
                            nums = [n for n in nums if n not in ["0", "05"]]


                            if len(nums) >= 3:
                                wash_rcs_budget = to_number(nums[-3])
                                wash_rcs_expenditure = to_number(nums[-2])


                            elif len(nums) == 2:
                                # one column blank
                                first = row[-3] if len(row) >= 3 else ""
                                second = row[-2] if len(row) >= 2 else ""


                                wash_rcs_budget = to_number(first) if first.strip() else 0
                                wash_rcs_expenditure = to_number(second) if second.strip() else 0




    except Exception as e:
        print("PDF error:", pdf_url, e)


    if os.path.exists("temp.pdf"):
        os.remove("temp.pdf")

    return (
            grand_budget,
            grand_expenditure,
            po_budget,
            po_expenditure,
            wash_po_budget,
            wash_po_expenditure,
            wash_rcs_budget,
            wash_rcs_expenditure
        )



# -----------------------------
# AI PROMPT
# -----------------------------
def extract_water_data(wash_text, indicators):

    prompt = f"""
You are an expert humanitarian data annotator.

Your task is to create a structured research dataset from an IFRC DREF report.

Read BOTH:

1. The WASH indicators.
2. The narrative text.

The narrative often contains more complete information than the indicators.

If both contain the same information, combine them.

If they disagree, prefer the source that appears more complete and internally consistent.

Do NOT invent numbers.
Your response will be parsed automatically by Python.

Return STRICT JSON only.

Do not use markdown.

Do not use comments.

Do not use //.

Do not use /* */.

Do not explain your reasoning.

Every key and every string must be enclosed in double quotes.

The response must be valid json.loads().

--------------------------------------------------
EXTRACT THREE SECTORS
--------------------------------------------------

1. WATER

Extract:

- wells
- boreholes
- pumps
- water points
- water tanks
- water treatment plants
- chlorine tablets

2. SANITATION

Extract:

- community latrines
- family latrines
- toilets
- VIP toilets
- Sanplats

Treat toilets, pit latrines, VIP toilets and Sanplats as community_latrine unless the report explicitly says they are family or household latrines.

3. HYGIENE

Extract:

- hygiene promotion
- hygiene kits
- dignity kits
- MHM kits
- cleaning kits

For kits, if both procured and distributed are reported, use the distributed number.

Never invent new type names.

If an item does not fit one of these categories, do not extract it.

If no water items are found, return

"water": []

If no sanitation items are found, return

"sanitation": []

If no hygiene items are found, return
"hygiene": []

Do not add comments.
Do not explain why.
Do not include any text outside the JSON.

--------------------------------------------------
BENEFICIARIES
--------------------------------------------------

If beneficiaries are reported:

store the reported number.

If households or families are reported:

multiply by 5.

If beneficiaries are not reported:

return null.

Never estimate beneficiaries yourself.

If the report explicitly states households or families,
store BOTH:

households_helped

and

people_helped

where people_helped = households × 5.


If multiple beneficiary counts are reported for the same activity:

Prefer

1. Direct beneficiaries

2. Households converted to people

3. Total beneficiaries

4. Indirect beneficiaries

Only use indirect beneficiaries if no direct beneficiary count exists.

Do not add direct and indirect beneficiaries together unless the report explicitly states they are separate non-overlapping groups.

--------------------------------------------------
IGNORE
--------------------------------------------------

Ignore:

- volunteers
- trainings
- meetings
- assessments
- monitoring
- percentages
- litres of water delivered
- budgets
- procurement
- logistics

--------------------------------------------------
EVIDENCE
--------------------------------------------------

For every extracted item include:

- evidence

The evidence must be copied exactly from the report.

--------------------------------------------------
CONFIDENCE
--------------------------------------------------

Return:

high
medium
low

High:
The report clearly states the infrastructure and quantities.

Medium:
The wording is slightly ambiguous but likely correct.

Low:
The extraction required interpretation.

--------------------------------------------------
SOURCE
--------------------------------------------------

people_helped_source must be ONE of:

reported
households
estimated

"estimated" means beneficiaries were not reported.

--------------------------------------------------
CONFLICTS
--------------------------------------------------

If the indicators and narrative disagree:

1. Choose the value you believe is most accurate for "count".

2. Record the indicator value in:

indicator_count

3. Record the narrative value in:

narrative_count

4. Briefly explain the disagreement in the "notes" section.

--------------------------------------------------
OVERLAPPING BENEFICIARIES
--------------------------------------------------

Determine whether the beneficiaries of the water interventions
appear to overlap across the report.

Return ONE top-level value:

"water_overlap"

Choose:

-"same" → the report clearly indicates the same population benefited from multiple water interventions
(for example, the same households received both chlorine tablets and water from rehabilitated boreholes).

-"different" → the report clearly indicates different communities, villages, districts, or beneficiary groups received different water interventions.

- "unknown" → the report does not provide enough information to determine
  whether the beneficiary populations overlap.

Do not guess.

If there is not enough information, always return "unknown".



--------------------------------------------------
OUTPUT
--------------------------------------------------

Return ONLY valid JSON.

{{
    "water_overlap":"unknown",
    "water":[
        {{ 
            "type":"",
            "action":"",
            "count":0,
            "people_helped":null,
            "households_helped":null,
            "people_helped_source":"",
            "confidence":"",
            "evidence":"",
            "indicator_count":null,
            "narrative_count":null
        }}
    ],

    "sanitation":[
        {{
            "type":"",
            "action":"",
            "count":0,
            "people_helped":null,
            "people_helped_source":"",
            "confidence":"",
            "evidence":"",
            "indicator_count":null,
            "narrative_count":null
        }}
    ],

    "hygiene":[
        {{
            "type":"",
            "action":"",
            "count":0,
            "people_helped":null,
            "people_helped_source":"",
            "confidence":"",
            "evidence":"",
            "indicator_count":null,
            "narrative_count":null
        }}
    ],

    "notes":[]
}}

Use "notes" for anything important, for example:

- indicators and narrative disagree
- multiple beneficiary values reported
- infrastructure mentioned but no quantity given
- uncertainty about infrastructure type

Indicators

{json.dumps(indicators, indent=2)}

Narrative

{wash_text}
"""

    import time

    print("Calling Gemini...")
    start = time.time()

    for attempt in range(5):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            break

        except Exception as e:

            print(f"Gemini failed ({attempt+1}/5): {e}")

            if attempt == 4:
                raise

            print("Waiting 10 seconds before retrying...")
            time.sleep(10)

    print(f"Gemini finished in {time.time()-start:.1f} seconds")

    print("\n========== GEMINI ==========")
    print(response.text)
    print("============================\n")

    text = response.text.strip()

    # Remove markdown fences if Gemini adds them
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)

    except Exception:
        print("\nFAILED TO PARSE JSON:")
        print(text)
        raise

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def count(results, infra):
    return results[infra]["final_count"]

def people(results, infra):
    return results[infra]["final_people"]

def evidence(results, infra):
    return "; ".join(results[infra]["evidence"])

def confidence(results, infra):
    return results[infra]["confidence"]


   
# -----------------------------
# CACHE FUNCTION
# -----------------------------
def load_or_extract_llm(appeal_code, wash_text, indicators):

    cache_file = os.path.join(
        CACHE_FOLDER,
        f"{appeal_code}_{PROMPT_VERSION}.json"
    )

    if os.path.exists(cache_file):

        with open(cache_file, "r") as f:
            return json.load(f)

    result = extract_water_data(
        wash_text,
        indicators
    )

    with open(cache_file, "w") as f:
        json.dump(result, f, indent=2)

    return result

# -----------------------------
# OUTPUT FILE
# -----------------------------
f = open(
    "dref_summary.csv",
    "w",
    newline="",
    encoding="utf-8"
)

writer = csv.writer(f)


writer.writerow([
    "Country",
    "Zone",
    "Start Date",
    "End Date",
    "Year",
    "Disaster Type",
    "Disaster Category",
    "Appeal Code",
    "Total Number of People Helped",
    "Total Budget (CHF)",
    "Total Expenditure (CHF)",
    "Planned Operations Budget (CHF)",
    "Planned Operations Expenditure (CHF)",
    "WASH Planned Operations Budget (CHF)",
    "WASH Planned Operations Expenditure (CHF)",
    "WASH Relief Items, Construction, Supplies Budget (CHF)",
    "WASH Relief Items, Construction, Supplies Expenditure (CHF)",
    "WASH Target Number of People Helped (stated)",
    "WASH Actual Number of People Helped (stated)",
    "WASH Budget (CHF) (stated)", 

    "Water People Reached",
    "Sanitation People Reached",
    "Hygiene People Reached",

    "LLM Notes",
    "Flags",
    "Water Overlap",

    "People reached by Safe Water Access",

    "Wells",
    "People Helped by Wells",
    "Evidence for Wells",
    "Confidence for Wells",

    "Boreholes",
    "People Helped by Boreholes",
    "Evidence for Boreholes",
    "Confidence for Boreholes",

    "Pumps",
    "People Helped by Pumps",
    "Evidence for Pumps",
    "Confidence for Pumps",

    "Water Treatment Plants",
    "People Helped by Water Treatment Plants",
    "Evidence for Water Treatment Plants",
    "Confidence for Water Treatment Plants",

    "Tanks",
    "People Helped by Tanks",
    "Evidence for Tanks",
    "Confidence for Tanks",

    "Water Points",
    "People Helped by Water Points",
    "Evidence for Water Points",
    "Confidence for Water Points",

    "Chlorine Tablets",
    "People Helped by Chlorine Tablets",
    "Evidence for Chlorine Tablets",
    "Confidence for Chlorine Tablets",

    "Community Latrines",
    "People Helped by Community Latrines",
    "Evidence for Community Latrines",
    "Confidence for Community Latrines",

    "Family Latrines",
    "People Helped by Family Latrines",
    "Evidence for Family Latrines",
    "Confidence for Family Latrines",

    "Hygiene Promotion",
    "People Helped by Hygiene Promotion",
    "Evidence for Hygiene Promotion",
    "Confidence for Hygiene Promotion",

    "Hygiene Kits",
    "People Helped by Hygiene Kits",
    "Evidence for Hygiene Kits",
    "Confidence for Hygiene Kits",

    "Cleaning Kits",
    "People Helped by Cleaning Kits",
    "Evidence for Cleaning Kits",
    "Confidence for Cleaning Kits",

    "Dignity Kits",
    "People Helped by Dignity Kits",
    "Evidence for Dignity Kits",
    "Confidence for Dignity Kits",

    "MHM Kits",
    "People Helped by MHM Kits",
    "Evidence for MHM Kits",
    "Confidence for MHM Kits"

])

review_file = open(
    "manual_review.csv",
    "w",
    newline="",
    encoding="utf-8"
)
review_writer = csv.writer(review_file) 

review_writer.writerow([
    "Appeal Code",
    "Country",
    "Flags"
])

total_reports = len(data)

for i, record in enumerate(data, start=1):

        appeal = record.get("appeal_code", "Unknown")
        country = record.get("country_details", {}).get("name", "Unknown")

        print(f"\n[{i}/{total_reports}] {appeal} - {country}")



        # zone
        zone = zone_map.get(country, "Unknown")


        # dates
        start_date = record.get("operation_start_date")
        end_date = record.get("operation_end_date")


        year = (
            datetime.strptime(start_date, "%Y-%m-%d").year
            if start_date else None
    )


        # disaster type
        disaster = record.get("disaster_type_details", {}).get("name", "Unknown")


        disaster_category = disaster_map.get(disaster, "Other")


        # appeal code
        appeal = record.get("appeal_code")


        num_assisted = record.get("num_assisted")

        # -----------------------------
        # WASH DATA
        # -----------------------------
        wash_targeted = 0
        wash_assisted = 0
        wash_budget = 0

        # ======================================================
        # MASTER RESULTS
        # ======================================================

        results = {}

        ALL_TYPES = [

            # -----------------
            # WATER
            # -----------------

            "well",
            "borehole",
            "pump",
            "water_point",
            "tank",
            "water_treatment_plant",
            "chlorine_tablet",

            # -----------------
            # SANITATION
            # -----------------

            "community_latrine",
            "family_latrine",

            # -----------------
            # HYGIENE
            # -----------------

            "hygiene_promotion",
            "hygiene_kit",
            "cleaning_kit",
            "dignity_kit",
            "mhm_kit"
        ]

        for item in ALL_TYPES:

            results[item] = {

                "indicator_count":0,

                "indicator_people":0,

                "llm_count":0,

                "llm_people":0,

                "final_count":0,

                "final_people":0,

                "confidence":"",

                "evidence":[],

                "source":"",

                "method":"",

                "indicator_count_llm":None,

                "narrative_count_llm":None,

            }


        safe_water_access_people = 0    
        safe_water_access_households = 0
        llm_notes = ""
        review_flags = []
        water_overlap = "unknown"


        for intervention in record.get("planned_interventions", []):

            if intervention.get("title") != "water_sanitation_and_hygiene":
                continue

            wash_targeted += intervention.get("person_targeted") or 0
            wash_assisted += intervention.get("person_assisted") or 0
            wash_budget += intervention.get("budget") or 0

            wash_text = "\n\n".join([
                intervention.get("description") or "",
                intervention.get("narrative_description_of_achievements") or "",
                intervention.get("lessons_learnt") or "",
                intervention.get("challenges") or ""
            ])

            llm = load_or_extract_llm(
                appeal,
                wash_text,
                intervention.get("indicators", [])
            )

            llm_notes = "; ".join(
                llm.get("notes", [])
            )

            water_overlap = llm.get(
                "water_overlap",
                "unknown"
            )

            print("LLM output:")
            print(json.dumps(llm, indent=2))


            # -----------------------------
            # LLM RESULTS
            # -----------------------------

            for item in llm.get("water", []):

                infra = item.get("type")

                infra = (infra or "").lower().strip()

                infra = WATER_NORMALIZE.get(infra, infra)

                if infra not in results:
                    continue

                results[infra]["llm_count"] += item.get("count") or 0

                if item.get("people_helped") is not None:
                    results[infra]["llm_people"] += item.get("people_helped") or 0

                results[infra]["source"] = item.get(
                    "people_helped_source",
                    "estimated"
                )

                if item.get("evidence"):
                    evidence_text = item.get("evidence", "")

                    if evidence_text:
                        results[infra]["evidence"].append(evidence_text)

                if item.get("confidence"):
                    results[infra]["confidence"] = item.get("confidence", "")

                results[infra]["indicator_count_llm"] = item.get("indicator_count")
                results[infra]["narrative_count_llm"] = item.get("narrative_count")

            for item in llm.get("sanitation", []):

                infra = item.get("type")

                infra = (infra or "").lower().strip()

                infra = SANITATION_NORMALIZE.get(infra, infra)

                if infra not in results:
                    continue


                results[infra]["llm_count"] += item.get("count") or 0

                if item.get("people_helped") is not None:
                    results[infra]["llm_people"] += item.get("people_helped") or 0

                results[infra]["source"] = item.get(
                    "people_helped_source",
                    "estimated"
                )

                if item.get("evidence"):
                    evidence_text = item.get("evidence", "")

                    if evidence_text:
                        results[infra]["evidence"].append(evidence_text)

                if item.get("confidence"):
                    results[infra]["confidence"] = item.get("confidence", "")

                results[infra]["indicator_count_llm"] = item.get("indicator_count")
                results[infra]["narrative_count_llm"] = item.get("narrative_count")

            for item in llm.get("hygiene", []):

                infra = item.get("type")

                infra = (infra or "").lower().strip()

                infra = HYGIENE_NORMALIZE.get(infra, infra)

                if infra not in results:
                    continue

                results[infra]["llm_count"] += item.get("count") or 0

                if item.get("people_helped") is not None:
                    results[infra]["llm_people"] += item.get("people_helped") or 0

                results[infra]["source"] = item.get(
                    "people_helped_source",
                    "estimated"
                )

                if item.get("evidence"):
                    evidence_text = item.get("evidence", "")

                    if evidence_text:
                        results[infra]["evidence"].append(evidence_text)

                if item.get("confidence"):
                    results[infra]["confidence"] = item.get("confidence", "")     

                results[infra]["indicator_count_llm"] = item.get("indicator_count")
                results[infra]["narrative_count_llm"] = item.get("narrative_count")       

            # -----------------------------
            # INDICATORS
            # -----------------------------

            for indicator in intervention.get("indicators", []):

                title = (indicator.get("title") or "").lower()

                actual = indicator.get("actual") or 0

                if any(k in title for k in SAFE_WATER_ACCESS_KEYWORDS):

                    if any(word in title for word in HOUSEHOLD_WORDS):

                        safe_water_access_households = max(
                            safe_water_access_households,
                            actual
                        )

                    elif any(word in title for word in PEOPLE_WORDS):

                        safe_water_access_people = max(
                            safe_water_access_people,
                            actual
                        )

                if any(word in title for word in EXCLUDE_WORDS):
                    continue

                # ------------------------------------------------
                # WATER
                # ------------------------------------------------

                for infra, keywords in WATER_KEYWORDS.items():

                    if any(word in title for word in keywords):

                        results[infra]["evidence"].append(
                            f"Indicator: {indicator.get('title')}"
                        )

                        if any(word in title for word in PEOPLE_WORDS):

                            results[infra]["indicator_people"] += actual

                        elif any(word in title for word in HOUSEHOLD_WORDS):

                            results[infra]["indicator_people"] += actual * 5

                        else:

                            results[infra]["indicator_count"] += actual

                # ------------------------------------------------
                # SANITATION
                # ------------------------------------------------

                for infra, keywords in SANITATION_KEYWORDS.items():

                    if any(word in title for word in keywords):

                        results[infra]["evidence"].append(
                            f"Indicator: {indicator.get('title')}"
                        )

                        if any(word in title for word in PEOPLE_WORDS):

                            results[infra]["indicator_people"] += actual

                        elif any(word in title for word in HOUSEHOLD_WORDS):

                            results[infra]["indicator_people"] += actual * 5

                        else:

                            results[infra]["indicator_count"] += actual

                # ------------------------------------------------
                # HYGIENE
                # ------------------------------------------------

                for infra, keywords in HYGIENE_KEYWORDS.items():

                    if any(word in title for word in keywords):

                        results[infra]["evidence"].append(
                            f"Indicator: {indicator.get('title')}"
                        )

                        if infra == "hygiene_promotion":

                            if any(word in title for word in PEOPLE_WORDS):

                                results[infra]["indicator_people"] += actual

                            elif any(word in title for word in HOUSEHOLD_WORDS):

                                results[infra]["indicator_people"] += actual * 5

                        else:

                            if any(word in title for word in PEOPLE_WORDS):

                                results[infra]["indicator_people"] += actual

                            elif any(word in title for word in HOUSEHOLD_WORDS):

                                results[infra]["indicator_people"] += actual * 5

                            else:

                                results[infra]["indicator_count"] += actual

        # ======================================================
        # MERGE RESULTS
        # ======================================================

        for infra, data in results.items():

            # -----------------------------
            # COUNT
            # -----------------------------

            if data["llm_count"] > 0:

                data["final_count"] = data["llm_count"]

            else:

                data["final_count"] = data["indicator_count"]


            # -----------------------------
            # PEOPLE HELPED
            # -----------------------------

            if data["llm_people"] > 0:

                data["final_people"] = data["llm_people"]

            elif data["indicator_people"] > 0:

                data["final_people"] = data["indicator_people"]

            elif infra in PEOPLE_PER_UNIT:

                data["final_people"] = (
                    data["final_count"]
                    * PEOPLE_PER_UNIT[infra]
                )

                if data["source"] == "":

                    data["source"] = "estimated"

            else:

                data["final_people"] = 0

        # Remove duplicate evidence

        for infra in results:

            results[infra]["evidence"] = list(
                dict.fromkeys(results[infra]["evidence"])
            )

        # ======================================================
        # SAFE WATER ACCESS
        # ======================================================

        if safe_water_access_households > 0:

            safe_water_access_people = max(

                safe_water_access_people,

                safe_water_access_households * 5

            )

        # ======================================================
        # CONFIDENCE
        # ======================================================

        for infra, data in results.items():

            if data["confidence"]:

                continue

            if data["llm_people"] > 0:

                data["confidence"] = "high"

            elif data["indicator_people"] > 0:

                data["confidence"] = "high"

            elif data["final_count"] > 0:

                data["confidence"] = "medium"

            else:

                data["confidence"] = "low"

        # ======================================================
        # EVIDENCE
        # ======================================================

        for infra, data in results.items():

            if data["evidence"]:

                continue

            if data["indicator_count"] > 0:

                data["evidence"].append("Indicator")

            elif data["indicator_people"] > 0:

                data["evidence"].append("Indicator")

            elif data["llm_count"] > 0:

                data["evidence"].append("Narrative")

            elif data["llm_people"] > 0:

                data["evidence"].append("Narrative")

            else:

                data["evidence"] = []

        # ======================================================
        # SOURCE
        # ======================================================

        for infra, data in results.items():

            if data["source"]:

                continue

            if data["llm_people"] > 0:

                data["source"] = "reported"

            elif data["indicator_people"] > 0:

                data["source"] = "reported"

            elif data["final_count"] > 0:

                data["source"] = "estimated"

            else:

                data["source"] = ""

        # ======================================================
        # EVIDENCE
        # ======================================================

        for infra, data in results.items():
            if data["llm_people"] > 0:

                data["method"] = "Narrative"

            elif data["indicator_people"] > 0:

                data["method"] = "Indicator"

            elif data["final_count"] > 0:

                data["method"] = "Sphere estimate"


         # ======================================================
        # FINANCIALS
        # ======================================================
        financial_report = record.get("financial_report_details") or {}
        pdf_url = financial_report.get("file")


        if not pdf_url:
            grand_budget = None
            grand_expenditure = None
            po_budget = None
            po_expenditure = None
            wash_po_budget = None
            wash_po_expenditure = None
            wash_rcs_budget = None
            wash_rcs_expenditure = None
        else:
            grand_budget, grand_expenditure, po_budget, po_expenditure, wash_po_budget, wash_po_expenditure, wash_rcs_budget, wash_rcs_expenditure = extract_financials(pdf_url)

         # convert to numbers
        grand_budget = to_number(grand_budget)
        grand_expenditure = to_number(grand_expenditure)


        po_budget = to_number(po_budget)
        po_expenditure = to_number(po_expenditure)


        wash_po_budget = to_number(wash_po_budget)
        wash_po_expenditure = to_number(wash_po_expenditure)


        wash_rcs_budget = to_number(wash_rcs_budget)
        wash_rcs_expenditure = to_number(wash_rcs_expenditure)


        #-----------------------------
        # Totals
        #-----------------------------
        
        water_total = [

            safe_water_access_people,

            people(results, "well"),
            people(results, "borehole"),
            people(results, "pump"),
            people(results, "tank"),
            people(results, "water_point"),
            people(results, "water_treatment_plant"),
            people(results, "chlorine_tablet")
        ]

        water_total = [x for x in water_total if x > 0]

        if not water_total:

            water_total = 0

        elif water_overlap == "same":

            water_total = max(water_total)

        elif water_overlap == "different":

            water_total = sum(water_total)

        else:
            # unknown -> conservative estimate
            water_total = max(water_total)


        sanitation_total = sum(
            people(results,infra)
            for infra in ["community_latrine","family_latrine"]
        )
        
        hygiene_total = max(
            people(results,"hygiene_promotion"),
            people(results,"hygiene_kit"),
            people(results,"cleaning_kit"),
            people(results,"dignity_kit"),
            people(results,"mhm_kit")
        )



        #-----------------------------
        # FLAGS
        #-----------------------------
        if wash_budget > 0 and wash_po_expenditure in [0, None]:
            review_flags.append(
                "WASH activity but no WASH expenditure"
            )

        if wash_po_expenditure not in [0, None] and wash_budget == 0:
            review_flags.append(
                "WASH expenditure but no WASH activity"
            )

        if (
            wash_budget == 0
            and wash_targeted == 0
            and wash_assisted == 0
        ):
            review_flags.append(
                "No WASH activities reported"
            )

        if not pdf_url:
            review_flags.append(
                "Missing financial report"
            )


        for infra, data in results.items():

            if (
                data["indicator_count_llm"] is not None
                and data["narrative_count_llm"] is not None
                and data["indicator_count_llm"]
                    != data["narrative_count_llm"]
            ):

                review_flags.append(
                    f"{infra}: indicator/narrative disagreement"
                )

        if (
            wash_po_expenditure not in [0, None]
            and water_total == 0
            and sanitation_total == 0
            and hygiene_total == 0
        ):
            review_flags.append(
                "WASH expenditure but no water, sanitation or hygiene beneficiaries extracted"
            )

        if (
            count(results, "chlorine_tablet") > 0
            and people(results, "chlorine_tablet") == 0
        ):
            review_flags.append(
                "Chlorine tablets reported but beneficiaries unknown"
            )


        writer.writerow([
            country,
            zone,
            start_date,
            end_date,
            year,
            disaster,
            disaster_category,
            appeal,
            num_assisted,
            grand_budget,
            grand_expenditure,
            po_budget,
            po_expenditure,
            wash_po_budget,
            wash_po_expenditure,
            wash_rcs_budget,
            wash_rcs_expenditure,
            wash_targeted,
            wash_assisted,
            wash_budget, 
            water_total,
            sanitation_total,
            hygiene_total,

            llm_notes,
            "; ".join(review_flags),
            water_overlap,

            safe_water_access_people,

            r(results,"well","final_count"),
            r(results,"well","final_people"),
            evidence(results,"well"),
            r(results,"well","confidence"),

            r(results,"borehole","final_count"),
            r(results,"borehole","final_people"),
            evidence(results,"borehole"),
            r(results,"borehole","confidence"),

            r(results,"pump","final_count"),
            r(results,"pump","final_people"),
            evidence(results,"pump"),
            r(results,"pump","confidence"),

            r(results,"water_treatment_plant","final_count"),
            r(results,"water_treatment_plant","final_people"),
            evidence(results,"water_treatment_plant"),
            r(results,"water_treatment_plant","confidence"),

            r(results,"tank","final_count"),
            r(results,"tank","final_people"),
            evidence(results,"tank"),
            r(results,"tank","confidence"),
            
            r(results,"water_point","final_count"),
            r(results,"water_point","final_people"),
            evidence(results,"water_point"),
            r(results,"water_point","confidence"),

            r(results,"chlorine_tablet","final_count"),
            r(results,"chlorine_tablet","final_people"),
            evidence(results,"chlorine_tablet"),
            r(results,"chlorine_tablet","confidence"),

            r(results,"community_latrine","final_count"),
            r(results,"community_latrine","final_people"),
            evidence(results,"community_latrine"),
            r(results,"community_latrine","confidence"),

            r(results,"family_latrine","final_count"),
            r(results,"family_latrine","final_people"),
            evidence(results,"family_latrine"),
            r(results,"family_latrine","confidence"),

            r(results,"hygiene_promotion","final_count"),
            r(results,"hygiene_promotion","final_people"),
            evidence(results,"hygiene_promotion"),
            r(results,"hygiene_promotion","confidence"),

            r(results,"hygiene_kit","final_count"),
            r(results,"hygiene_kit","final_people"),
            evidence(results,"hygiene_kit"),
            r(results,"hygiene_kit","confidence"),

            r(results,"cleaning_kit","final_count"),
            r(results,"cleaning_kit","final_people"),
            evidence(results,"cleaning_kit"),
            r(results,"cleaning_kit","confidence"),

            r(results,"dignity_kit","final_count"),
            r(results,"dignity_kit","final_people"),
            evidence(results,"dignity_kit"),
            r(results,"dignity_kit","confidence"),

            r(results,"mhm_kit","final_count"),
            r(results,"mhm_kit","final_people"),
            evidence(results,"mhm_kit"),
            r(results,"mhm_kit","confidence")
        ])

        if review_flags:

            review_writer.writerow([
                appeal,
                country,
                "; ".join(review_flags)
            ])

print("Done! Created dref_summary.csv")
f.close()
review_file.close() 
        
            