// Shared across all pages. State lives in localStorage so an acknowledged alert stays acknowledged.
const KEY = "tele_icu_state";
const blank = { acked: [], fa: [], sim: [], hosp: "all" };
const get_state = () => ({ ...blank, ...JSON.parse(localStorage.getItem(KEY) || "{}") });
const set_state = (s) => localStorage.setItem(KEY, JSON.stringify(s));
const reset_demo = () => { localStorage.removeItem(KEY); location.reload(); };

// Patients can be promoted by the simulate button, so always read them through here.
function all_patients() {
  const s = get_state();
  return DEMO.patients.map((p) => {
    let q = { ...p, acked: p.acked || s.acked.includes(p.id) };
    if (s.sim.includes(p.id)) q = { ...q, band: "red", risk: 88, trig: ["SpO₂ 84 ↓"], alertMin: 0, isNew: true };
    return q;
  });
}
const patients = () => { const s = get_state(); return all_patients().filter((p) => s.hosp === "all" || p.hosp === s.hosp); };
const by_id = (id) => all_patients().find((p) => p.id === id);
// Red list order: highest risk first, tie goes to whoever has waited longer.
const rank = (a, b) => b.risk - a.risk || b.alertMin - a.alertMin;
const fmt_wait = (m) => String(Math.floor(m)).padStart(2, "0") + ":" + String(Math.round((m % 1) * 60) || 0).padStart(2, "0");

function spark(vals, n = 24) {
  const v = vals.slice(-n), lo = Math.min(...v), hi = Math.max(...v), w = 96, h = 26;
  const pts = v.map((x, i) => `${(i / (v.length - 1)) * w},${h - 2 - ((x - lo) / (hi - lo || 1)) * (h - 4)}`).join(" ");
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" fill="none" stroke-width="1.6" aria-hidden="true"><polyline points="${pts}"/></svg>`;
}

function top_bar(active) {
  const s = get_state(), all = patients();
  const red = all.filter((p) => p.band === "red").length, amb = all.filter((p) => p.band === "amber").length;
  const hid = DEMO.hospitals.map((h) => `<option value="${h.id}" ${s.hosp === h.id ? "selected" : ""}>${h.id} · ${h.name}, ${h.city}</option>`).join("");
  const link = (f, t) => `<a href="${f}" class="${active === f ? "on" : ""}">${t}</a>`;
  document.getElementById("top").innerHTML = `
    <span class="logo">Tele-ICU</span>
    <nav class="nav">${link("matrix.html", "Matrix")}${link("triage.html", "Triage queue")}${link("settings.html", "Alert settings")}</nav>
    <select id="hosp" aria-label="Hospital filter"><option value="all">All hospitals (4)</option>${hid}</select>
    <span class="sp"></span>
    <span class="pill red num">⚠ Critical ${red}</span><span class="pill amb num">↘ Watch ${amb}</span>
    <a class="pill mut num" href="settings.html" title="Open the filtered-alarm log">Filtered out: ${DEMO.suppressedBase + s.fa.length} (last hour)</a>
    <span class="clock num" id="clock"></span><span class="clock">Dr. Meera Iyer</span>`;
  document.getElementById("hosp").onchange = (e) => { s.hosp = e.target.value; set_state(s); location.reload(); };
  const tick = () => (document.getElementById("clock").textContent = new Date().toLocaleTimeString("en-GB"));
  tick(); setInterval(tick, 1000);
}

// Two-tone alert: low-high for critical. Browsers need a click first, which the simulate button gives us.
function play_tone(freqs = [520, 740], vol = 0.08) {
  try {
    const a = new (window.AudioContext || window.webkitAudioContext)();
    freqs.forEach((f, i) => {
      const o = a.createOscillator(), g = a.createGain();
      o.frequency.value = f; g.gain.value = vol; o.connect(g); g.connect(a.destination);
      o.start(a.currentTime + i * 0.22); o.stop(a.currentTime + i * 0.22 + 0.18);
    });
  } catch (e) { /* no audio, fine */ }
}

// Shared modal for Mark false alarm / Escalate / Call bedside. Every path ends in a clear result.
function open_action(kind, p, after) {
  const ov = Object.assign(document.createElement("div"), { className: "ov" }); document.body.append(ov);
  const close = () => { ov.remove(); after && after(); };
  const box = (t, b, f) => { ov.innerHTML = `<div class="modal" role="dialog" aria-label="${t}"><div class="mh"><b>${t}</b><button class="btn ghost" id="x" aria-label="Close">✕</button></div><div class="mb">${b}</div><div class="mf">${f}</div></div>`; ov.querySelector("#x").onclick = close; };
  const q = (s) => ov.querySelector(s), hm = () => new Date().toLocaleTimeString("en-GB").slice(0, 5);
  const ok = (m) => { box("Done", `<div class="okb"><div class="tick">✓</div><b>${m}</b><small class="num">Logged at ${hm()}</small></div>`, `<button class="btn pri" id="c">Close</button>`); q("#c").onclick = close; };
  const busy = (m, f) => { box(m, `<div class="okb"><div class="spin"></div><b>${m}…</b></div>`, `<button class="btn" id="c">${f}</button>`); q("#c").onclick = close; };
  if (kind === "fa") {
    box("Mark false alarm", `<label>Reason<select id="r"><option>Sensor off or loose</option><option>Patient movement</option><option>Lead disconnected</option><option>Other</option></select></label><label class="ck"><input type="checkbox" checked> Mute similar alerts for 30 minutes</label>`, `<button class="btn" id="c">Cancel</button><button class="btn pri" id="y">Confirm</button>`);
    q("#c").onclick = close;
    q("#y").onclick = () => { const s = get_state(); s.fa.push({ id: p.id, reason: q("#r").value, t: hm() }); set_state(s); ok("False alarm logged"); };
  } else if (kind === "esc") {
    const form = () => { box("Escalate", `<label>Send to<select id="t"><option>Bedside doctor</option><option>On-site intensivist</option></select></label><label>Reason<textarea id="n" rows="3">${p.id}: ${p.trig.join(", ") || "needs review"}. Risk ${p.risk}%.</textarea></label>`, `<button class="btn" id="c">Cancel</button><button class="btn pri" id="y">Send</button>`); q("#c").onclick = close;
      q("#y").onclick = () => { const t = q("#t").value; busy("Sending to " + t, "Cancel");
        setTimeout(() => { if (t.startsWith("On-site") && !window.__tried) { window.__tried = 1;
          box("Couldn't reach them", `<div class="okb"><div class="tick bad">!</div><b>The intensivist didn't pick up.</b><small>Try again, or send it to the bedside doctor instead.</small></div>`, `<button class="btn" id="c">Cancel</button><button class="btn pri" id="y">Try again</button>`);
          q("#c").onclick = close; q("#y").onclick = form; } else ok("Escalated to " + t); }, 1200); }; };
    form();
  } else { busy(`Calling ${p.nurse} (ext ${p.ext})`, "End call"); }
}

// Slow-drift check over the last 24h: compares now with the best value in that window.
const WORSE = { spo2: ["max", 3], map: ["max", 10], hr: ["min", 15], rr: ["min", 4] };
function drift(p, v) {
  const w = p.series[v].slice(-25), [kind, thr] = WORSE[v], ext = kind === "max" ? Math.max(...w) : Math.min(...w);
  if (Math.abs(p.cur[v] - ext) < thr) return null;
  const near = w.map((x, i) => (Math.abs(x - ext) < thr / 3 ? i : -1)).filter((i) => i >= 0).pop(); // last point still close to the old level
  return { from: Math.round(ext), hrs: Math.max(1, 24 - near) };
}
