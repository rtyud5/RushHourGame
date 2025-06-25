from collections import deque
from utils import Board

def bfs(initial_board):
    """Breadth-First Search: tìm đường ngắn nhất theo số bước."""
    start_key = initial_board.state_key()
    frontier = deque([(initial_board, [])])
    visited = {start_key}
    while frontier:
        board, path = frontier.popleft()
        if board.is_goal():
            return path
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                frontier.append((nb, path + [(vid, move)]))
    return None  # không tìm được