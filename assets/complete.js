// Mark-complete: localStorage + prefilled GitHub issue ("complete: <slug>") readable by gh.
(() => {
  const REPO = 'Siddhant085/daily-ai-lessons', KEY = 'dal.complete.v1';
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } };
  const save = s => localStorage.setItem(KEY, JSON.stringify(s));
  const issueURL = slug => `https://github.com/${REPO}/issues/new?` + new URLSearchParams({
    title: `complete: ${slug}`, labels: 'complete', body: `Marked complete from the site on ${new Date().toISOString()}`});
  async function remote(base) { // merge: data/completions.json + public issues API
    const out = {};
    try { const j = await (await fetch(base + 'data/completions.json', {cache: 'no-cache'})).json();
      (j.completed || []).forEach(s => out[typeof s === 'string' ? s : s.slug] = 1); } catch {}
    try { const j = await (await fetch(`https://api.github.com/repos/${REPO}/issues?labels=complete&state=all&per_page=100`)).json();
      (Array.isArray(j) ? j : []).forEach(i => { const m = /^complete:\s*(\S+)/i.exec(i.title); if (m) out[m[1]] = 1; }); } catch {}
    return out;
  }
  async function all(base) { return Object.assign({}, await remote(base), load()); }
  function mark(slug) { const s = load(); s[slug] = Date.now(); save(s); window.open(issueURL(slug), '_blank'); }
  function unmark(slug) { const s = load(); delete s[slug]; save(s); }
  window.DALComplete = {load, all, mark, unmark, issueURL};
  // Lesson page: inject button
  const m = /lessons\/\d{4}-\d{2}-\d{2}-(.+)\.html/.exec(location.pathname);
  if (!m) return;
  const slug = m[1];
  const box = document.createElement('div'); box.id = 'dal-complete';
  box.style.cssText = 'position:fixed;right:14px;bottom:14px;z-index:9999;font:600 16px system-ui,sans-serif';
  const b = document.createElement('button');
  b.style.cssText = 'padding:14px 18px;border:0;border-radius:999px;color:#fff;box-shadow:0 4px 14px #0004;cursor:pointer';
  const render = done => { b.textContent = done ? '✓ Completed' : 'Mark complete'; b.style.background = done ? '#16a34a' : '#2563eb'; b.dataset.done = done ? 1 : ''; };
  b.onclick = () => { if (b.dataset.done) { if (confirm('Re-open the GitHub issue form to record completion again?')) mark(slug); } else { mark(slug); render(true); } };
  box.appendChild(b); document.body.appendChild(box); render(!!load()[slug]);
  all('../').then(s => render(!!s[slug]));
})();
