import tkinter as tk
from tkinter import messagebox, ttk
import glob, os, threading, time

from map_loader import load_map
from utils import Board, Vehicle
from solver.bfs import bfs
from solver.dfs import dfs
from solver.ucs import ucs
from solver.astar import astar

CELL_SIZE = 80  # pixels per grid cell

class RushHourApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rush Hour")

        # Detect available level files map1.json ... mapN.json
        files = glob.glob(os.path.join('maps', 'map*.json'))
        self.levels = sorted(
            [int(os.path.splitext(os.path.basename(f))[0].replace('map',''))
             for f in files]
        )

        # Prepare three frames for Main, Select Level, and Game
        self.frame_main   = tk.Frame(self.root)
        self.frame_select = tk.Frame(self.root)
        self.frame_game   = tk.Frame(self.root)

        # Build UI for each frame
        self._build_main_menu()
        self._build_level_select()
        self._build_game_ui()

        # Start with main menu
        self.show_frame(self.frame_main)
        self.root.mainloop()

    def show_frame(self, frame):
        # Hide all frames then show selected one
        for f in (self.frame_main, self.frame_select, self.frame_game):
            f.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    # Main Menu
    def _build_main_menu(self):
        f = self.frame_main
        f.configure(bg='#888888')  # placeholder background
        tk.Label(f, text="RUSH HOUR", font=("Impact", 48), bg='#888888', fg='white')
        tk.Label(f, text="RUSH HOUR", font=("Impact", 48), bg='#888888', fg='white').pack(pady=80)
        tk.Button(f, text="START", font=("Arial", 24), width=10, height=2,
                  bg='#00AA00', fg='white', command=lambda: self.show_frame(self.frame_select)).pack(pady=20)
        tk.Button(f, text="EXIT", font=("Arial", 24), width=10, height=2,
                  bg='#AA0000', fg='white', command=self.root.destroy).pack()

    # Level Select
    def _build_level_select(self):
        f = self.frame_select
        f.configure(bg='#444444')  # dimmed background placeholder

        # Back button
        tk.Button(f, text="← BACK", font=("Arial", 16), bg='#FFFFFF',
                  command=lambda: self.show_frame(self.frame_main)).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # Title
        tk.Label(f, text="SELECT LEVEL", font=("Arial", 32), bg='#444444', fg='white')
        tk.Label(f, text="SELECT LEVEL", font=("Arial", 32), bg='#444444', fg='white').grid(row=0, column=1, columnspan=4, pady=20)

        # Colors from easy to hard
        colors = ['#FFFF66','#FFFF66','#FFFF66','#FFFF66','#FFFF66',
                  '#FFCC33','#FFCC33','#FF9933','#FF3333','#CC0000']

        # Create level buttons
        for idx, lvl in enumerate(self.levels):
            row = idx // 5 + 1
            col = idx % 5
            btn = tk.Button(
                f,
                text=str(lvl),
                font=("Arial", 20, "bold"),
                width=4,
                height=2,
                bg=colors[idx],
                command=lambda L=lvl: self._on_level_selected(L)
            )
            btn.grid(row=row, column=col, padx=20, pady=20)

    def _on_level_selected(self, level):
        # Load map JSON
        path = os.path.join('maps', f'map{level}.json')
        try:
            vehicles = load_map(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load map{level}.json:\n{e}")
            return
        # Current and initial board
        self.board = Board(vehicles)
        self.initial_board = Board({vid: v for vid, v in vehicles.items()})
        self.current_level = level

        # Draw and show
        self.redraw_game()
        self.show_frame(self.frame_game)

    # Game Play
    def _build_game_ui(self):
        f = self.frame_game
        f.configure(bg='#EEEEEE')  # placeholder background

        # Canvas for grid
        self.canvas = tk.Canvas(f, width=6*CELL_SIZE, height=6*CELL_SIZE, bg='#CCCCCC')
        self.canvas.grid(row=0, column=0, columnspan=3, padx=20, pady=20)

        # Back to Level Select
        tk.Button(f, text="← LEVELS", font=("Arial", 14),
                  command=lambda: self.show_frame(self.frame_select)).grid(row=1, column=0, pady=10)

        # Solve button
        tk.Button(f, text="Solve", font=("Arial", 14),
                  command=self._auto_solve).grid(row=1, column=1, pady=10)

        # Algo selector (radiobutton menu)
        self.algo_var = tk.StringVar(value='bfs')
        algo_btn = tk.Menubutton(f, text="Algo", font=("Arial", 14))
        menu = tk.Menu(algo_btn, tearoff=0)
        for a in ['bfs','dfs','ucs','astar']:
            menu.add_radiobutton(label=a.upper(), variable=self.algo_var, value=a)
        algo_btn.config(menu=menu)
        algo_btn.grid(row=1, column=2, pady=10)

    def redraw_game(self):
        # Clear canvas
        self.canvas.delete('all')

        # Draw grid lines
        for i in range(7):
            self.canvas.create_line(0, i*CELL_SIZE, 6*CELL_SIZE, i*CELL_SIZE)
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, 6*CELL_SIZE)

        # Draw vehicles
        for v in self.board.vehicles.values():
            x0 = v.col * CELL_SIZE
            y0 = v.row * CELL_SIZE
            w = (v.length if v.orientation=='H' else 1) * CELL_SIZE
            h = (v.length if v.orientation=='V' else 1) * CELL_SIZE
            color = 'red' if v.id=='X' else 'blue'
            self.canvas.create_rectangle(x0, y0, x0+w, y0+h, fill=color, outline='black')
            self.canvas.create_text(x0 + w/2, y0 + h/2,
                                    text=v.id, fill='white', font=('Arial',14,'bold'))

    def _auto_solve(self):
        # Choose solver based on selection
        funcs = {'bfs': bfs, 'dfs': dfs, 'ucs': ucs, 'astar': astar}
        solver = funcs[self.algo_var.get()]

        # Solve using initial board
        path = solver(self.initial_board)
        if not path:
            messagebox.showinfo("No Solution", "Cannot solve level.")
            return

        # Reset to initial
        self.board = Board({vid: v for vid, v in self.initial_board.vehicles.items()})
        self.redraw_game()

        # Animate solution
        def animate():
            for vid, move in path:
                time.sleep(0.3)
                v = self.board.vehicles[vid]
                if v.orientation=='H':
                    new_r, new_c = v.row, v.col + move
                else:
                    new_r, new_c = v.row + move, v.col
                self.board.vehicles[vid] = Vehicle(v.id, v.orientation, new_r, new_c, v.length)
                self.redraw_game()
            messagebox.showinfo("Solved", "Done!")
            self.show_frame(self.frame_select)

        threading.Thread(target=animate).start()

if __name__ == '__main__':
    RushHourApp()
