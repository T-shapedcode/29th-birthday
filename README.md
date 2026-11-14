# ❦ The Vision Book

A private, elegant guide & journal for becoming the woman you envision: identity narrative,
life chapters, psychological exercises, guided visualisations, daily journaling and a mood board.

## What's inside

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

## Run it

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The chapter follows your age (set it, or your birthday, in **My Book → Settings**; default 26 → Chapter 27).
Everything autosaves to `data/vision_book.json` (git-ignored, stays private on your device).

### Online (Streamlit Community Cloud)
1. Deploy this repo on [share.streamlit.io](https://share.streamlit.io).
2. In the app's **Secrets**, add `password = "your-secret-key"` so only you can open the book.
3. Cloud apps can restart and forget files — use **My Book → Download full backup** regularly, and restore it when needed.

## Make it yours
All prompts, quotes, affirmations, dares and visualisation scripts live in `vision_book/content.py` — plain text, easy to edit.
