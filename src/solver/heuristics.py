from utils import Board

def blocking_cars(board: Board) -> int:
    """
    Heuristic: đếm số xe chắn trước đầu xe X trên cùng hàng.
    Giúp A* định hướng nhanh hơn.
    """
    occ = board.get_occupied()
    target = board.vehicles['X']
    row = target.row
    blocks = 0
    # quét từ col cuối xe X +1 đến size-1
    for c in range(target.col + target.length, board.size):
        if occ[row][c] is not None:
            blocks += 1
    return blocks