# ❦ The Vision Book

A private, elegant guide & journal for becoming the woman you envision: identity narrative,
life chapters, psychological exercises, guided visualisations, daily journaling and a mood board.

## ✦ Recommended: the offline app (`docs/`)

An installable web app that keeps **everything on your own device**: no server that restarts and forgets.

- **Works offline.** Once opened, it runs without internet.
- **Saved with every letter you type**, in the browser's storage on your phone or laptop.
- **Optional backup file** (Chrome/Edge on a laptop): auto-saves into a file you choose, e.g. in iCloud Drive / OneDrive / Google Drive.
- **Optional private vault**: syncs phone ⇄ laptop through a *private* GitHub repository (public ones are refused).
  Edits from both devices are merged per field. Old data from the Streamlit version loads automatically.
- Install it: iPhone → Safari → Share → *Add to Home Screen*; Android / laptop → browser menu → *Install app*.

**Put it online (once):** repository **Settings → Pages → Build and deployment → Deploy from a branch →**
branch `claude/vision-book-app-oe1pni` (or `main` after merging), folder **`/docs`** → Save.
After a minute it's live at `https://t-shapedcode.github.io/29th-birthday/`.
Anyone could open that address, but they'd only see an empty book of their own: your writing never leaves your devices and your private vault.

Test locally: `cd docs && python3 -m http.server` → http://localhost:8000

---

## The original Streamlit version (`streamlit_app.py`)

### What's inside

| Page | What you do there | Psychology behind it |
|---|---|---|
| **Welcome** | Quote & affirmation of the day (IT / FR / RU), stats, your wheel of life | Priming, language practice |
| **Who I'm Becoming** | Her portrait, values & core feelings, letter from your next-birthday self, Best Possible Self, *walk my talk* audit | Identity-based habits, future-self continuity (Hershfield), Best Possible Self (King), ACT values |
| **Life Chapters** | Wheel of life + 8 chapters: Self-Love & Body, Love & Partnership, Career & Calling, Money & Abundance, Experiences, Home & Aesthetic, Mind & Spirit, Friendships & Joy | Structural tension (Fritz), Odyssey Plans, money scripts (Klontz) |
| **Horizons** | Timeline: Chapter 27 in ink, 2–5 years in pencil, 10+ years as essence — linked by backcasting | Construal-level theory, backcasting |
| **Goals → Process** | Dream → outcome → quarterly markers → weekly process goals → tiny habit, with WOOP & if-then shield and a weekly promise tracker | Process goals, WOOP (Oettingen), implementation intentions (Gollwitzer), Tiny Habits (Fogg) |
| **Daily Journal** | Morning intention, self-care checklist, evening reflection, weekly review, mood/energy/adored chart | Three Good Things (Seligman), self-distancing, self-compassion (Neff) |
| **Belief Alchemy** | Rewrite limiting beliefs and rate their strength before/after | ABC model (CBT), Byron Katie's four questions, behavioural experiments |
| **Comfort Zone** | Draw a daily dare by chapter & intensity, log expected vs. felt fear | Comfort–stretch–panic zones, graded exposure |
| **Visualise** | Five guided scripts, step by step | Process simulation (Taylor & Pham), mental contrasting |
| **Muses & Mood Board** | Muses (Grace Beverley, Lidia Poët, Jamie Sea, Shi Heng Yi…), Pinterest/image board, quotes | Role models (Lockwood & Kunda) |
| **My Book** | Read everything as one story, export Markdown, backup/restore, settings | |

### Run it

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The chapter follows your age (set it, or your birthday, in **My Book → Settings**; default 26 → Chapter 27).
Everything autosaves to `data/vision_book.json` (git-ignored, stays private on your device).

### ⚠ Keep your journal safe online
Streamlit Cloud wipes the app's local files on every update and restart. Online, connect a **private**
GitHub repository as your journal's vault (the app refuses public ones). Step-by-step instructions are in the app under
**My Book → Keep it safe**. In short, add to your app's Secrets:

```toml
[storage]
github_token = "github_pat_..."              # fine-grained token: only that repo, Contents read & write
github_repo  = "your-name/vision-book-data"  # PRIVATE repository
```

Edits from phone and laptop are merged per field, so both devices can be used.

### Online (Streamlit Community Cloud)
1. Deploy this repo on [share.streamlit.io](https://share.streamlit.io).
2. In the app's **Secrets**, add `password = "your-secret-key"` so only you can open the book.
3. Set up the private vault (see below) so your journal survives restarts and updates.

### Make it yours
All prompts, quotes, affirmations, dares and visualisation scripts live in `vision_book/content.py`. After editing, regenerate the offline app's copy with:

```bash
python3 -c "import json,sys; sys.path.insert(0,'.'); from vision_book import content as C; n=[k for k in dir(C) if k.isupper() and k!='CATEGORY_BY_KEY']; open('docs/content.js','w').write('export const C = '+json.dumps({k:getattr(C,k) for k in n},ensure_ascii=False,indent=1)+';\\n')"
```
