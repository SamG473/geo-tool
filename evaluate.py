from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

category = "barber"
location = "Cardiff"

def judge(business, answer):
    prompt = f"""You are checking whether one specific business appears in a block of text.

Business name: "{business}"
Category: {category}
Location: {location}

The text below is an AI assistant's answer to a question about {category} businesses in {location}. Decide whether this specific business appears anywhere in it — whether as the main recommendation, one option in a list, or any passing mention. Count it as a match even if the name is shortened or written slightly differently, as long as it clearly refers to the same business. Do NOT count a different business that merely shares a common word with it.

Answer with a single word — "yes" if the business appears, or "no" if it does not.

Text:
{answer}"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text.strip()

# A real answer you already paid for last run — pasted in so we reuse it for free.
ANSWER = """If you're looking for a barber in Cardiff, here are good options:

- Jones The Barber - 45 Castle Arcade, city centre. Traditional, central Cardiff barber, established 2015.
- Lazarou Barbers Cardiff Castle - 1 Duke Street Arcade, opposite Cardiff Castle. Modern cuts, skin fades, hot towel shaves; South Wales brand since 1966.
- Rume Barbershop - 828 Newport Road, Rumney. Adult cut £24, skin fade £28, haircut & beard trim £28.
- Bears Barbershop - Cardiff Bay, Mount Stuart Square. Popular Cardiff Bay option.
- Bonnie & Clyde Barber Shop - 99 Queen Street, city centre. Central haircuts and beard trims.

Quick pick: city centre - Jones The Barber or Lazarou. Skin fade - Lazarou or Rume. Cardiff Bay - Bears."""

# You decide the correct answer for each name. The judge has to match you.
test_cases = [
    ("Lazarou Barbers",   "HIT"),   # really there
    ("Jones the Barber",  "HIT"),   # really there — "jones" is the kind of name string matching trips on
    ("The Barber Shop",   "MISS"),  # all generic words — no business actually called this
    ("City Cuts",         "MISS"),  # "city" shows up ("city centre"), but there's no "City Cuts"
    ("Sharkey's Barbers", "MISS"),  # totally absent — sanity check it doesn't just say yes to everything
]

for business, expected in test_cases:
    raw = judge(business, ANSWER)
    verdict = "HIT" if raw.lower().startswith("y") else "MISS"
    result = "ok" if verdict == expected else "WRONG"
    print(f"{business:<20} expected {expected:<5} got {verdict:<5} [{result}]")