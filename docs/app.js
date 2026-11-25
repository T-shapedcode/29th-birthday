// The Vision Book — offline-first app. Everything you write stays on your device
// (and, if you connect them, in your backup file and private vault).
import { C } from "./content.js";
import * as S from "./store.js";

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
const B = () => S.state.book;
const get = (k, d = "") => (Object.prototype.hasOwnProperty.call(B(), k) ? B()[k] : d);
const set = (k, v) => { B()[k] = v; S.save(); };
const items = (n) => { if (!Array.isArray(B()[n])) B()[n] = []; return B()[n]; };
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const nl = (s) => esc(s).replace(/\n/g, "<br>");
const $ = (s, el = document) => el.querySelector(s);

const pad = (n) => String(n).padStart(2, "0");
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parse = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const today = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; };
const TODAY = () => iso(today());
const monday = (d) => addDays(d, -((d.getDay() + 6) % 7));
function isoWeek(d) {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = t.getUTCDay() || 7; t.setUTCDate(t.getUTCDate() + 4 - day);
  const y = t.getUTCFullYear(); const w = Math.ceil(((t - Date.UTC(y, 0, 1)) / 864e5 + 1) / 7);
  return [y, w];
}
const weekKey = (d) => { const [y, w] = isoWeek(d); return `${y}-W${pad(w)}`; };
const fmt = (s, o = { weekday: "long", day: "numeric", month: "long", year: "numeric" }) => parse(s).toLocaleDateString("en-GB", o);
const dayIndex = (n) => Math.floor(today().getTime() / 864e5) % n;

function ageNow() {
  const b = get("birthday");
  if (b) {
    const d = parse(b), t = today();
    return t.getFullYear() - d.getFullYear() - ((t.getMonth() < d.getMonth() || (t.getMonth() === d.getMonth() && t.getDate() < d.getDate())) ? 1 : 0);
  }
  return Number(get("age", C.DEFAULT_AGE));
}
const ordinal = (n) => n + ((n % 100 >= 11 && n % 100 <= 13) ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"));
function ages() { const now = ageNow(); return { now, next: now + 1, nth: ordinal(now + 1), mid_from: now + 2, mid_to: now + 5, far: now + 10 }; }
const A = (s) => { const a = ages(); return String(s).replace(/\{(now|next|nth|mid_from|mid_to|far)\}/g, (_, k) => a[k]); };
const chapter = () => `Chapter ${ageNow() + 1}`;
const name = () => get("name") || C.OWNER;

const journalDates = () => [...new Set(Object.keys(B()).filter((k) => k.startsWith("journal::")).map((k) => k.split("::")[1]))].sort();
function streak() {
  const ds = new Set(journalDates()); let n = 0, d = today();
  if (!ds.has(iso(d))) d = addDays(d, -1);
  while (ds.has(iso(d))) { n++; d = addDays(d, -1); }
  return n;
}
const filled = (keys) => keys.filter((k) => String(get(k)).trim()).length;

// ---------------------------------------------------------------------------
// UI building blocks (return HTML strings)
// ---------------------------------------------------------------------------
const header = (eyebrow, title, lede = "") =>
  `<div class="eyebrow">${eyebrow}</div><h1>${title}</h1>${lede ? `<div class="lede">${lede}</div>` : ""}`;
const ornament = () => `<div class="ornament">✦ ❦ ✦</div>`;
const psych = (t, label = "Why this works") => `<div class="psych"><b>${label} ·</b> ${t}</div>`;
const chips = (arr, gold = false) => arr.map((x) => `<span class="chip ${gold ? "gold" : ""}">${esc(x)}</span>`).join("");
const card = (body, cls = "") => `<div class="card ${cls}">${body}</div>`;

const text = (k, label, rows = 4, ph = "Write freely…") =>
  `<div class="field">${label ? `<label>${esc(label)}</label>` : ""}<textarea data-k="${esc(k)}" rows="${rows}" placeholder="${esc(ph)}">${esc(get(k))}</textarea></div>`;
const line = (k, label, ph = "") =>
  `<div class="field">${label ? `<label>${esc(label)}</label>` : ""}<input type="text" data-k="${esc(k)}" value="${esc(get(k))}" placeholder="${esc(ph)}"></div>`;
const slider = (k, label, lo = 1, hi = 10, def = 5) => {
  const v = get(k, def);
  return `<div class="field"><div class="row between"><span class="lbl">${esc(label)}</span><span class="range-val" data-show="${esc(k)}">${v}</span></div>
  <input type="range" min="${lo}" max="${hi}" value="${v}" data-k="${esc(k)}" data-num></div>`;
};
const check = (k, label) =>
  `<label class="check"><input type="checkbox" data-k="${esc(k)}" ${get(k, false) ? "checked" : ""}> ${esc(label)}</label>`;
const multi = (k, label, opts, max = 99, rerender = false) => {
  const sel = get(k, []);
  return `<div class="field"><span class="lbl">${esc(label)} <span class="small" style="font-style:normal">(choose up to ${max})</span></span>
  <div>${opts.map((o) => `<button type="button" class="pick ${sel.includes(o) ? "on" : ""}" data-multi="${esc(k)}" data-opt="${esc(o)}" data-max="${max}" ${rerender ? "data-rerender" : ""}>${esc(o)}</button>`).join("")}</div></div>`;
};
const tabs = (group, labels) => {
  const cur = ui.tabs[group] ?? labels[0];
  return `<div class="tabs">${labels.map((l) => `<button class="${l === cur ? "on" : ""}" data-act="tab" data-g="${group}" data-v="${esc(l)}">${esc(l)}</button>`).join("")}</div>`;
};
const tabIs = (group, label, first) => (ui.tabs[group] ?? first) === label;
const btn = (label, act, args = {}, cls = "") =>
  `<button type="button" class="${cls}" data-act="${act}" ${Object.entries(args).map(([k, v]) => `data-${k}="${esc(v)}"`).join(" ")}>${label}</button>`;

// ---------------------------------------------------------------------------
// charts (pure SVG — work offline)
// ---------------------------------------------------------------------------
function radar(size = 430) {
  const cats = C.CATEGORIES, n = cats.length, cx = size / 2, cy = size / 2, R = size * 0.32;
  const pt = (i, v) => { const a = -Math.PI / 2 + (i * 2 * Math.PI) / n; return [cx + Math.cos(a) * R * v / 10, cy + Math.sin(a) * R * v / 10]; };
  const poly = (vals) => vals.map((v, i) => pt(i, v).join(",")).join(" ");
  const now = cats.map((c) => Number(get(`wheel::${c.key}::now`, 5)));
  const want = cats.map((c) => Number(get(`wheel::${c.key}::want`, 9)));
  let g = "";
  for (const r of [2, 4, 6, 8, 10]) g += `<polygon points="${poly(Array(n).fill(r))}" fill="none" stroke="#EADBD3"/>`;
  cats.forEach((c, i) => {
    const [x, y] = pt(i, 10), [lx, ly] = pt(i, 12.4);
    const anchor = Math.abs(lx - cx) < 10 ? "middle" : lx > cx ? "start" : "end";
    g += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="#EADBD3"/>`;
    g += `<text x="${lx}" y="${ly + 4}" text-anchor="${anchor}" font-size="${size * 0.034}" fill="#6E3A42">${esc(c.name)}</text>`;
  });
  g += `<polygon points="${poly(want)}" fill="rgba(184,151,90,.1)" stroke="#B8975A" stroke-dasharray="4 4" stroke-width="1.5"/>`;
  g += `<polygon points="${poly(now)}" fill="rgba(158,90,99,.22)" stroke="#9E5A63" stroke-width="2"/>`;
  now.forEach((v, i) => { const [x, y] = pt(i, v); g += `<circle cx="${x}" cy="${y}" r="3" fill="#9E5A63"/>`; });
  return `<svg viewBox="-120 -10 ${size + 240} ${size + 20}" style="width:100%;max-width:600px;display:block;margin:auto">${g}</svg>
  <div class="small" style="text-align:center"><span style="color:#9E5A63">●</span> Today &nbsp; <span style="color:#B8975A">◌</span> The life I'm creating</div>`;
}

function lineChart(dates, height = 220) {
  const series = [["mood", "Mood", "#9E5A63"], ["energy", "Energy", "#B8975A"], ["adored", "Felt adored", "#D9A5A0"]];
  const has = series.filter(([k]) => dates.some((d) => get(`journal::${d}::${k}`, null) !== null));
  if (!dates.length || !has.length) return "";
  const W = 700, H = height, L = 30, Rr = 10, T = 14, Bt = 34;
  const x = (i) => (dates.length === 1 ? (L + W - Rr) / 2 : L + (i * (W - L - Rr)) / (dates.length - 1));
  const y = (v) => T + (H - T - Bt) * (1 - v / 10);
  let g = "";
  for (const v of [0, 5, 10]) g += `<line x1="${L}" x2="${W - Rr}" y1="${y(v)}" y2="${y(v)}" stroke="#EADBD3"/><text x="${L - 8}" y="${y(v) + 4}" text-anchor="end" font-size="12" fill="#8A7472">${v}</text>`;
  const step = Math.max(1, Math.ceil(dates.length / 7));
  dates.forEach((d, i) => { if (i % step === 0 || i === dates.length - 1) g += `<text x="${x(i)}" y="${H - 10}" text-anchor="middle" font-size="12" fill="#8A7472">${fmt(d, { weekday: "short", day: "numeric", month: "short" })}</text>`; });
  for (const [k, , col] of has) {
    const pts = dates.map((d, i) => [i, get(`journal::${d}::${k}`, null)]).filter((p) => p[1] !== null);
    g += `<polyline fill="none" stroke="${col}" stroke-width="2.2" stroke-linejoin="round" points="${pts.map(([i, v]) => `${x(i)},${y(v)}`).join(" ")}"/>`;
    pts.forEach(([i, v]) => (g += `<circle cx="${x(i)}" cy="${y(v)}" r="3.5" fill="${col}"/>`));
  }
  const legend = has.map(([, n, col]) => `<span style="color:${col}">●</span> ${n}`).join(" &nbsp; ");
  return `<div class="small">${legend}</div><svg viewBox="0 0 ${W} ${H}" style="width:100%;display:block">${g}</svg>`;
}

function barChart(rows) {
  const W = 700, H = 220, L = 26, T = 10, Bt = 30, n = rows.length, bw = Math.min(26, (W - L) / n / 2.6);
  const y = (v) => T + (H - T - Bt) * (1 - v / 10);
  let g = "";
  for (const v of [0, 5, 10]) g += `<line x1="${L}" x2="${W}" y1="${y(v)}" y2="${y(v)}" stroke="#EADBD3"/><text x="${L - 6}" y="${y(v) + 4}" text-anchor="end" font-size="12" fill="#8A7472">${v}</text>`;
  rows.forEach((r, i) => {
    const cx = L + ((i + 0.5) * (W - L)) / n;
    g += `<rect x="${cx - bw - 1}" y="${y(r.pred)}" width="${bw}" height="${y(0) - y(r.pred)}" rx="4" fill="#D9A5A0"/>`;
    g += `<rect x="${cx + 1}" y="${y(r.real)}" width="${bw}" height="${y(0) - y(r.real)}" rx="4" fill="#9E5A63"/>`;
    g += `<text x="${cx}" y="${H - 10}" text-anchor="middle" font-size="11" fill="#8A7472">${fmt(r.date, { day: "numeric", month: "short" })}</text>`;
  });
  return `<div class="small"><span style="color:#D9A5A0">■</span> Fear I expected &nbsp; <span style="color:#9E5A63">■</span> Fear I felt</div><svg viewBox="0 0 ${W} ${H}" style="width:100%">${g}</svg>`;
}

// ---------------------------------------------------------------------------
// state of the interface (not saved)
// ---------------------------------------------------------------------------
const ui = { tabs: {}, chapter: 0, horizon: 0, viz: 0, vizStep: {}, vizFull: false, jdate: null, period: "This week", from: null, to: null, dareCats: null, dareMax: 6, boardFilter: "All", belief: "" };

// ===========================================================================
// PAGES
// ===========================================================================
const PAGES = [
  ["home", "Welcome", "❦"], ["identity", "Who I'm Becoming", "✧"], ["chapters", "Life Chapters", "◎"], ["horizons", "Horizons", "⟡"],
  ["goals", "Goals → Process", "⇡"], ["journal", "Daily Journal", "✎"], ["beliefs", "Belief Alchemy", "⚗"], ["comfort", "Comfort Zone", "◌"],
  ["visualise", "Visualise", "☾"], ["muses", "Muses & Mood Board", "✿"], ["book", "My Book & Backup", "❧"],
];

function pageHome() {
  const [lang, aff, trans] = C.AFFIRMATIONS[dayIndex(C.AFFIRMATIONS.length)];
  const greet = { "Italiano": "Buongiorno", "Français": "Bonjour", "Русский": "Доброе утро" }[lang];
  let [q, by] = C.QUOTES[dayIndex(C.QUOTES.length)];
  const own = items("quotes");
  if (own.length && dayIndex(2)) ({ text: q, by } = own[dayIndex(own.length)]);
  const dateStr = today().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  let next = "—", nextL = "set birthday in My Book";
  if (get("birthday")) {
    const b = parse(get("birthday")); let nb = new Date(today().getFullYear(), b.getMonth(), b.getDate());
    if (nb < today()) nb = new Date(today().getFullYear() + 1, b.getMonth(), b.getDate());
    next = Math.round((nb - today()) / 864e5); nextL = "days to my next birthday";
  }
  const stats = [[journalDates().length, "journal days"], [streak(), "day streak"], [items("beliefs").length, "beliefs rewritten"],
    [items("dares").filter((d) => d.done).length, "dares completed"], [next, nextL]];
  const feels = get("core_feelings", []);
  const her = String(get("id::she_is")).trim();
  const dare = get(`dare::${TODAY()}`);
  return `${header(`${chapter()} · ${dateStr}`, `${greet}, ${esc(name())}.`, C.TAGLINE)}
  ${ornament()}<div class="quote">“${esc(q)}”</div><div class="quote-by">${esc(by)}</div>${ornament()}
  <div class="grid g4" style="grid-template-columns:repeat(auto-fit,minmax(120px,1fr))">${stats.map(([v, l]) => `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`).join("")}</div><br>
  <div class="grid g2"><div>
    ${card(`<div class="eyebrow">affirmation of the day · ${lang}</div><h4>${esc(aff)}</h4><div class="small">${esc(trans)}</div><div class="small" style="margin-top:.6rem">Say it out loud three times — then write it once by hand.</div>`, "blush")}
    ${card(`<div class="eyebrow">how I choose to feel</div>${feels.length ? chips(feels) : `<span class="small">Choose them in “Who I'm Becoming”.</span>`}`)}
    ${her ? card(`<div class="eyebrow">she is…</div><div class="serif" style="font-size:1.2rem;font-style:italic">${esc(her.slice(0, 420))}${her.length > 420 ? "…" : ""}</div>`) : ""}
    ${card(`<div class="eyebrow">today's brave act</div><h4>${dare ? esc(dare) : "Not drawn yet."}</h4><div class="small">Growth lives just outside the comfort zone — not in panic, not in comfort.</div>`, "wine")}
  </div><div><div class="eyebrow">the wheel of my life</div>${radar()}</div></div>
  ${ornament()}<h3>Where would you like to begin?</h3>
  <div class="grid g4">${[["Morning pages", "Set today's feeling & intention", "journal"], ["Meet her", "Write the woman you're becoming", "identity"],
    ["Rewrite a belief", "Turn a 'can't' into a choice", "beliefs"], ["Draw a dare", "One step outside your comfort zone", "comfort"]]
    .map(([t, s, p]) => card(`<h4>${t}</h4><div class="small">${s}</div><br>${btn("Open", "nav", { p })}`)).join("")}</div>`;
}

function pageIdentity() {
  const a = ages(), L = ["Her portrait", "Values & feelings", `Letter from ${a.next}`, "Best Possible Self", "Walk my talk"];
  let h = header("identity · narrative", "Who I'm Becoming", "Not a list of goals — a woman. Write her so clearly that you could recognise her walking down the street.") + tabs("id", L);
  if (tabIs("id", L[0], L[0])) {
    h += psych("Identity drives behaviour more reliably than goals. When you act from <i>“I am a woman who…”</i> instead of <i>“I should…”</i>, each action becomes a vote for who you are becoming (James Clear, <i>Atomic Habits</i>; self-perception theory, Bem).");
    h += C.IDENTITY_PROMPTS.map(([k, q]) => text(`id::${k}`, A(q), 5)).join("");
  } else if (tabIs("id", L[1], L[0])) {
    h += psych("Core desired feelings: decide how you want to <b>feel</b>, then choose the goals and habits that create that feeling. Values (Acceptance & Commitment Therapy) are directions, not destinations — you can live them today.");
    h += multi("core_feelings", "Choose 3–5 core feelings I want to live in", C.FEELINGS, 5, true);
    h += get("core_feelings", []).map((f) => text(`feel::${f}`, `What creates “${f}” for me? (people, places, habits, clothes, music…)`, 3)).join("");
    h += ornament() + multi("values", "Choose my top 5 values", C.VALUES_LIST, 5, true);
    h += get("values", []).map((v) => `<div class="grid g2">${text(`val::${v}::looks`, `${v} — what it looks like when I live it`, 3)}${slider(`val::${v}::score`, `How fully I live “${v}” right now`, 1, 10, 5)}</div>`).join("");
  } else if (tabIs("id", L[2], L[0])) {
    h += psych(A(C.FUTURE_LETTER_GUIDE), "Future-self continuity");
    h += `<div class="serif" style="font-size:1.3rem;font-style:italic">Dear ${esc(name())} at ${a.now},</div>`;
    h += text("letter_next", "", 16, A("I'm writing to you from the morning of our {nth} birthday…"));
    h += `<div class="serif" style="font-size:1.3rem;font-style:italic;text-align:right">With all my love, — you, at ${a.next}</div>`;
  } else if (tabIs("id", L[3], L[0])) {
    h += psych(C.BEST_SELF_GUIDE, "Best Possible Self") + text("bestself", "My best possible self, one year from today", 16, "It's a year from now. I wake up and…");
    h += line("bestself_line", "Now distil it: one sentence I want to read every morning");
  } else {
    h += psych("Walking your talk = value–behaviour congruence. The gap isn't failure; it's information. Look at it with curiosity (self-compassion), then design the next small step.");
    const vals = get("values", []), wk = weekKey(today());
    if (!vals.length) h += `<div class="banner">Choose your top values in the “Values & feelings” tab first.</div>`;
    h += `<div class="eyebrow">congruence audit · week ${wk}</div>`;
    h += vals.map((v) => `<details><summary>✦ ${esc(v)}</summary>${text(`talk::${wk}::${v}::yes`, `Where did I live ${v} this week?`, 3)}${text(`talk::${wk}::${v}::gap`, `Where did I drift from ${v}? What did I need in that moment?`, 3)}${line(`talk::${wk}::${v}::next`, "One tiny action that would close the gap next week")}</details>`).join("");
  }
  return h;
}

function pageChapters() {
  let h = header("life categories", "The Chapters of My Life", "Rate where you are, see where you're going — then write each chapter in the present tense.");
  h += psych("The Wheel of Life is a classic coaching tool. Seeing the gap between <i>today</i> and <i>the life I'm creating</i> creates healthy tension (Robert Fritz's 'structural tension') that pulls you forward.");
  const rated = C.CATEGORIES.some((c) => `wheel::${c.key}::now` in B());
  h += `<div class="grid g2"><div><details ${rated ? "" : "open"}><summary>Rate my wheel</summary>${C.CATEGORIES.map((c) =>
    `<div class="grid" style="grid-template-columns:1fr 1fr">${slider(`wheel::${c.key}::now`, `${c.symbol} ${c.name} · today`, 1, 10, 5)}${slider(`wheel::${c.key}::want`, A("by my {nth} birthday"), 1, 10, 9)}</div>`).join("")}
    ${btn("Update the wheel", "rerender", {}, "ghost")}</details>
    ${C.CATEGORIES.map((c) => { const keys = c.prompts.map(([k]) => `cat::${c.key}::${k}`), n = filled(keys);
      return `<div class="rung"><span class="rb lb">${c.symbol} ${n}/${keys.length} written</span><br><span class="serif" style="font-size:1.2rem">${c.name}</span><div class="progress"><i style="width:${(100 * n) / keys.length}%"></i></div></div>`; }).join("")}
  </div><div>${radar(480)}</div></div>${ornament()}`;
  h += `<div>${C.CATEGORIES.map((c, i) => `<button class="pick ${i === ui.chapter ? "on" : ""}" data-act="chapter" data-i="${i}">${c.symbol} ${c.name}</button>`).join("")}</div><br>`;
  const c = C.CATEGORIES[ui.chapter];
  h += `<div class="eyebrow">chapter</div><h2>${c.symbol} ${c.name}</h2><div class="lede">${c.essence}</div>${psych(c.psych)}`;
  h += multi(`cat::${c.key}::feelings`, "In this area of my life I want to feel…", C.FEELINGS, 4);
  h += c.prompts.map(([k, q]) => text(`cat::${c.key}::${k}`, q, 5)).join("");
  h += `<h4>From vision to process</h4><div class="small">Ideas for weekly process goals — fully in your control:</div>${chips(c.process, true)}<br><br>`;
  h += text(`cat::${c.key}::my_process`, "My process goals for this chapter (what I'll DO, weekly):", 3);
  h += btn("Turn a dream from this chapter into a ladder →", "nav", { p: "goals" });
  return h;
}

function pageHorizons() {
  const a = ages();
  let h = header("the long view", "Horizons", `You're ${a.now}. Live Chapter ${a.next} in ink — sketch the chapters after it in pencil.`);
  h += psych("Construal-level theory (Trope &amp; Liberman): the far future is best imagined in <b>why</b> — values, essence, feeling; the near future in <b>how</b> — concrete steps. <b>Backcasting</b> connects them: start from the distant picture and ask what must be true one step earlier. Big vision, small steps.");
  const nodes = [[`Today · ${a.now}`, "where you stand", "", 14, "#B8975A"], ...C.HORIZONS.map((H, i) => [A(H.label), H.span, H.mode, [46, 32, 22][i], ["#9E5A63", "#D9A5A0", "#F4E1DC"][i]])];
  h += card(`<div style="position:relative"><div style="position:absolute;left:12%;right:12%;top:24px;border-top:1px dashed #B8975A"></div>
    <div style="display:flex;position:relative">${nodes.map(([l, s, m, size, bg]) => `<div style="flex:1;text-align:center">
    <div style="height:48px;display:flex;align-items:center;justify-content:center"><div style="width:${size}px;height:${size}px;border-radius:50%;background:${bg};border:1px solid #B8975A"></div></div>
    <div class="serif" style="font-size:1.15rem;color:#6E3A42">${l}</div><div class="small">${s}${m ? `<br><i>${m}</i>` : ""}</div></div>`).join("")}</div></div>`);
  h += `<div>${C.HORIZONS.map((H, i) => `<button class="pick ${i === ui.horizon ? "on" : ""}" data-act="horizon" data-i="${i}">${A(H.label)} · ${H.span}</button>`).join("")}</div><br>`;
  const H = C.HORIZONS[ui.horizon];
  h += `<div class="eyebrow">${H.span} · written in ${H.mode}</div><h2>${A(H.label)}</h2><div class="lede">${H.essence}</div>`;
  h += multi(`hz::${H.key}::feelings`, "In this chapter I feel…", C.FEELINGS, 3);
  h += H.prompts.map(([k, q]) => text(`hz::${H.key}::${k}`, A(q), 4)).join("");
  if (H.key === "near") h += `<div class="small">Chapter ${a.next} is the heart of the book — go deeper in <i>Who I'm Becoming</i>, <i>Life Chapters</i> and <i>Goals → Process</i>.</div><br>${btn("Open Life Chapters →", "nav", { p: "chapters" })}`;
  else h += psych("Fill this lightly and revisit it on each birthday. Your future self is allowed to change her mind — only the <i>bridge</i> answer turns into action now.", "Pencil, not ink") + btn("Turn the bridge into a goal ladder →", "nav", { p: "goals" });
  return h;
}

function pageGoals() {
  let h = header("goal design", "From Dream to Daily Ritual", "Big goals inspire. Process goals change your life. Here you translate one into the other.");
  h += psych("Sport psychology distinguishes <b>outcome</b> goals (results you can't fully control), <b>performance</b> goals (personal markers) and <b>process</b> goals (behaviours fully in your control). Process goals reduce anxiety and raise consistency. Add <b>WOOP</b> (Gabriele Oettingen: Wish, Outcome, Obstacle, Plan) and if-then plans (Gollwitzer) — they roughly double follow-through in studies.");
  h += `<details ${items("ladders").length ? "" : "open"}><summary>✦ Build a new ladder</summary><form data-form="ladder">
    <div class="field"><label>Life chapter</label><select name="cat">${C.CATEGORIES.map((c) => `<option>${c.name}</option>`).join("")}</select></div>
    ${[["dream", "The dream (big, emotional, a little scary)", "Run a fully booked coaching practice I love"], ["outcome", A("Outcome goal — by my {nth} birthday"), "12 private clients and €X per month"]]
      .map(([n, l, p]) => `<div class="field"><label>${l}</label><input type="text" name="${n}" placeholder="${esc(p)}"></div>`).join("")}
    <div class="field"><label>Performance markers — quarterly milestones</label><textarea name="perf" rows="3" placeholder="Q1: offer defined & priced&#10;Q2: first 4 clients…"></textarea></div>
    <div class="field"><label>Process goals — weekly, 100% in my control</label><textarea name="process" rows="3" placeholder="2 deep-work blocks · 1 post · 3 conversations"></textarea></div>
    ${[["tiny", "Tiny daily habit (BJ Fogg): After I ___, I will ___", "After I pour my coffee, I will write one line of content"],
      ["obstacle", "WOOP · Obstacle — what inside ME is most likely to stop me?", "Perfectionism: I wait until it's 'ready'"],
      ["plan", "Plan — IF [obstacle], THEN I will…", "IF I want to polish more, THEN I publish at 80% and note one lesson"],
      ["feel", "When I reach this, I will feel…", "Proud, free, magnetic"]]
      .map(([n, l, p]) => `<div class="field"><label>${l}</label><input type="text" name="${n}" placeholder="${esc(p)}"></div>`).join("")}
    <button class="primary">Add to my book</button></form></details>`;
  const wk = weekKey(today());
  items("ladders").forEach((L, i) => {
    const rungs = [["the feeling", L.feel], [A("outcome · by {next}"), L.outcome], ["performance · quarterly", L.perf], ["process · weekly", L.process], ["tiny habit · daily", L.tiny], ["if-then shield", L.plan]];
    h += `<div class="eyebrow">${esc(L.cat)}</div><h3>${esc(L.dream)}</h3>${rungs.filter(([, v]) => v).map(([l, v]) => `<div class="rung"><div class="lb">${l}</div>${nl(v)}</div>`).join("")}
    <div class="row between"><label class="check"><input type="checkbox" data-act="ladderWeek" data-i="${i}" ${(L.weeks || []).includes(wk) ? "checked" : ""}> I lived my process goals this week (${wk})</label>
    <span class="status">${(L.weeks || []).length} week(s) of keeping my promise</span>${btn("Remove", "removeItem", { list: "ladders", i }, "ghost")}</div>${ornament()}`;
  });
  return h;
}

// --- journal ---------------------------------------------------------------
const DAY_FIELDS = [...C.JOURNAL_MORNING.slice(1), ...C.JOURNAL_EVENING, ["lang", "In another language"]];

function renderDay(x) {
  const f = get(`journal::${x}::feelings`, []);
  const meta = [["mood", "Mood"], ["energy", "Energy"], ["adored", "Adored"]].filter(([k]) => get(`journal::${x}::${k}`, null) !== null).map(([k, l]) => `${l} ${get(`journal::${x}::${k}`)}/10`);
  const care = C.SELF_CARE.filter((i) => get(`journal::${x}::care::${i}`, false));
  let h = f.length || meta.length ? `<div>${chips(f)}${chips(meta, true)}</div>` : "";
  for (const [k, q] of DAY_FIELDS) { const v = String(get(`journal::${x}::${k}`)).trim(); if (v) h += `<div class="book"><div class="q">${esc(A(q))}</div><p>${esc(v)}</p></div>`; }
  if (care.length) h += `<div class="small">Self-care: ${care.map(esc).join(" · ")}</div>`;
  return h || `<div class="small">Nothing written on this day.</div>`;
}

function pageJournal() {
  const d = ui.jdate || TODAY(), dd = parse(d), J = `journal::${d}::`, written = new Set(journalDates());
  let h = header("daily practice", "Daily Journal", "Small pages, written often, become a different life.");
  const mon = monday(dd);
  h += `<div class="week">${[0, 1, 2, 3, 4, 5, 6].map((i) => { const x = iso(addDays(mon, i));
    return `<button class="${x === d ? "on" : ""}" data-act="day" data-d="${x}" ${x > TODAY() ? "disabled" : ""}>${fmt(x, { weekday: "short" })} ${parse(x).getDate()} ${written.has(x) ? "●" : "○"}</button>`; }).join("")}</div>`;
  h += `<div class="row"><span class="lbl" style="margin:0">Page of</span><input type="date" data-act-change="pickdate" value="${d}" max="${TODAY()}" style="max-width:220px">
    ${btn("‹ week", "shiftWeek", { n: -7 }, "ghost")} ${mon <= addDays(today(), -7) ? btn("week ›", "shiftWeek", { n: 7 }, "ghost") : ""} ${d !== TODAY() ? btn("Today", "day", { d: TODAY() }, "ghost") : ""}</div>`;
  const L = ["☀ Morning", "☾ Evening", "Weekly review", "My story so far"];
  h += tabs("j", L);
  if (tabIs("j", L[0], L[0])) {
    h += psych("Morning intention-setting primes attention (what you look for, you find). Asking <i>“What would future me do?”</i> borrows her perspective — psychologists call it self-distancing, and it makes wiser choices easier.");
    h += multi(J + "feelings", "Today I want to feel…", C.FEELINGS, 3);
    h += C.JOURNAL_MORNING.slice(1).map(([k, q]) => text(J + k, A(q), 3)).join("");
    h += `<h4>Taking care of her</h4><div class="grid g2" style="gap:0 1rem">${C.SELF_CARE.map((i) => check(J + "care::" + i, i)).join("")}</div>`;
  } else if (tabIs("j", L[1], L[0])) {
    h += psych("‘Three good things’ (Martin Seligman) — writing three good things and <i>why</i> they happened increased happiness and reduced depressive symptoms for up to six months in a randomised trial.");
    h += `<div class="grid g3">${slider(J + "mood", "Mood", 1, 10, 6)}${slider(J + "energy", "Energy", 1, 10, 6)}${slider(J + "adored", "Felt adored (by me)", 1, 10, 6)}</div>`;
    h += C.JOURNAL_EVENING.map(([k, q]) => text(J + k, q, 3)).join("");
    const [lang, aff] = C.AFFIRMATIONS[Math.floor(dd.getTime() / 864e5) % C.AFFIRMATIONS.length];
    h += text(J + "lang", `Practise: write one sentence about today in ${lang} (e.g. “${aff}”)`, 2);
  } else if (tabIs("j", L[2], L[0])) {
    const wk = weekKey(dd), W = `week::${wk}::`, days = [0, 1, 2, 3, 4, 5, 6].map((i) => iso(addDays(mon, i))).filter((x) => written.has(x));
    h += `<div class="eyebrow">week ${wk}</div>` + psych("A weekly review turns experience into learning (Kolb's learning cycle). Focus on design changes, not on trying harder — willpower is a poor strategy, systems are a good one.");
    h += `<h3>First, read your week back (${days.length} of 7 days written)</h3>`;
    h += days.length ? lineChart(days, 200) + days.map((x) => `<details><summary>${fmt(x, { weekday: "long", day: "numeric", month: "long" })}</summary>${renderDay(x)}</details>`).join("")
      : `<div class="banner">No daily pages in this week yet — you can still reflect from memory.</div>`;
    h += `<h3>Then, reflect</h3>` + C.WEEKLY_REVIEW.map(([k, q]) => text(W + k, q, 3)).join("");
    h += `<h4>Quick pulse per chapter</h4><div class="grid g2">${C.CATEGORIES.map((c) => slider(W + "pulse::" + c.key, `${c.symbol} ${c.name}`, 1, 10, 5)).join("")}</div>`;
  } else {
    const ds = journalDates();
    if (!ds.length) h += `<div class="banner">Your story starts with the first page. Write this morning's intention ✦</div>`;
    else {
      h += lineChart(ds.slice(-60), 280);
      const care = C.SELF_CARE.map((i) => [i, ds.filter((x) => get(`journal::${x}::care::${i}`, false)).length]).filter(([, v]) => v).sort((a, b) => b[1] - a[1]);
      h += `<div class="eyebrow">self-care rituals kept</div>${chips(care.map(([k, v]) => `${k} · ${v}`), true)}<br><br>`;
      h += `<div class="small">Read a whole period at once in <a href="#book" data-act="nav" data-p="book">My Book → My journal</a>.</div><br>`;
      h += [...ds].reverse().map((x) => `<details><summary>${fmt(x)}</summary>${renderDay(x)}</details>`).join("");
    }
  }
  return h;
}

function pageBeliefs() {
  let h = header("cognitive reframing", "Belief Alchemy", "A belief is just a thought you've thought many times. You can practise a new one.");
  h += psych("This combines Albert Ellis' ABC model (CBT), Byron Katie's four questions and a behavioural experiment. Rating how strongly you believe a thought before and after helps you notice that beliefs move — and the tiny proof-action gives your brain new evidence.");
  const ta = (n, l, r = 2) => `<div class="field"><label>${l}</label><textarea name="${n}" rows="${r}"></textarea></div>`;
  h += `<details ${items("beliefs").length ? "" : "open"}><summary>✦ Transform a belief</summary><form data-form="belief">
    <div class="field"><label>Start from a common one, or write your own</label><select data-act-change="beliefPick"><option value="">— my own —</option>${C.COMMON_BELIEFS.map((b) => `<option>${esc(b)}</option>`).join("")}</select></div>
    <div class="field"><label>The belief that holds me back</label><input type="text" name="old" value="${esc(ui.belief)}" required></div>
    <div class="field"><div class="row between"><span class="lbl">How strongly do I believe it right now? (%)</span><output class="range-val">70</output></div><input type="range" name="before" min="0" max="100" value="70" oninput="this.previousElementSibling.lastElementChild.value=this.value"></div>
    ${ta("origin", "Where did I learn this? Whose voice is it?")}${ta("cost", "What has this belief cost me — in love, money, joy, freedom?")}
    <h4>The Work · four questions</h4>${C.BYRON_KATIE.map((q, i) => ta(`k${i}`, q)).join("")}
    ${ta("evidence", "Evidence that it is NOT (always) true — moments, people, facts:")}${ta("turn", "Turnaround — the opposite, and three ways it could be just as true:")}
    <div class="field"><label>My new, empowering belief (believable, not fake-positive):</label><input type="text" name="new" placeholder="I'm allowed to grow into readiness while doing it." required></div>
    <div class="field"><label>A tiny action that proves the new belief this week:</label><input type="text" name="proof"></div>
    <div class="field"><div class="row between"><span class="lbl">How strongly do I believe the OLD thought now? (%)</span><output class="range-val">40</output></div><input type="range" name="after" min="0" max="100" value="40" oninput="this.previousElementSibling.lastElementChild.value=this.value"></div>
    <button class="primary">Rewrite it</button></form></details>`;
  items("beliefs").map((b, i) => [b, i]).reverse().forEach(([b, i]) => {
    h += card(`<div class="eyebrow">${b.date} · belief strength ${b.before}% → ${b.after}%</div><div class="small" style="text-decoration:line-through">${esc(b.old)}</div><h4>✦ ${esc(b.new)}</h4>
      ${b.proof ? `<div class="small">Proof-action: ${esc(b.proof)}</div>` : ""}
      <div class="row between"><label class="check"><input type="checkbox" data-act="beliefProven" data-i="${i}" ${b.proven ? "checked" : ""}> I did the proof-action</label>${btn("Remove", "removeItem", { list: "beliefs", i }, "ghost")}</div>`);
  });
  return h;
}

const ZONES = `<svg viewBox="0 0 360 360" style="width:100%;max-width:330px;display:block;margin:auto">
<circle cx="180" cy="180" r="170" fill="#F4E1DC" stroke="#EADBD3"/><circle cx="180" cy="180" r="115" fill="#FBEFE8" stroke="#D9A5A0" stroke-dasharray="4 4"/><circle cx="180" cy="180" r="58" fill="#FFFDFA" stroke="#B8975A"/>
<text x="180" y="178" text-anchor="middle" font-size="18" fill="#6E3A42">comfort</text><text x="180" y="196" text-anchor="middle" font-size="9" letter-spacing="2" fill="#8A7472" font-family="Jost,sans-serif">SAFE · STATIC</text>
<text x="180" y="100" text-anchor="middle" font-size="19" font-style="italic" fill="#9E5A63">stretch — she lives here</text><text x="180" y="262" text-anchor="middle" font-size="9" letter-spacing="2" fill="#8A7472" font-family="Jost,sans-serif">FEAR 4–7 / 10 · GROWTH</text>
<text x="180" y="38" text-anchor="middle" font-size="16" fill="#8A7472">panic</text><text x="180" y="335" text-anchor="middle" font-size="9" letter-spacing="2" fill="#8A7472" font-family="Jost,sans-serif">FEAR 9–10 · TOO MUCH, TOO SOON</text></svg>`;

function darePool() {
  const cats = ui.dareCats || C.CATEGORIES.map((c) => c.key);
  return [...C.DARES, ...items("own_dares").map((x) => [x.cat, x.level, x.dare])].filter(([c, l]) => cats.includes(c) && l <= ui.dareMax);
}

function pageComfort() {
  const cats = ui.dareCats || C.CATEGORIES.map((c) => c.key);
  let h = header("courage practice", "Out of My Comfort Zone", "Confidence isn't the cause of brave action. It's the result.");
  h += `<div class="grid g2"><div>${ZONES}</div><div>${psych("The comfort–stretch–panic model (Karl Rohnke; Yerkes–Dodson): we learn best with moderate arousal. Graded exposure means climbing a ladder of fear — start around 3–4/10 and move up as each step becomes ordinary. Predict your fear before, rate it after: the gap is usually big, and that gap is the lesson.")}
    <span class="lbl">Draw from these chapters</span><div>${C.CATEGORIES.map((c) => `<button class="pick ${cats.includes(c.key) ? "on" : ""}" data-act="dareCat" data-k="${c.key}">${c.name}</button>`).join("")}</div><br>
    <div class="row between"><span class="lbl">Maximum intensity today</span><span class="range-val">${ui.dareMax}</span></div><input type="range" min="1" max="10" value="${ui.dareMax}" data-act-change="dareMax"><br><br>
    ${btn("✦ Draw today's dare", "drawDare", {}, "primary")}</div></div>`;
  const dare = get(`dare::${TODAY()}`);
  if (dare) {
    h += card(`<div class="eyebrow">today's dare</div><h4>${esc(dare)}</h4>`, "wine");
    h += `<form data-form="dareLog" class="card"><div class="grid g2">
      <div class="field"><div class="row between"><span class="lbl">Fear I expect (0–10)</span><output class="range-val">6</output></div><input type="range" name="pred" min="0" max="10" value="6" oninput="this.previousElementSibling.lastElementChild.value=this.value"></div>
      <div class="field"><div class="row between"><span class="lbl">Fear I actually felt (0–10)</span><output class="range-val">3</output></div><input type="range" name="real" min="0" max="10" value="3" oninput="this.previousElementSibling.lastElementChild.value=this.value"></div></div>
      <div class="field"><label>What I learned about myself:</label><input type="text" name="learned"></div><button class="primary">I did it ✦</button></form>`;
  }
  h += `<details><summary>Add my own dare to the deck</summary><form data-form="ownDare">
    <div class="field"><label>Chapter</label><select name="cat">${C.CATEGORIES.map((c) => `<option value="${c.key}">${c.name}</option>`).join("")}</select></div>
    <div class="field"><div class="row between"><span class="lbl">Intensity</span><output class="range-val">5</output></div><input type="range" name="level" min="1" max="10" value="5" oninput="this.previousElementSibling.lastElementChild.value=this.value"></div>
    <div class="field"><label>The dare</label><input type="text" name="dare" required></div><button>Add</button></form></details>`;
  const done = items("dares");
  if (done.length) {
    h += ornament() + `<h3>My courage log</h3>` + barChart(done.slice(-20));
    h += [...done].reverse().map((d) => `<div class="rung"><span class="lb">${d.date} · ${d.pred} → ${d.real}</span><br>${esc(d.dare)}<br><i class="small">${esc(d.learned || "")}</i></div>`).join("");
  }
  return h;
}

function pageVisualise() {
  const V = C.VISUALIZATIONS[ui.viz], n = V.steps.length, step = ui.vizStep[V.key] || 0;
  let h = header("guided imagery", "Visualise", "Read one line, close your eyes, see it. Then the next.");
  h += psych("Visualisation works best when you imagine the <b>process</b>, not only the result (Taylor & Pham, 1999). Pure fantasy can even lower your energy (Oettingen) — so these scripts always include the steps and the obstacles.");
  h += `<div class="field"><label>Choose a journey</label><select data-act-change="viz">${C.VISUALIZATIONS.map((v, i) => `<option value="${i}" ${i === ui.viz ? "selected" : ""}>${esc(A(v.title))} · ${v.minutes} min</option>`).join("")}</select></div>`;
  h += `<div class="eyebrow">${V.type}</div><h2>${esc(A(V.title))}</h2><div class="row">${btn("One step at a time", "vizMode", { full: 0 }, ui.vizFull ? "ghost" : "primary")}${btn("Full script", "vizMode", { full: 1 }, ui.vizFull ? "primary" : "ghost")}</div><br>`;
  if (ui.vizFull) h += V.steps.map((s, i) => `<div class="step"><div class="n">${i + 1}</div><div class="t">${esc(A(s))}</div></div>`).join("");
  else h += `<div class="progress"><i style="width:${(100 * (step + 1)) / n}%"></i></div>${card(`<div class="eyebrow">step ${step + 1} of ${n}</div><div class="quote">${esc(A(V.steps[step]))}</div>`, "blush")}
    <div class="row between">${btn("← Back", "vizStep", { d: -1 }, step === 0 ? "ghost" : "")}${btn("Next →", "vizStep", { d: 1 }, step === n - 1 ? "ghost" : "")}</div>`;
  return h + ornament() + text(`viz::${V.key}::${TODAY()}`, A(V.reflect), 4);
}

function pageMuses() {
  let h = header("inspiration", "Muses & Mood Board", "We become what we repeatedly look at. Curate it like a gallery.");
  h += psych("Role models work when they feel <b>relevant and attainable</b> (Lockwood & Kunda). So don't just admire them — ask what they would do in your situation, and borrow one behaviour.");
  const L = ["My muses", "Mood board", "Quotes"];
  h += tabs("m", L);
  if (tabIs("m", L[0], L[0])) {
    h += `<div class="grid g2">${[...C.MUSES, ...items("own_muses")].map((M) => `<div>${card(`<div class="muse-name">${esc(M.name)}</div><div class="muse-role">${esc(A(M.role))}</div>${chips(M.embodies || [])}<div class="serif" style="font-size:1.15rem;font-style:italic;margin-top:.7rem">${esc(M.lesson)}</div>`)}
      ${text(`muse::${M.name}::awakens`, "What she awakens in me / the behaviour I borrow", 3)}${line(`muse::${M.name}::wwsd`, "What would she do in my current situation?")}</div>`).join("")}</div>`;
    h += `<details><summary>Add a muse</summary><form data-form="muse">${[["name", "Name"], ["role", "Who she is"], ["embodies", "What she embodies (comma separated)"], ["lesson", "Her lesson for me"]]
      .map(([n, l]) => `<div class="field"><label>${l}</label><input type="text" name="${n}" ${n === "name" ? "required" : ""}></div>`).join("")}<button>Add</button></form></details>`;
  } else if (tabIs("m", L[1], L[0])) {
    h += `<div class="small">From Pinterest: open a pin → long-press / right-click the image → “Copy image address”, and paste it here. Or upload your own photos — they're kept on your device (and in your vault).</div><br>
    <form data-form="board" class="card"><div class="field"><label>Image link</label><input type="url" name="url" placeholder="https://i.pinimg.com/…"></div>
    <div class="field"><label>…or upload</label><input type="file" name="file" accept="image/*"></div>
    <div class="grid g2"><div class="field"><label>Caption / what it means to me</label><input type="text" name="caption"></div>
    <div class="field"><label>Chapter</label><select name="cat"><option>Everything</option>${C.CATEGORIES.map((c) => `<option>${c.name}</option>`).join("")}</select></div></div><button class="primary">Pin it</button></form>`;
    const board = items("board"), cats = [...new Set(board.map((b) => b.cat))].sort();
    if (board.length) h += `<div>${["All", ...cats].map((c) => `<button class="pick ${ui.boardFilter === c ? "on" : ""}" data-act="boardFilter" data-c="${esc(c)}">${esc(c)}</button>`).join("")}</div><br>`;
    h += `<div class="board">${board.map((b, i) => [b, i]).filter(([b]) => ui.boardFilter === "All" || b.cat === ui.boardFilter)
      .map(([b, i]) => `<figure><img data-src="${esc(b.src)}" alt="" loading="lazy">${b.caption ? `<figcaption>${esc(b.caption)}</figcaption>` : ""}<div style="text-align:center;padding:0 0 .6rem">${btn("Unpin", "removeItem", { list: "board", i }, "ghost")}</div></figure>`).join("")}</div>`;
  } else {
    h += [...C.QUOTES, ...items("quotes").map((x) => [x.text, x.by])].map(([q, by]) => `<div class="quote" style="font-size:1.4rem">“${esc(q)}”</div><div class="quote-by">${esc(by)}</div>`).join("");
    h += ornament() + `<form data-form="quote"><div class="field"><label>Add a quote that moves you</label><textarea name="text" rows="2" required></textarea></div><div class="field"><label>Who said it</label><input type="text" name="by"></div><button>Add quote</button></form>`;
  }
  return h;
}

// --- book -----------------------------------------------------------------
function bookNodes() {
  const out = [{ h1: `The Vision Book of ${name()}` }, { p: `${chapter()} — ${C.TAGLINE}` }];
  const add = (q, v) => { if (Array.isArray(v)) v = v.join(", "); if (String(v ?? "").trim()) out.push({ q, v: String(v) }); };
  out.push({ h2: "Who I'm Becoming" });
  add("Core feelings", get("core_feelings", [])); add("Values", get("values", []));
  C.IDENTITY_PROMPTS.forEach(([k, q]) => add(A(q), get(`id::${k}`)));
  add(A("Letter from my {next}-year-old self"), get("letter_next") || get("letter30"));
  add("Best Possible Self", get("bestself")); add("My morning sentence", get("bestself_line"));
  out.push({ h2: "Horizons" });
  C.HORIZONS.forEach((H) => H.prompts.forEach(([k, q]) => add(A(q), get(`hz::${H.key}::${k}`))));
  for (const c of C.CATEGORIES) {
    out.push({ h2: `${c.symbol} ${c.name}` }, { p: c.essence });
    add("I want to feel", get(`cat::${c.key}::feelings`, []));
    c.prompts.forEach(([k, q]) => add(q, get(`cat::${c.key}::${k}`)));
    add("My process goals", get(`cat::${c.key}::my_process`));
  }
  if (items("ladders").length) {
    out.push({ h2: "Dreams → Process" });
    items("ladders").forEach((L) => { out.push({ h3: L.dream }); [["Outcome", "outcome"], ["Performance", "perf"], ["Process", "process"], ["Tiny habit", "tiny"], ["If-then", "plan"]].forEach(([l, k]) => add(l, L[k])); });
  }
  if (items("beliefs").length) { out.push({ h2: "Beliefs I Rewrote" }); items("beliefs").forEach((b) => add(`✗ ${b.old}`, `✦ ${b.new}`)); }
  return out;
}

function journalNodes(dates) {
  const out = [];
  for (const x of dates) {
    out.push({ h3: fmt(x) });
    const f = get(`journal::${x}::feelings`, []);
    const sc = [["mood", "mood"], ["energy", "energy"], ["adored", "adored"]].filter(([k]) => get(`journal::${x}::${k}`, null) !== null).map(([k, l]) => `${l} ${get(`journal::${x}::${k}`)}/10`);
    if (f.length || sc.length) out.push({ p: [f.length ? "Feeling: " + f.join(", ") : "", sc.join(" · ")].filter(Boolean).join(" — ") });
    DAY_FIELDS.forEach(([k, q]) => { const v = String(get(`journal::${x}::${k}`)).trim(); if (v) out.push({ q: A(q), v }); });
  }
  const wanted = new Set(dates.map((x) => weekKey(parse(x))));
  [...new Set(Object.keys(B()).filter((k) => k.startsWith("week::")).map((k) => k.split("::")[1]))].sort().filter((w) => wanted.has(w)).forEach((w) => {
    out.push({ h3: `Weekly review · ${w}` });
    C.WEEKLY_REVIEW.forEach(([k, q]) => { const v = String(get(`week::${w}::${k}`)).trim(); if (v) out.push({ q, v }); });
  });
  return out;
}

const toHTML = (nodes) => `<div class="book">${nodes.map((n) => n.h1 ? `<h1>${esc(n.h1)}</h1>` : n.h2 ? `<h2>${esc(n.h2)}</h2>` : n.h3 ? `<h3>${esc(n.h3)}</h3>` : n.q ? `<div class="q">${esc(n.q)}</div><p>${esc(n.v)}</p>` : `<p class="small"><i>${esc(n.p)}</i></p>`).join("")}</div>`;
const toMD = (nodes) => nodes.map((n) => n.h1 ? `# ${n.h1}\n` : n.h2 ? `\n## ${n.h2}\n` : n.h3 ? `\n### ${n.h3}\n` : n.q ? `**${n.q}**\n\n${n.v}\n` : `*${n.p}*\n`).join("\n");

function download(name, content, type = "text/markdown") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name; document.body.appendChild(a); a.click(); a.remove();
}

function periodDates() {
  const ds = journalDates(), t = today();
  let from, to = TODAY();
  if (ui.period === "This week") from = iso(monday(t));
  else if (ui.period === "Last 30 days") from = iso(addDays(t, -30));
  else if (ui.period === "Everything") from = ds[0] || TODAY();
  else { from = ui.from || iso(addDays(t, -7)); to = ui.to || TODAY(); }
  return [from, to, ds.filter((x) => x >= from && x <= to)];
}

function safetyPanel() {
  const st = S.state.status, m = S.state.meta, v = m.vault;
  const when = (t) => (t ? new Date(t).toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "never");
  let h = psych("Your book now lives <b>on your own device</b>. There is no server that restarts and forgets — the app even works without internet. Two extra layers protect you if a phone gets lost or a browser is cleared.", "How your book is kept safe");
  h += card(`<div class="eyebrow">layer 1 · always on</div><h4>✓ On this device</h4><div class="small">Saved instantly with every letter you type, also offline.<br>
    <b>Tip:</b> install the app — iPhone: Safari → Share → <i>Add to Home Screen</i>. Android/laptop: browser menu → <i>Install app</i>. Then it opens like a real app, and the browser won't clear its storage.</div>`, "blush");
  if (S.fileSupported()) {
    h += card(`<div class="eyebrow">layer 2 · on your laptop</div><h4>${st.file === "connected" ? "✓ Backup file connected" : st.file === "needs-permission" ? "⚠ Backup file needs your OK" : "Backup file"}</h4>
      <div class="small">Choose a file in a folder that syncs to your cloud (iCloud Drive, OneDrive, Google Drive, Dropbox). Every change is copied into it automatically.${m.lastFileSave ? `<br>Last written: ${when(m.lastFileSave)}` : ""}</div><br>
      ${st.file === "connected" ? btn("Disconnect", "fileOff", {}, "ghost") : st.file === "needs-permission" ? btn("Allow again", "fileReconnect", {}, "primary") : btn("Choose backup file", "fileConnect", {}, "primary")}`);
  } else {
    h += card(`<div class="eyebrow">layer 2 · on your laptop</div><h4>Backup file</h4><div class="small">Open the app on your laptop in <b>Chrome</b> or <b>Edge</b> to let it save automatically into a file in your cloud folder. (Safari and phones don't support this — use layer 3 there.)</div>`);
  }
  const cs = { off: "Not connected", synced: `✓ Synced · ${when(m.lastCloudSync)}`, syncing: "Syncing…", offline: "Offline — will sync when you're back online", error: "⚠ Problem" }[st.cloud];
  h += card(`<div class="eyebrow">layer 3 · private vault (phone ⇄ laptop)</div><h4>${cs}</h4>
    ${st.cloud === "error" ? `<div class="banner">${esc(st.lastError)}</div>` : ""}
    ${v ? `<div class="small">Repository: <b>${esc(v.repo)}</b>. Your phone and laptop share one book; changes made on both are merged per field.</div><br>${btn("Sync now", "syncNow", {}, "primary")} ${btn("Disconnect", "vaultOff", {}, "ghost")}`
      : `<div class="small">Use the private repository and key (github_pat_…) you already made. If your old online app ever saved something there, it comes back automatically when you connect.</div><br>
      <form data-form="vault"><div class="field"><label>Repository</label><input type="text" name="repo" value="T-shapedcode/vision-book-data" required></div>
      <div class="field"><label>Key (github_pat_…)</label><input type="password" name="token" autocomplete="off" required></div><button class="primary">Connect my vault</button></form>`}`);
  h += card(`<div class="eyebrow">by hand</div><h4>Backup & restore</h4><div class="small">Last downloaded backup: ${when(m.lastExport)}</div><br>
    ${btn("Download full backup (.json)", "exportJSON", {}, "primary")}<br><br>
    <div class="field"><label>Restore from a backup (also works with backups from the old online app)</label><input type="file" accept=".json,application/json" data-act-change="restore"></div>`);
  return h;
}

function pageBook() {
  const L = ["Keep it safe", "Read my book", "My journal", "Settings"];
  let h = header("my book", "My Book & Backup", "Read your vision as one story — and keep it safe.") + tabs("b", L);
  if (tabIs("b", L[0], L[0])) h += safetyPanel();
  else if (tabIs("b", L[1], L[0])) {
    h += `<div class="row">${btn("Download (Markdown)", "exportBook")}${btn("Print / save as PDF", "print", {}, "ghost")}</div><br>` + card(toHTML(bookNodes()));
  } else if (tabIs("b", L[2], L[0])) {
    const [from, to, sel] = periodDates();
    h += `<div>${["This week", "Last 30 days", "Everything", "Choose dates"].map((p) => `<button class="pick ${ui.period === p ? "on" : ""}" data-act="period" data-p="${p}">${p}</button>`).join("")}</div><br>`;
    if (ui.period === "Choose dates") h += `<div class="row"><input type="date" value="${from}" max="${TODAY()}" data-act-change="from" style="max-width:200px"> → <input type="date" value="${to}" max="${TODAY()}" data-act-change="to" style="max-width:200px"></div><br>`;
    h += `<div class="status">${sel.length} page(s)</div>${lineChart(sel, 220)}<div class="row">${btn("Download these pages", "exportJournal")}${btn("Print / save as PDF", "print", {}, "ghost")}</div><br>`;
    h += card(sel.length ? toHTML(journalNodes(sel)) : `<i class="small">Nothing written in this period.</i>`);
  } else {
    h += line("name", "My name", C.OWNER);
    if (!get("birthday")) h += `<div class="field"><label>My age right now</label><input type="text" inputmode="numeric" data-act-change="age" value="${ageNow()}" style="max-width:120px"></div>`;
    h += `<div class="field"><label>My birthday</label><input type="date" data-act-change="birthday" value="${get("birthday")}" max="${TODAY()}" style="max-width:220px"></div>`;
    h += `<div class="small">You're ${ageNow()} — this book is ${chapter()}. With your birthday set, it turns the page by itself.</div>`;
  }
  return h;
}

const RENDER = { home: pageHome, identity: pageIdentity, chapters: pageChapters, horizons: pageHorizons, goals: pageGoals, journal: pageJournal,
  beliefs: pageBeliefs, comfort: pageComfort, visualise: pageVisualise, muses: pageMuses, book: pageBook };

// ===========================================================================
// shell, rendering & events
// ===========================================================================
const page = () => { const p = location.hash.slice(1); return RENDER[p] ? p : "home"; };

function sidebar() {
  const [, aff, trans] = C.AFFIRMATIONS[dayIndex(C.AFFIRMATIONS.length)];
  const st = S.state.status;
  const cloud = { synced: "☁ synced to your vault", syncing: "☁ syncing…", offline: "☁ offline — will sync later", error: "⚠ vault problem — see My Book" }[st.cloud] || "";
  return `<div class="eyebrow">the vision book of</div><div class="muse-name" style="font-size:2rem">${esc(name())}</div><div class="muse-role">${chapter()}</div>
  <nav class="nav">${PAGES.map(([k, l, ic]) => `<a href="#${k}" class="${k === page() ? "on" : ""}"><span class="ic">${ic}</span>${l}</a>`).join("")}</nav>
  ${ornament()}<div class="serif" style="font-style:italic;font-size:1.1rem">${esc(aff)}</div><div class="small">${esc(trans)}</div><br>
  <div class="status">✦ saved on this device</div>${cloud ? `<div class="status ${st.cloud === "error" ? "bad" : ""}">${cloud}</div>` : ""}
  ${st.file === "connected" ? `<div class="status">✦ backup file on</div>` : st.file === "needs-permission" ? `<div class="status bad">⚠ backup file paused</div>` : ""}`;
}

function needsBackupNudge() {
  const m = S.state.meta, st = S.state.status;
  if (ui.nudgeClosed || m.vault || st.file === "connected" || !Object.keys(B()).length) return false;
  return !m.lastExport || Date.now() - new Date(m.lastExport) > 7 * 864e5;
}

function render(keepScroll = false) {
  const y = window.scrollY;
  $("#side").innerHTML = sidebar();
  $("#title").textContent = PAGES.find(([k]) => k === page())[1];
  const nudge = needsBackupNudge() && page() !== "book"
    ? `<div class="banner row between"><span>Your book is safe on this device. For extra peace of mind, add a backup copy (takes 1 minute).</span><span>${btn("Set it up", "nav", { p: "book" })} ${btn("Later", "closeNudge", {}, "ghost")}</span></div>` : "";
  $("#main").innerHTML = nudge + RENDER[page()]();
  document.querySelectorAll("img[data-src]").forEach(async (img) => { img.src = await S.imageURL(img.dataset.src); });
  if (keepScroll) window.scrollTo(0, y);
}
const rerender = () => render(true);

function toast(msg) {
  const t = document.createElement("div"); t.className = "toast"; t.textContent = msg; document.body.appendChild(t);
  setTimeout(() => t.remove(), 2600);
}

// --- typing in any field saves it --------------------------------------------
function onField(e) {
  const t = e.target;
  if (!t.dataset || t.dataset.k === undefined || t.closest("form")) return;
  const v = t.type === "checkbox" ? t.checked : t.dataset.num !== undefined ? Number(t.value) : t.value;
  set(t.dataset.k, v);
  const show = document.querySelector(`[data-show="${CSS.escape(t.dataset.k)}"]`);
  if (show) show.textContent = v;
}
document.addEventListener("input", onField);
document.addEventListener("change", (e) => {
  onField(e);
  const act = e.target.dataset?.actChange;
  if (act && CHANGE[act]) CHANGE[act](e.target);
});

const CHANGE = {
  pickdate: (el) => { if (el.value) { ui.jdate = el.value > TODAY() ? TODAY() : el.value; rerender(); } },
  beliefPick: (el) => { ui.belief = el.value; const f = el.form.elements.old; f.value = el.value; },
  dareMax: (el) => { ui.dareMax = Number(el.value); rerender(); },
  viz: (el) => { ui.viz = Number(el.value); rerender(); },
  from: (el) => { ui.from = el.value; rerender(); },
  to: (el) => { ui.to = el.value; rerender(); },
  age: (el) => { const n = parseInt(el.value, 10); if (n > 0 && n < 120) { set("age", n); render(true); } },
  birthday: (el) => { set("birthday", el.value); render(true); },
  restore: async (el) => {
    const f = el.files[0]; if (!f) return;
    try {
      const data = JSON.parse(await f.text());
      if (typeof data !== "object" || Array.isArray(data)) throw new Error();
      const n = Object.keys(data).length;
      if (!confirm(`Restore this backup (${n} entries)? It replaces the book on this device.`)) return;
      await S.replaceBook(data); toast("Restored ✦"); render();
    } catch (e) { alert("That file doesn't look like a Vision Book backup."); }
  },
};

const ACT = {
  nav: (el) => { location.hash = el.dataset.p; },
  tab: (el) => { ui.tabs[el.dataset.g] = el.dataset.v; rerender(); },
  rerender: () => rerender(),
  chapter: (el) => { ui.chapter = Number(el.dataset.i); rerender(); },
  horizon: (el) => { ui.horizon = Number(el.dataset.i); rerender(); },
  day: (el) => { ui.jdate = el.dataset.d; rerender(); },
  shiftWeek: (el) => { const d = addDays(parse(ui.jdate || TODAY()), Number(el.dataset.n)); ui.jdate = iso(d) > TODAY() ? TODAY() : iso(d); rerender(); },
  ladderWeek: (el) => { const L = items("ladders")[el.dataset.i], wk = weekKey(today()); L.weeks = el.checked ? [...new Set([...(L.weeks || []), wk])] : (L.weeks || []).filter((w) => w !== wk); S.save(); rerender(); },
  beliefProven: (el) => { items("beliefs")[el.dataset.i].proven = el.checked; S.save(); },
  removeItem: (el) => { if (!confirm("Remove this?")) return; items(el.dataset.list).splice(Number(el.dataset.i), 1); S.save(); rerender(); },
  dareCat: (el) => { const all = C.CATEGORIES.map((c) => c.key); let s = ui.dareCats || all; s = s.includes(el.dataset.k) ? s.filter((x) => x !== el.dataset.k) : [...s, el.dataset.k]; ui.dareCats = s; rerender(); },
  drawDare: () => { const pool = darePool(); if (!pool.length) return toast("No dares match — widen the filter."); set(`dare::${TODAY()}`, pool[Math.floor(Math.random() * pool.length)][2]); rerender(); },
  vizMode: (el) => { ui.vizFull = el.dataset.full === "1"; rerender(); },
  vizStep: (el) => { const V = C.VISUALIZATIONS[ui.viz]; ui.vizStep[V.key] = Math.max(0, Math.min(V.steps.length - 1, (ui.vizStep[V.key] || 0) + Number(el.dataset.d))); rerender(); },
  boardFilter: (el) => { ui.boardFilter = el.dataset.c; rerender(); },
  period: (el) => { ui.period = el.dataset.p; rerender(); },
  exportBook: () => download(`vision-book-${TODAY()}.md`, toMD(bookNodes())),
  exportJournal: () => { const [f, t, sel] = periodDates(); download(`journal-${f}-${t}.md`, toMD(journalNodes(sel))); },
  exportJSON: async () => { download(`vision-book-backup-${TODAY()}.json`, JSON.stringify(B(), null, 1), "application/json"); await S.markExported(); rerender(); },
  print: () => window.print(),
  fileConnect: async () => { try { await S.connectFile(); toast("Backup file connected ✦"); } catch (e) {} rerender(); },
  fileReconnect: async () => { await S.reconnectFile(); rerender(); },
  fileOff: async () => { await S.disconnectFile(); rerender(); },
  syncNow: async () => { await S.sync(); rerender(); },
  vaultOff: async () => { if (confirm("Disconnect the vault on this device? Your book stays on this device and in the vault.")) { await S.disconnectVault(); rerender(); } },
  closeNudge: () => { ui.nudgeClosed = true; rerender(); },
};

document.addEventListener("click", (e) => {
  const m = e.target.closest("[data-multi]");
  if (m) {
    const k = m.dataset.multi, o = m.dataset.opt, max = Number(m.dataset.max);
    let sel = get(k, []).slice();
    if (sel.includes(o)) sel = sel.filter((x) => x !== o);
    else if (sel.length < max) sel.push(o);
    else return toast(`Choose up to ${max} — deselect one first.`);
    set(k, sel);
    if (m.dataset.rerender !== undefined) rerender(); else m.classList.toggle("on");
    return;
  }
  const a = e.target.closest("[data-act]");
  if (a && ACT[a.dataset.act]) {
    if (a.tagName === "A") e.preventDefault();
    if (a.type !== "checkbox") e.preventDefault();
    ACT[a.dataset.act](a);
    return;
  }
  if (e.target.closest(".nav a")) closeMenu();
});

const FORMS = {
  ladder: (f) => items("ladders").push({ ...f, created: TODAY(), weeks: [] }),
  belief: (f) => items("beliefs").push({ old: f.old, new: f.new, before: +f.before, after: +f.after, origin: f.origin, cost: f.cost,
    katie: [f.k0, f.k1, f.k2, f.k3], evidence: f.evidence, turn: f.turn, proof: f.proof, date: TODAY(), proven: false }),
  dareLog: (f) => { items("dares").push({ dare: get(`dare::${TODAY()}`), date: TODAY(), pred: +f.pred, real: +f.real, learned: f.learned, done: true }); toast("Brava! ✦ One more vote for her."); },
  ownDare: (f) => items("own_dares").push({ cat: f.cat, level: +f.level, dare: f.dare }),
  muse: (f) => items("own_muses").push({ name: f.name, role: f.role, embodies: f.embodies.split(",").map((s) => s.trim()).filter(Boolean), lesson: f.lesson }),
  quote: (f) => items("quotes").push({ text: f.text, by: f.by || "—" }),
};
document.addEventListener("submit", async (e) => {
  const form = e.target, kind = form.dataset.form;
  if (!kind) return;
  e.preventDefault();
  const fd = new FormData(form), f = {};
  for (const [k, v] of fd.entries()) if (typeof v === "string") f[k] = v.trim();
  if (kind === "board") {
    const file = form.elements.file.files[0];
    const src = file ? await S.addImage(file) : f.url;
    if (!src) return toast("Add a link or choose a photo.");
    items("board").push({ src, caption: f.caption, cat: f.cat });
  } else if (kind === "vault") {
    toast("Connecting…");
    const problem = await S.connectVault(f.token, f.repo);
    if (problem) { alert(problem); return rerender(); }
    toast("Vault connected ✦"); return render(true);
  } else if (kind === "ladder" && !f.dream) return toast("Write the dream first.");
  else FORMS[kind](f);
  S.save(); ui.belief = ""; rerender();
});

// --- mobile menu -------------------------------------------------------------
function closeMenu() { $("#side").classList.remove("open"); $("#scrim")?.remove(); }
$("#menu").addEventListener("click", () => {
  $("#side").classList.add("open");
  const s = document.createElement("div"); s.id = "scrim"; s.className = "scrim"; s.onclick = closeMenu; document.body.appendChild(s);
});

window.addEventListener("hashchange", () => { closeMenu(); render(); window.scrollTo(0, 0); });

// --- start -----------------------------------------------------------------
S.state.onStatus = () => { const side = $("#side"); if (side && !side.classList.contains("open")) side.innerHTML = sidebar(); };
S.state.onRemoteChange = () => {
  const a = document.activeElement;
  if (a && (a.tagName === "TEXTAREA" || a.tagName === "INPUT")) return; // don't disturb typing
  rerender();
};
await S.init();
render();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
