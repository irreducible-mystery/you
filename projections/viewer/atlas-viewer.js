"use strict";
/**
 * Derived atlas viewer (TypeScript projection, pi_ts).
 * A GENERATED PROJECTION, never primary reality (LIM-0001).
 * Force-directed graph over field/derived/atlas.json with the five filters
 * from FIELD.md / doc Q7 §15: scale, time, primitive framework,
 * contribution class, status — plus observer-class colouring that never
 * collapses the human / ai-system / document-surrogate distinction.
 */
const OBSERVER_COLORS = {
    "human": "#e8b04b",
    "ai-system": "#5aa9e6",
    "document-surrogate": "#9b8ec4",
    "hybrid": "#6ec69b",
};
// Lineage is not collapsed either: observers of a different builder lineage
// get a distinct hue within their class (OBS-0009..0011 — organization-level
// difference attested; weights-level undecidable, which the shared class
// membership continues to represent).
const OBSERVER_LINEAGE_HUES = {
    "OBS-AI-0003": "#d98a5f",
};
const KIND_SHAPES = {
    tension: "◆", claim: "●", assumption: "○", definition: "■",
    perspective: "▲", limit: "▣", observation: "●", bridge: "⬡",
    test: "✚", "dimension-proposal": "✦", synthesis: "⬢",
};
let atlas;
let nodes = [];
let edges = [];
let selected = null;
const filters = {
    scale: "", time: "", framework: "", contribution: "", status: "", observerClass: "",
};
function visible(n) {
    if (filters.scale && n.scale !== filters.scale)
        return false;
    if (filters.time && n.temporal_scope !== filters.time)
        return false;
    if (filters.framework && !n.primitive_framework.includes(filters.framework))
        return false;
    if (filters.contribution && n.origin_class !== filters.contribution)
        return false;
    if (filters.status && n.status !== filters.status)
        return false;
    if (filters.observerClass && n.observer_class !== filters.observerClass)
        return false;
    return true;
}
function initSim() {
    const W = 1200, H = 800;
    nodes = atlas.nodes.map((n, i) => ({
        ...n,
        x: W / 2 + 300 * Math.cos((2 * Math.PI * i) / atlas.nodes.length) + (n.id === "TEN-0001" ? -300 * Math.cos((2 * Math.PI * i) / atlas.nodes.length) : 0),
        y: H / 2 + 300 * Math.sin((2 * Math.PI * i) / atlas.nodes.length) + (n.id === "TEN-0001" ? -300 * Math.sin((2 * Math.PI * i) / atlas.nodes.length) : 0),
        vx: 0, vy: 0,
    }));
    edges = atlas.edges;
}
function step() {
    const W = 1200, H = 800;
    const byId = new Map(nodes.map(n => [n.id, n]));
    // repulsion
    for (const a of nodes) {
        for (const b of nodes) {
            if (a === b)
                continue;
            const dx = a.x - b.x, dy = a.y - b.y;
            const d2 = Math.max(dx * dx + dy * dy, 100);
            const f = 2200 / d2;
            const d = Math.sqrt(d2);
            a.vx += (dx / d) * f;
            a.vy += (dy / d) * f;
        }
    }
    // springs
    for (const e of edges) {
        const s = byId.get(e.source), t = byId.get(e.target);
        if (!s || !t)
            continue;
        const dx = t.x - s.x, dy = t.y - s.y;
        const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const f = (d - 130) * 0.012;
        s.vx += (dx / d) * f;
        s.vy += (dy / d) * f;
        t.vx -= (dx / d) * f;
        t.vy -= (dy / d) * f;
    }
    // centering + integrate
    for (const n of nodes) {
        n.vx += (W / 2 - n.x) * 0.0015;
        n.vy += (H / 2 - n.y) * 0.0015;
        n.vx *= 0.85;
        n.vy *= 0.85;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(30, Math.min(W - 30, n.x));
        n.y = Math.max(30, Math.min(H - 30, n.y));
    }
}
function draw(ctx) {
    ctx.clearRect(0, 0, 1200, 800);
    const byId = new Map(nodes.map(n => [n.id, n]));
    // edges
    for (const e of edges) {
        const s = byId.get(e.source), t = byId.get(e.target);
        if (!s || !t || !visible(s) || !visible(t))
            continue;
        const conflict = e.type.startsWith("contradicts") || e.type === "challenges" ||
            e.type === "counterexample-to" || e.type === "remains-unresolved-with";
        ctx.strokeStyle = conflict ? "rgba(224,108,117,0.55)" : "rgba(140,150,170,0.35)";
        ctx.lineWidth = conflict ? 1.6 : 1;
        ctx.setLineDash(e.type.includes("translat") ? [4, 3] : []);
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.stroke();
        ctx.setLineDash([]);
    }
    // nodes
    for (const n of nodes) {
        if (!visible(n))
            continue;
        const color = OBSERVER_LINEAGE_HUES[n.observer] ?? OBSERVER_COLORS[n.observer_class ?? ""] ?? "#888";
        const r = n.id === "TEN-0001" ? 13 : n.kind === "tension" ? 10 : 7;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, 2 * Math.PI);
        ctx.fillStyle = n.status === "preserved-unresolved" ? "rgba(0,0,0,0)" : color;
        if (n.status === "preserved-unresolved") {
            ctx.strokeStyle = color;
            ctx.lineWidth = 2.5;
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(n.x, n.y, r - 4, 0, 2 * Math.PI);
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
        else {
            ctx.fill();
            if (n.origin_confirmation === "unconfirmed") {
                ctx.strokeStyle = "#e06c75";
                ctx.lineWidth = 1.5;
                ctx.setLineDash([2, 2]);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }
        if (n === selected) {
            ctx.beginPath();
            ctx.arc(n.x, n.y, r + 5, 0, 2 * Math.PI);
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
        ctx.fillStyle = "#c9d1e0";
        ctx.font = "10px monospace";
        ctx.fillText(n.id, n.x + r + 3, n.y + 3);
    }
}
function showDetail(n) {
    const el = document.getElementById("detail");
    if (!n) {
        el.innerHTML = "<em>Select a node. The atlas is a generated projection, not primary reality.</em>";
        return;
    }
    const shape = KIND_SHAPES[n.kind] ?? "●";
    el.innerHTML = `
    <h3>${shape} ${n.id} <span class="kind">${n.kind}</span></h3>
    <p class="expr">"${n.expression.original}"</p>
    ${n.expression.elaboration ? `<p class="elab">${n.expression.elaboration}</p>` : ""}
    <table>
      <tr><td>status</td><td class="${n.status}">${n.status}</td></tr>
      <tr><td>observer</td><td>${n.observer} <span class="oc oc-${n.observer_class}">${n.observer_class}</span></td></tr>
      <tr><td>origin class</td><td>${n.origin_class}</td></tr>
      <tr><td>confirmation</td><td>${n.origin_confirmation}</td></tr>
      <tr><td>scale / time</td><td>${n.scale} / ${n.temporal_scope}</td></tr>
      <tr><td>frameworks</td><td>${n.primitive_framework.join(", ")}</td></tr>
      ${n.tension_class ? `<tr><td>tension class</td><td>${n.tension_class}</td></tr>` : ""}
    </table>
    <h4>relations</h4>
    <ul>${edges.filter(e => e.source === n.id || e.target === n.id)
        .map(e => `<li><code>${e.id}</code> ${e.source === n.id ? "→" : "←"} <b>${e.type}</b> ${e.source === n.id ? e.target : e.source}</li>`)
        .join("") || "<li>none</li>"}</ul>`;
}
async function main() {
    const res = await fetch("atlas.json");
    atlas = await res.json();
    initSim();
    const counts = document.getElementById("counts");
    counts.textContent = `${atlas.counts.elements} elements · ${atlas.counts.relations} relations · ` +
        `${atlas.counts.observers} observers · ${atlas.counts.unresolved_tensions} unresolved`;
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    canvas.addEventListener("click", ev => {
        const rect = canvas.getBoundingClientRect();
        const x = (ev.clientX - rect.left) * (canvas.width / rect.width);
        const y = (ev.clientY - rect.top) * (canvas.height / rect.height);
        selected = nodes.filter(visible).find(n => (n.x - x) ** 2 + (n.y - y) ** 2 < 200) ?? null;
        showDetail(selected);
    });
    for (const [key, elId] of Object.entries({
        scale: "f-scale", time: "f-time", framework: "f-framework",
        contribution: "f-contribution", status: "f-status", observerClass: "f-observer",
    })) {
        const sel = document.getElementById(elId);
        sel.addEventListener("change", () => { filters[key] = sel.value; });
    }
    showDetail(null);
    (function loop() { step(); draw(ctx); requestAnimationFrame(loop); })();
}
main();
