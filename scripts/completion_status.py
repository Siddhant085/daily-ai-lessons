#!/usr/bin/env python3
"""Print lesson completion status as JSON (issues 'complete: <slug>' via gh + data/completions.json)."""
import json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "Siddhant085/daily-ai-lessons"; SITE = "https://siddhant085.github.io/daily-ai-lessons/"
lessons = json.loads((ROOT / "data/lessons.json").read_text())["lessons"]
done = {}
r = subprocess.run(["gh", "issue", "list", "-R", REPO, "--state", "all", "--limit", "1000", "--search", "complete: in:title",
                    "--json", "title,createdAt,state"], capture_output=True, text=True)
errors = [] if r.returncode == 0 else [r.stderr.strip()]
for i in (json.loads(r.stdout) if r.returncode == 0 else []):
    m = re.match(r"\s*complete:\s*(\S+)", i["title"], re.I)
    if m: done.setdefault(m.group(1), i["createdAt"])
cf = ROOT / "data/completions.json"
if cf.exists():
    for s in json.loads(cf.read_text()).get("completed", []):
        done.setdefault(s if isinstance(s, str) else s["slug"], "completions.json")
inc = [{"slug": l["slug"], "date": l["date"], "title": l["title"], "url": SITE + l["path"]} for l in lessons if l["slug"] not in done]
total = len(lessons); comp = total - len(inc)
out = {"total": total, "completed": comp, "percent": round(100 * comp / total, 1) if total else 0.0,
       "completed_slugs": sorted(s for s in done if any(l["slug"] == s for l in lessons)), "incomplete": inc}
if errors: out["errors"] = errors
print(json.dumps(out, indent=2))
