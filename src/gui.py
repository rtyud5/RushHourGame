import tkinter as tk
from tkinter import messagebox, ttk
import glob, os, threading, time

from map_loader import load_map
from utils import Board, Vehicle
from solver.bfs import bfs
from solver.dfs import dfs
from solver.ucs import ucs
from solver.astar import astar

# Kích thước mỗi ô trong canvas (80px) để board 6x6 = 480x480px
CELL_SIZE = 80

class RushHourGUI:
    def __init__(self):
        # Khởi tạo cửa sổ chính
        self.root = tk.Tk()
        self.root.title('Rush Hour Solver')

        # Canvas hiển thị board 6x6
        self.canvas = tk.Canvas(
            self.root,
            width=6 * CELL_SIZE,
            height=6 * CELL_SIZE,
            bg='white'
        )
        self.canvas.grid(row=0, column=0, columnspan=6)

        # Chuẩn bị danh sách levels tự động từ file maps/mapN.json
        files = glob.glob(os.path.join('maps', 'map*.json'))
        levels = sorted(
            [os.path.splitext(os.path.basename(f))[0].replace('map', '')
             for f in files],
            key=lambda x: int(x)
        )
        # ComboBox chọn level
        self.level_var = tk.StringVar(value=levels[0] if levels else '')
        ttk.Label(self.root, text='Level:').grid(row=1, column=0, padx=4)
        ttk.Combobox(
            self.root,
            textvariable=self.level_var,
            values=levels,
            state='readonly',
            width=5
        ).grid(row=1, column=1)

        # ComboBox chọn chế độ Manual hoặc Auto
        self.mode_var = tk.StringVar(value='Manual')
        ttk.Label(self.root, text='Mode:').grid(row=1, column=2, padx=4)
        ttk.Combobox(
            self.root,
            textvariable=self.mode_var,
            values=['Manual', 'Auto'],
            state='readonly',
            width=7
        ).grid(row=1, column=3)

        # ComboBox chọn thuật toán khi Auto
        self.algo_var = tk.StringVar(value='bfs')
        ttk.Label(self.root, text='Algo:').grid(row=1, column=4, padx=4)
        ttk.Combobox(
            self.root,
            textvariable=self.algo_var,
            values=['bfs', 'dfs', 'ucs', 'astar'],
            state='readonly',
            width=7
        ).grid(row=1, column=5)

        # Khởi tạo Buttons: Load, Solve, Reset, Quit
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=5)
        ttk.Button(btn_frame, text='Load Level', command=self.load_level).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Solve',      command=self.solve).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Reset',      command=self.redraw).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Quit',       command=self.root.destroy).pack(side='left', padx=5)

        # Biến lưu board hiện tại và board gốc (cho Auto)
        self.board = None
        self.initial_board = None
        # Xe đang chọn (Manual)
        self.selected_id = None

        # Gán sự kiện chuột và phím mũi tên cho Manual mode
        self.canvas.bind('<Button-1>', self.on_click)
        self.root.bind('<Left>',  lambda e: self.try_move(-1,  0))
        self.root.bind('<Right>', lambda e: self.try_move( 1,  0))
        self.root.bind('<Up>',    lambda e: self.try_move( 0, -1))
        self.root.bind('<Down>',  lambda e: self.try_move( 0,  1))

        # Bắt đầu main loop
        self.root.mainloop()

    def load_level(self):
        """
        Load bản đồ từ maps/map{level}.json
        Tạo self.board và self.initial_board để sử dụng cho cả Manual & Auto.
        Reset self.selected_id.
        """
        lvl = self.level_var.get()
        path = os.path.join('maps', f'map{lvl}.json')
        try:
            vehicles = load_map(path)
        except Exception as e:
            messagebox.showerror('Error', f'Không thể load {path}:\n{e}')
            return
        # Khởi tạo board hiện tại và bản sao gốc
        self.board = Board(vehicles)
        self.initial_board = Board({vid: v for vid, v in vehicles.items()})
        self.selected_id = None
        self.redraw()

    def redraw(self):
        """
        Vẽ lại toàn bộ Canvas:
        1. Lưới 6x6
        2. Các block (xe) với màu đỏ cho X và xanh dương cho còn lại
        3. Highlight block được chọn (viền cam)
        """
        self.canvas.delete('all')
        # Vẽ lưới ngang và dọc
        for i in range(7):
            self.canvas.create_line(0, i*CELL_SIZE, 6*CELL_SIZE, i*CELL_SIZE)
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, 6*CELL_SIZE)
        if not self.board:
            return
        # Vẽ các block
        for v in self.board.vehicles.values():
            x0 = v.col * CELL_SIZE
            y0 = v.row * CELL_SIZE
            w = (v.length if v.orientation == 'H' else 1) * CELL_SIZE
            h = (v.length if v.orientation == 'V' else 1) * CELL_SIZE
            color = 'red' if v.id == 'X' else 'skyblue'
            rect = self.canvas.create_rectangle(
                x0, y0, x0 + w, y0 + h,
                fill=color, outline='black', width=2
            )
            # Vẽ chữ id ở giữa block
            self.canvas.create_text(
                x0 + w/2, y0 + h/2,
                text=v.id, font=('Arial', 16, 'bold')
            )
            # Gắn tag theo id để detect click
            self.canvas.itemconfig(rect, tags=(v.id,))
        # Nếu manual mode và có block chọn, highlight
        if self.selected_id:
            v = self.board.vehicles[self.selected_id]
            x0 = v.col * CELL_SIZE
            y0 = v.row * CELL_SIZE
            w = (v.length if v.orientation == 'H' else 1) * CELL_SIZE
            h = (v.length if v.orientation == 'V' else 1) * CELL_SIZE
            self.canvas.create_rectangle(
                x0, y0, x0 + w, y0 + h,
                outline='orange', width=4
            )

    def on_click(self, event):
        """
        Bắt sự kiện click: chọn xe ở vị trí click (Manual mode only).
        """
        if self.mode_var.get() != 'Manual' or not self.board:
            return
        # Lấy item overlap
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for it in items:
            tags = self.canvas.gettags(it)
            if tags and tags[0] in self.board.vehicles:
                self.selected_id = tags[0]
                self.redraw()
                return

    def try_move(self, dx, dy):
        """
        Di chuyển block được chọn một ô dx,dy (Manual mode only).
        Kiểm biên, collision, update self.board rồi redraw.
        Sau đó kiểm goal.
        """
        if self.mode_var.get() != 'Manual' or not self.board or not self.selected_id:
            return
        v = self.board.vehicles[self.selected_id]
        # Chỉ di chuyển theo chiều của xe
        if (v.orientation == 'H' and dy != 0) or (v.orientation == 'V' and dx != 0):
            return
        new_row = v.row + dy
        new_col = v.col + dx
        # Kiểm biên
        if new_row < 0 or new_col < 0:
            return
        end_r = new_row + (v.length - 1 if v.orientation == 'V' else 0)
        end_c = new_col + (v.length - 1 if v.orientation == 'H' else 0)
        if end_r > 5 or end_c > 5:
            return
        # Kiểm collision với các block khác
        occ = self.board.get_occupied()
        # Xóa vị trí cũ của block
        for i in range(v.length):
            rr = v.row + (i if v.orientation == 'V' else 0)
            cc = v.col + (i if v.orientation == 'H' else 0)
            occ[rr][cc] = None
        # Kiểm chỗ mới có trống không
        for i in range(v.length):
            rr = new_row + (i if v.orientation == 'V' else 0)
            cc = new_col + (i if v.orientation == 'H' else 0)
            if occ[rr][cc] is not None:
                return
        # Cập nhật vị trí và vẽ lại
        self.board.vehicles[self.selected_id] = Vehicle(
            v.id, v.orientation, new_row, new_col, v.length
        )
        self.redraw()
        # Kiểm goal
        if self.board.is_goal():
            messagebox.showinfo('Level Completed', 'Bạn đã hoàn thành!')
            self.board = None
            self.selected_id = None
            self.redraw()

    def solve(self):
        """
        Auto-solve khi mode='Auto'.
        1. Lấy path từ BFS/DFS/UCS/A*
        2. Reset board về self.initial_board
        3. Animate di chuyển từng bước
        4. Hiện thông báo khi xong và reset GUI
        """
        if not self.board:
            messagebox.showwarning('Warning', 'Chưa load level!')
            return
        if self.mode_var.get() == 'Manual':
            messagebox.showinfo('Manual Mode', 'Bạn đang chơi thủ công.')
            return
        # Chọn hàm thuật toán
        funcs = {'bfs': bfs, 'dfs': dfs, 'ucs': ucs, 'astar': astar}
        path = funcs[self.algo_var.get()](self.initial_board)
        if path is None:
            messagebox.showinfo('No Solution', 'Không tìm thấy lời giải.')
            return
        # Reset board
        self.board = Board({vid:v for vid,v in self.initial_board.vehicles.items()})
        self.redraw()
        # Animate in separate thread để không block GUI
        threading.Thread(target=self.animate, args=(path,)).start()

    def animate(self, path):
        """
        Di chuyển tự động theo path (danh sách (vid, move)).
        Sleep giữa các bước để thấy animation.
        """
        for vid, move in path:
            time.sleep(0.4)  # điều chỉnh tốc độ tại đây
            v = self.board.vehicles[vid]
            # tính dx, dy dựa vào orientation
            dx, dy = (move, 0) if v.orientation=='H' else (0, move)
            self.board.vehicles[vid] = Vehicle(
                v.id, v.orientation, v.row+dy, v.col+dx, v.length
            )
            self.redraw()
        messagebox.showinfo('Solved', 'Game đã tự giải xong!')
        self.board = None
        self.selected_id = None
        self.redraw()

if __name__ == '__main__':
    RushHourGUI()