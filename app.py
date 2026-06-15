import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

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
            if business.lower() in answer.lower():
                results.append(f"✅ {query}")
                hits += 1
            else:
                results.append(f"❌ {query}")

    score = hits / len(queries) * 100

    st.metric("Share of voice", f"{score:.0f}%")
    for line in results:
        st.write(line)