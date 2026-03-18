# HW7 Prompt Log

## Date
March 18, 2026

## AI tools used
- GitHub Copilot (GPT-5.3-Codex)

## Session notes
1. Created HW7 under `/Users/ruizema/clawd/hw7` (correct location).
2. Synced repository with `https://github.com/raymaruize/hw7.git`.
3. Reviewed Phase 1 guideline priorities:
   - clarity over cleverness,
   - document while building,
   - ship a clean starter, not a finished game.
4. Switched project from CLI placeholder to `pygame` Pac-Man starter.
5. Implemented a readable tile-map loop with comments and TODO points for handoff.

## Key prompts used (summary)
- "Create HW7 directly under clawd, not SQLite."
- "Read the phase guideline image and make the project very clear and explicit."
- "Use pygame and start a Pac-Man game that someone else can continue easily."

## What was implemented in this phase
- Pygame window/game loop.
- Tile map parsing (`#`, `.`, `P`, `G`).
- Pac-Man movement and pellet collection.
- One ghost with simple movement logic.
- Score + pellets-left HUD.
- Win/lose detection.
- README updated with setup/run/completed/remaining details.

## TODO handoff markers for next phase
- Improve ghost behavior (chase/scatter).
- Add animation and polish.
- Add restart/lives flow.
- Consider splitting code into modules once mechanics stabilize.
