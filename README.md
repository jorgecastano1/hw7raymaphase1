# HW7 — Phase 1 Pac-Man Starter (pygame)

This repository contains a **Phase 1 handoff** for HW7: a readable, runnable Pac-Man starter built with `pygame`.

## Phase 1 objective
Create a strong starting point (not a finished game) that another student can understand and continue quickly.

## What this starter currently does
- Opens a `pygame` window with a tile-based maze.
- Draws walls, pellets, Pac-Man, and one ghost.
- Supports Pac-Man movement with arrow keys or WASD.
- Uses **one key press = one tile move** control (step-based movement).
- Lets Pac-Man eat pellets (`+10` score per pellet).
- Includes basic ghost movement (simple random valid direction logic).
- Shows score and pellets-left with a **font-free HUD** (works even when `pygame.font` is unavailable).
- Detects game over conditions:
	- lose when ghost collides with Pac-Man,
	- win when all pellets are eaten.

## Project structure
- `app.py` — main game file with clear section headers and TODO notes.
- `prompt_log.md` — AI-assisted development record.
- `.gitignore` — excludes cache and virtual environment artifacts.

---

## Setup and run

### 1) Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
python -m pip install pygame
```

### 3) Run
```bash
python app.py
```

Controls:
- Arrow keys / WASD to move
- Close window to quit

---

## Quick test checklist
1. Game window opens without crash.
2. Press one arrow key once → Pac-Man moves exactly one tile.
3. Eat a pellet → score increases by `10`.
4. Collide with ghost → game over state appears.
5. Eat all pellets → win state appears.

---

## Known environment note (macOS + Python 3.14)
Some pygame builds do not include `pygame.font`.
This project intentionally avoids font dependencies and uses shape-based HUD rendering.
So if font modules are missing, the game still runs normally.

---

## Design decisions (clarity-first)
1. **Single-file layout for Phase 1**: easier handoff for early-stage project.
2. **Sectioned code**: configuration, level data, state, update loop, rendering.
3. **`GameState` dataclass**: centralizes mutable state.
4. **Tile-based movement**: simpler than pixel physics for readability.
5. **Explicit TODOs**: makes Phase 2 extension points obvious.

---

## What remains for Phase 2
- Add smoother Pac-Man animation (mouth open/close, directional facing).
- Implement smarter ghost AI (chase/scatter/frightened modes).
- Add multiple levels and better map loading.
- Add start screen / restart flow / lives system.
- Separate into modules (`entities.py`, `level.py`, `render.py`) if project grows.
- Add basic tests for helper functions (`is_wall`, movement rules).

---

## Handoff notes for the next student
Start with these functions in `app.py`:
1. `update_ghost()` — easiest place to improve gameplay quickly.
2. `draw_pacman()` — add direction-aware and animated sprite behavior.
3. `check_end_conditions()` — extend with lives and restart logic.

Prioritize readability over cleverness and commit in small increments.
