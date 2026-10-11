"""Visual components for the app.

Everything that is not a Streamlit control is built here as plain HTML so it
can be checked in a real browser. No external libraries; works offline (the
typeface falls back to the system sans-serif without internet). Animations
respect prefers-reduced-motion.

Two rules used throughout:
- numbers are formatted the Vietnamese way (5.110; 22,8%), see causach.vn
- exponents are real <sup> elements, not Unicode superscripts, because the
  typeface only has ² and ³ and the others came out in a different font
"""
from __future__ import annotations

import html
import json
import re

import numpy as np

from .data import Problem
from .model import Plan
from .vn import fmt_dec, fmt_int, fmt_pct

INK, INK_DEEP, RED, GRID, WASH, MUTED = "#1F4E99", "#14213D", "#B83227", "#D9DEF0", "#F1F4FA", "#5A6482"
FONT = "'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');"

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿᵐ"
_SUP_BACK = str.maketrans(_SUP, "0123456789+−()nm")


def rich(text: str) -> str:
    """Escape for HTML and turn Unicode superscript runs into <sup> elements."""
    escaped = html.escape(str(text))
    return re.sub(f"[{_SUP}]+", lambda m: f"<sup>{m.group(0).translate(_SUP_BACK)}</sup>", escaped)


def one_block(markup: str) -> str:
    """st.markdown treats blank lines and 4-space indents as Markdown; keep raw HTML as one block."""
    return re.sub(r"\n\s*", " ", markup).strip()


# ---------------------------------------------------------------------------
# Global styles and header
# ---------------------------------------------------------------------------
APP_CSS = f"""<style>
{FONT_IMPORT}
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp input, .stApp textarea, .stApp button {{ font-family: {FONT}; }}
.stApp {{ color: {INK_DEEP}; }}
.block-container {{ padding-top: 2.2rem; max-width: 1280px; }}
.stApp h3 {{ font-size: 1.3rem; font-weight: 600; letter-spacing: -0.01em; color: {INK_DEEP}; margin-bottom: .1rem; }}
.stTabs [data-baseweb="tab"] p {{ font-size: .98rem; font-weight: 500; }}
.cs-header {{ margin: 0 0 4px; }}
.cs-header .cs-name {{ display: block; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; color: {INK_DEEP}; line-height: 1.2; }}
.cs-header .cs-line {{ display: block; font-size: 1rem; color: {MUTED}; max-width: 80ch; margin-top: 4px; }}
.cs-intro {{ font-size: .98rem; line-height: 1.55; color: {MUTED}; max-width: 72ch; margin: 0 0 14px; }}
.cs-label {{ font-size: .95rem; font-weight: 600; color: {INK_DEEP}; margin: 18px 0 8px; }}
.cs-label span {{ font-weight: 400; color: {MUTED}; }}
.cs-status {{ font-size: .95rem; line-height: 1.5; margin: 2px 0 10px; color: {INK_DEEP}; }}
.cs-status b {{ color: {INK}; }}
.cs-status.bad, .cs-status.bad b {{ color: {RED}; }}
.cs-status.quiet {{ color: {MUTED}; }}
.cs-table-wrap {{ max-height: 380px; overflow: auto; border-top: 1px solid {GRID}; border-bottom: 1px solid {GRID}; }}
.stApp table.cs-table {{ width: 100%; border-collapse: collapse; font-size: .9rem; margin: 0; border: none; }}
.stApp table.cs-table th {{ background: #fff; text-align: right; font-weight: 600;
  font-size: .8rem; color: {MUTED}; padding: 8px 10px; border: none; border-bottom: 1px solid {GRID}; white-space: nowrap; }}
.stApp table.cs-table td {{ text-align: right; padding: 7px 10px; border: none; border-bottom: 1px solid #EEF1F7;
  font-variant-numeric: tabular-nums; white-space: nowrap; }}
.stApp table.cs-table th:first-child, .stApp table.cs-table td:first-child {{ text-align: left; }}
.cs-table-wrap table.cs-table th {{ position: sticky; top: 0; z-index: 1; }}
.stApp table.cs-table tr.pick td {{ font-weight: 600; color: {INK}; background: {WASH}; }}
.stApp table.cs-table tr:last-child td {{ border-bottom: none; }}
.cs-bar {{ display: inline-flex; align-items: center; gap: 8px; justify-content: flex-end; }}
.cs-bar i {{ display: inline-block; width: 90px; height: 6px; border-radius: 3px; background: #E4E8F2; position: relative; overflow: hidden; }}
.cs-bar i b {{ position: absolute; inset: 0 auto 0 0; background: {INK}; border-radius: 3px; }}
.cs-bar i b.low {{ background: {RED}; }}
.cs-bar em {{ font-style: normal; min-width: 4.4em; text-align: right; }}
.cs-paper {{ border: 1px solid {GRID}; border-radius: 4px; padding: 30px 38px 26px; max-width: 760px; background: #fff;
  line-height: 1.6; font-size: .98rem; color: {INK_DEEP}; }}
.cs-paper .k {{ font-size: .85rem; color: {MUTED}; }}
.cs-paper .t {{ font-size: 1.45rem; font-weight: 700; letter-spacing: -0.01em; margin: 2px 0 2px; line-height: 1.3; }}
.cs-paper .ref {{ font-size: .85rem; color: {MUTED}; font-style: italic; margin-bottom: 14px; }}
.cs-paper .h {{ font-size: 1.02rem; font-weight: 700; margin: 18px 0 6px; padding-top: 10px; border-top: 1px solid #EEF1F7; }}
.cs-paper ul, .cs-paper ol {{ margin: 0 0 4px; padding-left: 1.3em; }}
.cs-paper li {{ margin: 3px 0; }}
.cs-paper p {{ margin: 4px 0; }}
.cs-paper .sol {{ color: {MUTED}; }}
.cs-paper .ans {{ font-size: .9rem; color: {MUTED}; margin: 2px 0 8px; }}
.cs-paper .ans b {{ color: {INK_DEEP}; }}
.cs-paper .ok {{ color: {INK}; font-weight: 600; }}
.cs-paper .bad {{ color: {RED}; font-weight: 600; }}
.cs-paper .foot {{ font-size: .8rem; color: {MUTED}; margin-top: 18px; padding-top: 10px; border-top: 1px solid #EEF1F7; }}
.cs-paper sup, .cs-report sup, table.cs-table sup {{ font-size: .7em; line-height: 0; }}
.cs-report {{ max-width: 820px; line-height: 1.6; font-size: .97rem; color: {INK_DEEP}; }}
.cs-report .h2 {{ font-size: 1.15rem; font-weight: 700; margin: 26px 0 8px; }}
.cs-report .h3 {{ font-size: 1rem; font-weight: 700; margin: 18px 0 6px; }}
.cs-report p {{ margin: 6px 0; }}
.cs-report ul {{ margin: 4px 0 8px; padding-left: 1.3em; }}
.cs-report table.cs-table td {{ white-space: normal; }}
.cs-report table.cs-table {{ margin: 10px 0 16px; }}
</style>"""

HEADER = one_block("""
<div class="cs-header">
  <span class="cs-name">Cầu Sách</span>
  <span class="cs-line">Chuyển sách thừa tới đúng em cần, và soạn phiếu học tạm có máy kiểm tra đáp án, giáo viên duyệt trước khi in.</span>
</div>""")


def intro(text: str) -> str:
    return f'<p class="cs-intro">{html.escape(text)}</p>'


def label(text: str, note: str = "") -> str:
    tail = f" <span>{html.escape(note)}</span>" if note else ""
    return f'<div class="cs-label">{html.escape(text)}{tail}</div>'


def status(markup: str, kind: str = "") -> str:
    return f'<p class="cs-status {kind}">{markup}</p>'


# ---------------------------------------------------------------------------
# Allocation: map with a built-in plan switcher
# ---------------------------------------------------------------------------
PLAN_LABELS = {
    "Không điều phối": "Không điều phối",
    "Tham lam (trường tự lo trước)": "Trường tự lo trước",
    "Tham lam (ưu tiên Luồng C)": "Ưu tiên Luồng C",
    "Tối ưu (MILP)": "Tối ưu",
}


def plan_sentence(stats: dict) -> str:
    share = fmt_pct(stats["coverage_c"])
    left = fmt_int(stats["luong_c_left"])
    if stats["trips"] == 0:
        return f"<b>{share}</b> học sinh Luồng C có sách in, còn <b>{left}</b> em thiếu. Không có chuyến chở sách nào."
    return (f"<b>{share}</b> học sinh Luồng C có sách in, còn <b>{left}</b> em thiếu. "
            f"<b>{fmt_int(stats['trips'])}</b> chuyến chở <b>{fmt_int(stats['books_moved'])}</b> cuốn, "
            f"tổng <b>{fmt_int(stats['km'])} km</b>.")


def flow_map_data(problem: Problem, plans: dict[str, Plan], stats: dict[str, dict], coords: np.ndarray,
                  baseline: str = "Không điều phối", initial: str = "Tối ưu (MILP)") -> dict:
    names = list(plans)
    out_plans = []
    for name in names:
        plan = plans[name]
        per_edge: dict[tuple[int, int], int] = {}
        for (s, d, _), copies in plan.flows.items():
            if s != d:
                per_edge[(s, d)] = per_edge.get((s, d), 0) + copies
        out_plans.append({
            "label": PLAN_LABELS.get(name, name),
            "edges": [{"s": s, "d": d, "copies": c} for (s, d), c in sorted(per_edge.items(), key=lambda kv: -kv[1])],
            "covered": [int(v) for v in plan.covered_c.sum(axis=1)],
            "sentence": plan_sentence(stats[name]),
        })
    need = problem.need_c.sum(axis=1)
    return {
        "schools": [{"name": n.replace("THCS ", ""), "x": float(coords[i, 0]), "y": float(coords[i, 1]),
                     "need": int(need[i])} for i, n in enumerate(problem.schools)],
        "plans": out_plans, "baseline": names.index(baseline), "initial": names.index(initial),
    }


def flow_map_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONT_IMPORT}
html, body {{ margin: 0; background: #fff; font-family: {FONT}; color: {INK_DEEP}; }}
.top {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }}
.seg {{ display: inline-flex; border: 1px solid {GRID}; border-radius: 8px; padding: 3px; background: {WASH}; }}
.seg button {{ font: inherit; font-size: 13.5px; border: 0; background: transparent; color: {MUTED};
  padding: 6px 12px; border-radius: 6px; cursor: pointer; white-space: nowrap; }}
.seg button[aria-selected="true"] {{ background: #fff; color: {INK_DEEP}; font-weight: 600;
  box-shadow: 0 1px 2px rgba(20,33,61,.12); }}
.actions {{ display: inline-flex; gap: 14px; }}
.seg button:focus-visible, .link:focus-visible {{ outline: 2px solid {INK}; outline-offset: 2px; }}
.link {{ font: inherit; font-size: 13px; color: {INK}; background: none; border: 0; cursor: pointer; padding: 6px 2px; }}
.link:hover {{ text-decoration: underline; }}
.sentence {{ font-size: 15px; line-height: 1.5; margin: 12px 0 6px; min-height: 22px; }}
.sentence b {{ color: {INK}; font-weight: 700; }}
svg {{ display: block; width: 100%; height: 440px; user-select: none; -webkit-user-select: none; }}
circle.school {{ cursor: grab; touch-action: none; }}
circle.school.dragging {{ cursor: grabbing; }}
.letter {{ font-size: 12px; font-weight: 700; fill: #fff; pointer-events: none; }}
.letter.out {{ fill: {INK_DEEP}; }}
.copies {{ font-size: 11.5px; font-weight: 600; fill: {INK}; paint-order: stroke; stroke: #fff; stroke-width: 3.5px; pointer-events: none; }}
.key {{ display: flex; align-items: center; gap: 26px; font-size: 12.5px; color: {MUTED}; margin-top: 6px; white-space: nowrap; }}
.ramp {{ display: inline-flex; align-items: center; gap: 6px; }}
.ramp i {{ width: 110px; height: 8px; border-radius: 4px; display: inline-block;
  background: linear-gradient(90deg, {RED}, #E2B3AC, {INK}); }}
</style></head><body>
<div class="top"><div class="seg" role="tablist" id="seg"></div>
<span class="actions"><button class="link" id="tidy" type="button">Xếp lại</button><button class="link" id="again" type="button">Phát lại</button></span></div>
<p class="sentence" id="sentence"></p>
<svg id="map" viewBox="0 0 900 440" role="img" aria-label="Bản đồ chuyển sách giữa các trường"></svg>
<div class="key"><span class="ramp">Luồng C có sách in: 0% <i></i> 100%</span>
<span>Chấm to: nhiều em cần sách</span><span>Kéo chấm để dời; vị trí chỉ gần đúng</span></div>
<script>
const D = {payload};
const W = 900, H = 440, NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("map");
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const stops = [[184,50,39],[226,179,172],[31,78,153]];
const color = t => {{ t = Math.max(0, Math.min(1, t));
  const [a, b, u] = t < .5 ? [stops[0], stops[1], t / .5] : [stops[1], stops[2], (t - .5) / .5];
  return `rgb(${{a.map((v, i) => Math.round(v + (b[i] - v) * u)).join(",")}})`; }};
function el(tag, attrs, parent) {{ const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]); (parent || svg).appendChild(n); return n; }}
const fmt = n => Math.round(n).toLocaleString("vi-VN");
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

// ---- layout: geographic positions, then spread so no two dots overlap ----
const xs = D.schools.map(s => s.x), ys = D.schools.map(s => s.y), pad = 40;
const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
const k = Math.min((W - 2 * pad) / Math.max(x1 - x0, 1e-6), (H - 2 * pad) / Math.max(y1 - y0, 1e-6));
const ox = (W - k * (x1 - x0)) / 2, oy = (H - k * (y1 - y0)) / 2;
const GEO = D.schools.map(s => [ox + k * (s.x - x0), H - (oy + k * (s.y - y0))]);
const maxNeed = Math.max(1, ...D.schools.map(s => s.need));
const R = D.schools.map(s => 7 + 19 * Math.sqrt(s.need / maxNeed));
const keepIn = (q, i) => {{ q[0] = clamp(q[0], R[i] + 2, W - R[i] - 2); q[1] = clamp(q[1], R[i] + 2, H - R[i] - 2); }};
function spread(points) {{
  const Q = points.map(p => p.slice());
  for (let it = 0; it < 400; it++) {{
    let moved = false;
    for (let i = 0; i < Q.length; i++) for (let j = i + 1; j < Q.length; j++) {{
      let dx = Q[j][0] - Q[i][0], dy = Q[j][1] - Q[i][1], d = Math.hypot(dx, dy);
      const need = R[i] + R[j] + 6;
      if (d >= need) continue;
      if (d < 1e-6) {{ dx = Math.cos(j * 2.4); dy = Math.sin(j * 2.4); d = 1; }}
      const push = (need - d) / 2 + .01, ux = dx / d, uy = dy / d;
      Q[i][0] -= ux * push; Q[i][1] -= uy * push; Q[j][0] += ux * push; Q[j][1] += uy * push; moved = true;
    }}
    Q.forEach(keepIn);
    if (!moved) break;
  }}
  return Q;
}}
const AUTO = spread(GEO);
let P = AUTO.map(p => p.slice());

// ---- static layers ----
const defs = el("defs", {{}});
const g1 = el("pattern", {{id: "g1", width: 12, height: 12, patternUnits: "userSpaceOnUse"}}, defs);
el("path", {{d: "M12 0H0V12", fill: "none", stroke: "#E4E8F3", "stroke-width": .6}}, g1);
const g4 = el("pattern", {{id: "g4", width: 48, height: 48, patternUnits: "userSpaceOnUse"}}, defs);
el("rect", {{width: 48, height: 48, fill: "url(#g1)"}}, g4);
el("path", {{d: "M48 0H0V48", fill: "none", stroke: "#D3DAEC", "stroke-width": .9}}, g4);
el("rect", {{width: W, height: H, fill: "url(#g4)"}});
const routeLayer = el("g", {{}}), flightLayer = el("g", {{}}), dotLayer = el("g", {{}}), textLayer = el("g", {{}});

const dots = D.schools.map((s, i) => {{
  const c = el("circle", {{r: R[i], stroke: "#fff", "stroke-width": 1.8, class: "school"}}, dotLayer);
  const tip = el("title", {{}}, c);
  const inside = R[i] >= 13;
  const letter = el("text", {{"text-anchor": "middle", class: inside ? "letter" : "letter out"}}, textLayer);
  letter.textContent = s.name;
  return {{c, tip, inside, letter, box: null}};
}});

// ---- geometry: everything that depends on positions ----
function curve(a, b) {{ const [mx, my] = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], [dx, dy] = [b[0] - a[0], b[1] - a[1]];
  return `M${{a[0]}},${{a[1]}} Q${{mx - dy * .16}},${{my + dx * .16}} ${{b[0]}},${{b[1]}}`; }}
const hitsDot = b => P.some((p, j) => {{ const cx = clamp(p[0], b.x, b.x + b.w), cy = clamp(p[1], b.y, b.y + b.h);
  return (cx - p[0]) ** 2 + (cy - p[1]) ** 2 < (R[j] + 1.5) ** 2; }});
const overlaps = (b, list) => list.some(o => b.x < o.x + o.w && o.x < b.x + b.w && b.y < o.y + o.h && o.y < b.y + b.h);

function placeLetters() {{
  const boxes = [];
  dots.forEach((d, i) => {{
    const [x, y] = P[i];
    if (d.inside) {{ d.letter.setAttribute("x", x); d.letter.setAttribute("y", y + 4);
      d.box = {{x: x - R[i], y: y - R[i], w: 2 * R[i], h: 2 * R[i]}}; boxes.push(d.box); return; }}
    const w = 8 * D.schools[i].name.length + 4, h = 14;
    const spots = [[x + R[i] + 3, y - h / 2], [x - R[i] - 3 - w, y - h / 2], [x - w / 2, y + R[i] + 2], [x - w / 2, y - R[i] - 2 - h]];
    const [bx, by] = spots.find(([bx, by]) => !hitsDot({{x: bx, y: by, w, h}}) && !overlaps({{x: bx, y: by, w, h}}, boxes)) || spots[0];
    d.box = {{x: bx, y: by, w, h}}; d.offset = [bx + w / 2 - x, by + 11 - y]; boxes.push(d.box);
    d.letter.setAttribute("x", bx + w / 2); d.letter.setAttribute("y", by + 11);
  }});
  return boxes;
}}
function moveDots() {{
  dots.forEach((d, i) => {{
    d.c.setAttribute("cx", P[i][0]); d.c.setAttribute("cy", P[i][1]);
    const [ddx, ddy] = d.inside ? [0, 4] : (d.offset || [R[i] + 8, 4]);
    d.letter.setAttribute("x", P[i][0] + ddx); d.letter.setAttribute("y", P[i][1] + ddy);
  }});
  routes.forEach(r => {{ r.path.setAttribute("d", curve(P[r.e.s], P[r.e.d])); r.len = r.path.getTotalLength(); }});
}}
function placeNumbers() {{
  const taken = dots.map(d => d.box);
  routes.forEach((r, i) => {{
    r.shown = false;
    if (!r.label || i >= 10) return;
    const mid = r.path.getPointAtLength(r.len / 2), w = 7.2 * String(r.e.copies).length + 6, h = 14;
    const b = {{x: mid.x - w / 2, y: mid.y - h / 2, w, h}};
    if (overlaps(b, taken) || hitsDot(b)) return;
    r.label.setAttribute("x", mid.x); r.label.setAttribute("y", mid.y + 4); taken.push(b); r.shown = true;
  }});
}}
function layout() {{ moveDots(); placeLetters(); placeNumbers(); showNumbers(); }}

// ---- plan, animation ----
const TRAVEL = 1400, GAP = 110, STAGGER = 200;
let current = D.initial, raf = 0, flights = [], routes = [], incoming = [], total = 0, started = 0, dragging = null;

function build(p) {{
  routeLayer.replaceChildren(); flightLayer.replaceChildren(); textLayer.querySelectorAll(".copies").forEach(n => n.remove());
  const plan = D.plans[p], maxCopies = Math.max(1, ...plan.edges.map(e => e.copies));
  routes = plan.edges.map(e => {{
    const path = el("path", {{fill: "none", stroke: "{INK}", "stroke-opacity": .2,
      "stroke-width": 1 + 4 * e.copies / maxCopies, "stroke-linecap": "round"}}, routeLayer);
    el("title", {{}}, path).textContent = `${{D.schools[e.d].name}} nhận ${{fmt(e.copies)}} cuốn từ ${{D.schools[e.s].name}}`;
    const label = el("text", {{"text-anchor": "middle", class: "copies", opacity: 0}}, textLayer);
    label.textContent = fmt(e.copies);
    return {{e, path, len: 0, label, shown: false, n: Math.max(1, Math.min(12, Math.round(e.copies / 25)))}};
  }});
  incoming = D.schools.map(() => 0);
  flights = [];
  routes.forEach((r, i) => {{ incoming[r.e.d] += r.n;
    for (let j = 0; j < r.n; j++) flights.push({{r, t0: 300 + i * STAGGER + j * GAP,
      dot: el("circle", {{r: 3, fill: "{INK}", opacity: 0}}, flightLayer)}}); }});
  total = flights.reduce((m, f) => Math.max(m, f.t0 + TRAVEL), 0) + 400;
  routes.forEach(r => r.last = Math.max(...flights.filter(f => f.r === r).map(f => f.t0)) + TRAVEL);
  document.getElementById("sentence").innerHTML = plan.sentence;
  layout();
}}
function elapsed() {{ return reduce || !flights.length ? 1e9 : performance.now() - started; }}
function showNumbers() {{
  const t = elapsed();
  routes.forEach(r => r.label.setAttribute("opacity", r.shown && !dragging && t >= r.last ? 1 : 0));
}}
function paint(t) {{
  const plan = D.plans[current], base = D.plans[D.baseline], arrived = D.schools.map(() => 0);
  for (const f of flights) {{ const u = (t - f.t0) / TRAVEL;
    if (u <= 0 || u >= 1) {{ f.dot.setAttribute("opacity", 0); if (u >= 1) arrived[f.r.e.d]++; continue; }}
    const e = u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, q = f.r.path.getPointAtLength(e * f.r.len);
    f.dot.setAttribute("cx", q.x); f.dot.setAttribute("cy", q.y); f.dot.setAttribute("opacity", .9); }}
  showNumbers();
  const timeShare = flights.length ? Math.min(1, t / Math.max(total - 400, 1)) : 1;
  D.schools.forEach((s, i) => {{
    const progress = incoming[i] ? arrived[i] / incoming[i] : timeShare;
    const covered = base.covered[i] + (plan.covered[i] - base.covered[i]) * progress;
    dots[i].c.setAttribute("fill", color(s.need ? covered / s.need : 1));
    dots[i].tip.textContent = s.need
      ? `THCS ${{s.name}}: ${{fmt(s.need)}} em Luồng C cần sách, ${{fmt(plan.covered[i])}} em có sách in (${{Math.round(100 * plan.covered[i] / s.need)}}%). Kéo để dời.`
      : `THCS ${{s.name}}: không có em Luồng C thiếu sách. Kéo để dời.`;
  }});
}}
function play(p) {{
  current = p; cancelAnimationFrame(raf); build(p);
  document.querySelectorAll(".seg button").forEach((b, i) => b.setAttribute("aria-selected", i === p));
  started = performance.now();
  if (reduce || !flights.length) {{ paint(1e9); return; }}
  const tick = now => {{ const t = now - started; paint(t); if (t < total) raf = requestAnimationFrame(tick); }};
  paint(0); raf = requestAnimationFrame(tick);
}}

// ---- dragging ----
function toSvg(evt) {{ const pt = svg.createSVGPoint(); pt.x = evt.clientX; pt.y = evt.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse()); }}
let frame = 0;
dots.forEach((d, i) => {{
  d.c.addEventListener("pointerdown", evt => {{
    evt.preventDefault(); const p = toSvg(evt);
    dragging = {{i, dx: P[i][0] - p.x, dy: P[i][1] - p.y}};
    d.c.setPointerCapture(evt.pointerId); d.c.classList.add("dragging"); showNumbers();
  }});
  d.c.addEventListener("pointermove", evt => {{
    if (!dragging || dragging.i !== i) return;
    const p = toSvg(evt); P[i] = [p.x + dragging.dx, p.y + dragging.dy]; keepIn(P[i], i);
    if (!frame) frame = requestAnimationFrame(() => {{ frame = 0; moveDots(); if (elapsed() >= total) paint(1e9); }});
  }});
  const drop = evt => {{
    if (!dragging || dragging.i !== i) return;
    dragging = null; d.c.classList.remove("dragging");
    // slide the dropped dot just far enough off any dot it landed on; the others stay put
    for (let it = 0; it < 60; it++) {{
      let moved = false;
      P.forEach((q, j) => {{ if (j === i) return;
        let dx = P[i][0] - q[0], dy = P[i][1] - q[1], dist = Math.hypot(dx, dy); const need = R[i] + R[j] + 6;
        if (dist >= need) return;
        if (dist < 1e-6) {{ dx = 1; dy = 0; dist = 1; }}
        P[i] = [q[0] + dx / dist * need, q[1] + dy / dist * need]; keepIn(P[i], i); moved = true; }});
      if (!moved) break;
    }}
    if (d.c.hasPointerCapture(evt.pointerId)) d.c.releasePointerCapture(evt.pointerId);
    layout();
  }};
  d.c.addEventListener("pointerup", drop); d.c.addEventListener("pointercancel", drop);
}});

const seg = document.getElementById("seg");
D.plans.forEach((plan, i) => {{ const b = document.createElement("button"); b.type = "button"; b.role = "tab";
  b.textContent = plan.label; b.addEventListener("click", () => play(i)); seg.appendChild(b); }});
document.getElementById("again").addEventListener("click", () => play(current));
document.getElementById("tidy").addEventListener("click", () => {{ P = AUTO.map(p => p.slice()); layout(); if (elapsed() >= total) paint(1e9); }});
play(D.initial);
</script></body></html>"""


FLOW_MAP_HEIGHT = 580


# ---------------------------------------------------------------------------
# Allocation tables
# ---------------------------------------------------------------------------
def _bar(share: float) -> str:
    width = max(0.0, min(1.0, share)) * 100
    low = " low" if share < 0.5 else ""
    return f'<span class="cs-bar"><i><b class="{low.strip()}" style="width:{width:.1f}%"></b></i><em>{fmt_pct(share, 1)}</em></span>'


def comparison_table_html(stats: dict[str, dict], highlight: str) -> str:
    rows = []
    for name, s in stats.items():
        pick = ' class="pick"' if name == highlight else ""
        rows.append(f"<tr{pick}><td>{html.escape(PLAN_LABELS.get(name, name))}</td><td>{_bar(s['coverage_c'])}</td>"
                    f"<td>{fmt_int(s['luong_c_left'])}</td><td>{fmt_int(s['books_moved'])}</td>"
                    f"<td>{fmt_int(s['trips'])}</td><td>{fmt_int(s['km'])} km</td></tr>")
    head = ("<tr><th>Cách làm</th><th>Luồng C có sách in</th><th>Còn thiếu</th>"
            "<th>Sách chuyển</th><th>Chuyến</th><th>Quãng đường</th></tr>")
    return one_block(f'<table class="cs-table">{head}{"".join(rows)}</table>')


def school_table_html(problem: Problem, plan: Plan) -> str:
    need = problem.need_c.sum(axis=1)
    got = plan.covered_c.sum(axis=1)
    sent = np.zeros(len(problem.schools), dtype=int)
    received = np.zeros(len(problem.schools), dtype=int)
    for (s, d, _), copies in plan.flows.items():
        if s != d:
            sent[s] += copies
            received[d] += copies
    order = sorted(range(len(problem.schools)), key=lambda i: -(need[i] - got[i]))
    rows = []
    for i in order:
        share = got[i] / need[i] if need[i] else 1.0
        rows.append(f"<tr><td>{html.escape(problem.schools[i])}</td><td>{fmt_int(need[i])}</td><td>{_bar(share)}</td>"
                    f"<td>{fmt_int(need[i] - got[i])}</td><td>{fmt_int(sent[i]) if sent[i] else '–'}</td>"
                    f"<td>{fmt_int(received[i]) if received[i] else '–'}</td></tr>")
    head = ("<tr><th>Trường</th><th>Em Luồng C cần sách</th><th>Có sách in</th><th>Còn thiếu</th>"
            "<th>Gửi đi</th><th>Nhận về</th></tr>")
    return one_block(f'<div class="cs-table-wrap"><table class="cs-table">{head}{"".join(rows)}</table></div>')


# ---------------------------------------------------------------------------
# Worksheet check board
# ---------------------------------------------------------------------------
LAYERS = ["Cú pháp", "Dạng đáp án", "Giá trị", "Đọc lại đề"]
FAILED_AT = {"loi_bieu_thuc": 0, "sai_dang": 1, "sai_dap_an": 2, "lam_tron_vo_nghia": 2,
             "khong_khop_de": 3, "nhieu_y": 3, "chua_doi_chieu": 3, "loi_doc_lai": 3, "chua_doc_lai": 3}
SHORT = {"loi_bieu_thuc": "lỗi cú pháp", "sai_dang": "sai dạng", "sai_dap_an": "sai đáp án",
         "lam_tron_vo_nghia": "làm tròn thừa", "khong_khop_de": "lệch đề", "nhieu_y": "hỏi nhiều ý",
         "chua_doi_chieu": "không đọc được", "loi_doc_lai": "lỗi hệ thống", "chua_doc_lai": "chưa đọc lại"}


def check_board_data(rounds: list[dict], labels: dict[str, str], cross_check: bool) -> dict:
    """rounds: [{"title", "items": [{"id", "status", "message"}]}]; labels: id -> problem text."""
    return {"rounds": rounds, "labels": {k: rich(v) for k, v in labels.items()}, "cross": cross_check,
            "layers": LAYERS, "failedAt": FAILED_AT, "short": SHORT}


def check_board_height(data: dict) -> int:
    # measured in Chromium: 70px per round (title, header row, note) + 37px per exercise row
    return 16 + sum(84 + 37 * len(r["items"]) for r in data["rounds"])


def check_board_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONT_IMPORT}
html, body {{ margin: 0; background: #fff; font-family: {FONT}; color: {INK_DEEP}; }}
.round {{ margin: 0 0 18px; }}
.head {{ display: flex; justify-content: space-between; align-items: baseline; margin: 6px 0 4px; }}
.head span {{ font-size: 14px; font-weight: 600; }}
.again {{ font: inherit; font-size: 13px; color: {INK}; background: none; border: 0; cursor: pointer; padding: 2px; }}
.again:hover {{ text-decoration: underline; }} .again:focus-visible {{ outline: 2px solid {INK}; outline-offset: 2px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; table-layout: fixed; }}
col.cell {{ width: 104px; }} col.res {{ width: 112px; }}
th {{ font-size: 12px; font-weight: 600; color: {MUTED}; padding: 6px 8px; text-align: center; white-space: nowrap;
  border-bottom: 1px solid {GRID}; }}
th:first-child {{ text-align: left; }}
td {{ padding: 0 8px; height: 36px; border-bottom: 1px solid #EEF1F7; text-align: center; }}
td.ex {{ text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
td.ex b {{ color: {INK}; margin-right: 8px; font-weight: 700; }}
sup {{ font-size: .7em; line-height: 0; }}
.tag {{ font-size: 11px; color: {INK}; background: {WASH}; border-radius: 3px; padding: 1px 6px; margin-right: 8px; }}
.m {{ display: inline-block; opacity: 0; transform: translateY(3px); transition: opacity .25s, transform .25s; }}
.m.on {{ opacity: 1; transform: none; }}
.ok {{ color: {INK}; font-size: 15px; }}
.bad {{ color: {RED}; font-weight: 600; font-size: 12.5px; }}
.skip {{ color: #B4BCD2; }}
.wait {{ color: {INK}; font-size: 12.5px; border-bottom: 1.5px dashed {INK}; }}
.res .ok {{ font-size: 13px; font-weight: 600; }}
.note {{ font-size: 12.5px; color: {MUTED}; margin: 7px 0 10px; opacity: 0; transition: opacity .4s; }}
@media (prefers-reduced-motion: reduce) {{ .m, .note {{ transition: none; }} }}
</style></head><body><div id="board"></div>
<script>
const D = {payload};
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const board = document.getElementById("board");
const STEP = 120, ROW = 80, PAUSE = 600;
let timers = [];
const at = (ms, fn) => reduce ? fn() : timers.push(setTimeout(fn, ms));
function mark(cls, text, title) {{ const s = document.createElement("span"); s.className = "m " + cls;
  s.textContent = text; if (title) s.title = title; return s; }}
function render() {{
  timers.forEach(clearTimeout); timers = []; board.replaceChildren();
  let clock = 150;
  D.rounds.forEach((round, ri) => {{
    const box = document.createElement("div"); box.className = "round";
    const head = document.createElement("div"); head.className = "head";
    const title = document.createElement("span"); title.textContent = round.title; head.appendChild(title);
    if (ri === 0) {{ const b = document.createElement("button"); b.className = "again"; b.type = "button";
      b.textContent = "Phát lại"; b.addEventListener("click", render); head.appendChild(b); }}
    box.appendChild(head);
    const table = document.createElement("table");
    table.innerHTML = '<colgroup><col><col class="cell"><col class="cell"><col class="cell"><col class="cell"><col class="res"></colgroup>';
    const hr = table.insertRow();
    ["Bài tập", ...D.layers, "Kết quả"].forEach(t => {{ const th = document.createElement("th"); th.textContent = t; hr.appendChild(th); }});
    let failures = 0, pending = 0;
    round.items.forEach((item, idx) => {{
      const row = table.insertRow();
      const prev = ri > 0 ? D.rounds[ri - 1].items.find(p => p.id === item.id) : null;
      const repaired = prev && prev.status !== "dat", added = ri > 0 && !prev;
      const ex = row.insertCell(); ex.className = "ex";
      const label = D.labels[item.id] || "";
      ex.innerHTML = `<b>${{item.id}}</b>` + (repaired ? '<span class="tag">đã sửa</span>' : added ? '<span class="tag">mới thêm</span>' : "") + label;
      ex.title = ex.textContent;
      const waiting = item.status === "chua_doc_lai";
      const fail = item.status in D.failedAt ? D.failedAt[item.status] : -1;
      if (waiting) pending++; else if (fail >= 0) failures++;
      const t0 = clock + idx * ROW;
      D.layers.forEach((_, li) => {{
        const td = row.insertCell(); let m;
        if (li === 3 && !D.cross) m = mark("skip", "không chạy");
        else if (fail >= 0 && li === fail) m = mark(waiting ? "wait" : "bad", D.short[item.status] || "lỗi", item.message);
        else if (fail >= 0 && li > fail) m = mark("skip", "–");
        else m = mark("ok", "✓");
        td.appendChild(m); at(t0 + li * STEP, () => m.classList.add("on"));
      }});
      const res = row.insertCell(); res.className = "res";
      const r = waiting ? mark("wait", "Chờ đọc lại", item.message) : fail >= 0 ? mark("bad", "Chưa đạt", item.message) : mark("ok", "Đạt");
      res.appendChild(r); at(t0 + 4 * STEP, () => r.classList.add("on"));
    }});
    box.appendChild(table);
    const note = document.createElement("p"); note.className = "note";
    const parts = [];
    if (failures) parts.push(D.rounds[ri + 1] ? `${{failures}} bài chưa đạt được gửi lại cho mô hình sửa.` : `${{failures}} bài còn chưa đạt.`);
    if (pending) parts.push(`${{pending}} bài vừa sửa đang chờ máy đọc lại đề mới.`);
    note.textContent = parts.length ? parts.join(" ") : "Mọi bài tập qua đủ bốn lớp kiểm tra.";
    box.appendChild(note); board.appendChild(box);
    clock += round.items.length * ROW + 4 * STEP;
    at(clock, () => note.style.opacity = 1);
    clock += PAUSE;
  }});
}}
render();
</script></body></html>"""


# ---------------------------------------------------------------------------
# Worksheet as a printed page
# ---------------------------------------------------------------------------
STATUS_TEXT = {
    "dat": "Đạt", "loi_bieu_thuc": "Lỗi biểu thức", "sai_dang": "Sai dạng đáp án", "sai_dap_an": "Sai đáp án",
    "khong_khop_de": "Biểu thức không khớp đề", "nhieu_y": "Đề hỏi nhiều ý", "lam_tron_vo_nghia": "Làm tròn không thay đổi số",
    "chua_doi_chieu": "Chưa đối chiếu được với đề", "loi_doc_lai": "Bước đọc lại không trả kết quả",
}


def worksheet_html(worksheet: dict, lesson, *, teacher: bool = False, report=None, unread=frozenset(),
                   clean=lambda s: s, pretty=lambda s: s) -> str:
    c = lambda s: rich(clean(s))
    parts = ['<div class="cs-paper">', f'<div class="k">Phiếu Cầu, Toán 6{", bản giáo viên" if teacher else ""}</div>',
             f'<div class="t">{html.escape(lesson.title)}</div>', '<div class="ref">Đối chiếu SGK: trang ……</div>']
    parts += ['<div class="h">Mục tiêu</div><ul>'] + [f"<li>{c(m)}</li>" for m in worksheet["muc_tieu"]] + ["</ul>"]
    parts += ['<div class="h">Kiến thức cốt lõi</div><ul>'] + [f"<li>{c(k)}</li>" for k in worksheet["kien_thuc_cot_loi"]] + ["</ul>"]
    parts.append('<div class="h">Ví dụ</div>')
    for n, ex in enumerate(worksheet["vi_du"], 1):
        parts.append(f"<p><b>Ví dụ {n}.</b> {c(ex['de_bai'])}</p><p class=\"sol\"><i>Lời giải.</i> {c(ex['loi_giai'])}</p>")
    parts.append('<div class="h">Bài tập</div><ol>')
    checks = report.by_id() if report is not None else {}
    for ex in worksheet["bai_tap"]:
        parts.append(f"<li>{c(ex['de_bai'])}")
        if teacher:
            check = checks.get(ex["id"])
            if ex["id"] in unread:
                verdict = '<span class="bad">Đề đã sửa, chưa đọc lại</span>'
            elif check is None:
                verdict = "chưa kiểm tra"
            elif check.passed:
                verdict = '<span class="ok">Đạt</span>'
            else:
                verdict = f'<span class="bad">{html.escape(STATUS_TEXT.get(check.status, check.status))}</span>'
            parts.append(f'<p class="sol"><i>Lời giải.</i> {c(ex["loi_giai"])}</p>'
                         f'<p class="ans">Đáp án <b>{rich(pretty(ex["dap_an"]))}</b>. '
                         f'{html.escape(", ".join(ex.get("yccd", [])))}. Máy kiểm tra: {verdict}</p>')
        parts.append("</li>")
    parts.append("</ol>")
    parts.append('<div class="foot">Phiếu Cầu, soạn theo yêu cầu cần đạt của Chương trình giáo dục phổ thông môn Toán 2018; '
                 'không chép từ sách giáo khoa. Giấy phép CC BY 4.0. Người biên soạn và duyệt: ____________</div></div>')
    return one_block("".join(parts))


# ---------------------------------------------------------------------------
# Evaluation report (the small Markdown subset bao_cao.md uses)
# ---------------------------------------------------------------------------
def _inline(text: str) -> str:
    text = rich(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r"\1", text)


def report_html(markdown: str) -> str:
    out, table, items, para = [], [], [], []

    def flush():
        nonlocal table, items, para
        if table:
            rows = [r for r in table if not re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", r)]
            cells = [[x.strip() for x in r.strip().strip("|").split("|")] for r in rows]
            head = "".join(f"<th>{_inline(x)}</th>" for x in cells[0])
            body = "".join("<tr>" + "".join(f"<td>{_inline(x)}</td>" for x in r) + "</tr>" for r in cells[1:])
            out.append(f'<table class="cs-table"><tr>{head}</tr>{body}</table>')
        if items:
            out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
        if para:
            out.append(f"<p>{_inline(' '.join(para))}</p>")
        table, items, para = [], [], []

    for line in markdown.splitlines():
        s = line.strip()
        if s.startswith("# "):
            flush()                                    # the tab already has its own title
        elif s.startswith("## "):
            flush(); out.append(f'<div class="h2">{_inline(s[3:])}</div>')
        elif s.startswith("### "):
            flush(); out.append(f'<div class="h3">{_inline(s[4:])}</div>')
        elif s.startswith("|"):
            if items or para:
                flush()
            table.append(s)
        elif s.startswith("- "):
            if table or para:
                flush()
            items.append(s[2:])
        elif not s:
            flush()
        else:
            if table or items:
                flush()
            para.append(s)
    flush()
    return one_block('<div class="cs-report">' + "".join(out) + "</div>")
