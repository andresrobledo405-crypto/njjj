"use strict";
/* ---------- utilidades ---------- */
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ic = (n, c = "sm") => `<svg class="ic ${c}" aria-hidden="true"><use href="#i-${n}"/></svg>`;
const fold = s => (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
const ST = { scheduled: "Agendada", arrived: "En espera", done: "Realizada", cancelled: "Cancelada", no_show: "No asistió" };
const PST = { active: "En curso", completed: "Completado", cancelled: "Cancelado" };
const clp = n => new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(n);
const localDay = (d = new Date()) => new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
const parseDay = s => new Date(s + "T12:00:00");
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const longDate = d => cap(new Intl.DateTimeFormat("es-CL", { weekday: "long", day: "numeric", month: "long" }).format(d));
const dm = d => d.slice(8, 10) + "/" + d.slice(5, 7);
const nul = v => (v && String(v).trim()) || null;
const initials = n => n.split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join("").toUpperCase();
const hue = n => [...n].reduce((a, c) => a + c.charCodeAt(0), 0) % 5;
const avatar = (n, big = "") => `<span class="avatar a${hue(n)} ${big}" aria-hidden="true">${esc(initials(n))}</span>`;
const age = b => { if (!b) return ""; const d = new Date(b), t = new Date(); let a = t.getFullYear() - d.getFullYear(); if (t < new Date(t.getFullYear(), d.getMonth(), d.getDate())) a--; return a >= 0 && a < 130 ? a + " años" : ""; };

async function api(u, o) {
  const r = await fetch(u, o);
  if (r.status === 401 && !u.includes("/auth/login")) { showLogin(); throw new Error("Sesión expirada"); }
  if (!r.ok) { let d = "Error"; try { d = (await r.json()).detail } catch { } throw new Error(typeof d === "string" ? d : "Datos inválidos"); }
  return r.status === 204 ? null : r.json();
}
const send = (m, u, b) => api(u, { method: m, headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) });
const post = (u, b) => send("POST", u, b);
let msgTimer;
function say(t) {
  const m = $("msg"); m.setAttribute("role", /inv[aá]lid|error|no existe|ya |omitid|expir|requerid|activo|pertenece/i.test(t) ? "alert" : "status");
  m.textContent = t; m.classList.add("on"); clearTimeout(msgTimer); msgTimer = setTimeout(() => m.classList.remove("on"), 3800);
}
const fail = x => say(x.message);

let pats = [], pros = [], plansAll = [], me = null, cat = "", lastFocus = null;
const patient = id => pats.find(p => p.id === +id);
const opts = (l, f) => l.map(x => `<option value="${x.id}">${esc(f(x))}</option>`).join("");
const activePlans = pid => plansAll.filter(p => p.patient_id === +pid && p.status === "active");

/* ---------- navegación y hoja lateral ---------- */
function go(t) {
  document.querySelectorAll("nav.tabs button").forEach(x => { const on = x.dataset.t === t; x.setAttribute("aria-selected", on); on ? x.setAttribute("aria-current", "page") : x.removeAttribute("aria-current"); });
  document.querySelectorAll("main section").forEach(s => s.hidden = s.id !== t);
  $("fab").hidden = t !== "agenda";
  if (t === "caja") pays().catch(fail);
  if (t === "admin") users().catch(fail);
  if (t === "biblioteca" && !$("tplPane").hidden) tplList().catch(fail);
  window.scrollTo({ top: 0 });
}
const sheetTop = back => `<div class="sheet-top">${back ? `<button class="btn ghost sm" data-act="${back.act}" data-id="${back.id ?? ""}">${ic("left")}${esc(back.label)}</button>` : "<span></span>"}<button class="iconbtn" data-act="close" aria-label="Cerrar">${ic("x", "")}</button></div>`;
function sheet(html) {
  const d = $("detail"), b = $("detailBody");
  if (!d.classList.contains("on")) lastFocus = document.activeElement;
  b.innerHTML = html; d.classList.add("on"); b.parentElement.scrollTop = 0; b.setAttribute("tabindex", "-1");
  const t = b.querySelector("h2"); if (t) { t.id = "sheetTitle"; d.setAttribute("aria-labelledby", "sheetTitle"); }
  document.querySelectorAll("header,main,nav,.fab").forEach(x => x.inert = true); b.focus({ preventScroll: true });
}
function closeSheet() {
  const d = $("detail"); if (!d.classList.contains("on")) return;
  d.classList.remove("on"); document.querySelectorAll("header,main,nav,.fab").forEach(x => x.inert = false);
  lastFocus?.isConnected && lastFocus.focus({ preventScroll: true });
}
document.addEventListener("keydown", e => { if (e.key === "Escape") closeSheet(); });
$("detail").addEventListener("click", e => { if (e.target.id === "detail") closeSheet(); });

/* ---------- piezas visuales ---------- */
const pips = (done, sched, total) => total > 24 ? `<span class="muted">${done} de ${total}</span>`
  : `<span class="pips" role="img" aria-label="${done} de ${total} sesiones realizadas">${Array.from({ length: total }, (_, i) => `<i class="${i < done ? "d" : i < done + sched ? "s" : ""}"></i>`).join("")}</span>`;
const empty = (t, s, btn = "") => `<div class="empty"><b>${t}</b>${s}${btn}</div>`;
const waLink = (p, a) => {
  if (!p || !p.phone) return "";
  let n = p.phone.replace(/\D/g, ""); if (n.length === 9 && n[0] === "9") n = "56" + n; else if (n.length === 8) n = "569" + n; if (n.length < 10) return "";
  const msg = `Hola ${p.name.split(" ")[0]}, te recordamos tu sesión de kinesiología el ${longDate(parseDay(a.starts_at.slice(0, 10))).toLowerCase()} a las ${a.starts_at.slice(11)}. ¿Confirmas tu asistencia?`;
  return `<a class="btn ghost sm" target="_blank" rel="noopener noreferrer" href="https://wa.me/${n}?text=${encodeURIComponent(msg)}">${ic("chat")}Recordar</a>`;
};

/* ---------- agenda ---------- */
function strip() {
  const sel = parseDay($("day").value), today = localDay(), out = [];
  const start = new Date(sel); start.setDate(sel.getDate() - 3);
  for (let i = 0; i < 7; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i); const iso = localDay(d);
    out.push(`<button class="d ${iso === today ? "today" : ""}" data-act="day" data-d="${iso}" aria-pressed="${iso === $("day").value}" aria-label="${longDate(d)}">${new Intl.DateTimeFormat("es-CL", { weekday: "short" }).format(d).replace(".", "")}<b>${d.getDate()}</b></button>`);
  }
  $("strip").innerHTML = out.join("");
}
const slotHTML = (a, next) => {
  const p = patient(a.patient_id), plan = a.plan_id && plansAll.find(x => x.id === a.plan_id), live = ["scheduled", "arrived"].includes(a.status);
  const tag = a.status === "done" ? `<span class="tag ok">${ic("check")}${ST.done}</span>` : a.status === "arrived" ? `<span class="tag wait">${ST.arrived}</span>` : next ? `<span class="tag now">Siguiente</span>` : (live ? "" : `<span class="tag">${ST[a.status]}</span>`);
  const end = new Date(parseDay(a.starts_at.slice(0, 10)).setHours(+a.starts_at.slice(11, 13), +a.starts_at.slice(14, 16) + a.duration_min)).toTimeString().slice(0, 5);
  return `<article class="slot"><div class="t">${a.starts_at.slice(11)}<small>${end}</small></div>
  <div class="ap ${next ? "next" : ""} ${["cancelled", "no_show"].includes(a.status) ? "off" : ""}"><div class="top2"><div><div class="name">${esc(a.patient_name)}</div>
  <div class="meta">${esc(a.professional_name)}${a.room ? " · " + esc(a.room) : ""}${a.reason && !a.plan_id ? " · " + esc(a.reason) : ""}</div></div>${tag}</div>
  ${plan ? `<div class="plan">${pips(plan.sessions_done, plan.sessions_scheduled, plan.total_sessions)}<span>${a.session_no ? `Sesión ${a.session_no} de ${a.plan_total} · ` : ""}${esc(a.plan_title)}</span></div>` : ""}
  ${a.allergies ? `<div class="alert">${ic("alert")}<span>${esc(a.allergies)}</span></div>` : ""}
  <div class="acts">${live ? `<button class="btn sm" data-act="attendAppt" data-id="${a.id}">${ic("note")}Atender</button>${waLink(p, a)}` : ""}
  <select data-status="${a.id}" aria-label="Estado de la cita de ${esc(a.patient_name)}">${Object.entries(ST).map(([k, v]) => `<option value="${k}" ${k === a.status ? "selected" : ""}>${v}</option>`).join("")}</select></div></div></article>`;
};
async function agenda() {
  const day = $("day").value, l = await api("/api/agenda?day=" + day);
  $("agTitle").textContent = longDate(parseDay(day));
  const live = l.filter(a => ["scheduled", "arrived"].includes(a.status)), done = l.filter(a => a.status === "done").length;
  $("agSub").textContent = l.length ? `${l.length} ${l.length === 1 ? "sesión" : "sesiones"} · ${live.length} por atender · ${done} ${done === 1 ? "realizada" : "realizadas"}` : "Sin sesiones agendadas";
  strip();
  let next = null;
  if (day === localDay()) { const now = new Date().toTimeString().slice(0, 5); next = live.find(a => a.starts_at.slice(11) >= now) || live[0]; }
  $("agendaList").innerHTML = l.length ? l.map(a => slotHTML(a, next && a.id === next.id)).join("")
    : empty("Día libre", "No hay sesiones para esta fecha.", `<br><button class="btn" data-act="newAppt">${ic("plus")}Agendar una sesión</button>`);
}

/* ---------- carga de datos ---------- */
async function load() {
  [pats, pros, plansAll] = await Promise.all([api("/api/patients"), api("/api/professionals"), api("/api/plans")]);
  const keepP = $("cPatient").value, keepR = $("cPro").value;
  $("cPatient").innerHTML = opts(pats, p => p.name + (p.rut ? " · " + p.rut : "")); $("cPro").innerHTML = opts(pros, p => p.name + " · " + p.specialty);
  if (keepP) $("cPatient").value = keepP; if (keepR) $("cPro").value = keepR;
  renderPatients(); await loadPlans($("cPlan").value);
}
const refresh = () => load().then(() => Promise.all([agenda(), cons()])).catch(fail);

/* ---------- pacientes ---------- */
function renderPatients() {
  const q = fold($("pSearch").value);
  $("patCount").textContent = pats.length + (pats.length === 1 ? " paciente" : " pacientes");
  const l = pats.filter(p => !q || fold(p.name + " " + (p.rut || "")).includes(q));
  $("patList").innerHTML = l.map(p => { const pl = activePlans(p.id)[0];
    return `<div class="prow" data-act="patient" data-id="${p.id}" tabindex="0" role="button">${avatar(p.name)}<div><div class="nm">${esc(p.name)}</div><div class="sub">${pl ? `${pips(pl.sessions_done, pl.sessions_scheduled, pl.total_sessions)}<span>${esc(pl.title)}</span>` : `<span>${esc(p.rut || "Sin RUT")}</span>`}${p.allergies ? `<span class="tag wait">${ic("alert")}Precaución</span>` : ""}</div></div>${ic("right", "")}</div>`; }).join("")
    || (pats.length ? empty("Sin coincidencias", "Pruebe con otro nombre o RUT.") : empty("Aún no hay pacientes", "Registre al primero para crear su plan de tratamiento.", `<br><button class="btn" data-act="newPatient">${ic("plus")}Nuevo paciente</button>`));
}
$("pSearch").addEventListener("input", renderPatients);
const patientForm = p => `${sheetTop(p ? { act: "patient", id: p.id, label: "Ficha" } : null)}<h2>${p ? "Editar paciente" : "Nuevo paciente"}</h2>
<form class="stack" data-form="patient" data-id="${p?.id ?? ""}" style="margin-top:1rem"><label class="field"><span>Nombre completo</span><input name="name" value="${esc(p?.name)}" required maxlength="120"></label>
<div class="cols"><label class="field"><span>RUT</span><input name="rut" value="${esc(p?.rut)}" maxlength="20"></label><label class="field"><span>Fecha de nacimiento</span><input type="date" name="birth_date" value="${esc(p?.birth_date)}"></label></div>
<div class="cols"><label class="field"><span>Teléfono (WhatsApp)</span><input name="phone" value="${esc(p?.phone)}" inputmode="tel" maxlength="40"></label><label class="field"><span>Correo</span><input name="email" type="email" value="${esc(p?.email)}" maxlength="160"></label></div>
<label class="field"><span>Previsión</span><input name="insurance" value="${esc(p?.insurance)}" maxlength="80" placeholder="Fonasa, Isapre, particular"></label>
<label class="field"><span>Alergias / precauciones</span><input name="allergies" value="${esc(p?.allergies)}" maxlength="300"></label><button class="btn block">Guardar</button></form>`;

const consRow = c => `<div class="rowl"><div class="d">${dm(c.occurred_at)}</div><div class="grow"><div>${c.eva != null ? `<span class="tag">EVA ${c.eva}/10</span> ` : ""}${(c.measurements || []).map(m => `<span class="tag">${esc(m.name)} ${m.value}${esc(m.unit)}</span>`).join(" ")}</div>
${c.diagnosis ? `<div style="margin-top:.3rem">${esc(c.diagnosis)}</div>` : ""}${c.treatment ? `<div class="muted">${esc(c.treatment)}</div>` : ""}
${(c.library || []).length ? `<div class="pick">${c.library.map(l => `<button class="btn ghost sm" data-act="lib" data-id="${l.id}">${ic("book")}${esc(l.title)}</button>`).join("")}</div>` : ""}
${c.attachment_path ? `<a class="btn ghost sm" href="/api/consultations/${c.id}/attachment" target="_blank" rel="noopener">Ver adjunto</a>` : ""}</div></div>`;

const planCard = p => `<div class="plancard"><div style="display:flex;justify-content:space-between;gap:.5rem;align-items:flex-start"><h4>${esc(p.title)}</h4><span class="tag ${p.status === "completed" ? "ok" : ""}">${PST[p.status]}</span></div>
<div style="margin:.5rem 0">${pips(p.sessions_done, p.sessions_scheduled, p.total_sessions)}</div><div class="muted">${p.sessions_done} de ${p.total_sessions} sesiones${p.sessions_scheduled ? ` · ${p.sessions_scheduled} agendadas` : ""}</div>
${p.reason ? `<p style="margin:.6rem 0 0"><span class="muted">Motivo:</span> ${esc(p.reason)}</p>` : ""}${p.kine_diagnosis ? `<p style="margin:.3rem 0 0"><span class="muted">Dx kinésico:</span> ${esc(p.kine_diagnosis)}</p>` : ""}
<div class="pick" style="margin-top:.7rem"><button class="btn sm" data-act="plan" data-id="${p.id}">Ver evolución</button>${p.status === "active" ? `<button class="btn soft sm" data-act="attendPlan" data-id="${p.id}" data-pt="${p.patient_id}">Atender</button><button class="btn ghost sm" data-act="sched" data-id="${p.id}">Agendar sesiones</button>` : ""}</div><div data-schedbox="${p.id}"></div></div>`;

async function openPatient(id, tab = "resumen") {
  try {
    const p = patient(id), [plans, cs] = await Promise.all([api("/api/plans?patient_id=" + id), api("/api/consultations?patient_id=" + id + "&limit=50")]);
    const tel = p.phone ? p.phone.replace(/[^\d+]/g, "") : "";
    const tabs = `<div class="seg" style="margin:1rem 0">${[["resumen", "Resumen"], ["planes", "Planes"], ["historial", "Historial"]].map(([k, v]) => `<button data-act="ptab" data-id="${id}" data-tab="${k}" aria-pressed="${k === tab}">${v}</button>`).join("")}</div>`;
    let body = "";
    if (tab === "resumen") {
      body = `<dl class="info"><dt>RUT</dt><dd>${esc(p.rut || "—")}</dd>${p.birth_date ? `<dt>Edad</dt><dd>${age(p.birth_date)}</dd>` : ""}<dt>Teléfono</dt><dd>${esc(p.phone || "—")}</dd>${p.email ? `<dt>Correo</dt><dd>${esc(p.email)}</dd>` : ""}<dt>Previsión</dt><dd>${esc(p.insurance || "—")}</dd></dl>
      ${p.allergies ? `<div class="alert">${ic("alert")}<span>${esc(p.allergies)}</span></div>` : ""}
      <div class="pick" style="margin-top:1rem"><button class="btn sm" data-act="attendPat" data-id="${id}">${ic("note")}Atención rápida</button><button class="btn ghost sm" data-act="editPatient" data-id="${id}">${ic("edit")}Editar datos</button></div>
      <h3>Plan en curso</h3>${plans.filter(x => x.status === "active").map(planCard).join("") || `<p class="muted">Sin plan en curso. Cree uno en la pestaña Planes.</p>`}
      <h3>Última atención</h3>${cs.slice(0, 1).map(consRow).join("") || `<p class="muted">Sin atenciones registradas.</p>`}`;
    } else if (tab === "planes") {
      body = `${plans.map(planCard).join("") || `<p class="muted">Aún no tiene planes de tratamiento.</p>`}
      <h3>Nuevo plan</h3><form class="stack" data-form="plan" data-id="${id}"><label class="field"><span>Nombre del plan</span><input name="title" placeholder="Ej.: Lumbalgia mecánica" required maxlength="120"></label>
      <label class="field"><span>Motivo de consulta</span><textarea name="reason" rows="2" maxlength="500" placeholder="En palabras del paciente"></textarea></label>
      <div class="cols"><label class="field"><span>Diagnóstico kinésico</span><input name="dx" maxlength="300"></label><label class="field"><span>Cantidad de sesiones</span><input name="n" type="number" min="1" max="100" value="10" inputmode="numeric" required></label></div><button class="btn block">Crear plan</button></form>`;
    } else body = cs.map(consRow).join("") || empty("Sin atenciones", "Se listan aquí al registrar la primera.");
    sheet(`${sheetTop()}<div class="person">${avatar(p.name, "big")}<div><h2 style="font-size:1.5rem">${esc(p.name)}</h2><div class="muted">${[p.rut, age(p.birth_date)].filter(Boolean).join(" · ")}</div></div></div>
    <div class="pick">${tel ? `<a class="btn ghost sm" href="tel:${esc(tel)}">${ic("phone")}Llamar</a>` : ""}</div>${tabs}${body}`);
  } catch (x) { fail(x); }
}

/* ---------- planes y evolución ---------- */
let chartN = 0;
function chart(title, pts, { min, max, unit = "", judge = false } = {}) {
  if (!pts.length) return "";
  const W = 320, H = 150, L = 30, R = 14, T = 20, B = 26, id = "g" + ++chartN, vs = pts.map(p => p.value);
  let lo = min ?? Math.min(...vs), hi = max ?? Math.max(...vs); if (lo === hi) { lo -= 1; hi += 1; }
  if (min == null) { const pad = (hi - lo) * .2; lo -= pad; hi += pad; }
  const x = i => pts.length === 1 ? (L + W - R) / 2 : L + i * (W - L - R) / (pts.length - 1), y = v => T + (hi - v) * (H - T - B) / (hi - lo);
  const grid = [lo, (lo + hi) / 2, hi].map(v => `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="var(--line)"/><text x="${L - 5}" y="${y(v) + 3.5}" text-anchor="end" font-size="9" fill="var(--ink2)">${Math.round(v * 10) / 10}</text>`).join("");
  const line = pts.map((p, i) => `${i ? "L" : "M"}${x(i)},${y(p.value)}`).join(" "), area = `${line} L${x(pts.length - 1)},${H - B} L${x(0)},${H - B} Z`;
  const dots = pts.map((p, i) => `<circle cx="${x(i)}" cy="${y(p.value)}" r="4" fill="var(--surface)" stroke="var(--brand)" stroke-width="2.2"/><text x="${x(i)}" y="${y(p.value) - 9}" text-anchor="middle" font-size="10.5" font-weight="700" fill="var(--ink)">${p.value}</text><text x="${x(i)}" y="${H - 8}" text-anchor="middle" font-size="9" fill="var(--ink2)">${dm(p.date)}</text>`).join("");
  const f = pts[0].value, l = pts[pts.length - 1].value, d = Math.round((l - f) * 10) / 10;
  const delta = pts.length > 1 ? `<div class="delta"><b>${f} → ${l}${esc(unit === "0–10" ? "" : unit)}</b><span class="${judge ? (d < 0 ? "t-ok" : d > 0 ? "t-bad" : "") : ""}">${d > 0 ? "+" : ""}${d}</span></div>` : "";
  return `<div class="chartwrap"><h3 style="margin:1.2rem 0 .1rem;font-size:1rem">${esc(title)} <span class="muted" style="font-family:var(--text);font-weight:400">${esc(unit)}</span></h3>${delta}
  <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(title)}: ${pts.map(p => dm(p.date) + " " + p.value).join(", ")}"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--brand)" stop-opacity=".28"/><stop offset="1" stop-color="var(--brand)" stop-opacity="0"/></linearGradient></defs>${grid}<path d="${area}" fill="url(#${id})"/><path d="${line}" fill="none" stroke="var(--brand)" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>${dots}</svg></div>`;
}
async function openPlan(id) {
  try {
    const p = await api("/api/plans/" + id), ev = p.evolution, tpls = await api("/api/templates");
    const charts = chart("EVA (dolor)", ev.eva, { min: 0, max: 10, unit: "0–10", judge: true }) + Object.entries(ev.measures).map(([n, pts]) => chart(n, pts, { unit: pts[0].unit })).join("");
    const next = p.appointments.filter(a => ["scheduled", "arrived"].includes(a.status));
    sheet(`${sheetTop({ act: "patient", id: p.patient_id, label: "Ficha" })}<h2>${esc(p.title)}</h2><p class="muted" style="margin:.2rem 0 .6rem">${esc(p.patient_name)} · ${PST[p.status]}</p>
    <div>${pips(p.sessions_done, p.sessions_scheduled, p.total_sessions).replace('class="pips"', 'class="pips lg"')}</div><p class="muted">${p.sessions_done} de ${p.total_sessions} sesiones realizadas</p>
    ${p.reason ? `<p><span class="muted">Motivo:</span> ${esc(p.reason)}</p>` : ""}${p.kine_diagnosis ? `<p><span class="muted">Dx kinésico:</span> ${esc(p.kine_diagnosis)}</p>` : ""}
    <div class="charts">${charts || empty("Aún no hay datos para graficar", "Registre EVA y mediciones al guardar las atenciones de este plan.")}</div>
    <h3>Sesiones realizadas</h3>${p.consultations.map(consRow).join("") || `<p class="muted">Sin sesiones registradas.</p>`}
    <h3>Próximas sesiones</h3>${next.map(a => `<div class="muted" style="padding:.2rem 0">${esc(longDate(parseDay(a.starts_at.slice(0, 10))))} · ${a.starts_at.slice(11)}${a.room ? " · " + esc(a.room) : ""}</div>`).join("") || `<p class="muted">Sin sesiones agendadas.</p>`}
    <h3>Ejercicios para el hogar</h3><div class="cols"><select id="homeTpl" aria-label="Plantilla">${opts(tpls, t => `${t.name} (${t.item_count})`) || '<option value="">No hay plantillas aún</option>'}</select><button class="btn sm" data-act="homePrint" data-pt="${p.patient_id}">${ic("print")}Imprimir / PDF</button></div>
    <p class="muted">Se abre una hoja con el nombre del paciente; use Imprimir o Guardar como PDF del navegador.</p>
    <div class="pick" style="margin-top:1.4rem">${p.status === "active" ? `<button class="btn ghost sm" data-act="planStatus" data-id="${p.id}" data-s="completed">Marcar como completado</button><button class="btn ghost sm" data-act="planStatus" data-id="${p.id}" data-s="cancelled">Cancelar plan</button>` : `<button class="btn ghost sm" data-act="planStatus" data-id="${p.id}" data-s="active">Reabrir plan</button>`}</div>`);
  } catch (x) { fail(x); }
}
async function planStatus(id, status) {
  try { const p = await api("/api/plans/" + id); await send("PUT", "/api/plans/" + id, { patient_id: p.patient_id, professional_id: p.professional_id, title: p.title, reason: p.reason, kine_diagnosis: p.kine_diagnosis, total_sessions: p.total_sessions, status }); say("Plan actualizado"); await load(); openPlan(id); } catch (x) { fail(x); }
}
function schedForm(id) {
  const box = document.querySelector(`[data-schedbox="${id}"]`), d = new Date(); d.setDate(d.getDate() + 1); d.setHours(9, 0, 0, 0);
  box.innerHTML = `<form class="stack" data-form="series" data-id="${id}" style="margin-top:.8rem;padding-top:.8rem;border-top:1px solid var(--line)"><label class="field"><span>Primera sesión</span><input type="datetime-local" name="s" value="${new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 16)}" required></label>
  <div class="cols"><label class="field"><span>Sesiones</span><input type="number" name="n" min="1" max="100" value="5" required inputmode="numeric"></label><label class="field"><span>Cada (días)</span><input type="number" name="i" min="1" max="30" value="2" required inputmode="numeric"></label><label class="field"><span>Minutos</span><input type="number" name="d" min="5" max="480" value="45" required inputmode="numeric"></label></div>
  <div class="cols"><label class="field"><span>Profesional</span><select name="p">${opts(pros, p => p.name)}</select></label><label class="field"><span>Sala / box</span><input name="r"></label></div><button class="btn block">Agendar serie</button></form>`;
  box.querySelector("input").focus();
}

/* ---------- citas, pagos (hojas) ---------- */
function apptForm(pre = {}) {
  const day = pre.day || $("day").value, pid = pre.patient || pats[0]?.id;
  if (!pats.length) { sheet(`${sheetTop()}<h2>Agendar sesión</h2>${empty("Primero registre un paciente", "Necesita al menos un paciente para agendar.", `<br><button class="btn" data-act="newPatient">${ic("plus")}Nuevo paciente</button>`)}`); return; }
  sheet(`${sheetTop()}<h2>Agendar sesión</h2><form class="stack" data-form="appt" style="margin-top:1rem">
  <label class="field"><span>Paciente</span><select name="patient" id="apPat" required>${opts(pats, p => p.name)}</select></label>
  <label class="field"><span>Plan de tratamiento</span><select name="plan" id="apPlan"></select></label>
  <label class="field"><span>Profesional</span><select name="pro" required>${opts(pros, p => p.name + " · " + p.specialty)}</select></label>
  <div class="cols"><label class="field"><span>Fecha y hora</span><input type="datetime-local" name="start" value="${day}T09:00" required></label><label class="field"><span>Duración (min)</span><input type="number" name="dur" value="45" min="5" max="480" inputmode="numeric"></label></div>
  <div class="cols"><label class="field"><span>Sala / box</span><input name="room" maxlength="40"></label><label class="field"><span>Motivo</span><input name="reason" maxlength="200"></label></div><button class="btn block">Agendar</button></form>`);
  $("apPat").value = pid; fillApPlans();
}
function fillApPlans() { $("apPlan").innerHTML = '<option value="">Cita suelta (sin plan)</option>' + opts(activePlans($("apPat").value), p => `${p.title} · ${p.sessions_done}/${p.total_sessions}`); }
function payForm() {
  sheet(`${sheetTop()}<h2>Registrar pago</h2><form class="stack" data-form="pay" style="margin-top:1rem"><label class="field"><span>Paciente</span><select name="patient" required>${opts(pats, p => p.name)}</select></label>
  <label class="field"><span>Concepto</span><input name="concept" required maxlength="160" placeholder="Sesión de kinesiología"></label>
  <div class="cols"><label class="field"><span>Monto (CLP)</span><input name="amount" type="number" min="0" required inputmode="numeric"></label><label class="field"><span>Medio</span><select name="method"><option value="cash">Efectivo</option><option value="card">Tarjeta</option><option value="transfer">Transferencia</option><option value="insurance">Seguro / Isapre</option></select></label></div><button class="btn block">Guardar pago</button></form>`);
}
async function pays() {
  const [d, l] = await Promise.all([api("/api/dashboard"), api("/api/payments")]);
  $("money").textContent = clp(d.month_revenue);
  $("payList").innerHTML = l.slice(0, 40).map(y => { const p = patient(y.patient_id); return `<div class="pay"><span>${esc(y.concept)}<br><span class="muted">${esc(p ? p.name : "")} · ${y.paid_at.slice(0, 10).split("-").reverse().join("/")}</span></span><b>${clp(y.amount)}</b></div>`; }).join("") || empty("Sin pagos registrados", "Los pagos del mes aparecerán aquí.");
}

/* ---------- atención ---------- */
let eva = null, links = new Map();
$("evaRow").innerHTML = [...Array(11).keys()].map(n => `<button type="button" aria-pressed="false" data-v="${n}" aria-label="EVA ${n}">${n}</button>`).join("");
$("evaRow").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; eva = eva === +b.dataset.v ? null : +b.dataset.v; document.querySelectorAll("#evaRow button").forEach(x => x.setAttribute("aria-pressed", +x.dataset.v === eva)); });
function addMeas(v = {}) {
  const d = document.createElement("div"); d.className = "meas";
  d.innerHTML = `<input list="measNames" placeholder="Movimiento" aria-label="Movimiento" value="${esc(v.name || "")}"><input type="number" step="any" inputmode="decimal" placeholder="Valor" aria-label="Valor" value="${v.value ?? ""}"><select aria-label="Unidad"><option>°</option><option ${v.unit === "cm" ? "selected" : ""}>cm</option></select><button type="button" class="iconbtn" aria-label="Quitar medición">${ic("x", "sm")}</button>`;
  $("measRows").append(d);
}
$("addMeas").addEventListener("click", () => addMeas());
$("measRows").addEventListener("click", e => { if (e.target.closest("button")) e.target.closest(".meas").remove(); });
$("repeatMeas").addEventListener("click", async () => {
  try {
    if (!$("cPlan").value) return say("Elija un plan para repetir sus mediciones");
    const p = await api("/api/plans/" + $("cPlan").value), last = [...p.consultations].reverse().find(c => c.measurements.length);
    if (!last) return say("Ese plan aún no tiene mediciones");
    const have = new Set([...document.querySelectorAll("#measRows .meas input:first-child")].map(i => i.value));
    last.measurements.filter(m => !have.has(m.name)).forEach(m => addMeas({ name: m.name, unit: m.unit }));
    $("measRows").querySelector(".meas:last-child input:nth-child(2)")?.focus();
  } catch (x) { fail(x); }
});
const measData = () => [...document.querySelectorAll("#measRows .meas")].map(r => { const [i, v, u] = r.querySelectorAll("input,select"); return { name: i.value.trim(), value: v.value, unit: u.value }; }).filter(m => m.name && m.value !== "").map(m => ({ ...m, value: +m.value }));
function drawLinks() { $("linkSel").innerHTML = [...links].map(([id, t]) => `<button type="button" class="chip" aria-pressed="true" data-rm="${id}">${esc(t)} ✕</button>`).join(""); }
let lt; $("linkQ").addEventListener("input", () => { clearTimeout(lt); lt = setTimeout(async () => { const q = $("linkQ").value.trim(); if (q.length < 2) { $("linkRes").innerHTML = ""; return; } const l = (await api("/api/library?q=" + encodeURIComponent(q)).catch(() => [])).slice(0, 6); $("linkRes").innerHTML = l.map(i => `<button type="button" class="chip" aria-pressed="false" data-add="${i.id}" data-t="${esc(i.title)}">+ ${esc(i.title)}</button>`).join("") || '<span class="muted">Sin resultados</span>'; }, 200); });
$("linkRes").addEventListener("click", e => { const b = e.target.closest("[data-add]"); if (!b) return; links.set(+b.dataset.add, b.dataset.t); drawLinks(); $("linkQ").value = ""; $("linkRes").innerHTML = ""; });
$("linkSel").addEventListener("click", e => { const b = e.target.closest("[data-rm]"); if (b) { links.delete(+b.dataset.rm); drawLinks(); } });
async function loadPlans(selected) {
  const pid = $("cPatient").value; if (!pid) { $("cPlan").innerHTML = ""; return; }
  const l = await api("/api/plans?patient_id=" + pid + "&status=active");
  $("cPlan").innerHTML = '<option value="">Sin plan (atención suelta)</option>' + l.map(p => `<option value="${p.id}">${esc(p.title)} · ${p.sessions_done}/${p.total_sessions}</option>`).join("");
  if (selected) $("cPlan").value = selected;
}
$("cPatient").addEventListener("change", () => { $("cAppt").value = ""; $("cApptNote").hidden = true; loadPlans().catch(fail); });
async function startAttention(apptId, opt = {}) {
  try {
    closeSheet(); go("atencion"); await load();
    if (apptId) { const a = await api("/api/appointments/" + apptId); $("cPatient").value = a.patient_id; $("cPro").value = a.professional_id; $("cAppt").value = a.id; $("cApptNote").hidden = false; $("cApptNote").textContent = "Atención de la cita del " + a.starts_at.replace("T", " a las "); await loadPlans(a.plan_id); }
    else { if (opt.patient) $("cPatient").value = opt.patient; $("cAppt").value = ""; $("cApptNote").hidden = true; await loadPlans(opt.plan); }
    $("cDiag").focus({ preventScroll: true });
  } catch (x) { fail(x); }
}
$("fCons").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const f = new FormData(); f.append("patient_id", $("cPatient").value); f.append("professional_id", $("cPro").value);
    if ($("cAppt").value) f.append("appointment_id", $("cAppt").value); if ($("cPlan").value) f.append("plan_id", $("cPlan").value); if (eva !== null) f.append("eva", eva);
    const m = measData(); if (m.length) f.append("measurements", JSON.stringify(m)); if (links.size) f.append("library_ids", [...links.keys()].join(","));
    f.append("diagnosis", $("cDiag").value); f.append("treatment", $("cTreat").value); f.append("notes", $("cNotes").value); if ($("cFile").files[0]) f.append("attachment", $("cFile").files[0]);
    await api("/api/consultations", { method: "POST", body: f });
    const keep = [$("cPatient").value, $("cPro").value, $("cPlan").value]; e.target.reset(); eva = null; links = new Map(); drawLinks(); $("measRows").innerHTML = "";
    document.querySelectorAll("#evaRow button").forEach(x => x.setAttribute("aria-pressed", "false")); $("cAppt").value = ""; $("cApptNote").hidden = true;
    $("cPatient").value = keep[0]; $("cPro").value = keep[1]; await refresh(); await loadPlans(keep[2]); say("Atención guardada");
  } catch (x) { fail(x); }
});
async function cons() { const l = await api("/api/consultations?limit=15"); $("consList").innerHTML = l.map(c => `<div class="panel" style="padding:.8rem 1rem"><div style="display:flex;justify-content:space-between;gap:1rem"><b>${esc(c.patient_name)}</b><span class="muted">${c.occurred_at.slice(0, 16).replace("T", " ")}</span></div>${consRow(c).replace('<div class="rowl">', '<div class="rowl" style="border:0;padding:.4rem 0 0">')}</div>`).join("") || empty("Aún no hay atenciones", "Las que registre aparecerán aquí."); }

/* ---------- biblioteca y plantillas ---------- */
const CATS = {};
async function libMeta() { const m = await api("/api/library/meta"); m.categories.forEach(c => CATS[c.id] = c.label); $("libCount").textContent = m.total + " entradas";
  $("cats").innerHTML = `<button class="chip" aria-pressed="${cat === ""}" data-c="">Todo</button>` + m.categories.map(c => `<button class="chip" aria-pressed="${cat === c.id}" data-c="${c.id}">${c.label} · ${c.count}</button>`).join("");
  $("regSel").innerHTML = '<option value="">Todas las regiones</option>' + m.regions.map(r => `<option>${esc(r)}</option>`).join(""); $("lCat").innerHTML = m.categories.map(c => `<option value="${c.id}">${c.label}</option>`).join(""); }
let t; async function libSearch() { const l = await api("/api/library?" + new URLSearchParams({ q: $("q").value, category: cat, region: $("regSel").value }));
  $("libList").innerHTML = l.map(i => `<div class="lrow" data-act="lib" data-id="${i.id}" tabindex="0" role="button"><div class="ti">${esc(i.title)}<span>${CATS[i.category] || i.category}${i.region ? " · " + esc(i.region) : ""}</span></div>${i.summary ? `<p>${esc(i.summary)}</p>` : ""}</div>`).join("") || empty("Sin resultados", "Pruebe con otras palabras o quite los filtros."); }
$("q").addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => libSearch().catch(fail), 200); }); $("regSel").addEventListener("change", () => libSearch().catch(fail));
$("cats").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; cat = b.dataset.c; document.querySelectorAll("#cats .chip").forEach(x => x.setAttribute("aria-pressed", x === b)); libSearch().catch(fail); });
async function libDetail(id) {
  const i = await api("/api/library/" + id), tpls = i.category === "ejercicio" ? await api("/api/templates") : [];
  sheet(`${sheetTop()}<div class="article"><p class="muted" style="margin:0 0 .3rem">${CATS[i.category] || ""}${i.region ? " · " + esc(i.region) : ""}</p><h2>${esc(i.title)}</h2>
  <div class="notice">${ic("alert")}<span>Contenido redactado con apoyo de IA, sin validación de un kinesiólogo.</span></div>${i.summary ? `<p style="font-weight:600">${esc(i.summary)}</p>` : ""}<div class="body">${esc(i.content || "")}</div>
  ${i.precautions ? `<div class="prec"><b>Precauciones</b><br>${esc(i.precautions)}</div>` : ""}${i.tags ? `<p class="muted">${esc(i.tags)}</p>` : ""}</div>
  ${tpls.length ? `<div class="cols" style="margin-top:1rem"><select id="addTplSel" aria-label="Plantilla">${opts(tpls, t => t.name)}</select><button class="btn soft sm" data-act="addToTpl" data-id="${i.id}">${ic("plus")}Agregar a plantilla</button></div>` : i.category === "ejercicio" ? `<p class="muted">Cree una plantilla en “Ejercicios para el hogar” para agregar este ejercicio.</p>` : ""}
  ${me.role === "admin" ? `<p style="margin-top:1.4rem"><button class="btn ghost sm" data-act="delLib" data-id="${i.id}">Eliminar entrada</button></p>` : ""}`);
}
let tplItems = [], tplId = null;
async function tplList() { const l = await api("/api/templates"); $("tplList").innerHTML = l.map(t => `<div class="lrow" data-act="tplOpen" data-id="${t.id}" tabindex="0" role="button"><div class="ti">${esc(t.name)}<span>${t.item_count} ejercicios</span></div>${t.notes ? `<p>${esc(t.notes)}</p>` : ""}</div>`).join("") || empty("Aún no hay plantillas", "Reúna ejercicios de la biblioteca en un programa para entregar al paciente."); }
function drawTplItems() { $("tplItems").innerHTML = tplItems.map((it, i) => `<div class="item"><div style="display:flex;justify-content:space-between;gap:.5rem;align-items:center"><b>${i + 1}. ${esc(it.title)}</b><button type="button" class="iconbtn" data-act="tplRm" data-i="${i}" aria-label="Quitar ${esc(it.title)}">${ic("x", "sm")}</button></div><input placeholder="Series / repeticiones (lo define usted)" aria-label="Dosificación" value="${esc(it.dosage || "")}" data-k="dosage" data-i="${i}" maxlength="80"><input placeholder="Indicación para el paciente (opcional)" aria-label="Indicación" value="${esc(it.notes || "")}" data-k="notes" data-i="${i}" maxlength="300"></div>`).join("") || '<p class="muted">Agregue ejercicios con el buscador.</p>'; }
async function openTemplate(id) {
  tplId = id; let t = { name: "", notes: "", items: [] }; if (id) t = await api("/api/templates/" + id);
  tplItems = t.items.map(i => ({ library_item_id: i.library_item_id, title: i.title, dosage: i.dosage, notes: i.notes }));
  sheet(`${sheetTop()}<h2>${id ? "Editar plantilla" : "Nueva plantilla"}</h2><div class="notice">${ic("alert")}<span>Contenido de la biblioteca redactado con apoyo de IA y sin validar por un kinesiólogo: revise cada ejercicio antes de entregarlo.</span></div>
  <div class="stack"><label class="field"><span>Nombre</span><input id="tplName" value="${esc(t.name)}" maxlength="120" placeholder="Rodilla – fase inicial"></label><label class="field"><span>Indicaciones generales</span><textarea id="tplNotes" rows="2" maxlength="600">${esc(t.notes || "")}</textarea></label>
  <div class="search"><svg class="ic"><use href="#i-search"/></svg><input id="tplQ" type="search" placeholder="Buscar ejercicio de la biblioteca" autocomplete="off" aria-label="Buscar ejercicio"></div><div class="pick" id="tplRes"></div><div id="tplItems"></div>
  <button class="btn block" data-act="tplSave">Guardar plantilla</button>
  ${id ? `<div class="cols"><select id="tplPatient" aria-label="Paciente"><option value="">Sin nombre de paciente</option>${opts(pats, p => p.name)}</select><button class="btn soft" data-act="tplPrint" data-id="${id}">${ic("print")}Imprimir / PDF</button></div><button class="btn ghost sm" data-act="tplDel" data-id="${id}">Eliminar plantilla</button>` : ""}</div>`);
  drawTplItems();
  $("tplItems").addEventListener("input", e => { const k = e.target.dataset.k; if (k) tplItems[+e.target.dataset.i][k] = e.target.value; });
  let tt; $("tplQ").addEventListener("input", () => { clearTimeout(tt); tt = setTimeout(async () => { const l = (await api("/api/library?category=ejercicio&q=" + encodeURIComponent($("tplQ").value.trim())).catch(() => [])).slice(0, 8); $("tplRes").innerHTML = l.map(i => `<button type="button" class="chip" aria-pressed="false" data-act="tplAdd" data-id="${i.id}" data-t="${esc(i.title)}">+ ${esc(i.title)}</button>`).join("") || '<span class="muted">Sin resultados</span>'; }, 200); });
}
async function saveTemplate() {
  try { const name = $("tplName").value.trim(); if (!name) return say("Ponga un nombre a la plantilla");
    const body = { name, notes: nul($("tplNotes").value), items: tplItems.map(i => ({ library_item_id: i.library_item_id, dosage: nul(i.dosage), notes: nul(i.notes) })) };
    const t = tplId ? await send("PUT", "/api/templates/" + tplId, body) : await post("/api/templates", body); say("Plantilla guardada"); tplList(); await openTemplate(t.id); } catch (x) { fail(x); }
}
$("libTabs").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; document.querySelectorAll("#libTabs button").forEach(x => x.setAttribute("aria-pressed", x === b)); $("libPane").hidden = b.dataset.p !== "lib"; $("tplPane").hidden = b.dataset.p !== "tpl"; if (b.dataset.p === "tpl") tplList().catch(fail); });

/* ---------- administración ---------- */
async function users() { const l = await api("/api/users"); $("userList").innerHTML = l.map(u => `<div class="rowl"><div class="grow"><b>${esc(u.name)}</b> <span class="muted">@${esc(u.username)}</span></div><span class="tag">${u.role}${u.active ? "" : " · inactivo"}</span></div>`).join(""); }
const simple = (id, fn) => $(id).addEventListener("submit", async e => { e.preventDefault(); try { await fn(); e.target.reset(); say("Guardado"); } catch (x) { fail(x); } });
simple("fUser", async () => { await post("/api/users", { username: $("uUser").value, name: $("uName").value, password: $("uPass").value, role: $("uRole").value }); users(); });
simple("fPass", () => post("/api/auth/password", { current: $("pwOld").value, new: $("pwNew").value }));
simple("fLib", async () => { await post("/api/library", { category: $("lCat").value, region: nul($("lRegion").value), title: $("lTitle").value, summary: nul($("lSum").value), content: nul($("lBody").value), precautions: nul($("lPrec").value), tags: nul($("lTags").value) }); libMeta(); libSearch(); });

/* ---------- acciones (delegación) ---------- */
const A = {
  close: closeSheet,
  logout: async () => { await api("/api/auth/logout", { method: "POST" }); location.reload(); },
  today: () => setDay(localDay()),
  week: b => setDay(localDay(new Date(parseDay($("day").value).getTime() + (+b.dataset.n) * 864e5))),
  day: b => setDay(b.dataset.d),
  newAppt: () => apptForm(), newPatient: () => sheet(patientForm()), newPay: payForm,
  patient: b => openPatient(+b.dataset.id), ptab: b => openPatient(+b.dataset.id, b.dataset.tab),
  editPatient: b => sheet(patientForm(patient(b.dataset.id))),
  plan: b => openPlan(+b.dataset.id), sched: b => schedForm(b.dataset.id),
  planStatus: b => planStatus(+b.dataset.id, b.dataset.s),
  attendAppt: b => startAttention(+b.dataset.id), attendPat: b => startAttention(null, { patient: b.dataset.id }),
  attendPlan: b => startAttention(null, { patient: b.dataset.pt, plan: b.dataset.id }),
  lib: b => libDetail(+b.dataset.id).catch(fail),
  delLib: async b => { if (confirm("¿Eliminar esta entrada de la biblioteca?")) try { await api("/api/library/" + b.dataset.id, { method: "DELETE" }); closeSheet(); libMeta(); libSearch(); } catch (x) { fail(x); } },
  addToTpl: async b => { try { const id = +$("addTplSel").value, tp = await api("/api/templates/" + id); await send("PUT", "/api/templates/" + id, { name: tp.name, notes: tp.notes, items: [...tp.items.map(i => ({ library_item_id: i.library_item_id, dosage: i.dosage, notes: i.notes })), { library_item_id: +b.dataset.id }] }); say("Agregado a la plantilla"); } catch (x) { fail(x); } },
  homePrint: b => { const tid = $("homeTpl").value; if (!tid) return say("Cree primero una plantilla"); window.open(`/api/templates/${tid}/print?patient_id=${b.dataset.pt}`, "_blank", "noopener"); },
  tplNew: () => openTemplate(null).catch(fail), tplOpen: b => openTemplate(+b.dataset.id).catch(fail), tplSave: saveTemplate,
  tplDel: async b => { if (confirm("¿Eliminar esta plantilla?")) try { await api("/api/templates/" + b.dataset.id, { method: "DELETE" }); closeSheet(); tplList(); } catch (x) { fail(x); } },
  tplPrint: b => window.open(`/api/templates/${b.dataset.id}/print${$("tplPatient").value ? "?patient_id=" + $("tplPatient").value : ""}`, "_blank", "noopener"),
  tplAdd: b => { tplItems.push({ library_item_id: +b.dataset.id, title: b.dataset.t, dosage: "", notes: "" }); drawTplItems(); $("tplQ").value = ""; $("tplRes").innerHTML = ""; },
  tplRm: b => { tplItems.splice(+b.dataset.i, 1); drawTplItems(); },
};
function setDay(d) { $("day").value = d; agenda().catch(fail); }
document.addEventListener("click", e => { const b = e.target.closest("[data-act]"); if (b && A[b.dataset.act]) A[b.dataset.act](b, e); const t = e.target.closest("nav.tabs button"); if (t) go(t.dataset.t); });
document.addEventListener("keydown", e => { if ((e.key === "Enter" || e.key === " ") && e.target.matches("[role=button][data-act]")) { e.preventDefault(); A[e.target.dataset.act](e.target, e); } });
document.addEventListener("change", async e => {
  if (e.target.id === "apPat") return fillApPlans();
  const s = e.target.dataset.status; if (!s) return;
  try { const f = new FormData(); f.append("status", e.target.value); await api(`/api/appointments/${s}/status`, { method: "POST", body: f }); await refresh(); } catch (x) { fail(x); await agenda(); }
});
$("day").addEventListener("change", () => agenda().catch(fail));

document.addEventListener("submit", async e => {
  const f = e.target, kind = f.dataset.form; if (!kind) return; e.preventDefault(); const q = f.elements;
  try {
    if (kind === "patient") {
      const body = { name: q.name.value.trim(), rut: nul(q.rut.value), birth_date: nul(q.birth_date.value), phone: nul(q.phone.value), email: nul(q.email.value), insurance: nul(q.insurance.value), allergies: nul(q.allergies.value), active: true };
      const id = f.dataset.id, saved = id ? await send("PUT", "/api/patients/" + id, body) : await post("/api/patients", body);
      say(id ? "Paciente actualizado" : "Paciente registrado"); await load(); id ? openPatient(saved.id) : openPatient(saved.id, "planes");
    } else if (kind === "plan") {
      const pt = +f.dataset.id; await post("/api/plans", { patient_id: pt, title: q.title.value, reason: nul(q.reason.value), kine_diagnosis: nul(q.dx.value), total_sessions: +q.n.value });
      say("Plan creado"); await load(); openPatient(pt, "planes");
    } else if (kind === "series") {
      const r = await post(`/api/plans/${f.dataset.id}/schedule`, { professional_id: +q.p.value, starts_at: q.s.value, count: +q.n.value, interval_days: +q.i.value, duration_min: +q.d.value, room: nul(q.r.value) });
      say(`${r.created.length} sesiones agendadas` + (r.skipped.length ? ` · ${r.skipped.length} omitidas por choque` : "") + (r.capped ? " · tope del plan" : ""));
      const card = f.closest(".plancard"); if (r.skipped.length) card.insertAdjacentHTML("beforeend", `<div class="notice">${ic("alert")}<span>Omitidas: ${r.skipped.map(s => esc(s.starts_at.replace("T", " ")) + " (" + esc(s.reason) + ")").join("; ")}</span></div>`);
      f.remove(); await load(); agenda();
    } else if (kind === "appt") {
      const s = q.start.value; await post("/api/appointments", { patient_id: +q.patient.value, professional_id: +q.pro.value, starts_at: s, duration_min: +q.dur.value || 45, room: nul(q.room.value), reason: nul(q.reason.value), plan_id: q.plan.value ? +q.plan.value : null });
      closeSheet(); say("Sesión agendada"); $("day").value = s.slice(0, 10); await load(); agenda();
    } else if (kind === "pay") {
      await post("/api/payments", { patient_id: +q.patient.value, concept: q.concept.value, amount: +q.amount.value, method: q.method.value }); closeSheet(); say("Pago registrado"); pays();
    }
  } catch (x) { fail(x); }
});
$("detail").addEventListener("input", () => { });

/* ---------- sesión ---------- */
function showLogin() { $("login").style.display = "grid"; }
async function start() {
  try { me = await api("/api/auth/me"); $("login").style.display = "none"; $("tabAdmin").hidden = me.role !== "admin"; $("day").value = localDay();
    await Promise.all([load(), libMeta()]); await Promise.all([agenda(), cons(), libSearch()]); go("agenda"); } catch { showLogin(); }
}
$("fLogin").addEventListener("submit", async e => { e.preventDefault(); $("lgErr").textContent = ""; try { await post("/api/auth/login", { username: $("lgUser").value, password: $("lgPass").value }); $("lgPass").value = ""; start(); } catch (x) { $("lgErr").textContent = x.message; } });
fetch("/api/meta").then(r => r.json()).then(m => { $("askBox").hidden = !m.ask_enabled; document.title = m.name; }).catch(() => { });
$("fAsk").addEventListener("submit", async e => { e.preventDefault(); $("askOut").innerHTML = '<p class="muted">Consultando…</p>'; try { const r = await post("/api/library/ask", { question: $("askQ").value }); $("askOut").innerHTML = `<div class="panel"><div style="white-space:pre-wrap">${esc(r.answer)}</div><div class="muted" style="margin-top:.6rem">Fuentes: ${r.sources.map(s => `<a href="#" data-act="lib" data-id="${s.id}">${esc(s.title)}</a>`).join(" · ") || "—"}</div></div>`; } catch (x) { $("askOut").innerHTML = ""; fail(x); } });
$("askOut").addEventListener("click", e => { if (e.target.closest("a[data-act]")) e.preventDefault(); });
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => { });
start();
