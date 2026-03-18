"""
HW7 Phase 1 starter

Purpose:
- Provide a clear, readable starting point for a simple CLI game.
- Emphasize handoff quality over completeness.
"""

from dataclasses import dataclass


@dataclass
class GameState:
    """Holds the current game state."""
    score: int = 0
    turn: int = 0
    running: bool = True


def print_welcome() -> None:
    print("\n=== HW7 Starter Game (Phase 1) ===")
    print("Type 'help' to see commands.\n")


def print_help() -> None:
    print("Available commands:")
    print("  play   - run one placeholder game action")
    print("  status - show current score and turn")
    print("  help   - show this help message")
    print("  quit   - exit the game")


def handle_play_action(state: GameState) -> None:
    """
    Placeholder game mechanic for Phase 1.

    TODO (Phase 2):
    - Replace with real game logic.
    - Add rules, outcomes, and win/lose checks.
    """
    state.turn += 1
    state.score += 10
    print(f"You played turn {state.turn}. +10 points!")


def print_status(state: GameState) -> None:
    print(f"Turn: {state.turn} | Score: {state.score}")


def handle_command(command: str, state: GameState) -> None:
    """Routes user commands to the correct action."""
    if command == "play":
        handle_play_action(state)
    elif command == "status":
        print_status(state)
    elif command == "help":
        print_help()
    elif command == "quit":
        state.running = False
        print("Goodbye.")
    else:
        print("Unknown command. Type 'help' to see valid commands.")


def main() -> None:
    state = GameState()
    print_welcome()
    print_help()

    while state.running:
        user_input = input("\n> ").strip().lower()
        handle_command(user_input, state)


if __name__ == "__main__":
    main()
