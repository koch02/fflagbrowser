import argparse
import curses
import random
import time

WORDS = [
    "apple",
    "banana",
    "cherry",
    "dragon",
    "elephant",
    "frog",
    "galaxy",
    "honey",
    "island",
    "jungle",
    "keyboard",
    "lemon",
    "mountain",
    "nebula",
    "ocean",
    "python",
    "quantum",
    "rocket",
    "sunshine",
    "tiger",
    "umbrella",
    "violet",
    "whisper",
    "xylophone",
    "yogurt",
    "zephyr",
]

TICK_RATE = 0.5


class FallingWord:
    """Represents a word falling down the screen."""

    def __init__(self, text: str, x: int):
        self.text = text
        self.x = x
        self.y = 0

    def step(self) -> None:
        """Move the word one row down."""
        self.y += 1


def run(screen: "curses._CursesWindow", tick: float) -> None:
    """Main game loop executed within the curses wrapper."""

    curses.curs_set(0)
    screen.nodelay(True)
    height, width = screen.getmaxyx()

    buffer = ""
    words: list[FallingWord] = []
    score = 0
    rng = random.Random()

    while True:
        # Spawn new word with some probability
        if rng.random() < 0.3:
            text = rng.choice(WORDS)
            x = rng.randint(0, max(0, width - len(text) - 1))
            words.append(FallingWord(text, x))

        # Read user input
        try:
            ch = screen.getch()
        except curses.error:
            ch = -1

        if ch != -1:
            if ch in (10, 13, 32):  # Enter or space submits the buffer
                if buffer:
                    remaining: list[FallingWord] = []
                    for w in words:
                        if w.text == buffer:
                            score += len(w.text)
                        else:
                            remaining.append(w)
                    words = remaining
                    buffer = ""
            elif ch in (27, ord("q")):
                return
            elif ch in (8, 127, curses.KEY_BACKSPACE):
                buffer = buffer[:-1]
            elif 32 <= ch <= 126:
                buffer += chr(ch)

        # Move words
        for w in words:
            w.step()
            if w.y >= height - 1:
                screen.clear()
                screen.addstr(
                    height // 2, max(0, (width - len("Game Over")) // 2), "Game Over"
                )
                screen.addstr(
                    height // 2 + 1,
                    max(0, (width - len(f"Score: {score}")) // 2),
                    f"Score: {score}",
                )
                screen.nodelay(False)
                screen.getch()
                return

        # Draw everything
        screen.clear()
        for w in words:
            # Protect against words going off screen horizontally
            if 0 <= w.y < height:
                screen.addstr(w.y, w.x, w.text)
        screen.addstr(height - 1, 0, buffer)
        screen.addstr(0, 0, f"Score: {score}")
        screen.refresh()
        time.sleep(tick)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Type falling words before they reach the bottom."
    )
    parser.add_argument(
        "--tick",
        type=float,
        default=TICK_RATE,
        help="Seconds between each falling step (default: %(default)s)",
    )
    args = parser.parse_args()
    curses.wrapper(run, args.tick)


if __name__ == "__main__":
    main()
