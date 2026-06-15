from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# --- the business being audited ---
business = "Lazarou Barbers"
category = "barber"
location = "Cardiff"

# --- 10 customer queries, built from category + location ---
queries = [
    f"best {category} in {location}",
    f"top-rated {category} in {location}",
    f"recommend a {category} in {location}",
    f"who are the best {category} in {location}",
    f"most popular {category} in {location}",
    f"affordable {category} in {location}",
    f"{category} in {location} city centre",
    f"where can I find a good {category} in {location}",
    f"{category} {location}",
    f"is there a good {category} in {location}",
]

hits = 0

for query in queries:
    response = client.responses.create(
        model="gpt-5.5",
        tools=[{"type": "web_search"}],
        input=query
    )
    answer = response.output_text
    if business.lower() in answer.lower():
        print(f"✅ {query}")
        hits += 1
    else:
        print(f"❌ {query}")

score = hits / len(queries) * 100
print(f"\n{business} share of voice: {score:.0f}%")