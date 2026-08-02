/**
 * Chronicle viewer (TypeScript projection, pi_ts) — the atlas learns time.
 * Renders the accepted-state sequence F_0 -> F_1 -> ... with a scrubber,
 * animating each transition: appearing elements bloom in, status changes
 * pulse, confirmations turn their dashed borders solid.
 *
 * A GENERATED PROJECTION of history, never primary reality (LIM-0001).
 * Reading the field's history is itself participation (CLM-0020).
 */

interface ChronNode {
  id: string; kind: string; status: string; observer: string | null;
  origin_confirmation: string | null; label: string;
}
interface ChronEdge { id: string; type: string; source: string; target: string; status: string | null; }
interface ChronState {
  index: number; label: string; commit: string; time: string; subject: string;
  counts: Record<string, number>;
  nodes: ChronNode[]; edges: ChronEdge[];
}
interface Transition {
  from: string; to: string; commit: string; subject: string; time: string;
  added: { elements: ChronNode[]; relations: ChronEdge[]; observers: { id: string }[] };
  status_changes: { id: string; from: string; to: string }[];
  confirmation_changes: { id: string; from: string; to: string }[];
  removed: { kind: string; id: string }[];
}
interface Chronicle { note: string; states: ChronState[]; transitions: Transition[]; }

interface SimN { id: string; x: number; y: number; vx: number; vy: number; birth: number; }

const OBS_COLOR: Record<string, string> = {
  "OBS-HUM": "#e8b04b", "OBS-AI": "#5aa9e6", "OBS-HYB": "#6ec69b", "OBS-DOC": "#9b8ec4",
};
function colorOf(observer: string | null): string {
  if (!observer) return "#888";
  for (const k of Object.keys(OBS_COLOR)) if (observer.startsWith(k)) return OBS_COLOR[k];
  return "#888";
}

let chron: Chronicle;
let cur = 0;                       // current state index
let sim = new Map<string, SimN>(); // persistent positions across states
let flash = new Map<string, number>(); // id -> frames remaining of highlight
const W = 1200, H = 720;

function ensureNodes(state: ChronState): void {
  const ids = new Set(state.nodes.map(n => n.id));
  let i = 0;
  for (const n of state.nodes) {
    if (!sim.has(n.id)) {
      const a = (2 * Math.PI * i) / state.nodes.length;
      sim.set(n.id, { id: n.id, x: W / 2 + 280 * Math.cos(a), y: H / 2 + 280 * Math.sin(a), vx: 0, vy: 0, birth: 24 });
    }
    i++;
  }
  for (const id of Array.from(sim.keys())) if (!ids.has(id)) sim.delete(id);
}

function step(state: ChronState): void {
  const nodes = state.nodes.map(n => sim.get(n.id)!).filter(Boolean);
  for (const a of nodes) for (const b of nodes) {
    if (a === b) continue;
    const dx = a.x - b.x, dy = a.y - b.y;
    const d2 = Math.max(dx * dx + dy * dy, 100), d = Math.sqrt(d2);
    const f = 2000 / d2;
    a.vx += (dx / d) * f; a.vy += (dy / d) * f;
  }
  for (const e of state.edges) {
    const s = sim.get(e.source), t = sim.get(e.target);
    if (!s || !t) continue;
    const dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
    const f = (d - 125) * 0.012;
    s.vx += (dx / d) * f; s.vy += (dy / d) * f;
    t.vx -= (dx / d) * f; t.vy -= (dy / d) * f;
  }
  for (const n of nodes) {
    n.vx += (W / 2 - n.x) * 0.0015; n.vy += (H / 2 - n.y) * 0.0015;
    n.vx *= 0.85; n.vy *= 0.85;
    n.x = Math.max(28, Math.min(W - 28, n.x + n.vx));
    n.y = Math.max(28, Math.min(H - 28, n.y + n.vy));
    if (n.birth > 0) n.birth--;
  }
}

function draw(ctx: CanvasRenderingContext2D, state: ChronState): void {
  ctx.clearRect(0, 0, W, H);
  const byId = new Map(state.nodes.map(n => [n.id, n]));
  for (const e of state.edges) {
    const s = sim.get(e.source), t = sim.get(e.target);
    if (!s || !t) continue;
    const conflict = e.type.startsWith("contradicts") || e.type === "challenges" ||
      e.type === "counterexample-to" || e.type === "remains-unresolved-with";
    ctx.strokeStyle = conflict ? "rgba(224,108,117,0.55)" : "rgba(140,150,170,0.32)";
    ctx.lineWidth = conflict ? 1.6 : 1;
    ctx.setLineDash(e.type.includes("translat") ? [4, 3] : []);
    ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(t.x, t.y); ctx.stroke();
    ctx.setLineDash([]);
  }
  for (const n of state.nodes) {
    const p = sim.get(n.id); if (!p) continue;
    const color = colorOf(n.observer);
    const base = n.id === "TEN-0001" ? 13 : n.kind === "tension" ? 10 : 7;
    const r = base + (p.birth > 0 ? p.birth * 0.6 : 0);
    const fl = flash.get(n.id) ?? 0;
    if (fl > 0) {
      ctx.beginPath(); ctx.arc(p.x, p.y, r + 8 + 3 * Math.sin(fl * 0.5), 0, 2 * Math.PI);
      ctx.strokeStyle = `rgba(229,192,123,${Math.min(fl / 30, 0.9)})`;
      ctx.lineWidth = 2; ctx.stroke();
      flash.set(n.id, fl - 1);
    }
    ctx.globalAlpha = p.birth > 0 ? 1 - p.birth / 30 : 1;
    ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 2 * Math.PI);
    if (n.status === "preserved-unresolved") {
      ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
      ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(r - 4, 2), 0, 2 * Math.PI);
      ctx.lineWidth = 1; ctx.stroke();
    } else {
      ctx.fillStyle = color; ctx.fill();
      if (n.origin_confirmation === "unconfirmed") {
        ctx.strokeStyle = "#e06c75"; ctx.lineWidth = 1.5;
        ctx.setLineDash([2, 2]); ctx.stroke(); ctx.setLineDash([]);
      }
    }
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#c9d1e0"; ctx.font = "10px monospace";
    ctx.fillText(n.id, p.x + r + 3, p.y + 3);
  }
}

function setState(i: number): void {
  const prev = cur;
  cur = Math.max(0, Math.min(chron.states.length - 1, i));
  const state = chron.states[cur];
  ensureNodes(state);
  // flash what changed arriving at this state (forward direction)
  if (cur === prev + 1) {
    const t = chron.transitions[cur - 1];
    for (const n of t.added.elements) { const s = sim.get(n.id); if (s) s.birth = 24; }
    for (const c of t.status_changes) flash.set(c.id, 60);
    for (const c of t.confirmation_changes) flash.set(c.id, 60);
  }
  (document.getElementById("scrub") as HTMLInputElement).value = String(cur);
  renderPanel();
}

function renderPanel(): void {
  const s = chron.states[cur];
  const head = document.getElementById("state-head")!;
  head.innerHTML = `<b>${s.label}</b> · <code>${s.commit.slice(0, 8)}</code> · ${new Date(s.time).toLocaleString()}<br>
    <span class="subj">${s.subject}</span><br>
    ${s.counts.elements} elements · ${s.counts.relations} relations · ${s.counts.observers} observers ·
    <span class="unres">${s.counts.unresolved} preserved-unresolved</span> ·
    <span class="unconf">${s.counts.unconfirmed} unconfirmed</span>`;

  const tr = document.getElementById("transition")!;
  if (cur === 0) {
    tr.innerHTML = `<h4>Genesis</h4><p>The field was born by self-ingesting the source document's claims.
      First element: <b>TEN-0001</b>, preserved-unresolved, per seed instruction of OBS-HUM-0001.</p>`;
    return;
  }
  const t = chron.transitions[cur - 1];
  const li = (arr: string[]) => arr.length ? `<ul>${arr.map(x => `<li>${x}</li>`).join("")}</ul>` : "<p class='none'>none</p>";
  tr.innerHTML = `<h4>Transition ${t.from} → ${t.to}</h4>
    <p class="subj">${t.subject}</p>
    <h5>appeared</h5>${li([
      ...t.added.elements.map(e => `<code>${e.id}</code> <span class="k">${e.kind}</span> — ${e.label}`),
      ...t.added.relations.map(r => `<code>${r.id}</code> ${r.source} <b>${r.type}</b> ${r.target}`),
      ...t.added.observers.map(o => `<code>${o.id}</code> observer registered`)])}
    <h5>status changes</h5>${li(t.status_changes.map(c => `<code>${c.id}</code> ${c.from} → <b>${c.to}</b>`))}
    <h5>origin confirmations</h5>${li(t.confirmation_changes.map(c => `<code>${c.id}</code> ${c.from} → <b>${c.to}</b>`))}
    ${t.removed.length ? `<h5 class="warn">removals (append-preservation violated?)</h5>${li(t.removed.map(r => `${r.kind}/${r.id}`))}` : ""}`;
}

async function main(): Promise<void> {
  const res = await fetch("chronicle.json");
  chron = await res.json() as Chronicle;

  const scrub = document.getElementById("scrub") as HTMLInputElement;
  scrub.max = String(chron.states.length - 1);
  scrub.addEventListener("input", () => setState(Number(scrub.value)));
  document.getElementById("prev")!.addEventListener("click", () => setState(cur - 1));
  document.getElementById("next")!.addEventListener("click", () => setState(cur + 1));

  let playing = false;
  const playBtn = document.getElementById("play")!;
  playBtn.addEventListener("click", () => {
    playing = !playing;
    playBtn.textContent = playing ? "⏸ pause" : "▶ play";
    if (playing) {
      const tick = () => {
        if (!playing) return;
        if (cur < chron.states.length - 1) { setState(cur + 1); setTimeout(tick, 2600); }
        else { playing = false; playBtn.textContent = "▶ play"; }
      };
      if (cur >= chron.states.length - 1) setState(0);
      setTimeout(tick, 1200);
    }
  });

  const canvas = document.getElementById("canvas") as HTMLCanvasElement;
  const ctx = canvas.getContext("2d")!;
  setState(0);
  (function loop() { const s = chron.states[cur]; step(s); draw(ctx, s); requestAnimationFrame(loop); })();
}

main();
