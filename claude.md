# GEO Audit Tool — project context for Claude Code

## What this is
A GEO (Generative Engine Optimisation) audit tool: it asks an LLM a set of
search-style questions and measures how often a given business appears in the
answers, producing a "share of voice" %. It's a portfolio project to land a
software engineering placement. The reviewer ("Chris") is a senior engineer who
values evaluation methodology, honest trade-offs/limitations, and production
habits over visual polish — reasoning quality matters more than a slick demo.
Test case throughout: "Lazarou Barbers", category "barber", location "Cardiff".

## ⚠️ Cost — read first
A full audit is ~10 OpenAI web-search calls and costs ~£2. **Do NOT run live
audits.** Do not call `run_audit()` or trigger the audit pipeline. Iterate
against the saved `latest_run.json`, which holds one real run's query→answer
pairs; the Results page reads it with no API calls. Detection over saved answers
(the judge) is cheap and fine — it's the web-search calls that are expensive.

## Stack / layout
- Python, Streamlit multipage (`pages/`). Windows, PowerShell, venv active.
- `app.py` — input wizard (`st.session_state`, one question per page) +
  `run_audit()` (the paid pipeline, NOT yet wired to the wizard — placeholder).
- `pages/Results.py` — dashboard, 3 tabs via `st.tabs`
  ("Your visibility", "You vs competitors", "What's next").
- `detection.py` — pure detection logic (no Streamlit).
- `init_db.py` — SQLite (`geo.db`); `leads` table live, `runs` vestigial.
- `latest_run.json` — one saved paid run (iterate against this).
- OpenAI Responses API, model `gpt-5.5`, `web_search` tool for audits; plain
  calls for the judge.

## Detection (don't redesign without asking)
Hybrid router in `detection.py`: `distinctive_tokens()` uses wordfreq zipf
(threshold 2.5) to find rare/coined tokens after dropping category/location/
legal-suffix words → `has_anchor()` → if anchored, free `cheap_match()`
(word-boundary regex); else fall back to the paid LLM `judge()`. Guarantee is
"changes cost, not accuracy" — ambiguous names always hit the judge. Judge
verdicts are cached (`@st.cache_data`).

## Locked decisions — do NOT reopen
- LLM judge replaced the original string matcher (deliberate, validated 5/5
  adversarial). Not a downgrade.
- Hybrid wordfreq routing as above. No spaCy / GLiNER / heavy NER.
- Single saved-run dashboard, not daily tracking-over-time.
- Results via `st.tabs`, not a separate pages/ structure for the three tabs.
- Competitors are user-entered (wizard Q4), saved to `latest_run.json`
  under `competitors`.

## UI / design system
Custom theme injected as one `<style>` block in `Results.py`, all classes
prefixed `geo-`. Keep this palette — don't introduce a competing one:
primary `#2E6F95`, page white, secondary bg `#F4F6F8`, text `#1A1A1A`,
borders `#ECEFF2`, muted `#5A6672`/`#8A95A1`, empty-track `#E1E6EB`.
`.streamlit/config.toml` sets the matching Streamlit theme. Style with
whitespace + thin dividers, not heavy boxes. No red for "missing" — keep it calm.

**Honesty rule:** never put fabricated numbers on screen. Every stat/metric must
come from real data or a citable source. (Avoid past mistakes: an invented
"potential visibility %" and a made-up "70% of search is LLM".)

## Known limitations (keep honest — these are for Chris)
- The eval/labelled dataset was Claude-generated, not human-verified.
- `cheap_match` detects presence, not endorsement; the judge backstops
  dismissive mentions.
- Router is only safe for distinctive/coined names, by design.

## How to work
- Focused, reviewable changes — Sam reviews diffs and decides. Explain reasoning
  before non-trivial changes. Don't over-engineer or add unrequested scope.
  Push back when something's wrong rather than just agreeing.