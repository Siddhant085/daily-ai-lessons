#!/usr/bin/env python3
"""Publish a Daily AI lesson to the GitHub Pages site.

Usage:
  python3 scripts/publish_lesson.py LESSON.html --title "..." --tags fundamentals \
      --summary "..." --minutes 15 --cards cards.json [--date YYYY-MM-DD] [--slug x] [--no-push]

LESSON.html should be named YYYY-MM-DD-<slug>.html (date/slug inferred) or pass --date/--slug.
--title defaults to the lesson's <title>. --tags accepts comma-separated values.
cards.json: a JSON list of {"q","a","choices"?:[...],"explanation"?}.
Re-publishing the same date+slug replaces the existing entry.

Content rule (see LESSON_GUIDELINES.md): no equation without its variables defined. Every equation
needs a where-list, one-sentence intuition, and a worked example (<div class="where">).
"""
import argparse, datetime, html, json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = "dal-nav"
NAV = (f'<nav id="{MARK}" style="position:sticky;top:0;z-index:9999;display:flex;gap:6px;flex-wrap:wrap;'
       'padding:8px 12px;background:#111827;font:600 15px/1.2 system-ui,sans-serif">'
       + "".join(f'<a href="../{h}" style="color:#e5e7eb;text-decoration:none;padding:10px 12px;border-radius:8px;'
                 f'background:#1f2937">{t}</a>' for h, t in
                 [("", "← Home"), ("archive.html", "Archive"), ("review.html", "Review")])
       + "</nav>")

COMPLETE_MARK = "dal-complete-js"
COMPLETE_TAG = '<script id="dal-complete-js" src="../assets/complete.js"></script>'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson"); ap.add_argument("--title"); ap.add_argument("--tags", default="fundamentals")
    ap.add_argument("--summary", default=""); ap.add_argument("--minutes", type=int, default=15)
    ap.add_argument("--cards"); ap.add_argument("--date"); ap.add_argument("--slug")
    ap.add_argument("--no-push", action="store_true", help="commit but don't push")
    ap.add_argument("--no-git", action="store_true", help="skip commit and push")
    a = ap.parse_args()

    src = pathlib.Path(a.lesson)
    text = src.read_text(encoding="utf-8")
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)$", src.stem)
    date = a.date or (m.group(1) if m else datetime.date.today().isoformat())
    slug = a.slug or (m.group(2) if m else re.sub(r"[^a-z0-9]+", "-", src.stem.lower()).strip("-"))
    datetime.date.fromisoformat(date)
    title = a.title
    if not title:
        t = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
        title = html.unescape(t.group(1)).strip() if t else slug.replace("-", " ").title()
    tags = [t.strip() for t in a.tags.split(",") if t.strip()]
    cards = json.loads(pathlib.Path(a.cards).read_text()) if a.cards else []
    if not isinstance(cards, list) or any(not isinstance(c, dict) or "q" not in c or "a" not in c for c in cards):
        sys.exit("cards.json must be a list of objects with 'q' and 'a'")

    n_eq = len(re.findall(r'<div class="eq[^"]*">.*?</div>|\$\$.+?\$\$', text.split("<script>")[0] if "<body" not in text
                          else text[:text.find("<script>", text.find("<body")) % (len(text) + 1)], re.S))
    n_where = text.count('class="where"')
    if n_where < n_eq:
        print(f"WARNING: {n_eq} equations but only {n_where} 'where' blocks. LESSON_GUIDELINES.md: "
              "no equation without its variables defined.", file=sys.stderr)
    if MARK not in text:
        b = re.search(r"<body[^>]*>", text, re.I)
        text = text[:b.end()] + NAV + text[b.end():] if b else NAV + text
    if COMPLETE_MARK not in text:
        i = text.lower().rfind("</body>")
        text = text[:i] + COMPLETE_TAG + text[i:] if i >= 0 else text + COMPLETE_TAG
    rel = f"lessons/{date}-{slug}.html"
    (ROOT / "lessons").mkdir(exist_ok=True)
    (ROOT / rel).write_text(text, encoding="utf-8")

    mf = ROOT / "data/lessons.json"
    data = json.loads(mf.read_text()) if mf.exists() else {"lessons": []}
    entry = {"date": date, "slug": slug, "title": title, "tags": tags, "summary": a.summary,
             "minutes": a.minutes, "path": rel, "cards": cards}
    data["lessons"] = [l for l in data["lessons"] if l.get("path") != rel] + [entry]
    data["lessons"].sort(key=lambda l: l["date"], reverse=True)
    mf.parent.mkdir(exist_ok=True)
    mf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Published {rel} ({len(cards)} cards)")

    if a.no_git: return
    g = lambda *c: subprocess.run(["git", "-C", str(ROOT), *c], check=True)
    g("add", rel, "data/lessons.json")
    if subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--quiet"]).returncode == 0:
        print("Nothing changed."); return
    g("commit", "-m", f"Lesson {date}: {title}")
    if not a.no_push:
        g("pull", "--rebase", "--autostash"); g("push")
        print("Pushed. Live at https://siddhant085.github.io/daily-ai-lessons/" + rel)

if __name__ == "__main__":
    main()
