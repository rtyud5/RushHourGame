from collections import namedtuple

# Vehicle là namedtuple lưu trữ đặc tính của mỗi block trên board
# id: ký hiệu (chuỗi), orientation: 'H' hoặc 'V', row/col: vị trí góc trên-trái, length: độ dài
Vehicle = namedtuple('Vehicle', ['id', 'orientation', 'row', 'col', 'length'])

class Board:
    """
    Lớp Board quản lý trạng thái của trò chơi:
      - self.vehicles: dict id->Vehicle
      - self.size: kích thước board (6)
    Các phương thức:
      - state_key(): trả về key để đánh dấu visited
      - is_goal(): kiểm tra xe X đã đến đích chưa
      - get_occupied(): tạo ma trận 6x6 đánh dấu ô đã chiếm
      - successors(): liệt kê các board có thể tới sau 1 bước di chuyển
    """
    def __init__(self, vehicles):
        self.vehicles = vehicles  # dict id -> Vehicle
        self.size = 6

    def state_key(self):
        # Trả tuple sắp xếp theo id, dùng để so sánh visited
        return tuple((v.id, v.row, v.col)
                     for v in sorted(self.vehicles.values(), key=lambda x: x.id))

    def is_goal(self):
        # Mục tiêu: xe X ngang (H) và ô cuối cùng của nó nằm ở col == size-1
        target = self.vehicles['X']
        return (target.orientation == 'H' and
                target.col + target.length - 1 == self.size - 1)

    def get_occupied(self):
        # Trả danh sách 2D 6x6, mỗi ô chứa id xe hoặc None
        occ = [[None] * self.size for _ in range(self.size)]
        for v in self.vehicles.values():
            for i in range(v.length):
                r = v.row + (i if v.orientation == 'V' else 0)
                c = v.col + (i if v.orientation == 'H' else 0)
                occ[r][c] = v.id
        return occ

    def successors(self):
        # Sinh tất cả board con bằng cách di chuyển từng xe 1 bước
        occ = self.get_occupied()
        succs = []
        # Duyệt qua từng xe
        for vid, v in self.vehicles.items():
            if v.orientation == 'H':
                # Di chuyển ngang: trái và phải
                # trái: col-1
                if v.col > 0 and occ[v.row][v.col - 1] is None:
                    new = dict(self.vehicles)
                    new[vid] = Vehicle(v.id, 'H', v.row, v.col - 1, v.length)
                    succs.append((vid, -1, Board(new)))
                # phải: end+1
                end = v.col + v.length - 1
                if end < self.size - 1 and occ[v.row][end + 1] is None:
                    new = dict(self.vehicles)
                    new[vid] = Vehicle(v.id, 'H', v.row, v.col + 1, v.length)
                    succs.append((vid, +1, Board(new)))
            else:
                # Di chuyển dọc: lên và xuống
                if v.row > 0 and occ[v.row - 1][v.col] is None:
                    new = dict(self.vehicles)
                    new[vid] = Vehicle(v.id, 'V', v.row - 1, v.col, v.length)
                    succs.append((vid, -1, Board(new)))
                end = v.row + v.length - 1
                if end < self.size - 1 and occ[end + 1][v.col] is None:
                    new = dict(self.vehicles)
                    new[vid] = Vehicle(v.id, 'V', v.row + 1, v.col, v.length)
                    succs.append((vid, +1, Board(new)))
        return succs