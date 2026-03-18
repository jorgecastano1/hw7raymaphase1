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
PACMAN_MOVE_DELAY_MS = 140
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

    pacman_dir: tuple[int, int] = (0, 0)
    ghost_dir: tuple[int, int] = (0, 0)

    last_pacman_move_ms: int = 0
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
                state.pacman_dir = DIRECTIONS["LEFT"]
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                state.pacman_dir = DIRECTIONS["RIGHT"]
            elif event.key in (pygame.K_UP, pygame.K_w):
                state.pacman_dir = DIRECTIONS["UP"]
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                state.pacman_dir = DIRECTIONS["DOWN"]
            elif event.key == pygame.K_r and state.game_over:
                # TODO (Phase 2): support full reset without restarting process
                pass


def update_pacman(grid: list[list[str]], state: GameState, now_ms: int) -> None:
    """Move Pac-Man on a fixed time step and eat pellets."""
    if now_ms - state.last_pacman_move_ms < PACMAN_MOVE_DELAY_MS:
        return

    state.last_pacman_move_ms = now_ms

    if state.pacman_dir != (0, 0):
        state.pacman_pos = try_move(state.pacman_pos, state.pacman_dir, grid)

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


def draw_hud(surface: pygame.Surface, state: GameState, font: pygame.font.Font) -> None:
    score_text = font.render(f"Score: {state.score}", True, TEXT_COLOR)
    pellets_left = state.total_pellets - state.pellets_eaten
    pellets_text = font.render(f"Pellets Left: {pellets_left}", True, TEXT_COLOR)

    surface.blit(score_text, (12, 8))
    surface.blit(pellets_text, (180, 8))

    if state.game_over:
        if state.win:
            message = "YOU WIN!"
            color = (120, 255, 120)
        else:
            message = "GAME OVER"
            color = (255, 120, 120)
        end_text = font.render(message, True, color)
        surface.blit(end_text, (420, 8))


def main() -> None:
    pygame.init()

    grid, state = load_level()
    map_width = len(grid[0]) * TILE_SIZE
    map_height = len(grid) * TILE_SIZE
    hud_height = 42

    screen = pygame.display.set_mode((map_width, map_height + hud_height))
    pygame.display.set_caption("HW7 Phase 1 - Pac-Man Starter")

    font = pygame.font.SysFont("Arial", 22)
    clock = pygame.time.Clock()

    while state.running:
        now_ms = pygame.time.get_ticks()

        handle_input(state)

        if not state.game_over:
            update_pacman(grid, state, now_ms)
            update_ghost(grid, state, now_ms)
            check_end_conditions(state)

        screen.fill(BG_COLOR)

        # Draw gameplay area on a translated surface
        game_surface = screen.subsurface((0, hud_height, map_width, map_height))
        game_surface.fill(BG_COLOR)
        draw_grid(game_surface, grid)
        draw_pacman(game_surface, state.pacman_pos)
        draw_ghost(game_surface, state.ghost_pos)

        draw_hud(screen, state, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
