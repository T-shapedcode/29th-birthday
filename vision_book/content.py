"""All prompts, exercises, scripts and inspiration that fill the Vision Book.

Everything here is plain data so it is easy to edit, translate or extend.
"""

OWNER = "Tatyana"
DEFAULT_AGE = 26  # the book is written towards the NEXT birthday: Chapter {next}
TAGLINE = "The year I walk my talk — and adore the woman doing it."

# ---------------------------------------------------------------------------
# Core desired feelings (inspired by Danielle LaPorte's "Desire Map" idea:
# set goals by how you want to FEEL, then choose actions that create it).
# ---------------------------------------------------------------------------
FEELINGS = [
    "Adored", "Radiant", "Alive", "Free", "Grounded", "Magnetic", "Sovereign",
    "Elegant", "Playful", "Abundant", "Calm", "Powerful", "Cherished", "Inspired",
    "Safe", "Sensual", "Disciplined", "Curious", "Light", "Brave", "Respected",
    "Seen", "Nourished", "Creative", "Focused", "Joyful", "Worthy", "Wild",
]

# ---------------------------------------------------------------------------
# Life categories — each one is a chapter of the book.
# ---------------------------------------------------------------------------
CATEGORIES = [
    {
        "key": "self",
        "name": "Self-Love & Body",
        "symbol": "❦",
        "essence": "Being adored — starting with the way I treat myself.",
        "psych": "Self-compassion (Kristin Neff) predicts more motivation, not less: "
                 "women who treat themselves kindly recover faster from setbacks and keep going.",
        "prompts": [
            ("vision", "Describe a regular Tuesday in which you feel completely adored by yourself. What do you do from waking up to falling asleep?"),
            ("rituals", "Which rituals make you feel like a woman who is taken care of? (beauty, movement, food, rest, clothes, scent…)"),
            ("body", "How do you want to speak to and about your body? Write three sentences you will use from now on."),
            ("nonneg", "My non-negotiables of self-care (the things I protect even on busy days):"),
        ],
        "process": ["Move my body 4x per week", "Lights out before 23:00", "One beauty ritual every evening", "Eat one colourful, nourishing meal daily"],
    },
    {
        "key": "love",
        "name": "Love & Partnership",
        "symbol": "♡",
        "essence": "A love that feels safe, sparkling and grown-up.",
        "psych": "Attachment research shows we accept the love we believe we deserve. "
                 "Clear standards are not demands — they are self-respect made visible.",
        "prompts": [
            ("vision", "Describe the relationship you are creating. What does an ordinary evening together look like? A Sunday morning? A disagreement?"),
            ("treated", "How do I want to be treated? Be specific: words, gestures, attention, respect, loyalty, ambition."),
            ("feel", "How do I want to FEEL with my partner — and who am I when I feel that way?"),
            ("give", "What do I bring? How do I love, support and inspire the person I choose?"),
            ("standards", "My standards & deal-breakers (calmly written, without apology):"),
            ("pattern", "Which old pattern am I lovingly leaving behind?"),
        ],
        "process": ["Say what I need within 24h instead of hoping it is guessed", "One date or quality evening per week", "Notice & name one thing I appreciate daily"],
    },
    {
        "key": "career",
        "name": "Career & Calling",
        "symbol": "✦",
        "essence": "Work that uses my T-shape: depth in one thing, breadth in many — and pays me well for it.",
        "psych": "'Designing Your Life' (Burnett & Evans, Stanford) shows that sketching several possible "
                 "futures — Odyssey Plans — creates more energy and less fear than chasing one 'right' path.",
        "prompts": [
            ("vision", "It is three years from now and you love your work. Describe your workday, your clients, your income, your reputation."),
            ("zone", "My zone of genius — what do people thank me for that feels effortless to me?"),
            ("odyssey1", "Odyssey Plan 1 — The path I'm already on, fully grown:"),
            ("odyssey2", "Odyssey Plan 2 — If that path disappeared tomorrow, what would I do?"),
            ("odyssey3", "Odyssey Plan 3 — The wild one: if money and opinions didn't matter…"),
            ("known", "What do I want to be known for? (one sentence)"),
        ],
        "process": ["Two deep-work blocks per week on my own business", "One visible post / piece of content weekly", "One meaningful conversation with someone ahead of me per month"],
    },
    {
        "key": "money",
        "name": "Money & Abundance",
        "symbol": "◈",
        "essence": "Money as a calm, elegant partner that funds my freedom.",
        "psych": "Money scripts (Klontz) are beliefs we absorb before age 10. Naming them makes them "
                 "choosable. Abundance is a mindset AND a set of very concrete numbers.",
        "prompts": [
            ("story", "My money story: what did I learn about money growing up (spoken or unspoken)?"),
            ("numbers", "My numbers: monthly income I'm creating, savings rate, investment amount, 'freedom fund' goal."),
            ("feel", "How do I want to feel when I open my banking app?"),
            ("spend", "What do I spend on with zero guilt because it reflects my values? What do I happily cut?"),
            ("receive", "Where do I block receiving (compliments, help, payment, raising prices)? How will I practise receiving?"),
        ],
        "process": ["Weekly 20-min 'money date' with myself", "Automate savings on payday", "Send one offer / invoice / raise-request I've been postponing"],
    },
    {
        "key": "experiences",
        "name": "Experiences & Adventure",
        "symbol": "✈",
        "essence": "A life that feels like a film I would want to rewatch.",
        "psych": "Experiences produce longer-lasting happiness than possessions (Van Boven & Gilovich): "
                 "they become part of identity and stories we share.",
        "prompts": [
            ("bucket", "My bucket list for this year (places, skills, moments):"),
            ("languages", "Where will I use my Italian, French and Russian? Describe the scene — the café, the people, the conversation."),
            ("alive", "When did I last feel completely alive? What were the ingredients?"),
            ("solo", "One experience I'll gift myself alone, just because I deserve it:"),
        ],
        "process": ["Plan one new experience every month", "15 minutes of language practice daily", "Say yes to one invitation I'd normally decline"],
    },
    {
        "key": "home",
        "name": "Home & Aesthetic",
        "symbol": "❀",
        "essence": "A home and wardrobe that already belong to the woman I'm becoming.",
        "psych": "Environment design beats willpower (Wendy Wood, habit research). Your space is a silent coach.",
        "prompts": [
            ("home", "Walk through your future home. Light, materials, scent, sound, what's on the table, what's on the walls:"),
            ("style", "My signature style in five words — and three pieces I'd wear as 'future me':"),
            ("cue", "Which object in my home will remind me daily of who I'm becoming?"),
            ("release", "What do I release (clothes, clutter, objects) that belongs to an old version of me?"),
        ],
        "process": ["10-minute evening reset of my space", "Fresh flowers or one beautiful detail weekly", "Dress for future me, even when working from home"],
    },
    {
        "key": "mind",
        "name": "Mind, Spirit & Discipline",
        "symbol": "☯",
        "essence": "A calm, focused mind that chooses instead of reacts.",
        "psych": "Shi Heng Yi teaches the five hindrances to self-mastery (from Buddhist psychology): "
                 "sensual desire, ill-will, sloth & torpor, restlessness, doubt. Naming them weakens them.",
        "prompts": [
            ("practice", "My daily practice of stillness (meditation, breath, prayer, walk, journaling):"),
            ("hindrance", "Which of the five hindrances visits me most often? What does it whisper, and how will I answer it?"),
            ("discipline", "What does discipline look like when it's an act of self-love, not punishment?"),
            ("learn", "What do I want to master or study this year?"),
        ],
        "process": ["10 minutes of stillness every morning", "Phone-free first hour 5x a week", "Read 20 pages a day"],
    },
    {
        "key": "joy",
        "name": "Friendships & Joy",
        "symbol": "✿",
        "essence": "Women who rise together, laughter, play and real connection.",
        "psych": "The Harvard Study of Adult Development (80+ years) found that the quality of our "
                 "relationships is the strongest predictor of health and happiness.",
        "prompts": [
            ("circle", "Who is in my inner circle? Who would I love to grow closer to?"),
            ("friend", "What kind of friend do I want to be?"),
            ("play", "What did I love doing as a girl that I could bring back? (dancing, painting, singing…)"),
            ("community", "What community or circle would I love to belong to — or create?"),
        ],
        "process": ["One intentional friend-date per week", "One hour of pure play weekly", "Send one voice note of appreciation weekly"],
    },
]

CATEGORY_BY_KEY = {c["key"]: c for c in CATEGORIES}

# ---------------------------------------------------------------------------
# Identity — "The Woman I Am Becoming"
# ---------------------------------------------------------------------------
IDENTITY_PROMPTS = [
    ("she_is", "Who is she? Describe the {next}-year-old you as if you were writing her character for a film. How does she walk into a room?"),
    ("i_am", "Write 5–10 'I am the kind of woman who…' statements. (Identity-based habits, James Clear: every action is a vote for who you become.)"),
    ("values", "Her top 5 values — and what each one looks like in behaviour:"),
    ("voice", "How does she speak — to herself, to others, about her dreams?"),
    ("no", "What does she say NO to without guilt?"),
    ("signature", "Her signature: three habits, three phrases, three style details that make her unmistakably her."),
]

VALUES_LIST = [
    "Freedom", "Love", "Growth", "Beauty", "Courage", "Integrity", "Adventure",
    "Wisdom", "Health", "Family", "Creativity", "Independence", "Elegance",
    "Excellence", "Kindness", "Abundance", "Discipline", "Joy", "Authenticity",
    "Connection", "Faith", "Justice", "Learning", "Play", "Security", "Impact",
    "Self-respect", "Loyalty", "Passion", "Peace",
]

# Hershfield: stronger "future self continuity" -> better long-term choices.
FUTURE_LETTER_GUIDE = (
    "Psychologist Hal Hershfield found that the more connected we feel to our future self, the "
    "better we take care of her today. Write a letter FROM yourself on your {nth} birthday TO you "
    "now. Tell her what you're proud of, what she let go of, what she was afraid of that turned out "
    "fine, and what she should start doing this week."
)

BEST_SELF_GUIDE = (
    "Best Possible Self (Laura King, 2001). Imagine everything has gone as well as it possibly could. "
    "You worked hard and succeeded at all your life goals. Write for 15 minutes, in the present tense, "
    "with as many sensory details as you can. Studies show this boosts optimism and well-being for weeks."
)

# ---------------------------------------------------------------------------
# Limiting beliefs — reframing tools
# ---------------------------------------------------------------------------
COMMON_BELIEFS = [
    "I'm not ready yet.",
    "Wanting a lot of money makes me greedy.",
    "If I ask for what I need, I'll be too much.",
    "Good things don't last for me.",
    "I have to earn rest.",
    "Who am I to charge that much?",
    "Successful women have to sacrifice love.",
    "It's too late to start over.",
    "People will judge me if I show who I really am.",
    "I always lose my discipline after a few weeks.",
]

BYRON_KATIE = [
    "Is it true?",
    "Can I absolutely know that it's true?",
    "How do I react — what happens — when I believe that thought?",
    "Who would I be without that thought?",
]

# ---------------------------------------------------------------------------
# Comfort-zone dares (graded exposure: start at a 3/10, climb to 8/10)
# ---------------------------------------------------------------------------
DARES = [
    # (category, level 1-10, dare)
    ("self", 3, "Eat a beautiful lunch alone, phone away, as if you are your own date."),
    ("self", 5, "Take 10 photos of yourself you genuinely love — no deleting, no filters."),
    ("self", 6, "Receive a compliment with only 'Thank you' — no deflecting, no explaining."),
    ("love", 4, "Tell someone exactly what you appreciate about them, in detail."),
    ("love", 6, "Express a need clearly in one sentence, without apologising."),
    ("love", 8, "Say no to something that doesn't fit your standards — and don't justify it."),
    ("career", 4, "Share one insight from your coaching work publicly."),
    ("career", 6, "Message someone you admire and ask for a 20-minute conversation."),
    ("career", 7, "Record a 60-second video about what you do and post it."),
    ("career", 8, "Raise your price — or name it out loud without dropping your eyes."),
    ("money", 3, "Open your banking app and look calmly at every number for 5 minutes."),
    ("money", 5, "Calculate exactly what your dream lifestyle costs per month."),
    ("money", 7, "Send the invoice / offer / proposal you've been postponing."),
    ("experiences", 3, "Order your coffee in Italian, French or Russian today (online counts)."),
    ("experiences", 5, "Go to an event, class or exhibition alone."),
    ("experiences", 7, "Have a 10-minute conversation entirely in a language you're learning."),
    ("home", 3, "Give away five items that belong to an old version of you."),
    ("home", 5, "Wear the outfit you're 'saving for a special occasion' — today is the occasion."),
    ("mind", 4, "Sit in silence for 15 minutes. No music, no phone, no book."),
    ("mind", 6, "Spend a full day without complaining. Restart the count if you slip."),
    ("joy", 4, "Invite a friend for something new you've both never done."),
    ("joy", 6, "Dance or sing where someone might see you."),
    ("joy", 8, "Organise a gathering of women you'd love to know better."),
]

# ---------------------------------------------------------------------------
# Guided visualisations. Process visualisation (imagining the STEPS) works
# better than outcome-only fantasy (Taylor & Pham, 1999; Oettingen).
# ---------------------------------------------------------------------------
VISUALIZATIONS = [
    {
        "key": "next_birthday",
        "title": "The Morning of My {nth} Birthday",
        "type": "Outcome · identity",
        "minutes": 8,
        "steps": [
            "Close your eyes. Take three slow breaths, exhaling longer than you inhale.",
            "It is the morning of your {nth} birthday. Notice where you wake up. The light. The sheets. The scent in the room.",
            "Before you open your phone, you lie still and feel it: you kept your promises to yourself this year.",
            "Walk to the mirror. Look at the woman there. What has changed in her eyes, her posture, her skin, her smile?",
            "You get dressed. What do you choose to wear? Feel the fabric on your skin.",
            "Messages are arriving. Who is writing to you? What do they say about the year you've had?",
            "Think of your work, your bank account, your love life, your body. Let one image appear for each.",
            "Future you turns to you — the {now}-year-old — and says one sentence. Listen. Remember it.",
            "Breathe in that feeling. Anchor it: press your thumb and middle finger together. Open your eyes.",
        ],
        "reflect": "What sentence did she say to you? What feeling will you carry today?",
    },
    {
        "key": "walkthrough",
        "title": "A Walk Through My Ideal Day",
        "type": "Process · lifestyle",
        "minutes": 10,
        "steps": [
            "Settle in. Shoulders down, jaw soft, three deep breaths.",
            "You wake up naturally on an ordinary weekday in the life you designed. What time is it?",
            "Your morning ritual: what do you do first — movement, stillness, coffee, journaling? Feel each step.",
            "You start work. Where are you? Who are you helping? What problem are you solving that energises you?",
            "Lunch: what do you eat, where, with whom?",
            "Afternoon: notice a moment of challenge. Watch yourself handle it calmly and competently.",
            "Evening: you come home to your space. Who is there, or what does solitude feel like?",
            "Before sleep you write three lines in your journal. Read them over your own shoulder.",
            "Pick ONE element of this day you can bring into tomorrow. Open your eyes.",
        ],
        "reflect": "Which element of the ideal day will I bring into tomorrow — and at what time?",
    },
    {
        "key": "obstacle",
        "title": "Rehearsing the Hard Moment",
        "type": "Process · mental contrasting",
        "minutes": 6,
        "steps": [
            "Think of the goal that matters most to you right now. See the best outcome vividly for 30 seconds.",
            "Now gently ask: what inside ME is most likely to stop me? (a feeling, a habit, a thought)",
            "See that obstacle arriving as a scene: the time, the place, the moment you'd normally give in.",
            "Watch yourself pause. One breath. You recognise it: 'Ah, there you are.'",
            "See yourself doing the planned action instead — in detail, step by step.",
            "Feel the quiet pride afterwards. This is what keeping promises to yourself feels like.",
            "Formulate it: 'IF ___ happens, THEN I will ___.' Say it three times.",
        ],
        "reflect": "My IF-THEN plan:",
    },
    {
        "key": "temple",
        "title": "The Inner Temple (stillness)",
        "type": "Calm · self-mastery",
        "minutes": 7,
        "steps": [
            "Sit upright like a mountain: rooted below, light above.",
            "Count ten breaths. If a thought pulls you away, smile, and begin again at one — no judgement.",
            "Imagine a quiet courtyard. Stone, a tree, the sound of water. This is your inner temple.",
            "Five visitors knock: desire, irritation, tiredness, restlessness, doubt. Let each come in, bow, and leave.",
            "In the centre of the courtyard: you, calm and awake. Nothing to prove, nothing to chase.",
            "Ask: 'What does the wisest part of me want me to know today?' Wait for the answer.",
            "Bow to yourself. Return slowly.",
        ],
        "reflect": "What did the wisest part of me say?",
    },
    {
        "key": "adored",
        "title": "Being Adored",
        "type": "Receiving · self-worth",
        "minutes": 6,
        "steps": [
            "Place one hand on your heart, one on your belly. Feel the warmth of your own hands.",
            "Remember a moment you felt truly cherished — by anyone, even briefly. Let it fill your chest.",
            "Now imagine the person who will adore you in exactly the way you deserve. Not their face — their presence.",
            "Notice how they look at you. How they listen. What they do without being asked.",
            "Now notice: you already know this feeling. You can give it to yourself first.",
            "Say silently: 'I am easy to love. I receive love with grace.'",
        ],
        "reflect": "What does being adored feel like in my body? How can I give that to myself this week?",
    },
]

# ---------------------------------------------------------------------------
# Muses — inspirational women & teachers. Descriptions describe what each
# person is publicly known for; the "what she awakens in me" part is yours.
# ---------------------------------------------------------------------------
MUSES = [
    {
        "name": "Grace Beverley",
        "role": "Entrepreneur · founder of TALA · author of 'Working Hard, Hardly Working'",
        "embodies": ["Ambition with balance", "Building a business from your own passion", "Productivity without burnout", "Owning your success unapologetically"],
        "lesson": "Productivity is not about doing more; it's about designing a life where hard work and rest both have a place.",
    },
    {
        "name": "Lidia Poët",
        "role": "The first woman admitted to the Italian bar (Turin, 1883)",
        "embodies": ["Intellect & elegance", "Refusing to be made small", "Fighting for women's rights", "Persistence for decades when the door closed"],
        "lesson": "When they struck her from the register, she kept working anyway — and lived to see the law change.",
    },
    {
        "name": "Jamie Sea",
        "role": "Your muse — describe her in your own words",
        "embodies": ["(add what she represents to you)"],
        "lesson": "Write the lesson she teaches you below.",
    },
    {
        "name": "Shi Heng Yi",
        "role": "Shaolin master · head of Shaolin Temple Europe",
        "embodies": ["Self-mastery", "Calm discipline", "Awareness of the five hindrances", "Strength without aggression"],
        "lesson": "Mastery begins with seeing clearly what is happening inside you — before you try to change it.",
    },
    {
        "name": "The Woman Who Values Herself",
        "role": "The archetype — the you of Chapter {next}",
        "embodies": ["Passionate about her life", "Keeps promises to herself", "Receives with grace", "Chooses, never settles"],
        "lesson": "She doesn't wait to be chosen. She chooses — herself first.",
    },
]

# Widely-documented quotes only. Add your own on the Muse page.
QUOTES = [
    ("Life shrinks or expands in proportion to one's courage.", "Anaïs Nin"),
    ("Tell me, what is it you plan to do with your one wild and precious life?", "Mary Oliver"),
    ("The soul becomes dyed with the color of its thoughts.", "Marcus Aurelius"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("You yourself, as much as anybody in the entire universe, deserve your love and affection.", "Sharon Salzberg (after the Buddha)"),
    ("Do one thing every day that scares you.", "Eleanor Roosevelt (attributed)"),
    ("Nothing is impossible; the word itself says 'I'm possible'!", "Audrey Hepburn"),
    ("I am not afraid of storms, for I am learning how to sail my ship.", "Louisa May Alcott"),
    ("Caring for myself is not self-indulgence, it is self-preservation.", "Audre Lorde"),
    ("The most courageous act is still to think for yourself. Aloud.", "Coco Chanel"),
    ("Between stimulus and response there is a space. In that space is our power to choose our response.", "Viktor Frankl (attributed)"),
    ("Be the heroine of your life, not the victim.", "Nora Ephron"),
]

# Affirmations in the languages you're practising — one per day.
AFFIRMATIONS = [
    ("Italiano", "Sono la donna che scelgo di essere.", "I am the woman I choose to be."),
    ("Français", "Je mérite d'être adorée — et je commence par moi-même.", "I deserve to be adored — and I start with myself."),
    ("Русский", "Я выбираю себя каждый день.", "I choose myself every day."),
    ("Italiano", "La mia vita è un'opera d'arte che creo ogni giorno.", "My life is a work of art I create every day."),
    ("Français", "L'abondance coule vers moi avec élégance.", "Abundance flows towards me with elegance."),
    ("Русский", "Я спокойна, сильна и свободна.", "I am calm, strong and free."),
    ("Italiano", "Mantengo le promesse che faccio a me stessa.", "I keep the promises I make to myself."),
    ("Français", "J'ose sortir de ma zone de confort.", "I dare to step out of my comfort zone."),
    ("Русский", "Я достойна любви и уважения.", "I am worthy of love and respect."),
    ("Italiano", "Ricevo amore, denaro e gioia con gratitudine.", "I receive love, money and joy with gratitude."),
    ("Français", "Je marche comme je parle.", "I walk my talk."),
    ("Русский", "Моя жизнь полна страсти и смысла.", "My life is full of passion and meaning."),
]

SELF_CARE = [
    "Water & nourishing food", "Movement", "Daylight / fresh air", "Beauty ritual",
    "Stillness (10 min)", "Language practice", "Reading", "Phone-free first hour",
    "Dressed as future me", "In bed on time",
]

JOURNAL_MORNING = [
    ("feel", "Today I want to feel… (three words)"),
    ("future_me", "What would {next}-year-old me do today?"),
    ("adore", "One way I will adore myself today:"),
    ("brave", "One brave act (outside my comfort zone):"),
    ("ifthen", "IF ___ gets in my way, THEN I will ___"),
]

JOURNAL_EVENING = [
    ("good", "Three good things today — and why they happened (Seligman):"),
    ("walked", "Where did I walk my talk today?"),
    ("gap", "Where didn't I? (with self-compassion: what did I need in that moment?)"),
    ("proud", "One thing future me is proud of:"),
]

WEEKLY_REVIEW = [
    ("wins", "Wins of this week (big and tiny):"),
    ("lessons", "What did I learn about myself?"),
    ("evidence", "Evidence that I am becoming her:"),
    ("adjust", "What will I adjust next week? (not more effort — smarter design)"),
    ("focus", "My ONE focus for next week:"),
]


# ---------------------------------------------------------------------------
# Horizons — the further future, one chapter at a time.
# Construal-level theory (Trope & Liberman): we think about the distant future
# in abstract "why" terms and the near future in concrete "how" terms. So the
# far horizons ask about essence and values; the near one asks about actions.
# Backcasting connects them: "what must be true by {next} for this to happen?"
# ---------------------------------------------------------------------------
HORIZONS = [
    {
        "key": "near",
        "label": "Chapter {next}",
        "span": "the next 12 months",
        "mode": "ink",
        "essence": "Concrete. Daily. This is where you live — the rest of the book is this chapter.",
        "prompts": [
            ("headline", "If this year were a film, its title would be…"),
            ("three", "The three things that would make Chapter {next} unforgettable:"),
        ],
    },
    {
        "key": "mid",
        "label": "Chapters {mid_from}–{mid_to}",
        "span": "2 to 5 years from now",
        "mode": "pencil",
        "essence": "Broad strokes. Write it in pencil, not ink — directions, not plans.",
        "prompts": [
            ("life", "At {mid_to}, a regular week in my life looks like…"),
            ("work", "My work and income at {mid_to}, in a few sentences:"),
            ("love", "My love life and home at {mid_to}:"),
            ("bridge", "Backcasting: what must be true by {next} so that this future becomes likely?"),
        ],
    },
    {
        "key": "far",
        "label": "Chapter {far}+",
        "span": "10 years and beyond",
        "mode": "watercolour",
        "essence": "Essence only. Who she is, what she stands for, how she makes people feel.",
        "prompts": [
            ("essence", "At {far}, what does my life stand for?"),
            ("legacy", "What do the people I love say about me when I'm not in the room?"),
            ("whisper", "What does {far}-year-old me whisper to me today?"),
            ("bridge", "Backcasting: which one quality must I start practising now to become her?"),
        ],
    },
]
