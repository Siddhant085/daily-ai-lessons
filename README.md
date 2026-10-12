# Daily AI Lessons

Mobile-first site for daily interactive AI / computer-use lessons from the Daily AI Tutor bot.
Live: https://siddhant085.github.io/daily-ai-lessons/

- `index.html` — today's lesson, streak, cards due
- `archive.html` — all lessons, search + filter (fundamentals / latest)
- `review.html` — spaced-repetition review (SM-2, stored in `localStorage`, ~10 cards/session: due first, then up to 5 new)
- `lessons/YYYY-MM-DD-<slug>.html` — self-contained lesson files
- `data/lessons.json` — manifest `{ "lessons": [ {date, slug, title, tags, summary, minutes, path, cards:[{q,a,choices?,explanation?}]} ] }`
- `assets/site.css`, `assets/site.js` — shared; vanilla JS, no build step

## Publishing a lesson

```bash
python3 scripts/publish_lesson.py /workspace/daily-lessons/2026-10-12-what-is-an-agent.html \
  --title "What is an AI agent?" --tags fundamentals \
  --summary "Agents = model + tools + loop." --minutes 15 --cards cards.json
```

- Date and slug come from the filename (`YYYY-MM-DD-<slug>.html`) or `--date` / `--slug`.
- `--title` defaults to the lesson's `<title>`. `--tags` is comma-separated (`fundamentals`, `latest`, ...).
- `cards.json` is a list: `[{"q": "...", "a": "...", "choices": ["...", "..."], "explanation": "..."}]`.
  For multiple choice, `a` must equal one of the `choices` (or be its index).
- The script copies the file into `lessons/`, injects a Home/Archive/Review nav bar if missing,
  upserts `data/lessons.json`, commits, pulls --rebase, and pushes. `--no-push` / `--no-git` skip those steps.
