import re
from wordfreq import zipf_frequency
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

LEGAL_SUFFIXES = {"ltd", "limited", "inc", "llc", "co", "plc", "company"}

def distinctive_tokens(name, category, location, threshold=2.5):
    drop = {category.lower(), category.lower() + "s", location.lower()} | LEGAL_SUFFIXES
    clean = re.sub(r"[^\w\s]", " ", name.lower())
    tokens = [t for t in clean.split() if t not in drop]
    return [t for t in tokens if zipf_frequency(t, "en") < threshold]

def has_anchor(name, category, location):
    return len(distinctive_tokens(name, category, location)) > 0

def cheap_match(name, answer, category, location):
    terms = distinctive_tokens(name, category, location)
    answer_lower = answer.lower()
    return all(re.search(rf"\b{re.escape(t)}\b", answer_lower) for t in terms)

def judge(name, answer, category, location):
    prompt = f"""You are checking whether one specific business appears in a block of text.

Business name: "{name}"
Category: {category}
Location: {location}

The text below is an AI assistant's answer to a question about {category} businesses in {location}. Decide whether this specific business appears anywhere in it — whether as the main recommendation, one option in a list, or any passing mention. Count it as a match even if the name is shortened or written slightly differently, as long as it clearly refers to the same business. Do NOT count a different business that merely shares a common word with it.

Answer with a single word — "yes" if the business appears, or "no" if it does not.

Text:
{answer}"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text.strip().lower().startswith("y")

def detect(name, answer, category, location):
    if has_anchor(name, category, location):
        return cheap_match(name, answer, category, location)
    return judge(name, answer, category, location)