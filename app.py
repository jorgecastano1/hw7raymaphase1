"""
HW7 Phase 1 - Pac-Man Starter (pygame)

Design goals for Phase 1:
1) Keep the code easy to read for handoff.
2) Build a runnable core loop with basic mechanics.
3) Clearly mark what is done vs what remains for Phase 2.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame


# =============================
# CONFIGURATION
# =============================
TILE_SIZE = 32
FPS = 60
GHOST_MOVE_DELAY_MS = 180
PACMAN_MOVE_DELAY_MS = 220  # continuous movement interval (higher = slower)

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
# Layout: loops and through-corridors; fewer dead ends
LEVEL_MAP = [
    "###############",
    "#P............#",
    "#.##########.#",
    "#............#",
    "#.##......##.#",
    "#.....##.....#",
    "#.##.....##.#",
    "#.....##.....#",
    "#.##......##.#",
    "#............#",
    "#.##########.#",
    "#...........G.#",
    "###############",
]


# Movement vectors in tile space
DIRECTIONS = {
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP": (0, -1),
    "DOWN": (0, 1),
}

# Font (optional): use for nicer lettering when available
_FONT: pygame.font.Font | None = None
_FONT_LARGE: pygame.font.Font | None = None


def _init_fonts() -> None:
    global _FONT, _FONT_LARGE
    try:
        pygame.font.init()
        for name in ("Arial", "Helvetica", "Sans", None):
            try:
                _FONT = pygame.font.SysFont(name, 24) if name else pygame.font.Font(None, 28)
                _FONT_LARGE = pygame.font.SysFont(name, 38) if name else pygame.font.Font(None, 42)
                break
            except Exception:
                continue
        else:
            _FONT = _FONT_LARGE = None
    except Exception:
        _FONT = _FONT_LARGE = None


def _draw_text(surface: pygame.Surface, text: str, x: int, y: int, color: tuple[int, int, int], font: pygame.font.Font | None = None, center: bool = False) -> None:
    """Draw text when font is available; otherwise no-op."""
    f = font or _FONT
    if f is None:
        return
    img = f.render(text, True, color)
    if center:
        r = img.get_rect(center=(x, y))
    else:
        r = img.get_rect(topleft=(x, y))
    surface.blit(img, r)


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


LIVES_START = 3


@dataclass
class GameState:
    """All mutable state in one place to simplify handoff."""

    running: bool = True
    game_over: bool = False
    win: bool = False
    started: bool = False  # False until player presses key on start screen
    score: int = 0
    total_pellets: int = 0
    pellets_eaten: int = 0
    lives: int = LIVES_START

    pacman_pos: tuple[int, int] = (1, 1)
    ghost_pos: tuple[int, int] = (1, 1)
    pacman_spawn: tuple[int, int] = (1, 1)
    ghost_spawn: tuple[int, int] = (1, 1)

    # Continuous movement: key sets facing, Pac-Man auto-moves every PACMAN_MOVE_DELAY_MS
    pending_move: tuple[int, int] | None = None
    pacman_facing: tuple[int, int] = (-1, 0)  # start left
    ghost_dir: tuple[int, int] = (0, 0)

    last_pacman_move_ms: int = 0
    last_ghost_move_ms: int = 0
    anim_frame: int = 0  # for mouth open/close


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
                state.pacman_spawn = (x, y)
                state.pacman_facing = DIRECTIONS["LEFT"]  # start moving left
                grid[y][x] = " "
            elif cell == "G":
                state.ghost_pos = (x, y)
                state.ghost_spawn = (x, y)
                state.ghost_dir = random.choice(list(DIRECTIONS.values()))
                grid[y][x] = " "
            elif cell == ".":
                state.total_pellets += 1

    state.lives = LIVES_START
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


def handle_input(state: GameState) -> bool:
    """
    Handle key presses and quit events.
    Returns True if the player requested a full restart (R when game over).
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
            return False
        if event.type != pygame.KEYDOWN:
            continue
        # Restart on R when game over
        if state.game_over and event.key == pygame.K_r:
            return True
        # Start screen: any key starts the game
        if not state.started:
            state.started = True
            return False
        if state.game_over:
            continue
        if event.key in (pygame.K_LEFT, pygame.K_a):
            state.pending_move = DIRECTIONS["LEFT"]
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            state.pending_move = DIRECTIONS["RIGHT"]
        elif event.key in (pygame.K_UP, pygame.K_w):
            state.pending_move = DIRECTIONS["UP"]
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            state.pending_move = DIRECTIONS["DOWN"]
    return False


def update_pacman(grid: list[list[str]], state: GameState, now_ms: int) -> None:
    """
    Continuous movement: key press only changes facing when that direction is not into a wall.
    Pac-Man can only turn into a valid tile; he stops only by moving straight into a wall.
    Every PACMAN_MOVE_DELAY_MS we move one tile in the current facing direction.
    """
    if state.pending_move is not None:
        # Only allow turn if the new direction leads to a non-wall (can't turn into wall to stop)
        if try_move(state.pacman_pos, state.pending_move, grid) != state.pacman_pos:
            state.pacman_facing = state.pending_move
        state.pending_move = None

    if now_ms - state.last_pacman_move_ms < PACMAN_MOVE_DELAY_MS:
        return
    state.last_pacman_move_ms = now_ms

    new_pos = try_move(state.pacman_pos, state.pacman_facing, grid)
    if new_pos != state.pacman_pos:
        state.pacman_pos = new_pos
        state.anim_frame = (state.anim_frame + 1) % 4

    x, y = state.pacman_pos
    if grid[y][x] == ".":
        grid[y][x] = " "
        state.score += 10
        state.pellets_eaten += 1


def _reverse_dir(d: tuple[int, int]) -> tuple[int, int]:
    return (-d[0], -d[1])


def _valid_directions(ghost_pos: tuple[int, int], grid: list[list[str]], avoid_reverse_of: tuple[int, int] | None) -> list[tuple[int, int]]:
    """All directions that are not walls. If avoid_reverse_of is set, exclude that reverse unless it's the only option."""
    valid = [d for d in DIRECTIONS.values() if try_move(ghost_pos, d, grid) != ghost_pos]
    if avoid_reverse_of is None or len(valid) <= 1:
        return valid
    rev = _reverse_dir(avoid_reverse_of)
    no_reverse = [d for d in valid if d != rev]
    return no_reverse if no_reverse else valid


def _direction_toward(ghost_pos: tuple[int, int], target: tuple[int, int], grid: list[list[str]], exclude_reverse_of: tuple[int, int] | None = None) -> tuple[int, int] | None:
    """Pick a direction that gets the ghost closer to target. Optionally exclude 180° reversal to avoid bounce."""
    tx, ty = target
    best_dir = None
    best_dist = float("inf")
    candidates = _valid_directions(ghost_pos, grid, exclude_reverse_of)
    for direction in candidates:
        nx, ny = try_move(ghost_pos, direction, grid)
        if (nx, ny) == ghost_pos:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        if dist < best_dist:
            best_dist = dist
            best_dir = direction
    return best_dir


def update_ghost(grid: list[list[str]], state: GameState, now_ms: int) -> None:
    """
    Ghost logic: chase Pac-Man when possible. Never reverse 180° unless in a dead end (reduces stuck/bounce).
    """
    if now_ms - state.last_ghost_move_ms < GHOST_MOVE_DELAY_MS:
        return

    state.last_ghost_move_ms = now_ms

    # Prefer chase direction, but never pick the reverse of current (avoids bounce in corridors)
    chase_dir = _direction_toward(state.ghost_pos, state.pacman_pos, grid, exclude_reverse_of=state.ghost_dir)
    if chase_dir is not None:
        if random.random() < 0.85:
            state.ghost_dir = chase_dir
        else:
            valid_dirs = _valid_directions(state.ghost_pos, grid, avoid_reverse_of=state.ghost_dir)
            if valid_dirs:
                state.ghost_dir = random.choice(valid_dirs)
    else:
        # Current direction blocked or no chase option: pick new direction without reversing if possible
        candidate = try_move(state.ghost_pos, state.ghost_dir, grid)
        if candidate == state.ghost_pos:
            valid_dirs = _valid_directions(state.ghost_pos, grid, avoid_reverse_of=state.ghost_dir)
            if valid_dirs:
                state.ghost_dir = random.choice(valid_dirs)

    state.ghost_pos = try_move(state.ghost_pos, state.ghost_dir, grid)


def check_end_conditions(grid: list[list[str]], state: GameState) -> None:
    """Detect ghost collision (lose a life or game over) or win (all pellets eaten)."""
    if state.pacman_pos == state.ghost_pos:
        state.lives -= 1
        if state.lives <= 0:
            state.game_over = True
            state.win = False
            return
        # Respawn
        state.pacman_pos = state.pacman_spawn
        state.pacman_facing = DIRECTIONS["LEFT"]
        state.ghost_pos = state.ghost_spawn
        state.ghost_dir = random.choice(list(DIRECTIONS.values()))
        state.pending_move = None
        return

    if state.pellets_eaten >= state.total_pellets:
        state.game_over = True
        state.win = True


WALL_THICKNESS = 6  # thickness of wall boundary lines (connected outline)

def _is_wall(grid: list[list[str]], x: int, y: int) -> bool:
    """True if (x,y) is inside grid and is a wall."""
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
        return True
    return grid[y][x] == "#"


def draw_grid(surface: pygame.Surface, grid: list[list[str]]) -> None:
    """Draw pellets and walls. Walls are drawn as connected thick boundaries (no gaps)."""
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            if cell == ".":
                cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
                pygame.draw.circle(surface, PELLET_COLOR, (cx, cy), 4)

    # Draw wall boundaries: for each wall cell, draw edges that face a non-wall (connects into one outline)
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell != "#":
                continue
            px, py = x * TILE_SIZE, y * TILE_SIZE
            h = WALL_THICKNESS // 2
            # Left edge (draw when neighbor left is not wall)
            if not _is_wall(grid, x - 1, y):
                pygame.draw.rect(surface, WALL_COLOR, (px - h, py - h, WALL_THICKNESS, TILE_SIZE + WALL_THICKNESS))
            # Right edge
            if not _is_wall(grid, x + 1, y):
                pygame.draw.rect(surface, WALL_COLOR, (px + TILE_SIZE - h, py - h, WALL_THICKNESS, TILE_SIZE + WALL_THICKNESS))
            # Top edge
            if not _is_wall(grid, x, y - 1):
                pygame.draw.rect(surface, WALL_COLOR, (px - h, py - h, TILE_SIZE + WALL_THICKNESS, WALL_THICKNESS))
            # Bottom edge
            if not _is_wall(grid, x, y + 1):
                pygame.draw.rect(surface, WALL_COLOR, (px - h, py + TILE_SIZE - h, TILE_SIZE + WALL_THICKNESS, WALL_THICKNESS))


def draw_pacman(surface: pygame.Surface, tile_pos: tuple[int, int], facing: tuple[int, int], anim_frame: int) -> None:
    """Draw Pac-Man with direction-facing and mouth open/close animation."""
    x, y = tile_pos
    cx = x * TILE_SIZE + TILE_SIZE // 2
    cy = y * TILE_SIZE + TILE_SIZE // 2
    r = TILE_SIZE // 2 - 3
    pygame.draw.circle(surface, PACMAN_COLOR, (cx, cy), r)
    # Mouth: wedge in facing direction; opening cycles with anim_frame (0=wide, 3=nearly closed)
    mouth_open = 0.6 - (anim_frame % 4) * 0.12  # radians
    angle_center = math.atan2(facing[1], facing[0])
    a1 = angle_center - mouth_open
    a2 = angle_center + mouth_open
    pts = [(cx, cy), (cx + r * math.cos(a1), cy + r * math.sin(a1)), (cx + r * math.cos(a2), cy + r * math.sin(a2))]
    pygame.draw.polygon(surface, BG_COLOR, pts)


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


def draw_start_screen(surface: pygame.Surface, map_width: int, map_height: int, hud_height: int) -> None:
    """Draw start screen with title and instruction."""
    overlay = pygame.Surface((map_width, map_height + hud_height))
    overlay.set_alpha(220)
    overlay.fill(BG_COLOR)
    surface.blit(overlay, (0, 0))
    cx = map_width // 2
    bar_y = (map_height + hud_height) // 2 - 40
    # Title area
    pygame.draw.rect(surface, PACMAN_COLOR, (cx - 130, bar_y, 260, 36), border_radius=10)
    pygame.draw.rect(surface, (30, 30, 50), (cx - 124, bar_y + 4, 248, 28), border_radius=8)
    _draw_text(surface, "PAC-MAN", cx, bar_y + 18, PACMAN_COLOR, _FONT_LARGE, center=True)
    _draw_text(surface, "Press any key to start", cx, bar_y + 52, TEXT_COLOR, center=True)
    pygame.draw.circle(surface, (120, 255, 120), (cx, bar_y + 82), 10)


def draw_hud(surface: pygame.Surface, state: GameState, hud_height: int, map_width: int) -> None:
    """Clean HUD: one bar, three equal sections with dividers."""
    # Background and top border
    hud_rect = pygame.Rect(0, 0, map_width, hud_height)
    pygame.draw.rect(surface, (18, 18, 28), hud_rect)
    pygame.draw.line(surface, (50, 50, 70), (0, 0), (map_width, 0), 2)
    pygame.draw.line(surface, (60, 60, 90), (0, hud_height - 1), (map_width, hud_height - 1), 1)

    pellets_left = max(0, state.total_pellets - state.pellets_eaten)
    section_w = map_width // 3
    mid_y = hud_height // 2
    label_y = 6
    value_y = 24

    # Section 1: Score (center of first third)
    cx1 = section_w // 2
    _draw_text(surface, "SCORE", cx1, label_y, (130, 130, 150), center=True)
    if _FONT:
        _draw_text(surface, str(state.score), cx1, value_y, TEXT_COLOR, center=True)
    else:
        draw_number(surface, state.score, cx1 - 20, value_y - 4, TEXT_COLOR)

    # Vertical divider
    pygame.draw.line(surface, (45, 45, 65), (section_w, 8), (section_w, hud_height - 8), 1)
    # Section 2: Lives (center of second third)
    cx2 = section_w + section_w // 2
    _draw_text(surface, "LIVES", cx2, label_y, (130, 130, 150), center=True)
    life_icon_spacing = 20
    start_x = cx2 - (state.lives - 1) * life_icon_spacing // 2
    for i in range(state.lives):
        pygame.draw.circle(surface, PACMAN_COLOR, (start_x + i * life_icon_spacing, value_y + 6), 6)
    # Vertical divider
    pygame.draw.line(surface, (45, 45, 65), (2 * section_w, 8), (2 * section_w, hud_height - 8), 1)
    # Section 3: Pellets (center of third third)
    cx3 = 2 * section_w + section_w // 2
    _draw_text(surface, "PELLETS", cx3, label_y, (130, 130, 150), center=True)
    if _FONT:
        _draw_text(surface, str(pellets_left), cx3, value_y, TEXT_COLOR, center=True)
    else:
        draw_number(surface, pellets_left, cx3 - 20, value_y - 4, TEXT_COLOR)

    # Status dot (far right)
    if state.game_over and state.win:
        c = (100, 220, 120)
    elif state.game_over and not state.win:
        c = (220, 100, 100)
    else:
        c = (100, 150, 220)
    pygame.draw.circle(surface, c, (map_width - 16, mid_y), 6)


def draw_game_over_overlay(surface: pygame.Surface, map_width: int, map_height: int, hud_height: int, win: bool) -> None:
    """Draw game over / win message and restart hint."""
    overlay = pygame.Surface((map_width, map_height + hud_height))
    overlay.set_alpha(200)
    overlay.fill(BG_COLOR)
    surface.blit(overlay, (0, 0))
    cx = map_width // 2
    cy = (map_height + hud_height) // 2
    if win:
        _draw_text(surface, "YOU WIN!", cx, cy - 24, (120, 255, 140), _FONT_LARGE, center=True)
    else:
        _draw_text(surface, "GAME OVER", cx, cy - 24, (255, 120, 120), _FONT_LARGE, center=True)
    _draw_text(surface, "Press R to restart", cx, cy + 12, TEXT_COLOR, center=True)


def main() -> None:
    pygame.init()
    _init_fonts()

    grid, state = load_level()
    map_width = len(grid[0]) * TILE_SIZE
    map_height = len(grid) * TILE_SIZE
    hud_height = 42

    screen = pygame.display.set_mode((map_width, map_height + hud_height))
    pygame.display.set_caption("HW7 Phase 1 - Pac-Man Starter")

    clock = pygame.time.Clock()

    while state.running:
        now_ms = pygame.time.get_ticks()

        reset_requested = handle_input(state)
        if reset_requested:
            grid, state = load_level()
            continue

        if not state.game_over and state.started:
            update_pacman(grid, state, now_ms)
            update_ghost(grid, state, now_ms)
            check_end_conditions(grid, state)

        pellets_left = state.total_pellets - state.pellets_eaten
        status = "RUNNING"
        if not state.started:
            status = "Press any key to start"
        elif state.game_over and state.win:
            status = "YOU WIN - Press R to restart"
        elif state.game_over and not state.win:
            status = "GAME OVER - Press R to restart"
        pygame.display.set_caption(
            f"HW7 Pac-Man | Score: {state.score} | Pellets: {pellets_left} | Lives: {state.lives} | {status}"
        )

        screen.fill(BG_COLOR)

        # Draw gameplay area on a translated surface
        game_surface = screen.subsurface((0, hud_height, map_width, map_height))
        game_surface.fill(BG_COLOR)
        draw_grid(game_surface, grid)
        draw_pacman(game_surface, state.pacman_pos, state.pacman_facing, state.anim_frame)
        draw_ghost(game_surface, state.ghost_pos)

        if not state.started:
            draw_start_screen(screen, map_width, map_height, hud_height)
        else:
            draw_hud(screen, state, hud_height, map_width)
            if state.game_over:
                draw_game_over_overlay(screen, map_width, map_height, hud_height, state.win)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
