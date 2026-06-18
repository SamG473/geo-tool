import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def judge(business, answer, category, location):
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

st.title("GEO Audit Tool")
st.write("Check whether a business shows up in AI answers.")

business = st.text_input("Business name")
category = st.text_input("What they do (e.g. barber)")
location = st.text_input("Location (e.g. Cardiff)")

if st.button("Run audit"):
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
    results = []

    with st.spinner("Running audit, this takes a minute..."):
        for query in queries:
            response = client.responses.create(
                model="gpt-5.5",
                tools=[{"type": "web_search"}],
                input=query
            )
            answer = response.output_text

            raw = judge(business, answer, category, location)
            if raw.lower().startswith("y"):
                results.append(f"✅ {query}")
                hits += 1
            else:
                results.append(f"❌ {query}")

    score = hits / len(queries) * 100

    st.metric("Share of voice", f"{score:.0f}%")
    for line in results:
        st.write(line)