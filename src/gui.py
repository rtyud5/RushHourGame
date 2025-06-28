import tkinter as tk
from tkinter import messagebox, ttk
import glob, os, threading, time

from map_loader import load_map
from utils import Board, Vehicle
from solver.bfs import bfs
from solver.dfs import dfs
from solver.ucs import ucs
from solver.astar import astar

# Kích thước mỗi ô trên board (6x6)
CELL_SIZE = 80

class RushHourApp:
    def __init__(self):
        # Khởi tạo cửa sổ chính
        self.root = tk.Tk()
        self.root.title("Rush Hour")

        # Tự động phát hiện các file mapN.json trong thư mục maps/
        files = glob.glob(os.path.join('maps', 'map*.json'))
        # levels = [1,2,3,...] dựa trên tên file map1.json -> 1
        self.levels = sorted(
            [int(os.path.splitext(os.path.basename(f))[0].replace('map',''))
             for f in files]
        )

        # Tạo 3 Frame để chuyển đổi giữa các màn hình:
        #  - frame_main: màn hình chính (START / EXIT)
        #  - frame_select: chọn level (1..10)
        #  - frame_game: màn hình chơi/solve
        self.frame_main   = tk.Frame(self.root)
        self.frame_select = tk.Frame(self.root)
        self.frame_game   = tk.Frame(self.root)

        # Xây dựng nội dung từng frame
        self._build_main_menu()
        self._build_level_select()
        self._build_game_ui()

        # Bắt đầu với màn hình chính
        self.show_frame(self.frame_main)
        self.root.mainloop()

    def show_frame(self, frame):
        """
        Ẩn tất cả các frame, chỉ hiển thị frame được truyền vào.
        Giúp chuyển giữa các màn hình.
        """
        for f in (self.frame_main, self.frame_select, self.frame_game):
            f.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    # Màn hình 1: Main Menu
    def _build_main_menu(self):
        f = self.frame_main
        # Thiết lập background
        f.configure(bg='#888888')

        # Tiêu đề game
        tk.Label(
            f,
            text="RUSH HOUR",
            font=("Impact", 48),
            bg='#888888',
            fg='white'
        ).pack(pady=80)

        # Nút START
        tk.Button(
            f,
            text="START",
            font=("Arial", 24),
            width=10, height=2,
            bg='#00AA00', fg='white',
            command=lambda: self.show_frame(self.frame_select)
        ).pack(pady=20)

        # Nút EXIT
        tk.Button(
            f,
            text="EXIT",
            font=("Arial", 24),
            width=10, height=2,
            bg='#AA0000', fg='white',
            command=self.root.destroy
        ).pack()

    # Màn hình 2: Level Select
    def _build_level_select(self):
        f = self.frame_select
        # Nền
        f.configure(bg='#444444')

        # Nút BACK về Main Menu
        tk.Button(
            f,
            text="← BACK",
            font=("Arial", 16),
            bg='#FFFFFF',
            command=lambda: self.show_frame(self.frame_main)
        ).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # Tiêu đề Select Level
        tk.Label(
            f,
            text="SELECT LEVEL",
            font=("Arial", 32),
            bg='#444444',
            fg='white'
        ).grid(row=0, column=1, columnspan=4, pady=20)

        # Tạo nút cho mỗi level (1..10)
        for idx, lvl in enumerate(self.levels):
            # Sắp xếp 2 hàng 5 cột
            r = idx // 5 + 1
            c = idx % 5
            # Màu
            colors = ['#FFFF66','#FFFF66','#FFFF66','#FFFF66','#FFFF66',
                      '#FFCC33','#FFCC33','#FF9933','#FF3333','#CC0000']
            btn = tk.Button(
                f,
                text=str(lvl),
                font=("Arial", 20, "bold"),
                width=4, height=2,
                bg=colors[idx],
                command=lambda L=lvl: self._on_level_selected(L)
            )
            btn.grid(row=r, column=c, padx=20, pady=20)

    def _on_level_selected(self, level):
        """
        Khi người chơi chọn một level:
        1. Load file maps/map{level}.json
        2. Tạo Board hiện tại và bản sao initial_board
        3. Redraw và chuyển sang màn hình chơi
        """
        path = os.path.join('maps', f'map{level}.json')
        try:
            vehicles = load_map(path)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Không load được map{level}.json:\n{e}")
            return

        # Board hiện tại
        self.board = Board(vehicles)
        # Bản sao ban đầu
        self.initial_board = Board({vid: v for vid, v in vehicles.items()})
        self.current_level = level
        # GUI sẽ luôn có thể quay về trạng thái map ban đầu
        self.redraw_game()
        self.show_frame(self.frame_game)

    # Màn hình 3: Game Play
    def _build_game_ui(self):
        f = self.frame_game
        # Nền tạm
        f.configure(bg='#EEEEEE')

        # Canvas để vẽ board (6x6 * CELL_SIZE)
        self.canvas = tk.Canvas(
            f,
            width=6*CELL_SIZE,
            height=6*CELL_SIZE,
            bg='#CCCCCC'
        )
        self.canvas.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

        # Nút LEVELS quay lại màn hình chọn level
        tk.Button(
            f,
            text="← LEVELS",
            font=("Arial", 14),
            command=lambda: self.show_frame(self.frame_select)
        ).grid(row=1, column=0, pady=10)

        # Nút Solve: auto-solve
        tk.Button(
            f,
            text="Solve",
            font=("Arial", 14),
            command=self._auto_solve
        ).grid(row=1, column=1, pady=10)

        # Menu chọn thuật toán (BFS/DFS/UCS/A*)
        btn_algo = tk.Menubutton(f, text="Algo", font=("Arial", 14))
        self.algo_menu = tk.Menu(btn_algo, tearoff=0)
        # Tạo radiobutton cho mỗi thuật toán
        for a in ['bfs','dfs','ucs','astar']:
            self.algo_menu.add_radiobutton(
                label=a.upper(),
                variable=tk.StringVar(value='bfs'),
                value=a,
                command=lambda v=a: setattr(self, 'chosen_algo', v)
            )
        btn_algo.config(menu=self.algo_menu)
        btn_algo.grid(row=1, column=2, pady=10)

        # Mặc định dùng BFS khi không chọn thuật toán nào
        self.chosen_algo = 'bfs'

    def redraw_game(self):
        """
        Vẽ lại toàn bộ board hiện tại lên canvas:
        - Lưới 6x6
        - Các block: màu đỏ cho X, xanh cho các block khác
        - ID block ở giữa
        """
        self.canvas.delete('all')

        # Vẽ lưới
        for i in range(7):
            self.canvas.create_line(0, i*CELL_SIZE, 6*CELL_SIZE, i*CELL_SIZE)
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, 6*CELL_SIZE)

        # Vẽ từng block
        for v in self.board.vehicles.values():
            x0 = v.col * CELL_SIZE
            y0 = v.row * CELL_SIZE
            w = (v.length if v.orientation=='H' else 1) * CELL_SIZE
            h = (v.length if v.orientation=='V' else 1) * CELL_SIZE
            # Màu: đỏ cho X, xanh cho các block còn lại
            color = 'red' if v.id=='X' else 'blue'
            self.canvas.create_rectangle(
                x0, y0, x0+w, y0+h,
                fill=color, outline='black'
            )
            # Vẽ ID block ở giữa
            self.canvas.create_text(
                x0 + w/2, y0 + h/2,
                text=v.id,
                fill='white',
                font=('Arial', 14, 'bold')
            )

    def _auto_solve(self):
        """
        Gọi thuật toán solve được chọn (BFS/DFS/UCS/A*):
        1. Nhận đường đi `path` từ initial_board
        2. Reset board về initial
        3. Animate từng bước với delay
        4. Thông báo khi xong và quay về màn hình chọn level
        """
        # Lấy hàm solver theo self.chosen_algo
        funcs = {'bfs': bfs, 'dfs': dfs, 'ucs': ucs, 'astar': astar}
        solver = funcs[self.chosen_algo]

        # Chạy solve trên initial_board
        path = solver(self.initial_board)
        if not path:
            messagebox.showinfo("No Solution", "Không tìm thấy lời giải.")
            return

        # Reset board trước khi animate
        self.board = Board({vid:v for vid,v in self.initial_board.vehicles.items()})
        self.redraw_game()

        # Hàm con để animate đường đi
        def animate():
            for vid, move in path:
                time.sleep(0.3)  # pause giữa các bước
                v = self.board.vehicles[vid]
                # Tính vị trí mới
                if v.orientation == 'H':
                    new_row, new_col = v.row, v.col + move
                else:
                    new_row, new_col = v.row + move, v.col
                # Cập nhật và vẽ lại
                self.board.vehicles[vid] = Vehicle(
                    v.id, v.orientation, new_row, new_col, v.length
                )
                self.redraw_game()
            # Kết thúc: thông báo và về màn hình chọn level
            messagebox.showinfo("Solved", "Đã giải xong!")
            self.show_frame(self.frame_select)

        # Chạy animation trong thread riêng để không block GUI
        threading.Thread(target=animate).start()

if __name__ == '__main__':
    RushHourApp()
