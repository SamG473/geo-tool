# GEO Audit Tool

Measure how often an AI search assistant recommends a given business — its
**share of voice** in generative search results.

As people increasingly ask LLM-backed assistants questions like *"best barber in
Cardiff"* instead of scrolling a results page, **being mentioned in the answer**
becomes the new ranking. This tool quantifies that: it puts a set of realistic
customer questions to a web-search-enabled model, then measures how often the
target business shows up across the answers.

The running example throughout is **Lazarou Barbers** — a barber in Cardiff.

---

## What it does

1. **Wizard** ([app.py](app.py)) collects the business name, category, location,
   and optional competitors.
2. **Audit pipeline** (`run_audit`) asks the model **10 templated search
   queries** (e.g. *"best {category} in {location}"*, *"affordable …"*,
   *"where can I find a good …"*) with the `web_search` tool enabled, and saves
   every query → answer (plus cited sources) to [latest_run.json](latest_run.json).
3. **Dashboard** ([pages/results.py](pages/results.py)) reads that saved run and
   shows three tabs:
   - **Your visibility** — share-of-voice gauge + which queries you appear in vs. miss.
   - **You vs competitors** — how often each business appears, and which sources the AI cited.
   - **What's next** — a recap and a lead-capture form (stored in SQLite).

---

## Detection 

The core problem is deceptively hard: *did this specific business appear in this
answer?* Naive substring matching breaks on abbreviations, shared common words
(a rival "City Barbers" vs. the category "barber"), and dismissive mentions.

The solution ([detection.py](detection.py)) is a **hybrid router** whose guiding
principle is **"change the cost, not the accuracy"**:

1. `distinctive_tokens()` — lower-cases the name, strips the category, location,
   and legal suffixes (Ltd, LLC, …), then keeps only **rare tokens** using
   [`wordfreq`](https://pypi.org/project/wordfreq/) zipf frequency below `2.5`.
   For *"Lazarou Barbers"* this isolates `lazarou` — a distinctive anchor.
2. `has_anchor()` — does the name contain such a distinctive token?
   - **Yes** → `cheap_match()`: a free word-boundary regex check. Safe, because a
     rare, coined token can't collide with everyday words.
   - **No** (generic/ambiguous names like *"City Barbers"*) → fall back to an
     **LLM judge** (`judge()`) that reasons about whether the business is really
     present, tolerating abbreviations and rejecting shared-word false positives.

So ambiguous names always get the accurate (paid) path; only clearly-distinctive
names take the free shortcut. Judge verdicts are cached on the dashboard
(`@st.cache_data`) so repeated views don't re-pay.

---

## Tech stack

- **Python** + **[Streamlit](https://streamlit.io/)** (multipage: wizard + dashboard)
- **OpenAI Responses API** — model `gpt-5.5`, `web_search` tool for audits; plain
  calls for the judge
- **`wordfreq`** for the distinctiveness heuristic
- **SQLite** ([init_db.py](init_db.py)) for captured leads

---

## Setup

```bash
# 1. create + activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. add your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# 4. create the SQLite database
python init_db.py

# 5. run the app
streamlit run app.py
```

---

## Cost

⚠️ **A full audit makes ~10 web-search calls and costs roughly 

---

## Repository layout

| File | Purpose |
|------|---------|
| [app.py](app.py) | Input wizard + the paid `run_audit` pipeline |
| [pages/results.py](pages/results.py) | Three-tab results dashboard |
| [detection.py](detection.py) | Hybrid detection router (tokens → cheap match / LLM judge) |
| [theme.py](theme.py) | Shared `geo-` visual design system for both pages |
| [init_db.py](init_db.py) | Creates the SQLite schema (`leads`) |
| [latest_run.json](latest_run.json) | One saved audit — the dashboard's data source |
| [evaluate.py](evaluate.py) | Diagnostic harness over a saved run |

---

## Limitations & future work

- **Presence, not endorsement.** `cheap_match` confirms a business is mentioned,
  not that it's *recommended*; a dismissive mention still counts as a hit. The
  LLM judge backstops the ambiguous cases.
- **Audit speed.** Some audits can take up to 90 seconds to load the results because of the Api calls. 
- **Single saved run.** The dashboard shows one audit at a time, not tracking
  over time; a new audit overwrites the previous saved run.
- **Fixed query set.** The 10 queries are templated from category + location, not
  tailored per industry.
