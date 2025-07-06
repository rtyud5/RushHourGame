from utils import Board
from statistics import Statistics

# Sử dụng stack thay vì recursion để tránh RecursionError
def dfs(initial_board, limit=50, stats=None):
    """Depth-First Search (tham lam, không đảm bảo ngắn nhất)."""
    if stats is None:
        stats = Statistics()
    
    stats.start_tracking("DFS")
    
    visited = {initial_board.state_key()}
    stack = [(initial_board, [])]
    paths_rejected_by_limit = 0
    max_depth_reached = 0
    while stack:
        # Update statistics
        stats.increment_expanded_nodes()
        
        board, path = stack.pop()
        current_depth = len(path)
        max_depth_reached = max(max_depth_reached, current_depth)
        if board.is_goal():
            stats.stop_tracking()
            stats.set_solution(path)
            return path, stats
        if len(path) >= limit:
            paths_rejected_by_limit += 1 # path bị từ chối bởi limit
            continue  # đạt limit độ sâu
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                # đẩy vào stack theo LIFO
                stack.append((nb, path + [(vid, move)]))
    # Check if we hit the limit (paths were rejected)
    if paths_rejected_by_limit > 0 or (stats.expanded_nodes > 500 and max_depth_reached >= limit * 0.8):
        stats.set_limit_reached()
    stats.stop_tracking()
    return None, stats
