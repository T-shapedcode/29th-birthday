"""Elegant, warm, feminine styling: ivory paper, blush, wine and champagne gold."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Jost:wght@300;400;500&display=swap');

:root {
  --ivory: #FBF7F2;
  --paper: #FFFDFA;
  --blush: #F4E1DC;
  --rose: #D9A5A0;
  --wine: #9E5A63;
  --wine-deep: #6E3A42;
  --gold: #B8975A;
  --ink: #3B2A2C;
  --muted: #8A7472;
  --line: #EADBD3;
}

html, body, [class*="css"], .stMarkdown, p, li, label, textarea, input {
  font-family: 'Jost', sans-serif !important;
  font-weight: 300;
  color: var(--ink);
}
h1, h2, h3, h4, .serif {
  font-family: 'Cormorant Garamond', serif !important;
  font-weight: 500 !important;
  color: var(--wine-deep) !important;
  letter-spacing: .01em;
}
h1 { font-size: 3rem !important; line-height: 1.05 !important; }
h2 { font-size: 2.1rem !important; }
h3 { font-size: 1.5rem !important; }

.stApp {
  background:
    radial-gradient(1200px 500px at 100% -10%, #F6E4DE 0%, rgba(246,228,222,0) 60%),
    radial-gradient(900px 400px at -10% 110%, #F3E6D6 0%, rgba(243,230,214,0) 60%),
    var(--ivory);
}
.block-container { padding-top: 4rem; max-width: 1100px; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F6E8E2 0%, #F3E7DD 100%);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] .stRadio label p { font-size: 1.02rem; }

/* Inputs */
textarea, .stTextInput input, .stDateInput input {
  background: var(--paper) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  font-size: 1rem !important;
  line-height: 1.6 !important;
}
textarea:focus, .stTextInput input:focus { border-color: var(--rose) !important; box-shadow: 0 0 0 3px rgba(217,165,160,.18) !important; }
.stTextArea label p, .stTextInput label p, .stSlider label p, .stMultiSelect label p, .stSelectbox label p {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 1.22rem !important; font-weight: 500; font-style: italic; color: var(--wine-deep) !important;
}

/* Buttons */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
  border-radius: 999px !important;
  border: 1px solid var(--wine) !important;
  background: var(--paper) !important;
  color: var(--wine-deep) !important;
  font-family: 'Jost', sans-serif !important;
  letter-spacing: .08em; text-transform: uppercase; font-size: .78rem !important;
  padding: .45rem 1.3rem !important;
  transition: all .25s ease;
}
.stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
  background: var(--wine) !important; color: #fff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
  font-family: 'Cormorant Garamond', serif !important; font-size: 1.15rem; color: var(--muted);
  background: transparent; border-radius: 12px 12px 0 0; padding: .4rem 1rem;
}
.stTabs [aria-selected="true"] { color: var(--wine-deep) !important; background: var(--blush) !important; }

/* Expanders */
div[data-testid="stExpander"] details {
  background: var(--paper); border: 1px solid var(--line); border-radius: 16px;
}
div[data-testid="stExpander"] summary p { font-family: 'Cormorant Garamond', serif !important; font-size: 1.2rem; color: var(--wine-deep); }

/* Custom components */
.eyebrow { font-family: 'Jost', sans-serif; letter-spacing: .32em; text-transform: uppercase; font-size: .72rem; color: var(--gold); margin-bottom: .2rem; }
.lede { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.35rem; color: var(--muted); margin-top: -.4rem; }
.ornament { text-align: center; color: var(--gold); letter-spacing: .6em; margin: 1.6rem 0; font-size: .9rem; }

.card {
  background: var(--paper); border: 1px solid var(--line); border-radius: 22px;
  padding: 1.4rem 1.6rem; margin-bottom: 1rem;
  box-shadow: 0 10px 30px -18px rgba(110,58,66,.25);
}
.card h4 { margin: 0 0 .3rem 0; font-size: 1.45rem !important; }
.card .small { color: var(--muted); font-size: .9rem; }
.card.blush { background: linear-gradient(135deg, #F8E7E2, #FBF1EA); }
.card.wine { background: linear-gradient(135deg, #8E4E57, #6E3A42); border: none; }
.card.wine, .card.wine * { color: #FBF1EA !important; }

.quote {
  font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.8rem; line-height: 1.3;
  color: var(--wine-deep); text-align: center; padding: .8rem 1rem 0;
}
.quote-by { text-align: center; letter-spacing: .25em; text-transform: uppercase; font-size: .7rem; color: var(--gold); margin-top: .6rem; }

.psych {
  border-left: 2px solid var(--gold); padding: .5rem 1rem; margin: .4rem 0 1.2rem;
  background: rgba(184,151,90,.07); border-radius: 0 12px 12px 0; font-size: .93rem; color: var(--muted);
}
.psych b { color: var(--wine-deep); font-weight: 500; }

.chip {
  display: inline-block; padding: .22rem .75rem; margin: .15rem .2rem .15rem 0; border-radius: 999px;
  background: var(--blush); color: var(--wine-deep); font-size: .82rem; border: 1px solid #EBCFC8;
}
.chip.gold { background: rgba(184,151,90,.12); border-color: rgba(184,151,90,.35); }

.step { display: flex; gap: 1rem; align-items: flex-start; margin: .7rem 0; }
.step .n {
  flex: 0 0 2.1rem; height: 2.1rem; border-radius: 50%; border: 1px solid var(--gold); color: var(--gold);
  display: flex; align-items: center; justify-content: center; font-family: 'Cormorant Garamond', serif; font-size: 1.1rem;
}
.step .t { font-family: 'Cormorant Garamond', serif; font-size: 1.25rem; line-height: 1.45; }

.ladder { display: flex; flex-direction: column; gap: .5rem; }
.rung { border-radius: 14px; padding: .7rem 1rem; background: var(--paper); border: 1px solid var(--line); }
.rung .lbl { letter-spacing: .2em; text-transform: uppercase; font-size: .68rem; color: var(--gold); }

.muse-name { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; color: var(--wine-deep); line-height: 1.1; }
.muse-role { font-size: .85rem; color: var(--muted); margin-bottom: .6rem; }

.stat { text-align: center; }
.stat .v { font-family: 'Cormorant Garamond', serif; font-size: 2.4rem; color: var(--wine); line-height: 1; }
.stat .l { letter-spacing: .2em; text-transform: uppercase; font-size: .66rem; color: var(--muted); }

.saved { color: var(--gold); font-size: .78rem; letter-spacing: .15em; text-transform: uppercase; }

#MainMenu, footer { visibility: hidden; }
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def header(eyebrow: str, title: str, lede: str = "") -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if lede:
        st.markdown(f'<div class="lede">{lede}</div>', unsafe_allow_html=True)


def ornament() -> None:
    st.markdown('<div class="ornament">✦ ❦ ✦</div>', unsafe_allow_html=True)


def psych(text: str, label: str = "Why this works") -> None:
    st.markdown(f'<div class="psych"><b>{label} ·</b> {text}</div>', unsafe_allow_html=True)


def chips(items, gold: bool = False) -> str:
    cls = "chip gold" if gold else "chip"
    return "".join(f'<span class="{cls}">{i}</span>' for i in items)
