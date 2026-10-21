# Lesson guidelines

**Rule: no equation without its variables defined.**

1. Define every symbol and term before or exactly where it first appears. Never assume notation that hasn't been stated.
2. Intuition before math: give the plain-language idea first, then the formula.
3. Build from first principles; introduce notation gradually. Longer math lessons get a notation glossary near the top.
4. Directly beside/under EVERY equation, add a `<div class="where">` block containing:
   - a compact **where:** list giving a plain-language meaning for each symbol (e.g. γ = discount factor, how much future reward counts, between 0 and 1);
   - one sentence of **Intuition** about what the equation says;
   - a small **Worked example** with concrete numbers (e.g. a 3-step trajectory).
5. Every key mechanism (even without an equation) gets a small worked example.
6. Keep content technically correct and cite only real sources.

`scripts/publish_lesson.py` warns when a lesson has equations (`class="eq"` or `$$…$$`) but fewer `class="where"` blocks.
