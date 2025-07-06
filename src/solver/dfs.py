from utils import Board
from statistics import Statistics

# Sử dụng stack thay vì recursion để tránh RecursionError
def dfs(initial_board, limit=500, stats=None):
    """Depth-First Search (tham lam, không đảm bảo ngắn nhất)."""
    if stats is None:
        stats = Statistics()
    
    stats.start_tracking("DFS")
    
    visited = {initial_board.state_key()}
    stack = [(initial_board, [])]
    while stack:
        # Update statistics
        stats.increment_expanded_nodes()
        
        board, path = stack.pop()
        if board.is_goal():
            stats.stop_tracking()
            stats.set_solution(path)
            return path, stats
        if len(path) >= limit:
            continue  # đạt limit độ sâu
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                # đẩy vào stack theo LIFO
                stack.append((nb, path + [(vid, move)]))
    stats.stop_tracking()
    return None, stats
