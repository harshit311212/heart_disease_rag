import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/query"

def ask(label, query):
    try:
        data = json.dumps({"query": query}).encode()
        req = urllib.request.Request(BASE_URL, method="POST",
              headers={"Content-Type": "application/json"}, data=data)
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        answer = res.get("answer", "")
        print(f"\n{'='*60}")
        print(f"[TEST] {label}")
        print(f"[Q]    {query}")
        print(f"[A]    {answer}")
    except Exception as e:
        print(f"\n[FAIL] {label}: {e}")
    time.sleep(1)  # avoid rate limiting

# ── CATEGORY 1: Exact numeric patient lookup ──────────────────────
ask("Exact match: 40M chol 289",
    "Tell me about the 40-year old male patient with a cholesterol of 289. Does he have heart disease?")

ask("Exact match: 49F chol 180",
    "Tell me about the 49-year old female patient with a cholesterol level of 180. Does she have heart disease?")

ask("Exact match: 37M chol 283",
    "Is there a 37-year old male patient with cholesterol 283? What is his heart disease status?")

ask("Exact match: 54M chol 195",
    "What can you tell me about the 54-year old male with cholesterol 195?")

# ── CATEGORY 2: HeartDisease=1 patients (model must say YES) ──────
ask("Must say YES: 49F chol 180",
    "Does the 49-year-old female with cholesterol 180 have heart disease?")

ask("Must say YES: 37M chol 207",
    "The 37-year-old male patient with cholesterol 207 - does he have heart disease?")

# ── CATEGORY 3: Ambiguous / multiple matches ──────────────────────
ask("Multiple matches: age only",
    "Tell me about 62-year-old male patients. Do any of them have heart disease?")

ask("Multiple matches: sex only",
    "List some female patients and whether they have heart disease.")

# ── CATEGORY 4: Borderline numbers (substring trap) ───────────────
ask("Substring trap: chol 28 (not 289)",
    "Is there a patient with cholesterol of 28?")

ask("Number in context phrase only",
    "What about patient number 10? Does he have heart disease?")

# ── CATEGORY 5: Aggregate / statistical questions ─────────────────
ask("Aggregate: count heart disease",
    "How many patients in the dataset have heart disease?")

ask("Aggregate: oldest patient",
    "Who is the oldest patient and do they have heart disease?")

ask("Aggregate: highest cholesterol",
    "Which patient has the highest cholesterol level?")

# ── CATEGORY 6: Feature-based semantic queries ────────────────────
ask("Semantic: exercise angina",
    "Which patients have exercise-induced angina and heart disease?")

ask("Semantic: fasting blood sugar",
    "Are patients with high fasting blood sugar more likely to have heart disease?")

ask("Semantic: ST slope",
    "What is the relationship between ST Slope and heart disease in this dataset?")

# ── CATEGORY 7: Out-of-domain / hallucination traps ───────────────
ask("Out of domain: geography",
    "What is the capital of France?")

ask("Out of domain: medicine not in data",
    "What medications should a heart disease patient take?")

ask("Hallucination trap: nonexistent patient",
    "Tell me about the 25-year-old female patient with a cholesterol of 999. Does she have heart disease?")

# ── CATEGORY 8: Edge wording variations ──────────────────────────
ask("Rewording: abbreviations",
    "Is the 40 yr old M patient with chol 289 positive for HD?")

ask("Rewording: informal",
    "the 40 year old guy with 289 cholesterol - does he have a heart problem?")

print("\n\n✅ All tests complete.")
