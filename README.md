# HW7 — Phase 1 Starter (Clear Handoff Version)

This project is a **Phase 1 starter** for HW7.

## Goal of this phase
Build a clean starting point (not a finished game) so another student can continue it easily.

## What I followed from the class slide
1. Start coding with AI help, but keep code readable.
2. Document as you build.
3. Include a clear README: what it is, how to run, what is done, what remains.
4. Commit and push after the in-class phase even if incomplete.
5. Leave clean, understandable code for the next person.

---

## Project structure
- `app.py` — starter game loop + clearly marked TODO sections.
- `prompt_log.md` — development and AI prompt notes.
- `.gitignore` — ignores Python cache/system files.

---

## How to run
From this folder:

```bash
python3 app.py
```

---

## What is completed (Phase 1)
- Basic CLI structure for a small text game.
- `GameState` object to hold score, turn count, and game status.
- Main game loop with command handling.
- Placeholder commands (`status`, `play`, `help`, `quit`) implemented simply.
- Clear comments for handoff.

---

## What remains (for Phase 2)
- Replace placeholder `play` logic with real game mechanics.
- Add win/lose conditions tied to actual rules.
- Add richer content (levels/events/items).
- Improve input validation and user feedback.
- Add tests if required by the assignment.

---

## Handoff notes for the next student
- Start in `app.py` at `handle_play_action()`.
- Expand that function first, then update `print_help()`.
- Keep changes small and commit frequently.
- Preserve readability over cleverness.
