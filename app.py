"""
HW7 Phase 1 - Pac-Man Starter (pygame)

Design goals for Phase 1:
1) Keep the code easy to read for handoff.
2) Build a runnable core loop with basic mechanics.
3) Clearly mark what is done vs what remains for Phase 2.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame


# =============================
# CONFIGURATION
# =============================
TILE_SIZE = 32
FPS = 60
GHOST_MOVE_DELAY_MS = 180

# Colors (kept centralized for readability)
BG_COLOR = (8, 8, 16)
WALL_COLOR = (35, 95, 255)
PELLET_COLOR = (255, 230, 140)
PACMAN_COLOR = (255, 220, 0)
GHOST_COLOR = (255, 80, 80)
TEXT_COLOR = (240, 240, 240)


# =============================
# LEVEL DATA (simple but clear)
# =============================
# # = wall
# . = pellet
# P = pacman spawn
# G = ghost spawn
#   = empty floor
LEVEL_MAP = [
    "###############",
    "#P....#.......#",
    "#.###.#.#####.#",
    "#.....#.....#.#",
    "#.###.###.#.#.#",
    "#...#.....#...#",
    "###.#.###.###.#",
    "#...#...#...#.#",
    "#.#####.#.#.#.#",
    "#.....#.#.#...#",
    "#.###.#.#.###.#",
    "#...#...#...G.#",
    "###############",
]


# Movement vectors in tile space
DIRECTIONS = {
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP": (0, -1),
    "DOWN": (0, 1),
}

# Seven-segment mapping for font-free numeric display
DIGIT_SEGMENTS = {
    "0": (1, 1, 1, 0, 1, 1, 1),
    "1": (0, 0, 1, 0, 0, 1, 0),
    "2": (1, 0, 1, 1, 1, 0, 1),
    "3": (1, 0, 1, 1, 0, 1, 1),
    "4": (0, 1, 1, 1, 0, 1, 0),
    "5": (1, 1, 0, 1, 0, 1, 1),
    "6": (1, 1, 0, 1, 1, 1, 1),
    "7": (1, 0, 1, 0, 0, 1, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}


@dataclass
class GameState:
    """All mutable state in one place to simplify handoff."""

    running: bool = True
    game_over: bool = False
    win: bool = False
    score: int = 0
    total_pellets: int = 0
    pellets_eaten: int = 0

    pacman_pos: tuple[int, int] = (1, 1)
    ghost_pos: tuple[int, int] = (1, 1)

    # Key phase-1 behavior: one key press -> one tile move
    pending_move: tuple[int, int] | None = None
    ghost_dir: tuple[int, int] = (0, 0)

    last_ghost_move_ms: int = 0


def load_level() -> tuple[list[list[str]], GameState]:
    """
    Build a mutable grid from LEVEL_MAP and initialize state.
    This function keeps level parsing logic out of the main loop.
    """
    grid = [list(row) for row in LEVEL_MAP]
    state = GameState()

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == "P":
                state.pacman_pos = (x, y)
                grid[y][x] = " "
            elif cell == "G":
                state.ghost_pos = (x, y)
                state.ghost_dir = random.choice(list(DIRECTIONS.values()))
                grid[y][x] = " "
            elif cell == ".":
                state.total_pellets += 1

    return grid, state


def is_wall(grid: list[list[str]], x: int, y: int) -> bool:
    """Return True if target tile is outside map or a wall."""
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
        return True
    return grid[y][x] == "#"


def try_move(pos: tuple[int, int], direction: tuple[int, int], grid: list[list[str]]) -> tuple[int, int]:
    """Move one tile if destination is not a wall."""
    x, y = pos
    dx, dy = direction
    nx, ny = x + dx, y + dy
    if is_wall(grid, nx, ny):
        return pos
    return nx, ny


def handle_input(state: GameState) -> None:
    """Handle key presses and quit events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
        elif event.type == pygame.KEYDOWN and not state.game_over:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                state.pending_move = DIRECTIONS["LEFT"]
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                state.pending_move = DIRECTIONS["RIGHT"]
            elif event.key in (pygame.K_UP, pygame.K_w):
                state.pending_move = DIRECTIONS["UP"]
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                state.pending_move = DIRECTIONS["DOWN"]
            elif event.key == pygame.K_r and state.game_over:
                # TODO (Phase 2): support full reset without restarting process
                pass


def update_pacman(grid: list[list[str]], state: GameState) -> None:
    """
    Move Pac-Man exactly one tile per key press.
    This makes control behavior explicit and easy to test.
    """
    if state.pending_move is not None:
        state.pacman_pos = try_move(state.pacman_pos, state.pending_move, grid)
        state.pending_move = None

    x, y = state.pacman_pos
    if grid[y][x] == ".":
        grid[y][x] = " "
        state.score += 10
        state.pellets_eaten += 1


def update_ghost(grid: list[list[str]], state: GameState, now_ms: int) -> None:
    """
    Very simple ghost logic for Phase 1.
    - Continue current direction when possible.
    - Otherwise choose a random valid direction.

    TODO (Phase 2): implement chase/scatter behavior.
    """
    if now_ms - state.last_ghost_move_ms < GHOST_MOVE_DELAY_MS:
        return

    state.last_ghost_move_ms = now_ms

    candidate = try_move(state.ghost_pos, state.ghost_dir, grid)
    if candidate == state.ghost_pos:
        valid_dirs = []
        for direction in DIRECTIONS.values():
            if try_move(state.ghost_pos, direction, grid) != state.ghost_pos:
                valid_dirs.append(direction)
        if valid_dirs:
            state.ghost_dir = random.choice(valid_dirs)

    state.ghost_pos = try_move(state.ghost_pos, state.ghost_dir, grid)


def check_end_conditions(state: GameState) -> None:
    """Detect loss (ghost collision) or win (all pellets eaten)."""
    if state.pacman_pos == state.ghost_pos:
        state.game_over = True
        state.win = False
        return

    if state.pellets_eaten >= state.total_pellets:
        state.game_over = True
        state.win = True


def draw_grid(surface: pygame.Surface, grid: list[list[str]]) -> None:
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            px, py = x * TILE_SIZE, y * TILE_SIZE

            if cell == "#":
                rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, WALL_COLOR, rect, border_radius=6)
            elif cell == ".":
                cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
                pygame.draw.circle(surface, PELLET_COLOR, (cx, cy), 4)


def draw_pacman(surface: pygame.Surface, tile_pos: tuple[int, int]) -> None:
    x, y = tile_pos
    cx = x * TILE_SIZE + TILE_SIZE // 2
    cy = y * TILE_SIZE + TILE_SIZE // 2
    pygame.draw.circle(surface, PACMAN_COLOR, (cx, cy), TILE_SIZE // 2 - 3)


def draw_ghost(surface: pygame.Surface, tile_pos: tuple[int, int]) -> None:
    x, y = tile_pos
    rect = pygame.Rect(x * TILE_SIZE + 4, y * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8)
    pygame.draw.rect(surface, GHOST_COLOR, rect, border_radius=8)


def draw_digit(surface: pygame.Surface, digit: str, x: int, y: int, color: tuple[int, int, int]) -> None:
    """Draw one 7-segment digit (font-free)."""
    segments = DIGIT_SEGMENTS.get(digit, DIGIT_SEGMENTS["0"])
    w, h, t = 14, 24, 3

    # A, B, C, D, E, F, G segments
    rects = [
        pygame.Rect(x + t, y, w, t),                 # A
        pygame.Rect(x, y + t, t, h // 2 - t),        # F
        pygame.Rect(x + w + t, y + t, t, h // 2 - t),# B
        pygame.Rect(x + t, y + h // 2, w, t),        # G
        pygame.Rect(x, y + h // 2 + t, t, h // 2 - t),
        pygame.Rect(x + w + t, y + h // 2 + t, t, h // 2 - t),
        pygame.Rect(x + t, y + h - t, w, t),         # D
    ]

    for on, rect in zip(segments, rects):
        if on:
            pygame.draw.rect(surface, color, rect, border_radius=2)


def draw_number(surface: pygame.Surface, value: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    """Draw an integer using multiple 7-segment digits."""
    digits = str(max(0, value))
    cursor_x = x
    for ch in digits:
        draw_digit(surface, ch, cursor_x, y, color)
        cursor_x += 20


def draw_hud(surface: pygame.Surface, state: GameState, hud_height: int, map_width: int) -> None:
    """
    Font-free HUD.
    Some Python/pygame builds do not include pygame.font, so this HUD uses shapes only.
    Detailed values are shown in the window title via pygame.display.set_caption.
    """
    # HUD background strip
    pygame.draw.rect(surface, (20, 20, 32), pygame.Rect(0, 0, map_width, hud_height))

    # Score progress bar based on pellets eaten ratio
    ratio = 0.0
    if state.total_pellets > 0:
        ratio = state.pellets_eaten / state.total_pellets

    bar_x, bar_y = 12, 12
    bar_w, bar_h = 260, 16
    pygame.draw.rect(surface, (60, 60, 80), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(surface, PACMAN_COLOR, pygame.Rect(bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=6)

    # Status indicator on the right
    if state.game_over and state.win:
        indicator_color = (120, 255, 120)
    elif state.game_over and not state.win:
        indicator_color = (255, 120, 120)
    else:
        indicator_color = (120, 190, 255)
    pygame.draw.circle(surface, indicator_color, (map_width - 18, hud_height // 2), 8)

    # Numeric score display (font-free)
    # Yellow icon + score near left-middle
    pygame.draw.circle(surface, PACMAN_COLOR, (300, 20), 6)
    draw_number(surface, state.score, 314, 8, TEXT_COLOR)

    # Pellet count on the right
    pellets_left = max(0, state.total_pellets - state.pellets_eaten)
    pygame.draw.circle(surface, PELLET_COLOR, (440, 20), 4)
    draw_number(surface, pellets_left, 452, 8, TEXT_COLOR)


def main() -> None:
    pygame.init()

    grid, state = load_level()
    map_width = len(grid[0]) * TILE_SIZE
    map_height = len(grid) * TILE_SIZE
    hud_height = 42

    screen = pygame.display.set_mode((map_width, map_height + hud_height))
    pygame.display.set_caption("HW7 Phase 1 - Pac-Man Starter")

    clock = pygame.time.Clock()

    while state.running:
        now_ms = pygame.time.get_ticks()

        handle_input(state)

        if not state.game_over:
            update_pacman(grid, state)
            update_ghost(grid, state, now_ms)
            check_end_conditions(state)

        pellets_left = state.total_pellets - state.pellets_eaten
        status = "RUNNING"
        if state.game_over and state.win:
            status = "YOU WIN"
        elif state.game_over and not state.win:
            status = "GAME OVER"
        pygame.display.set_caption(
            f"HW7 Phase 1 - Pac-Man Starter | Score: {state.score} | Pellets Left: {pellets_left} | {status}"
        )

        screen.fill(BG_COLOR)

        # Draw gameplay area on a translated surface
        game_surface = screen.subsurface((0, hud_height, map_width, map_height))
        game_surface.fill(BG_COLOR)
        draw_grid(game_surface, grid)
        draw_pacman(game_surface, state.pacman_pos)
        draw_ghost(game_surface, state.ghost_pos)

        draw_hud(screen, state, hud_height, map_width)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
