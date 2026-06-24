import json
import sqlite3
from datetime import datetime
from html import escape
from urllib.parse import urlparse

import streamlit as st
from detection import detect
from theme import inject_theme, donut

st.set_page_config(page_title="Results · GEO Audit", page_icon="🔎", layout="centered")
inject_theme()

try:
    with open("latest_run.json", "r", encoding="utf-8") as f:
        run = json.load(f)
except FileNotFoundError:
    st.info("No audit yet — run one on the main page first.")
    st.stop()

business = run["business"].strip()
category = run["category"].strip()
location = run["location"].strip()
answers = [q["answer"] for q in run["queries"]]
total = len(answers)

# --- page header ---
meta_chips = [f"{escape(category)} in {escape(location)}", f"{total} queries"]
run_at = run.get("run_at", "")
if run_at:
    meta_chips.append(f"audited {escape(run_at.replace('T', ' '))}")
st.markdown(
    f'<div class="geo-results-header">'
    f'<div class="geo-results-kicker">Audit results</div>'
    f'<div class="geo-results-title">{escape(business)}</div>'
    f'<div class="geo-results-meta">'
    + "".join(f'<span class="geo-meta-chip">{chip}</span>' for chip in meta_chips)
    + '</div></div>',
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def detect_cached(name, answer, category, location):
    return detect(name, answer, category, location)

tab1, tab2, tab3 = st.tabs(["Your visibility", "You vs competitors", "What's next"])

with tab1:
    visible, missing = [], []
    for q in run["queries"]:
        query_text = " ".join(q["query"].split())          # tidy the double spaces
        if detect_cached(business, q["answer"], category, location):
            visible.append(query_text)
        else:
            missing.append(query_text)

    pct = round(len(visible) / total * 100) if total else 0
    gap = len(missing)

    # hero: donut gauge + plain-language summary
    note = (f"{gap} of the {total} test queries don't mention you yet."
            if gap else "You appear in every query tested — full coverage.")
    st.markdown(
        f'<div class="geo-hero">'
        f'{donut(pct, "visible")}'
        f'<div class="geo-hero-body">'
        f'<div class="geo-hero-headline">{escape(business)} appears in '
        f'{len(visible)} of {total} AI search answers.</div>'
        f'<div class="geo-hero-note">{escape(note)}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # side-by-side: where you show up | queries to target
    if visible:
        hit_items = "".join(
            f'<div class="geo-item is-hit"><span class="geo-item-dot"></span>'
            f'<span>{escape(q)}</span></div>'
            for q in visible
        )
    else:
        hit_items = ('<div class="geo-item is-miss"><span class="geo-item-dot"></span>'
                     '<span>Not showing up anywhere yet.</span></div>')

    if missing:
        miss_items = "".join(
            f'<div class="geo-item is-miss"><span class="geo-item-dot"></span>'
            f'<span>{escape(q)}</span></div>'
            for q in missing
        )
    else:
        miss_items = ('<div class="geo-item is-hit"><span class="geo-item-dot"></span>'
                      '<span>Full coverage — you appear in every query.</span></div>')

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f'<div class="geo-card">'
            f'<div class="geo-card-head"><span class="geo-card-title">Where you show up</span>'
            f'<span class="geo-count-badge">{len(visible)}</span></div>'
            f'<div class="geo-card-sub">AI answers that mention {escape(business)}</div>'
            f'{hit_items}</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f'<div class="geo-card">'
            f'<div class="geo-card-head"><span class="geo-card-title">Queries to target</span>'
            f'<span class="geo-count-badge is-muted">{gap}</span></div>'
            f'<div class="geo-card-sub">Answers that don\'t mention you yet</div>'
            f'{miss_items}</div>',
            unsafe_allow_html=True,
        )

    # nudge across to the competitors tab
    st.markdown(
        '<div class="geo-nudge">→ Next: see how you stack up against your competitors in the '
        '<b>You vs competitors</b> tab above.</div>',
        unsafe_allow_html=True,
    )

with tab2:
    # competitors are user-entered in the wizard and saved to latest_run.json
    competitors = [c.strip() for c in run.get("competitors", []) if c.strip()]

    if not competitors:
        st.markdown(
            '<div class="geo-empty">No competitors entered for this audit — add some in the '
            'form to see how your share of AI answers compares.</div>',
            unsafe_allow_html=True,
        )
    else:
        businesses = [business] + competitors
        counts = {b: sum(detect_cached(b, a, category, location) for a in answers) for b in businesses}

        ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        you_count = counts[business]
        leader_name, leader_count = ranked[0]

        if leader_name == business:
            headline = (f"{business} leads this set — appearing in {you_count} of {total} AI answers, "
                        f"more than any competitor compared.")
        else:
            headline = (f"{business} appears in {you_count} of {total} AI answers, "
                        f"behind {leader_name} ({leader_count}).")

        st.markdown(f'<div class="geo-headline">{escape(headline)}</div>', unsafe_allow_html=True)

        # ranked comparison bars
        bar_rows = ""
        for rank, (name, c) in enumerate(ranked, start=1):
            bar_pct = round(c / total * 100) if total else 0
            is_you = name == business
            you_cls = " is-you" if is_you else ""
            you_tag = '<span class="geo-you-tag">You</span>' if is_you else ""
            bar_rows += (
                f'<div class="geo-rankbar{you_cls}">'
                f'<div class="geo-rank">{rank}</div>'
                f'<div class="geo-rankbar-main">'
                f'<div class="geo-rankbar-head">'
                f'<span class="geo-rankbar-name">{escape(name)}{you_tag}</span>'
                f'<span class="geo-rankbar-val">{c} of {total} · {bar_pct}%</span></div>'
                f'<div class="geo-rankbar-track"><div class="geo-rankbar-fill" style="width:{bar_pct}%"></div></div>'
                f'</div></div>'
            )
        st.markdown(
            f'<div class="geo-section-title">Share of AI answers</div>'
            f'<div class="geo-section-sub">How often each business appears across the {total} queries</div>'
            f'{bar_rows}',
            unsafe_allow_html=True,
        )

    # where the AI gets its answers — sources cited (empty until a live audit captures them)
    source_counts = {}
    for q in run["queries"]:
        seen = set()
        for cit in q.get("citations", []):
            url = cit.get("url", "")
            if not url:
                continue
            domain = urlparse(url).netloc.replace("www.", "") or url
            if domain in seen:                 # count each source once per answer
                continue
            seen.add(domain)
            if domain not in source_counts:
                source_counts[domain] = {"count": 0, "url": url}
            source_counts[domain]["count"] += 1

    ranked_sources = sorted(source_counts.items(), key=lambda kv: kv[1]["count"], reverse=True)

    if ranked_sources:
        src_rows = "".join(
            f'<div class="geo-src">'
            f'<div class="geo-src-rank">{rank}</div>'
            f'<div class="geo-src-main">'
            f'<div class="geo-src-top">'
            f'<span class="geo-src-name">'
            f'<a href="{escape(data["url"])}" target="_blank" rel="noopener">{escape(domain)}</a></span>'
            f'<span class="geo-src-meta">in {data["count"]} of {total} answers</span></div>'
            f'<div class="geo-src-track"><div class="geo-src-fill" '
            f'style="width:{round(data["count"] / total * 100) if total else 0}%"></div></div>'
            f'</div></div>'
            for rank, (domain, data) in enumerate(ranked_sources, start=1)
        )
    else:
        src_rows = ('<div class="geo-empty">No source data in this run yet — citations are captured '
                    'when you run a live audit. Re-run one and the sites the AI pulled from will list here.</div>')

    st.markdown(
        f'<div class="geo-section-title">Where the AI gets its answers</div>'
        f'<div class="geo-section-sub">Sources cited across all {total} answers — the sites shaping your visibility</div>'
        f'{src_rows}',
        unsafe_allow_html=True,
    )

    # nudge across to the what's-next tab
    st.markdown(
        '<div class="geo-nudge">→ Next: turn this into an action plan in the '
        '<b>What\'s next</b> tab above.</div>',
        unsafe_allow_html=True,
    )

with tab3:
    missing = [" ".join(q["query"].split()) for q in run["queries"]
               if not detect_cached(business, q["answer"], category, location)]
    visible_count = total - len(missing)

    st.markdown(
        f'<div class="geo-recap">'
        f'<div class="geo-recap-num">{visible_count}/{total}</div>'
        f'<div class="geo-recap-body">'
        f'<div class="geo-recap-title">You\'re showing up in {visible_count} of {total} searches.</div>'
        f'<div class="geo-recap-sub">Want help closing the {len(missing)} you\'re missing? '
        f'Leave your details and we\'ll send the full breakdown.</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        with st.form("lead_form"):
            name = st.text_input("Your name")
            email = st.text_input("Your email")
            submitted = st.form_submit_button("Send me the breakdown", type="primary")

    if submitted:
        if "@" not in email or "." not in email:
            st.error("That doesn't look like a valid email — mind checking it?")
        else:
            conn = sqlite3.connect("geo.db")
            conn.execute(
                "INSERT INTO leads (created_at, name, email, business, score) "
                "VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(timespec="minutes"), name, email,
                 business, f"{visible_count}/{total}"),
            )
            conn.commit()
            conn.close()
            st.success("Got it — we'll be in touch with your full breakdown.")

    st.caption("Prefer to talk it through? [Book a consultation](https://calendly.com/your-link)")
