"""The Vision Book — a private guide & journal for becoming her.

Run:  streamlit run streamlit_app.py
"""
import datetime as dt
import html
import json
import random
from zoneinfo import ZoneInfo

import plotly.graph_objects as go
import streamlit as st

from vision_book import content as C
from vision_book import storage, style

st.set_page_config(page_title="The Vision Book", page_icon="❦", layout="wide", initial_sidebar_state="expanded")
style.inject()
esc = html.escape

WINE, GOLD, ROSE, MUTED = "#9E5A63", "#B8975A", "#D9A5A0", "#8A7472"
TODAY = dt.datetime.now(ZoneInfo("Europe/Amsterdam")).date()


# ---------------------------------------------------------------------------
# Privacy gate — set `password = "..."` in .streamlit/secrets.toml (or the
# Streamlit Cloud secrets panel) and the book asks for it before opening.
# ---------------------------------------------------------------------------
def _password():
    try:
        return st.secrets.get("password")
    except Exception:
        return None


def gate() -> bool:
    pw = _password()
    if not pw or st.session_state.get("unlocked"):
        return True
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="eyebrow" style="text-align:center">private</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align:center">The Vision Book</h1>', unsafe_allow_html=True)
        entered = st.text_input("Your key", type="password")
        if entered:
            if entered == pw:
                st.session_state.unlocked = True
                st.rerun()
            st.error("Not quite. Try again, bella.")
    return False


# ---------------------------------------------------------------------------
# Data binding: every field autosaves into one JSON file.
# ---------------------------------------------------------------------------
def _storage_cfg():
    try:
        return dict(st.secrets.get("storage", {}))
    except Exception:
        return {}


def store() -> storage.BookStore:
    if "store" not in st.session_state:
        st.session_state.store = storage.BookStore(_storage_cfg())
    return st.session_state.store


def D() -> dict:
    if "data" not in st.session_state:
        try:
            st.session_state.data = store().load()
        except (storage.SaveError, Exception) as e:  # never start with an empty book silently
            st.error(f"I couldn't open your book from the cloud: {e}. Nothing was overwritten — try refreshing in a minute.")
            st.stop()
    return st.session_state.data


def persist():
    try:
        store().save(D())
        st.session_state.save_error = ""
    except Exception as e:
        st.session_state.save_error = str(e)
        st.toast(f"⚠ Not saved to the cloud: {e}", icon="⚠️")


def _sync(key):
    D()[key] = st.session_state["w::" + key]
    persist()


def _bind(key, default):
    wk = "w::" + key
    if wk not in st.session_state:
        st.session_state[wk] = D().get(key, default)
    return wk


def text(key, label, height=110, placeholder="Write freely…", help=None):
    wk = _bind(key, "")
    st.text_area(label or "Write", key=wk, height=height, placeholder=placeholder, help=help, on_change=_sync, args=(key,),
                 label_visibility="visible" if label else "collapsed")
    return st.session_state[wk]


def line(key, label, placeholder=""):
    wk = _bind(key, "")
    st.text_input(label, key=wk, placeholder=placeholder, on_change=_sync, args=(key,))
    return st.session_state[wk]


def slider(key, label, lo=1, hi=10, default=5, help=None):
    wk = _bind(key, default)
    st.slider(label, lo, hi, key=wk, on_change=_sync, args=(key,), help=help)
    return st.session_state[wk]


def multi(key, label, options, max_selections=None):
    wk = _bind(key, [])
    st.session_state[wk] = [o for o in st.session_state[wk] if o in options]
    st.multiselect(label, options, key=wk, max_selections=max_selections, on_change=_sync, args=(key,))
    return st.session_state[wk]


def check(key, label):
    wk = _bind(key, False)
    st.checkbox(label, key=wk, on_change=_sync, args=(key,))
    return st.session_state[wk]


def get(key, default=""):
    return D().get(key, default)


def items(name) -> list:
    return D().setdefault(name, [])


def reset_widgets():
    for k in [k for k in st.session_state if str(k).startswith("w::")]:
        del st.session_state[k]


def go_to(page):
    st.session_state.nav = page


def day_index(n):
    return TODAY.toordinal() % n


def name():
    return get("name") or C.OWNER


def age_now():
    b = get("birthday")
    if b:
        b = dt.date.fromisoformat(b)
        return TODAY.year - b.year - ((TODAY.month, TODAY.day) < (b.month, b.day))
    return int(get("age", C.DEFAULT_AGE))


def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def ages():
    now = age_now()
    return dict(now=now, next=now + 1, nth=ordinal(now + 1), mid_from=now + 2, mid_to=now + 5, far=now + 10)


def A(s):
    """Fill the age placeholders ({now}, {next}, {nth}…) in a content string."""
    return s.format(**ages())


def chapter():
    return f"Chapter {age_now() + 1}"


def card(body, cls=""):
    st.markdown(f'<div class="card {cls}">{body}</div>', unsafe_allow_html=True)


def filled(keys):
    return sum(1 for k in keys if str(get(k)).strip())


# ---------------------------------------------------------------------------
# Visual helpers
# ---------------------------------------------------------------------------
def wheel_chart(height=420):
    labels = [c["name"] for c in C.CATEGORIES]
    now = [get(f"wheel::{c['key']}::now", 5) for c in C.CATEGORIES]
    want = [get(f"wheel::{c['key']}::want", 9) for c in C.CATEGORIES]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=want + want[:1], theta=labels + labels[:1], name="The life I'm creating",
                                  fill="toself", line=dict(color=GOLD, width=1.5, dash="dot"),
                                  fillcolor="rgba(184,151,90,0.10)"))
    fig.add_trace(go.Scatterpolar(r=now + now[:1], theta=labels + labels[:1], name="Today",
                                  fill="toself", line=dict(color=WINE, width=2),
                                  fillcolor="rgba(158,90,99,0.22)"))
    fig.update_layout(
        height=height, margin=dict(l=95, r=95, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Cormorant Garamond, serif", size=14, color="#6E3A42"),
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"),
        polar=dict(bgcolor="rgba(255,253,250,0.6)",
                   radialaxis=dict(range=[0, 10], showticklabels=False, gridcolor="#EADBD3", linecolor="#EADBD3"),
                   angularaxis=dict(gridcolor="#EADBD3", linecolor="#EADBD3")),
    )
    return fig


def journal_dates():
    return sorted({k.split("::")[1] for k in D() if k.startswith("journal::")})


def streak():
    dates = set(journal_dates())
    n, d = 0, TODAY
    if d.isoformat() not in dates:
        d -= dt.timedelta(days=1)
    while d.isoformat() in dates:
        n += 1
        d -= dt.timedelta(days=1)
    return n



DAY_FIELDS = C.JOURNAL_MORNING[1:] + C.JOURNAL_EVENING + [("lang", "In another language")]


def day_has_writing(x):
    return any(str(get(f"journal::{x}::{k}")).strip() for k, _ in DAY_FIELDS)


def render_day(x):
    f = get(f"journal::{x}::feelings", [])
    meta = [f"{lbl} {get(f'journal::{x}::{k}')}/10" for k, lbl in (("mood", "Mood"), ("energy", "Energy"), ("adored", "Adored"))
            if get(f"journal::{x}::{k}", None) is not None]
    care = [i for i in C.SELF_CARE if get(f"journal::{x}::care::{i}", False)]
    if f or meta:
        st.markdown(style.chips(f) + style.chips(meta, gold=True), unsafe_allow_html=True)
    for k, q in DAY_FIELDS:
        v = get(f"journal::{x}::{k}")
        if str(v).strip():
            st.markdown(f"**{esc(A(q))}**  \n{esc(v)}")
    if care:
        st.caption("Self-care: " + " · ".join(care))
    if not (f or meta or care or day_has_writing(x)):
        st.caption("Nothing written on this day.")


def mood_chart(dates, height):
    fig = go.Figure()
    for k, nm, col in (("mood", "Mood", WINE), ("energy", "Energy", GOLD), ("adored", "Felt adored", ROSE)):
        pts = [(x, get(f"journal::{x}::{k}", None)) for x in dates]
        pts = [p for p in pts if p[1] is not None]
        if pts:
            fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], name=nm, mode="lines+markers",
                                     line=dict(color=col, width=2, shape="spline"), marker=dict(size=7)))
    if not fig.data:
        return
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 10.5], gridcolor="#EADBD3"),
                      xaxis=dict(type="date", tickformat="%a %d %b", dtick=86400000 * max(1, len(dates) // 10)),
                      font=dict(family="Jost, sans-serif", color="#6E3A42"), legend=dict(orientation="h", y=1.2))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _pick_day(x):
    st.session_state.jdate = x


def week_strip():
    """Seven little day buttons: see at a glance which days you wrote, jump to any of them."""
    sel = st.session_state.get("jdate", TODAY)
    monday = sel - dt.timedelta(days=sel.weekday())
    written = set(journal_dates())
    cols = st.columns(7)
    for i, col in enumerate(cols):
        x = monday + dt.timedelta(days=i)
        mark = "●" if x.isoformat() in written else "○"
        label = f"{x.strftime('%a')} {x.day} {mark}"
        col.button(label, key=f"wk_{x}", on_click=_pick_day, args=(x,), disabled=x > TODAY,
                   type="primary" if x == sel else "secondary", width="stretch")


# ===========================================================================
# PAGES
# ===========================================================================
def page_home():
    lang, aff, trans = C.AFFIRMATIONS[day_index(len(C.AFFIRMATIONS))]
    greeting = {"Italiano": "Buongiorno", "Français": "Bonjour", "Русский": "Доброе утро"}[lang]
    style.header(f"{chapter()} · {TODAY.strftime('%A %d %B %Y')}", f"{greeting}, {esc(name())}.", C.TAGLINE)

    q, by = C.QUOTES[day_index(len(C.QUOTES))]
    own = items("quotes")
    if own and day_index(2):
        pick = own[day_index(len(own))]
        q, by = pick["text"], pick["by"]
    style.ornament()
    st.markdown(f'<div class="quote">“{esc(q)}”</div><div class="quote-by">{esc(by)}</div>', unsafe_allow_html=True)
    style.ornament()

    # Stats
    bday = get("birthday")
    cols = st.columns(5)
    stats = [
        (len(journal_dates()), "journal days"),
        (streak(), "day streak"),
        (len(items("beliefs")), "beliefs rewritten"),
        (sum(1 for d in items("dares") if d.get("done")), "dares completed"),
    ]
    if bday:
        b = dt.date.fromisoformat(bday)
        nxt = b.replace(year=TODAY.year)
        if nxt < TODAY:
            nxt = nxt.replace(year=TODAY.year + 1)
        stats.append(((nxt - TODAY).days, "days to my next birthday"))
    else:
        stats.append(("—", "set birthday in My Book"))
    for col, (v, l) in zip(cols, stats):
        col.markdown(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.05, 1])
    with left:
        card(f'<div class="eyebrow">affirmation of the day · {lang}</div>'
             f'<h4>{esc(aff)}</h4><div class="small">{esc(trans)}</div>'
             f'<div class="small" style="margin-top:.6rem">Say it out loud three times — then write it once by hand.</div>',
             "blush")
        feels = get("core_feelings", [])
        body = style.chips(feels) if feels else '<span class="small">Choose them in “Who I’m Becoming”.</span>'
        card(f'<div class="eyebrow">how I choose to feel</div>{body}')

        her = get("id::she_is").strip()
        if her:
            card(f'<div class="eyebrow">she is…</div><div class="serif" style="font-size:1.2rem;font-style:italic">'
                 f'{esc(her[:420])}{"…" if len(her) > 420 else ""}</div>')

        dare = get(f"dare::{TODAY.isoformat()}")
        card(f'<div class="eyebrow">today\'s brave act</div>'
             f'<h4>{esc(dare) if dare else "Not drawn yet."}</h4>'
             f'<div class="small">Growth lives just outside the comfort zone — not in panic, not in comfort.</div>',
             "wine")
    with right:
        st.markdown('<div class="eyebrow">the wheel of my life</div>', unsafe_allow_html=True)
        st.plotly_chart(wheel_chart(400), width="stretch", config={"displayModeBar": False})

    style.ornament()
    st.markdown("### Where would you like to begin?")
    starts = [
        ("Morning pages", "Set today's feeling & intention", "Daily Journal"),
        ("Meet her", "Write the woman you're becoming", "Who I'm Becoming"),
        ("Rewrite a belief", "Turn a 'can't' into a choice", "Belief Alchemy"),
        ("Draw a dare", "One step outside your comfort zone", "Comfort Zone"),
    ]
    for col, (t, s, p) in zip(st.columns(4), starts):
        with col:
            card(f'<h4>{t}</h4><div class="small">{s}</div>')
            st.button("Open", key=f"start_{p}", on_click=go_to, args=(p,), width="stretch")


# ---------------------------------------------------------------------------
def page_identity():
    style.header("identity · narrative", "Who I'm Becoming",
                 "Not a list of goals — a woman. Write her so clearly that you could recognise her walking down the street.")
    t1, t2, t3, t4, t5 = st.tabs(["Her portrait", "Values & feelings", f"Letter from {ages()['next']}", "Best Possible Self", "Walk my talk"])

    with t1:
        style.psych("Identity drives behaviour more reliably than goals. When you act from "
                    "<i>“I am a woman who…”</i> instead of <i>“I should…”</i>, each action becomes a vote for who you are becoming (James Clear, <i>Atomic Habits</i>; self-perception theory, Bem).")
        for k, q in C.IDENTITY_PROMPTS:
            text(f"id::{k}", A(q), height=140)

    with t2:
        style.psych("Core desired feelings: decide how you want to <b>feel</b>, then choose the goals and habits that create that feeling. "
                    "Values (Acceptance & Commitment Therapy) are directions, not destinations — you can live them today.")
        feels = multi("core_feelings", "Choose 3–5 core feelings I want to live in", C.FEELINGS, max_selections=5)
        if feels:
            for f in feels:
                text(f"feel::{f}", f"What creates “{f}” for me? (people, places, habits, clothes, music…)", height=80)
        style.ornament()
        vals = multi("values", "Choose my top 5 values", C.VALUES_LIST, max_selections=5)
        for v in vals:
            c1, c2 = st.columns([1, 1])
            with c1:
                text(f"val::{v}::looks", f"{v} — what it looks like when I live it", height=80)
            with c2:
                slider(f"val::{v}::score", f"How fully I live “{v}” right now", 1, 10, 5)

    with t3:
        style.psych(A(C.FUTURE_LETTER_GUIDE), "Future-self continuity")
        st.markdown(f'<div class="serif" style="font-size:1.3rem;font-style:italic">Dear {esc(name())} at {ages()['now']},</div>', unsafe_allow_html=True)
        text("letter_next", "", height=420, placeholder=A("I'm writing to you from the morning of our {nth} birthday…"))
        st.markdown(f'<div class="serif" style="font-size:1.3rem;font-style:italic;text-align:right">With all my love, — you, at {ages()["next"]}</div>', unsafe_allow_html=True)

    with t4:
        style.psych(C.BEST_SELF_GUIDE, "Best Possible Self")
        text("bestself", "My best possible self, one year from today", height=420,
             placeholder="It's a year from now. I wake up and…")
        line("bestself_line", "Now distil it: one sentence I want to read every morning")

    with t5:
        style.psych("Walking your talk = value–behaviour congruence. The gap isn't failure; it's information. "
                    "Look at it with curiosity (self-compassion), then design the next small step.")
        vals = get("values", [])
        if not vals:
            st.info("Choose your top values in the “Values & feelings” tab first.")
        week = TODAY.isocalendar()
        wk = f"{week.year}-W{week.week:02d}"
        st.markdown(f'<div class="eyebrow">congruence audit · week {wk}</div>', unsafe_allow_html=True)
        for v in vals:
            with st.expander(f"✦ {v}", expanded=False):
                text(f"talk::{wk}::{v}::yes", f"Where did I live {v} this week?", height=70)
                text(f"talk::{wk}::{v}::gap", f"Where did I drift from {v}? What did I need in that moment?", height=70)
                line(f"talk::{wk}::{v}::next", "One tiny action that would close the gap next week")


# ---------------------------------------------------------------------------
def page_chapters():
    style.header("life categories", "The Chapters of My Life",
                 "Rate where you are, see where you're going — then write each chapter in the present tense.")
    style.psych("The Wheel of Life is a classic coaching tool. Seeing the gap between <i>today</i> and <i>the life I'm creating</i> "
                "creates healthy tension (Robert Fritz's 'structural tension') that pulls you forward.")

    left, right = st.columns([1, 1.1])
    with left:
        with st.expander("Rate my wheel", expanded=not any(f"wheel::{c['key']}::now" in D() for c in C.CATEGORIES)):
            for c in C.CATEGORIES:
                a, b = st.columns(2)
                with a:
                    slider(f"wheel::{c['key']}::now", f"{c['symbol']} {c['name']} · today", 1, 10, 5)
                with b:
                    slider(f"wheel::{c['key']}::want", A("by my {nth} birthday"), 1, 10, 9)
        st.markdown("<br>", unsafe_allow_html=True)
        for c in C.CATEGORIES:
            keys = [f"cat::{c['key']}::{k}" for k, _ in c["prompts"]]
            n = filled(keys)
            st.markdown(f'<div class="rung"><span class="lbl">{c["symbol"]} {n}/{len(keys)} written</span><br>'
                        f'<span class="serif" style="font-size:1.2rem">{c["name"]}</span></div>', unsafe_allow_html=True)
            st.progress(n / len(keys))
    with right:
        st.plotly_chart(wheel_chart(520), width="stretch", config={"displayModeBar": False})

    style.ornament()
    names = [f"{c['symbol']}  {c['name']}" for c in C.CATEGORIES]
    choice = st.radio("Open a chapter", names, horizontal=True, label_visibility="collapsed")
    c = C.CATEGORIES[names.index(choice)]

    st.markdown(f'<div class="eyebrow">chapter</div><h2>{c["symbol"]} {c["name"]}</h2>'
                f'<div class="lede">{c["essence"]}</div>', unsafe_allow_html=True)
    style.psych(c["psych"])
    multi(f"cat::{c['key']}::feelings", "In this area of my life I want to feel…", C.FEELINGS, max_selections=4)
    for k, q in c["prompts"]:
        text(f"cat::{c['key']}::{k}", q, height=130)

    st.markdown("#### From vision to process")
    st.markdown('<div class="small">Ideas for weekly process goals — fully in your control:</div>'
                + style.chips(c["process"], gold=True), unsafe_allow_html=True)
    text(f"cat::{c['key']}::my_process", "My process goals for this chapter (what I'll DO, weekly):", height=90)
    st.button("Turn a dream from this chapter into a ladder →", on_click=go_to, args=("Goals → Process",))


# ---------------------------------------------------------------------------
def page_horizons():
    a = ages()
    style.header("the long view", "Horizons",
                 f"You're {a['now']}. Live Chapter {a['next']} in ink — sketch the chapters after it in pencil.")
    style.psych("Construal-level theory (Trope &amp; Liberman): the far future is best imagined in <b>why</b> — values, essence, feeling; "
                "the near future in <b>how</b> — concrete steps. <b>Backcasting</b> connects them: start from the distant picture and ask "
                "what must be true one step earlier. Big vision, small steps.")
    nodes = "".join(
        f'<div style="flex:1;text-align:center">'
        f'<div style="width:{s}px;height:{s}px;border-radius:50%;margin:0 auto .5rem;background:{bg};border:1px solid {GOLD}"></div>'
        f'<div class="serif" style="font-size:1.25rem;color:#6E3A42">{A(h["label"])}</div>'
        f'<div class="small" style="color:{MUTED}">{h["span"]}<br><i>{h["mode"]}</i></div></div>'
        for h, s, bg in zip(C.HORIZONS, (46, 32, 22), (WINE, ROSE, "#F4E1DC")))
    st.markdown(f'<div class="card" style="position:relative"><div style="position:absolute;left:16%;right:16%;top:3.0rem;'
                f'border-top:1px dashed {GOLD}"></div><div style="display:flex;position:relative">'
                f'<div style="flex:1;text-align:center"><div style="width:14px;height:14px;border-radius:50%;margin:16px auto .5rem;'
                f'background:{GOLD}"></div><div class="serif" style="font-size:1.25rem;color:#6E3A42">Today · {a["now"]}</div>'
                f'<div class="small" style="color:{MUTED}">where you stand</div></div>{nodes}</div></div>',
                unsafe_allow_html=True)

    labels = [f'{A(h["label"])} · {h["span"]}' for h in C.HORIZONS]
    pick = st.radio("Horizon", labels, horizontal=True, label_visibility="collapsed")
    H = C.HORIZONS[labels.index(pick)]
    st.markdown(f'<div class="eyebrow">{H["span"]} · written in {H["mode"]}</div><h2>{A(H["label"])}</h2>'
                f'<div class="lede">{H["essence"]}</div>', unsafe_allow_html=True)
    multi(f"hz::{H['key']}::feelings", "In this chapter I feel…", C.FEELINGS, max_selections=3)
    for k, q in H["prompts"]:
        text(f"hz::{H['key']}::{k}", A(q), height=110 if H["key"] != "far" else 90)
    if H["key"] == "near":
        st.markdown('<div class="small">Chapter ' + str(a["next"]) + ' is the heart of the book — go deeper in '
                    '<i>Who I\'m Becoming</i>, <i>Life Chapters</i> and <i>Goals → Process</i>.</div>', unsafe_allow_html=True)
        st.button("Open Life Chapters →", on_click=go_to, args=("Life Chapters",))
    else:
        style.psych("Fill this lightly and revisit it on each birthday. Your future self is allowed to change her mind — "
                    "only the <i>bridge</i> answer turns into action now.", "Pencil, not ink")
        bridge = get(f"hz::{H['key']}::bridge").strip()
        if bridge:
            st.button("Turn the bridge into a goal ladder →", on_click=go_to, args=("Goals → Process",))


# ---------------------------------------------------------------------------
def page_goals():
    style.header("goal design", "From Dream to Daily Ritual",
                 "Big goals inspire. Process goals change your life. Here you translate one into the other.")
    style.psych("Sport psychology distinguishes <b>outcome</b> goals (results you can't fully control), <b>performance</b> goals (personal markers) "
                "and <b>process</b> goals (behaviours fully in your control). Process goals reduce anxiety and raise consistency. "
                "Add <b>WOOP</b> (Gabriele Oettingen: Wish, Outcome, Obstacle, Plan) and if-then plans (Gollwitzer) — they roughly double follow-through in studies.")

    with st.expander("✦ Build a new ladder", expanded=not items("ladders")):
        with st.form("ladder", clear_on_submit=True):
            cat = st.selectbox("Life chapter", [c["name"] for c in C.CATEGORIES])
            dream = st.text_input("The dream (big, emotional, a little scary)", placeholder="Run a fully booked coaching practice I love")
            outcome = st.text_input(A("Outcome goal — by my {nth} birthday"), placeholder="12 private clients and €X per month")
            perf = st.text_area("Performance markers — quarterly milestones", placeholder="Q1: offer defined & priced\nQ2: first 4 clients…", height=90)
            process = st.text_area("Process goals — weekly, 100% in my control", placeholder="2 deep-work blocks · 1 post · 3 conversations", height=90)
            tiny = st.text_input("Tiny daily habit (BJ Fogg): After I ___, I will ___", placeholder="After I pour my coffee, I will write one line of content")
            st.markdown("**WOOP** — make it obstacle-proof")
            obstacle = st.text_input("Obstacle — what inside ME is most likely to stop me?", placeholder="Perfectionism: I wait until it's 'ready'")
            plan = st.text_input("Plan — IF [obstacle], THEN I will…", placeholder="IF I want to polish more, THEN I publish at 80% and note one lesson")
            feel = st.text_input("When I reach this, I will feel…", placeholder="Proud, free, magnetic")
            if st.form_submit_button("Add to my book") and dream.strip():
                items("ladders").append(dict(cat=cat, dream=dream, outcome=outcome, perf=perf, process=process,
                                             tiny=tiny, obstacle=obstacle, plan=plan, feel=feel,
                                             created=TODAY.isoformat(), weeks=[]))
                persist()
                st.rerun()

    week = TODAY.isocalendar()
    wk = f"{week.year}-W{week.week:02d}"
    for i, L in enumerate(items("ladders")):
        st.markdown(f'<div class="eyebrow">{esc(L["cat"])}</div><h3>{esc(L["dream"])}</h3>', unsafe_allow_html=True)
        rungs = [("the feeling", L.get("feel")), (A("outcome · by {next}"), L["outcome"]), ("performance · quarterly", L["perf"]),
                 ("process · weekly", L["process"]), ("tiny habit · daily", L["tiny"]),
                 ("if-then shield", L["plan"])]
        st.markdown('<div class="ladder">' + "".join(
            f'<div class="rung"><div class="lbl">{lbl}</div>{esc(v or "—").replace(chr(10), "<br>")}</div>'
            for lbl, v in rungs if v) + "</div>", unsafe_allow_html=True)
        a, b, c = st.columns([2, 2, 1])
        done = wk in L["weeks"]
        if a.checkbox(f"I lived my process goals this week ({wk})", value=done, key=f"lw_{i}") != done:
            L["weeks"] = sorted(set(L["weeks"]) ^ {wk})
            persist()
            st.rerun()
        b.markdown(f'<span class="saved">{len(L["weeks"])} week(s) of keeping my promise</span>', unsafe_allow_html=True)
        if c.button("Remove", key=f"ldel_{i}"):
            items("ladders").pop(i)
            persist()
            st.rerun()
        style.ornament()


# ---------------------------------------------------------------------------
def page_beliefs():
    style.header("cognitive reframing", "Belief Alchemy",
                 "A belief is just a thought you've thought many times. You can practise a new one.")
    style.psych("This combines Albert Ellis' ABC model (CBT), Byron Katie's four questions and a behavioural experiment. "
                "Rating how strongly you believe a thought before and after helps you notice that beliefs move — "
                "and the tiny proof-action gives your brain new evidence.")

    with st.expander("✦ Transform a belief", expanded=not items("beliefs")):
        pick = st.selectbox("Start from a common one, or write your own", ["— my own —"] + C.COMMON_BELIEFS)
        with st.form("belief", clear_on_submit=True):
            old = st.text_input("The belief that holds me back", value="" if pick == "— my own —" else pick)
            before = st.slider("How strongly do I believe it right now? (%)", 0, 100, 70)
            origin = st.text_area("Where did I learn this? Whose voice is it?", height=70)
            cost = st.text_area("What has this belief cost me — in love, money, joy, freedom?", height=70)
            st.markdown("**The Work · four questions**")
            answers = [st.text_area(q, height=60, key=f"bk{j}") for j, q in enumerate(C.BYRON_KATIE)]
            evidence = st.text_area("Evidence that it is NOT (always) true — moments, people, facts:", height=70)
            turn = st.text_area("Turnaround — the opposite, and three ways it could be just as true:", height=70)
            new = st.text_input("My new, empowering belief (believable, not fake-positive):",
                                placeholder="I'm allowed to grow into readiness while doing it.")
            proof = st.text_input("A tiny action that proves the new belief this week:")
            after = st.slider("How strongly do I believe the OLD thought now? (%)", 0, 100, 40)
            if st.form_submit_button("Rewrite it") and old.strip() and new.strip():
                items("beliefs").append(dict(old=old, new=new, before=before, after=after, origin=origin, cost=cost,
                                             katie=answers, evidence=evidence, turn=turn, proof=proof,
                                             date=TODAY.isoformat(), proven=False))
                persist()
                st.rerun()

    for i, B in enumerate(reversed(items("beliefs"))):
        idx = len(items("beliefs")) - 1 - i
        card(f'<div class="eyebrow">{B["date"]} · belief strength {B["before"]}% → {B["after"]}%</div>'
             f'<div class="small" style="text-decoration:line-through">{esc(B["old"])}</div>'
             f'<h4>✦ {esc(B["new"])}</h4>'
             + (f'<div class="small">Proof-action: {esc(B["proof"])}</div>' if B.get("proof") else ""))
        a, b = st.columns([3, 1])
        proven = a.checkbox("I did the proof-action", value=B.get("proven", False), key=f"bp_{idx}")
        if proven != B.get("proven", False):
            B["proven"] = proven
            persist()
        if b.button("Remove", key=f"bdel_{idx}"):
            items("beliefs").pop(idx)
            persist()
            st.rerun()


# ---------------------------------------------------------------------------
ZONES_SVG = """
<svg viewBox="0 0 360 360" style="width:100%;max-width:340px;display:block;margin:auto" xmlns="http://www.w3.org/2000/svg">
  <circle cx="180" cy="180" r="170" fill="#F4E1DC" stroke="#EADBD3"/>
  <circle cx="180" cy="180" r="115" fill="#FBEFE8" stroke="#D9A5A0" stroke-dasharray="4 4"/>
  <circle cx="180" cy="180" r="58" fill="#FFFDFA" stroke="#B8975A"/>
  <text x="180" y="176" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="17" fill="#6E3A42">comfort</text>
  <text x="180" y="194" text-anchor="middle" font-family="Jost, sans-serif" font-size="9" letter-spacing="2" fill="#8A7472">SAFE · STATIC</text>
  <text x="180" y="100" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="19" font-style="italic" fill="#9E5A63">stretch — she lives here</text>
  <text x="180" y="262" text-anchor="middle" font-family="Jost, sans-serif" font-size="9" letter-spacing="2" fill="#8A7472">FEAR 4–7 / 10 · GROWTH</text>
  <text x="180" y="38" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="16" fill="#8A7472">panic</text>
  <text x="180" y="335" text-anchor="middle" font-family="Jost, sans-serif" font-size="9" letter-spacing="2" fill="#8A7472">FEAR 9–10 · TOO MUCH, TOO SOON</text>
</svg>
"""


def page_comfort():
    style.header("courage practice", "Out of My Comfort Zone",
                 "Confidence isn't the cause of brave action. It's the result.")
    a, b = st.columns([1, 1.3])
    with a:
        st.markdown(ZONES_SVG, unsafe_allow_html=True)
    with b:
        style.psych("The comfort–stretch–panic model (Karl Rohnke; Yerkes–Dodson): we learn best with moderate arousal. "
                    "Graded exposure means climbing a ladder of fear — start around 3–4/10 and move up as each step becomes ordinary. "
                    "Predict your fear before, rate it after: the gap is usually big, and that gap is the lesson.")
        cat_names = {c["name"]: c["key"] for c in C.CATEGORIES}
        f_cat = st.multiselect("Draw from these chapters", list(cat_names), default=list(cat_names))
        max_lvl = st.slider("Maximum intensity today", 1, 10, 6)
        pool = [d for d in C.DARES + [(x["cat"], x["level"], x["dare"]) for x in items("own_dares")]
                if d[0] in {cat_names[n] for n in f_cat} and d[1] <= max_lvl]
        if st.button("✦ Draw today's dare") and pool:
            d = random.choice(pool)
            D()[f"dare::{TODAY.isoformat()}"] = d[2]
            persist()
            st.rerun()

    today_dare = get(f"dare::{TODAY.isoformat()}")
    if today_dare:
        card(f'<div class="eyebrow">today\'s dare</div><h4>{esc(today_dare)}</h4>', "wine")
        with st.form("dare_log", clear_on_submit=True):
            c1, c2 = st.columns(2)
            pred = c1.slider("Fear I expect (0–10)", 0, 10, 6)
            real = c2.slider("Fear I actually felt (0–10)", 0, 10, 3)
            learned = st.text_input("What I learned about myself:")
            if st.form_submit_button("I did it ✦"):
                items("dares").append(dict(dare=today_dare, date=TODAY.isoformat(), pred=pred, real=real,
                                           learned=learned, done=True))
                persist()
                st.balloons()
                st.rerun()

    with st.expander("Add my own dare to the deck"):
        with st.form("own_dare", clear_on_submit=True):
            cat = st.selectbox("Chapter", [c["name"] for c in C.CATEGORIES])
            lvl = st.slider("Intensity", 1, 10, 5)
            txt = st.text_input("The dare")
            if st.form_submit_button("Add") and txt.strip():
                items("own_dares").append(dict(cat=C.CATEGORIES[[c["name"] for c in C.CATEGORIES].index(cat)]["key"],
                                               level=lvl, dare=txt))
                persist()
                st.rerun()

    done = items("dares")
    if done:
        style.ornament()
        st.markdown("### My courage log")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[d["date"] for d in done], y=[d["pred"] for d in done], name="Fear I expected", marker_color=ROSE))
        fig.add_trace(go.Bar(x=[d["date"] for d in done], y=[d["real"] for d in done], name="Fear I felt", marker_color=WINE))
        fig.update_layout(barmode="group", height=280, margin=dict(l=10, r=10, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(family="Jost, sans-serif", color="#6E3A42"), yaxis=dict(range=[0, 10], gridcolor="#EADBD3"),
                          legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        for d in reversed(done):
            st.markdown(f'<div class="rung"><span class="lbl">{d["date"]} · {d["pred"]} → {d["real"]}</span><br>'
                        f'{esc(d["dare"])}<br><i class="small">{esc(d.get("learned", ""))}</i></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
def page_visualise():
    style.header("guided imagery", "Visualise", "Read one line, close your eyes, see it. Then the next.")
    style.psych("Visualisation works best when you imagine the <b>process</b>, not only the result (Taylor & Pham, 1999). "
                "Pure fantasy can even lower your energy (Oettingen) — so these scripts always include the steps and the obstacles.")
    titles = [f'{A(v["title"])}  ·  {v["minutes"]} min' for v in C.VISUALIZATIONS]
    sel = st.selectbox("Choose a journey", titles)
    V = C.VISUALIZATIONS[titles.index(sel)]
    sk = f"vstep_{V['key']}"
    st.session_state.setdefault(sk, 0)
    step = st.session_state[sk]
    st.markdown(f'<div class="eyebrow">{V["type"]}</div><h2>{A(V["title"])}</h2>', unsafe_allow_html=True)

    mode = st.radio("Mode", ["One step at a time", "Full script"], horizontal=True, label_visibility="collapsed")
    if mode == "Full script":
        st.markdown("".join(f'<div class="step"><div class="n">{i + 1}</div><div class="t">{esc(A(s))}</div></div>'
                            for i, s in enumerate(V["steps"])), unsafe_allow_html=True)
    else:
        n = len(V["steps"])
        st.progress((step + 1) / n)
        card(f'<div class="eyebrow">step {step + 1} of {n}</div>'
             f'<div class="quote" style="font-size:1.7rem">{esc(A(V["steps"][step]))}</div>', "blush")
        a, _, b = st.columns([1, 3, 1])
        if a.button("← Back", disabled=step == 0):
            st.session_state[sk] -= 1
            st.rerun()
        if b.button("Next →", disabled=step == n - 1):
            st.session_state[sk] += 1
            st.rerun()
    style.ornament()
    text(f"viz::{V['key']}::{TODAY.isoformat()}", A(V["reflect"]), height=120)


# ---------------------------------------------------------------------------
def page_journal():
    style.header("daily practice", "Daily Journal", "Small pages, written often, become a different life.")
    st.session_state.setdefault("jdate", TODAY)
    week_strip()
    d = st.date_input("Page of", key="jdate", max_value=TODAY, format="DD/MM/YYYY")
    iso = d.isoformat()
    J = f"journal::{iso}::"

    t1, t2, t3, t4 = st.tabs(["☀ Morning", "☾ Evening", "Weekly review", "My story so far"])
    with t1:
        style.psych("Morning intention-setting primes attention (what you look for, you find). "
                    "Asking <i>“What would future me do?”</i> borrows her perspective — psychologists call it self-distancing, and it makes wiser choices easier.")
        multi(J + "feelings", "Today I want to feel…", C.FEELINGS, max_selections=3)
        for k, q in C.JOURNAL_MORNING[1:]:
            text(J + k, A(q), height=80)
        st.markdown("#### Taking care of her")
        cols = st.columns(2)
        for i, item in enumerate(C.SELF_CARE):
            with cols[i % 2]:
                check(J + "care::" + item, item)

    with t2:
        style.psych("‘Three good things’ (Martin Seligman) — writing three good things and <i>why</i> they happened "
                    "increased happiness and reduced depressive symptoms for up to six months in a randomised trial.")
        a, b, c = st.columns(3)
        with a:
            slider(J + "mood", "Mood", 1, 10, 6)
        with b:
            slider(J + "energy", "Energy", 1, 10, 6)
        with c:
            slider(J + "adored", "Felt adored (by me)", 1, 10, 6)
        for k, q in C.JOURNAL_EVENING:
            text(J + k, q, height=90)
        lang, aff, trans = C.AFFIRMATIONS[d.toordinal() % len(C.AFFIRMATIONS)]
        text(J + "lang", f"Practise: write one sentence about today in {lang} (e.g. “{aff}”)", height=70)

    with t3:
        y, w, _ = d.isocalendar()
        W = f"week::{y}-W{w:02d}::"
        st.markdown(f'<div class="eyebrow">week {w} · {y}</div>', unsafe_allow_html=True)
        style.psych("A weekly review turns experience into learning (Kolb's learning cycle). "
                    "Focus on design changes, not on trying harder — willpower is a poor strategy, systems are a good one.")
        monday = d - dt.timedelta(days=d.weekday())
        days = [(monday + dt.timedelta(days=i)).isoformat() for i in range(7)]
        written = [x for x in days if x in set(journal_dates())]
        st.markdown(f"#### First, read your week back ({len(written)} of 7 days written)")
        if written:
            mood_chart(written, 200)
            for x in written:
                with st.expander(dt.date.fromisoformat(x).strftime("%A %d %B")):
                    render_day(x)
        else:
            st.info("No daily pages in this week yet — you can still reflect from memory.")
        st.markdown("#### Then, reflect")
        for k, q in C.WEEKLY_REVIEW:
            text(W + k, q, height=90)
        st.markdown("#### Quick pulse per chapter")
        cols = st.columns(2)
        for i, c in enumerate(C.CATEGORIES):
            with cols[i % 2]:
                slider(W + "pulse::" + c["key"], f'{c["symbol"]} {c["name"]}', 1, 10, 5)

    with t4:
        dates = journal_dates()
        if not dates:
            st.info("Your story starts with the first page. Write this morning's intention ✦")
        else:
            mood_chart(dates, 300)
            care_total = {i: sum(1 for x in dates if get(f"journal::{x}::care::{i}", False)) for i in C.SELF_CARE}
            st.markdown('<div class="eyebrow">self-care rituals kept</div>' +
                        style.chips([f"{k} · {v}" for k, v in sorted(care_total.items(), key=lambda kv: -kv[1]) if v], gold=True),
                        unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("Read a whole period at once in **My Book → My journal**.")
            for x in reversed(dates):
                with st.expander(dt.date.fromisoformat(x).strftime("%A %d %B %Y")):
                    render_day(x)


# ---------------------------------------------------------------------------
def page_muses():
    style.header("inspiration", "Muses & Mood Board",
                 "We become what we repeatedly look at. Curate it like a gallery.")
    style.psych("Role models work when they feel <b>relevant and attainable</b> (Lockwood & Kunda). "
                "So don't just admire them — ask what they would do in your situation, and borrow one behaviour.")
    t1, t2, t3 = st.tabs(["My muses", "Mood board", "Quotes"])

    with t1:
        muses = C.MUSES + items("own_muses")
        for i in range(0, len(muses), 2):
            cols = st.columns(2)
            for col, M in zip(cols, muses[i:i + 2]):
                with col:
                    card(f'<div class="muse-name">{esc(M["name"])}</div><div class="muse-role">{esc(A(M["role"]))}</div>'
                         + style.chips([esc(e) for e in M["embodies"]]) +
                         f'<div class="serif" style="font-size:1.15rem;font-style:italic;margin-top:.7rem">{esc(M["lesson"])}</div>')
                    text(f"muse::{M['name']}::awakens", "What she awakens in me / the behaviour I borrow", height=80)
                    line(f"muse::{M['name']}::wwsd", "What would she do in my current situation?")
        with st.expander("Add a muse"):
            with st.form("muse", clear_on_submit=True):
                n = st.text_input("Name")
                r = st.text_input("Who she is")
                e = st.text_input("What she embodies (comma separated)")
                l = st.text_input("Her lesson for me")
                if st.form_submit_button("Add") and n.strip():
                    items("own_muses").append(dict(name=n, role=r, embodies=[x.strip() for x in e.split(",") if x.strip()], lesson=l))
                    persist()
                    st.rerun()

    with t2:
        st.markdown('<div class="small">From Pinterest: open a pin → right-click the image → “Copy image address”, and paste it here. '
                    'Or upload your own photos.</div>', unsafe_allow_html=True)
        with st.form("board", clear_on_submit=True):
            url = st.text_input("Image link")
            up = st.file_uploader("…or upload", type=["png", "jpg", "jpeg", "webp", "gif"])
            a, b = st.columns(2)
            cap = a.text_input("Caption / what it means to me")
            cat = b.selectbox("Chapter", ["Everything"] + [c["name"] for c in C.CATEGORIES])
            if st.form_submit_button("Pin it"):
                src = None
                if up is not None:
                    src = store().save_image(up.name, up.getvalue())
                elif url.strip():
                    src = url.strip()
                if src:
                    items("board").append(dict(src=src, caption=cap, cat=cat))
                    persist()
                    st.rerun()
        board = items("board")
        cats = sorted({b["cat"] for b in board})
        filt = st.radio("Show", ["All"] + cats, horizontal=True) if board else "All"
        shown = [(i, b) for i, b in enumerate(board) if filt == "All" or b["cat"] == filt]
        cols = st.columns(3)
        for n, (i, B) in enumerate(shown):
            with cols[n % 3]:
                src = B["src"]
                try:
                    st.image(store().image(src), width="stretch")
                except Exception:
                    st.caption("(image could not load)")
                if B.get("caption"):
                    st.markdown(f'<div class="serif" style="font-style:italic;text-align:center">{esc(B["caption"])}</div>',
                                unsafe_allow_html=True)
                if st.button("Unpin", key=f"unpin_{i}"):
                    board.pop(i)
                    persist()
                    st.rerun()

    with t3:
        for q, by in C.QUOTES + [(x["text"], x["by"]) for x in items("quotes")]:
            st.markdown(f'<div class="quote" style="font-size:1.4rem">“{esc(q)}”</div><div class="quote-by">{esc(by)}</div>',
                        unsafe_allow_html=True)
        style.ornament()
        with st.form("quote", clear_on_submit=True):
            q = st.text_area("Add a quote that moves you", height=70)
            by = st.text_input("Who said it")
            if st.form_submit_button("Add quote") and q.strip():
                items("quotes").append(dict(text=q, by=by or "—"))
                persist()
                st.rerun()


# ---------------------------------------------------------------------------
def compile_journal(dates) -> str:
    out = []
    for x in dates:
        out.append(f"### {dt.date.fromisoformat(x).strftime('%A %d %B %Y')}")
        f = get(f"journal::{x}::feelings", [])
        if f:
            out.append("*Feeling: " + ", ".join(f) + "*")
        scores = [f"{lbl} {get(f'journal::{x}::{k}')}/10" for k, lbl in (("mood", "mood"), ("energy", "energy"), ("adored", "adored"))
                  if get(f"journal::{x}::{k}", None) is not None]
        if scores:
            out.append("*" + " · ".join(scores) + "*")
        out.append("")
        for k, q in DAY_FIELDS:
            v = str(get(f"journal::{x}::{k}")).strip()
            if v:
                out.extend([f"**{A(q)}**", "", v, ""])
    weeks = sorted({k.split("::")[1] for k in D() if k.startswith("week::")})
    wanted = {f"{dt.date.fromisoformat(x).isocalendar()[0]}-W{dt.date.fromisoformat(x).isocalendar()[1]:02d}" for x in dates}
    for wk in [w for w in weeks if w in wanted]:
        out.append(f"### Weekly review · {wk}")
        for k, q in C.WEEKLY_REVIEW:
            v = str(get(f"week::{wk}::{k}")).strip()
            if v:
                out.extend([f"**{q}**", "", v, ""])
    return "\n".join(out)


def compile_book() -> str:
    out = [f"# The Vision Book of {name()}", f"*{chapter()} — {C.TAGLINE}*", f"_Compiled {TODAY.strftime('%d %B %Y')}_", ""]

    def add(title, val):
        if isinstance(val, list):
            val = ", ".join(val)
        if str(val).strip():
            out.extend([f"**{title}**", "", str(val), ""])

    out.append("## Who I'm Becoming")
    add("Core feelings", get("core_feelings", []))
    add("Values", get("values", []))
    for k, q in C.IDENTITY_PROMPTS:
        add(A(q), get(f"id::{k}"))
    add(A("Letter from my {next}-year-old self"), get("letter_next"))
    add("Best Possible Self", get("bestself"))
    add("My morning sentence", get("bestself_line"))
    for c in C.CATEGORIES:
        out.append(f"## {c['symbol']} {c['name']}")
        out.append(f"*{c['essence']}*\n")
        add("I want to feel", get(f"cat::{c['key']}::feelings", []))
        for k, q in c["prompts"]:
            add(q, get(f"cat::{c['key']}::{k}"))
        add("My process goals", get(f"cat::{c['key']}::my_process"))
    if items("ladders"):
        out.append("## Dreams → Process")
        for L in items("ladders"):
            out.append(f"### {L['dream']}")
            for lbl, k in [("Outcome", "outcome"), ("Performance", "perf"), ("Process", "process"), ("Tiny habit", "tiny"), ("If-then", "plan")]:
                add(lbl, L.get(k, ""))
    if items("beliefs"):
        out.append("## Beliefs I Rewrote")
        out.extend(f"- ~~{B['old']}~~ → **{B['new']}**" for B in items("beliefs"))
        out.append("")
    return "\n".join(out)


def storage_panel():
    S = store()
    if S.durable:
        card(f'<div class="eyebrow">☁ safe</div><h4>Your book is saved in your private repository</h4>'
             f'<div class="small">{esc(S.cloud.repo)} · every change is stored as it happens, and updates to the app '
             f'can no longer erase it. Phone and laptop see the same book.</div>', "blush")
    else:
        if S.problem:
            st.error(f"Cloud saving is set up but not working: {S.problem}")
        card('<div class="eyebrow">⚠ temporary storage</div><h4>Right now your writing only lives on the app’s server</h4>'
             '<div class="small">Online, Streamlit restarts the app after every update and after a period of rest — and then '
             'the server’s files are wiped. Set up private cloud saving once (≈10 minutes) and that can’t happen again.</div>', "wine")
        with st.expander("✦ Set up private cloud saving — step by step", expanded=True):
            st.markdown("""
**1 · Create a private vault for your journal**
On github.com click **+ → New repository**. Name: `vision-book-data`. Choose **Private** (important!). Click *Create repository*.

**2 · Create a key that only opens that vault**
Go to github.com → your photo → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
- Name: `vision book` · Expiration: 1 year (put a reminder in your agenda)
- **Repository access → Only select repositories →** `vision-book-data`
- **Permissions → Repository permissions → Contents → Read and write**
- Click *Generate token* and copy it (it starts with `github_pat_`). You see it only once.

**3 · Give the key to your app**
On share.streamlit.io → your app → **⋮ → Settings → Secrets**, and add below your password:
```toml
[storage]
github_token = "github_pat_...paste here..."
github_repo  = "YOUR-GITHUB-NAME/vision-book-data"
```
Save. The app restarts — this box turns blush pink and says ☁ *safe*.

**4 · Bring back what you still have**
If you downloaded a backup earlier, restore it below — it goes straight into the vault.
""")
    st.markdown("#### Backup & restore")
    st.caption("Extra safety: download a backup now and then and keep it somewhere you trust.")


def page_book():
    style.header("my book", "My Book & Settings", "Read your vision as one story — and keep it safe.")
    names = ["Read my book", "My journal", "Keep it safe", "Settings"]
    if not store().durable:  # safety first until the vault is set up
        names = ["Keep it safe"] + [n for n in names if n != "Keep it safe"]
    tabs = dict(zip(names, st.tabs(names)))
    t1, tj, t2, t3 = (tabs[n] for n in ["Read my book", "My journal", "Keep it safe", "Settings"])
    with tj:
        dates = journal_dates()
        if not dates:
            st.info("No journal pages yet.")
        else:
            period = st.radio("Show", ["This week", "Last 30 days", "Everything", "Choose dates"], horizontal=True)
            if period == "This week":
                start = TODAY - dt.timedelta(days=TODAY.weekday())
                end = TODAY
            elif period == "Last 30 days":
                start, end = TODAY - dt.timedelta(days=30), TODAY
            elif period == "Everything":
                start, end = dt.date.fromisoformat(dates[0]), TODAY
            else:
                rng = st.date_input("From – to", (TODAY - dt.timedelta(days=7), TODAY), max_value=TODAY, format="DD/MM/YYYY")
                start, end = (rng[0], rng[-1]) if isinstance(rng, tuple) and rng else (TODAY, TODAY)
            sel = [x for x in dates if start.isoformat() <= x <= end.isoformat()]
            st.markdown(f'<span class="saved">{len(sel)} page(s)</span>', unsafe_allow_html=True)
            mood_chart(sel, 220)
            jm = compile_journal(sel)
            st.download_button("Download these pages (Markdown)", jm, file_name=f"journal-{start}-{end}.md")
            with st.container(border=True):
                st.markdown(jm or "_Nothing written in this period._")
    with t1:
        md = compile_book()
        st.download_button("Download as Markdown", md, file_name=f"vision-book-{TODAY.isoformat()}.md")
        with st.container(border=True):
            st.markdown(md)
    with t2:
        storage_panel()
        st.download_button("Download full backup (.json)", json.dumps(D(), ensure_ascii=False, indent=2),
                           file_name=f"vision-book-backup-{TODAY.isoformat()}.json", mime="application/json")
        up = st.file_uploader("Restore from a backup", type=["json"])
        if up is not None and st.button("Restore — replace current book"):
            try:
                st.session_state.data = json.loads(up.getvalue().decode("utf-8"))
                persist()
                reset_widgets()
                st.success("Restored ✦")
                st.rerun()
            except json.JSONDecodeError:
                st.error("That file doesn't look like a Vision Book backup.")
    with t3:
        line("name", "My name", placeholder=C.OWNER)
        if not get("birthday"):
            v = st.number_input("My age right now", 16, 99, int(get("age", C.DEFAULT_AGE)),
                                help="The book is always written towards your next birthday.")
            if v != get("age", C.DEFAULT_AGE):
                D()["age"] = int(v)
                persist()
                st.rerun()
        st.caption(f"You're {age_now()} — this book is {chapter()}. Once you set your birthday, it turns the page by itself.")
        b = get("birthday")
        val = st.date_input("My birthday", dt.date.fromisoformat(b) if b else None,
                            min_value=dt.date(1980, 1, 1), max_value=TODAY, format="DD/MM/YYYY")
        if val and val.isoformat() != b:
            D()["birthday"] = val.isoformat()
            persist()
            st.rerun()


# ===========================================================================
PAGES = {
    "Welcome": ("❦", page_home),
    "Who I'm Becoming": ("✧", page_identity),
    "Life Chapters": ("◎", page_chapters),
    "Horizons": ("⟡", page_horizons),
    "Goals → Process": ("⇡", page_goals),
    "Daily Journal": ("✎", page_journal),
    "Belief Alchemy": ("⚗", page_beliefs),
    "Comfort Zone": ("◌", page_comfort),
    "Visualise": ("☾", page_visualise),
    "Muses & Mood Board": ("✿", page_muses),
    "My Book": ("❧", page_book),
}


def main():
    if not gate():
        return
    D()
    with st.sidebar:
        st.markdown(f'<div class="eyebrow">the vision book of</div>'
                    f'<div class="muse-name" style="font-size:2rem">{esc(name())}</div>'
                    f'<div class="muse-role">{chapter()}</div>', unsafe_allow_html=True)
        st.session_state.setdefault("nav", "Welcome")
        st.radio("Navigate", list(PAGES), key="nav", label_visibility="collapsed",
                 format_func=lambda p: f"{PAGES[p][0]}   {p}")
        style.ornament()
        lang, aff, trans = C.AFFIRMATIONS[day_index(len(C.AFFIRMATIONS))]
        st.markdown(f'<div class="serif" style="font-style:italic;font-size:1.1rem">{esc(aff)}</div>'
                    f'<div class="small" style="color:#8A7472">{esc(trans)}</div>', unsafe_allow_html=True)
        if st.session_state.get("save_error"):
            st.markdown('<br><div class="saved" style="color:#B04A4A">⚠ last change not saved to the cloud</div>', unsafe_allow_html=True)
        elif store().durable:
            st.markdown('<br><div class="saved">☁ saved in your private vault</div>', unsafe_allow_html=True)
        else:
            st.markdown('<br><div class="saved" style="color:#B04A4A">⚠ temporary storage only</div>', unsafe_allow_html=True)
            st.button("Make it safe →", on_click=go_to, args=("My Book",), key="mksafe")
    PAGES[st.session_state.nav][1]()


main()
