import json
import re
from wordfreq import zipf_frequency

with open("latest_run.json", "r", encoding="utf-8") as f:
    run = json.load(f)

category = run["category"].strip().lower()
location = run["location"].strip().lower()

def distinctive_tokens(name, threshold=2.5):
    drop = {category, category + "s", location}
    tokens = [t for t in name.lower().split() if t not in drop]
    return [t for t in tokens if zipf_frequency(t, "en") < threshold]

def cheap_match(name, answer):
    terms = distinctive_tokens(name)
    answer_lower = answer.lower()
    return all(re.search(rf"\b{re.escape(t)}\b", answer_lower) for t in terms)

business = run["business"].strip()

for q in run["queries"]:
    answer_lower = q["answer"].lower()
    cheap = "HIT " if cheap_match(business, q["answer"]) else "MISS"
    in_text = "yes" if "lazarou" in answer_lower else "no"
    print(f"{cheap}  lazarou-in-text:{in_text}  {q['query']}")