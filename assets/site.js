// Shared helpers for Daily AI Lessons (vanilla JS, no build step)
const DAL = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function loadLessons() {
    const r = await fetch('data/lessons.json', {cache: 'no-cache'});
    const j = await r.json();
    const list = Array.isArray(j) ? j : (j.lessons || []);
    return list.slice().sort((a, b) => b.date.localeCompare(a.date));
  }
  const todayISO = () => { const d = new Date(); return new Date(d - d.getTimezoneOffset()*6e4).toISOString().slice(0,10); };
  const fmtDate = iso => new Date(iso + 'T12:00:00').toLocaleDateString(undefined, {weekday:'short', month:'short', day:'numeric', year:'numeric'});
  const tagHtml = tags => `<div class="tags">${(tags||[]).map(t => `<span class="tag ${esc(t)}">${esc(t)}</span>`).join('')}</div>`;
  function lessonCard(l, opts = {}) {
    return `<article class="card">
      <div class="muted">${fmtDate(l.date)}${l.minutes ? ` · ${esc(l.minutes)} min` : ''}</div>
      <h3><a href="${esc(l.path)}">${esc(l.title)}</a></h3>${tagHtml(l.tags)}
      ${l.summary ? `<p>${esc(l.summary)}</p>` : ''}
      ${opts.cta ? `<div class="row"><a class="btn primary" href="${esc(l.path)}">Start lesson</a></div>` : ''}
    </article>`;
  }
  // Streak: consecutive days (ending today or yesterday) with a published lesson that was opened/marked
  function streak(lessons) {
    const days = new Set(lessons.map(l => l.date));
    let d = new Date(todayISO() + 'T12:00:00'), n = 0;
    if (!days.has(todayISO())) d.setDate(d.getDate() - 1);
    while (days.has(d.toISOString().slice(0,10))) { n++; d.setDate(d.getDate() - 1); }
    return n;
  }
  // ---- Spaced repetition (SM-2 variant) ----
  const KEY = 'dal.srs.v1';
  const loadSRS = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } };
  const saveSRS = s => localStorage.setItem(KEY, JSON.stringify(s));
  const cardId = (l, i) => `${l.slug || l.path}#${i}`;
  function schedule(st, grade) { // grade: 0 again,1 hard,2 good,3 easy
    st = Object.assign({ef: 2.5, interval: 0, reps: 0, lapses: 0}, st || {});
    const q = [1, 3, 4, 5][grade];
    if (grade === 0) { st.reps = 0; st.lapses++; st.interval = 0; }
    else {
      st.reps++;
      if (st.reps === 1) st.interval = grade === 3 ? 3 : 1;
      else if (st.reps === 2) st.interval = grade === 1 ? 3 : 6;
      else st.interval = Math.round(st.interval * (grade === 1 ? 1.2 : st.ef * (grade === 3 ? 1.3 : 1)));
    }
    st.ef = Math.max(1.3, st.ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)));
    const due = new Date(); due.setDate(due.getDate() + st.interval);
    st.due = grade === 0 ? Date.now() + 60e3 : due.setHours(0,0,0,0);
    st.last = Date.now();
    return st;
  }
  const preview = (st, g) => { const i = schedule(st, g).interval; return g === 0 ? '<1m' : i + 'd'; };
  return {esc, loadLessons, todayISO, fmtDate, tagHtml, lessonCard, streak, loadSRS, saveSRS, cardId, schedule, preview};
})();
