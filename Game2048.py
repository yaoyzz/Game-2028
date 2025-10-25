import tkinter as tk
import random
import copy

GRID_LEN = 4
TARGET = 2048

def rotate_cw(g):  
    return [list(r) for r in zip(*g[::-1])]

def rotate(g, k):  
    for _ in range(k % 4):
        g = rotate_cw(g)
    return g

class Game2048:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("2048 Game")

        self.score = 0
        self.high_score = 0
        self.history = []
        self.grid = [[0] * GRID_LEN for _ in range(GRID_LEN)]

        self.create_ui()
        self.start_game()
        self.window.mainloop()

    # --- UI ---
    def create_ui(self):
        top = tk.Frame(self.window)
        top.pack()

        self.start_btn = tk.Button(top, text="▶ Start", command=self.start_game)
        self.restart_btn = tk.Button(top, text="⟳ Restart", command=self.restart_game)
        self.undo_btn = tk.Button(top, text="↩ Undo", command=self.undo)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        self.restart_btn.grid(row=0, column=1, padx=5, pady=5)
        self.undo_btn.grid(row=0, column=2, padx=5, pady=5)

        self.score_label = tk.Label(top, text="Score: 0", font=("Arial", 12, "bold"))
        self.high_label = tk.Label(top, text="High: 0", font=("Arial", 12, "bold"))
        self.score_label.grid(row=0, column=3, padx=10)
        self.high_label.grid(row=0, column=4, padx=10)

        self.board = tk.Frame(self.window, bg="gray")
        self.board.pack(pady=10)
        self.cells = []
        for i in range(GRID_LEN):
            row = []
            for j in range(GRID_LEN):
                lbl = tk.Label(self.board, text="", width=6, height=3,
                               font=("Helvetica", 24, "bold"), bg="#ccc0b3",
                               relief="ridge", borderwidth=2)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells.append(row)

        # key bindings
        for key in ["<Key>", "<Up>", "<Down>", "<Left>", "<Right>"]:
            self.window.bind(key, self.key_handler)

    # --- Game Setup ---
    def start_game(self):
        self.grid = [[0] * GRID_LEN for _ in range(GRID_LEN)]
        self.score = 0
        self.history.clear()
        self.add_tile()
        self.add_tile()
        self.update_ui()

    def restart_game(self):
        self.start_game()

    def undo(self):
        if self.history:
            self.grid, self.score = self.history.pop()
            self.update_ui()

    # --- Core Mechanics ---
    def add_tile(self):
        empty = [(i, j) for i in range(GRID_LEN)
                 for j in range(GRID_LEN) if self.grid[i][j] == 0]
        if empty:
            i, j = random.choice(empty)
            self.grid[i][j] = random.choice([2, 4])

    def _compress(self, row):
        vals = [x for x in row if x]
        return vals + [0] * (GRID_LEN - len(vals))

    def _move_left_core(self, g):
        moved, gain = False, 0
        out = []
        for row in g:
            r = self._compress(row)
            for i in range(GRID_LEN - 1):
                if r[i] and r[i] == r[i + 1]:
                    r[i] *= 2
                    gain += r[i]
                    r[i + 1] = 0
            r2 = self._compress(r)
            if r2 != row:
                moved = True
            out.append(r2)
        return out, moved, gain

    def _apply_move(self, direction):
        k = {'left': 0, 'up': 3, 'right': 2, 'down': 1}[direction]
        g_rot = rotate(copy.deepcopy(self.grid), k)

        new_rot, moved, gain = self._move_left_core(g_rot)
        if not moved:
            return

        self.history.append((copy.deepcopy(self.grid), self.score))
        self.grid = rotate(new_rot, 4 - k)
        self.score += gain

        if self.score > self.high_score:
            self.high_score = self.score

        self.add_tile()
        self.update_ui()

        if self.check_win():
            self.game_over("🎉 You reached 2048! You win!")
        elif self.check_lose():
            self.game_over("💀 No more moves. Game Over.")

    # --- State Check ---
    def check_win(self):
        return any(TARGET in row for row in self.grid)

    def check_lose(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                v = self.grid[i][j]
                if v == 0:
                    return False
                if j + 1 < GRID_LEN and v == self.grid[i][j + 1]:
                    return False
                if i + 1 < GRID_LEN and v == self.grid[i + 1][j]:
                    return False
        return True

    # --- UI Update ---
    def update_ui(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                v = self.grid[i][j]
                txt = str(v) if v else ""
                self.cells[i][j].config(text=txt, bg=self.get_color(v))

        self.score_label.config(text=f"Score: {self.score}")
        self.high_label.config(text=f"High: {self.high_score}")

    @staticmethod
    def get_color(v):
        colors = {
            0: "#ccc0b3", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
            16: "#f59563", 32: "#f67c5f", 64: "#f65e3b",
            128: "#edcf72", 256: "#edcc61", 512: "#edc850",
            1024: "#edc53f", 2048: "#edc22e"
        }
        return colors.get(v, "#3c3a32")

    # --- Input ---
    def key_handler(self, event):
        k = event.keysym.lower()
        if k in ['a', 'left']:
            self._apply_move('left')
        elif k in ['d', 'right']:
            self._apply_move('right')
        elif k in ['w', 'up']:
            self._apply_move('up')
        elif k in ['s', 'down']:
            self._apply_move('down')

    # --- End Dialog ---
    def game_over(self, msg):
        top = tk.Toplevel(self.window)
        top.title("Game Over")
        tk.Label(top, text=msg, font=("Arial", 16, "bold")).pack(padx=20, pady=10)
        tk.Button(top, text="Restart", command=lambda: [top.destroy(), self.restart_game()]).pack(side="left", padx=10, pady=10)
        tk.Button(top, text="Exit", command=self.window.destroy).pack(side="right", padx=10, pady=10)

