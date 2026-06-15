from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

queries = [
    "best barber in Cardiff",
    "top-rated barber in Cardiff",
    "recommend a barber in Cardiff",
]
business = "Lazarou Barbers"

hits = 0                      # ← counter, starts at zero

for query in queries:
    response = client.responses.create(
        model="gpt-5.5",
        input=query
    )
    answer = response.output_text
    if business.lower() in answer.lower():
        print(f"✅ {query}")
        hits += 1            # ← add one each time it appears
    else:
        print(f"❌ {query}")

score = hits / len(queries) * 100        # ← hits ÷ total, as a %
print(f"\n{business} share of voice: {score:.0f}%")