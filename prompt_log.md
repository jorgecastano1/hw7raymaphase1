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
- Step 2 update: one key press moves Pac-Man exactly one tile.
- One ghost with simple movement logic.
- Score + pellets-left HUD.
- Runtime fix: removed dependency on `pygame.font` and switched to font-free HUD rendering.
- Win/lose detection.
- README updated with setup/run/completed/remaining details.

## TODO handoff markers for next phase
- Improve ghost behavior (chase/scatter).
- Add animation and polish.
- Add restart/lives flow.
- Consider splitting code into modules once mechanics stabilize.

## PHASE 2 PROMPTS

- From this file structure can you do what is necessary to complete the game according to what is in the prompt log and readme
- Great. I noticed that the ghost would get stuck sometimes and bounce in certain areas. Can you also update the lettering throughout the game to look nicer. Also, can you make it so that the pacman moves constantly in whatever direction it is facing. When the game starts have the pacman move left initially.
- how do I run this
- Can you make the pacman go a little slower. Also, there is significant overlap between the items in the hud.
- Also, when pacman is moving, it should not be able to turn into a wall to stop itself. Only if it is along the direction of the hallway should Pacman be able to run into a wall and stop
- Can you update the graphics ? to have thinner walls? Also can you restructure the maze so that there isn't as many deadends
- can you connect the walls, also the hud still looks atrocious
- great. How can I run this to see how it is working so far
- I am receiving the following errors (IndexError in `_is_wall` / `draw_grid` when running `app.py`)
- can you please describe what was added onto from the original code ? Also, how much of the original code was retained
- can you please make a concise bulleted list of the changes made since the first phase
- can you put this under changes made in the readme.md
- can you please make a list of all of the prompts since phase 1 and put them in a bulleted list under PHASE 2 PROMPTS in the prompt_log.md
