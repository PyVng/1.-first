"""Simple Snake game with a Tkinter interface."""

from __future__ import annotations

import random
import tkinter as tk
from collections import deque
from typing import Deque, Iterable, Tuple

# Game configuration constants
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
MOVE_DELAY_MS = 120

Direction = Tuple[int, int]
Point = Tuple[int, int]


class SnakeGame:
    """Minimal Snake implementation that runs in a Tkinter window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake")
        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="#202020",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.focus_set()

        self.status = tk.StringVar()
        tk.Label(root, textvariable=self.status, font=("Helvetica", 12)).pack(pady=8)

        self.root.bind("<KeyPress>", self.on_key_press)

        self.after_id: str | None = None
        self.snake: Deque[Point] = deque()
        self.direction: Direction = (1, 0)
        self.pending_direction: Direction = (1, 0)
        self.food: Point | None = None
        self.score = 0
        self.game_over = False

        self.reset()

    def reset(self) -> None:
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = deque([center, (center[0] - 1, center[1]), (center[0] - 2, center[1])])
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.canvas.focus_set()  # Keep keyboard focus on the game canvas
        self.update_status("Use arrow keys. Press Space to restart.")
        self.draw()
        self.schedule_step()

    def spawn_food(self) -> None:
        empty_cells = set(self.iter_grid()) - set(self.snake)
        if not empty_cells:
            self.food = None
            return
        self.food = random.choice(tuple(empty_cells))

    def iter_grid(self) -> Iterable[Point]:
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                yield (x, y)

    def on_key_press(self, event: tk.Event) -> None:
        if event.keysym in ("Up", "Down", "Left", "Right"):
            self.process_direction(event.keysym)
        elif event.keysym == "space" and self.game_over:
            self.reset()

    def process_direction(self, keysym: str) -> None:
        directions = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }
        new_direction = directions[keysym]

        # Prevent the snake from reversing onto itself.
        if self.snake and len(self.snake) > 1:
            opposite = (-self.direction[0], -self.direction[1])
            if new_direction == opposite:
                return

        self.pending_direction = new_direction

    def schedule_step(self) -> None:
        self.after_id = self.root.after(MOVE_DELAY_MS, self.step)

    def step(self) -> None:
        self.after_id = None
        if self.game_over:
            return

        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        next_cell = self.wrap_point((head_x + dx, head_y + dy))

        if next_cell in self.snake:
            self.game_over = True
            self.update_status(f"Game over! Score: {self.score}. Press Space to restart.")
            return

        self.snake.appendleft(next_cell)
        if next_cell == self.food:
            self.score += 1
            self.spawn_food()
        else:
            self.snake.pop()

        if self.food is None:
            self.game_over = True
            self.update_status("You win! Press Space to play again.")
            return

        self.draw()
        self.schedule_step()

    def wrap_point(self, cell: Point) -> Point:
        x, y = cell
        return (x % GRID_WIDTH, y % GRID_HEIGHT)

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_grid()

        for index, (x, y) in enumerate(self.snake):
            color = "#3bd16f" if index == 0 else "#2ea75a"
            self.draw_cell((x, y), color)

        if self.food:
            self.draw_cell(self.food, "#ff6464")

    def draw_grid(self) -> None:
        for x in range(GRID_WIDTH + 1):
            x_pos = x * CELL_SIZE
            self.canvas.create_line(x_pos, 0, x_pos, GRID_HEIGHT * CELL_SIZE, fill="#303030")
        for y in range(GRID_HEIGHT + 1):
            y_pos = y * CELL_SIZE
            self.canvas.create_line(0, y_pos, GRID_WIDTH * CELL_SIZE, y_pos, fill="#303030")

    def draw_cell(self, cell: Point, color: str) -> None:
        x, y = cell
        x0 = x * CELL_SIZE
        y0 = y * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def update_status(self, text: str) -> None:
        self.status.set(text)


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
