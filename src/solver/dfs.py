from utils import Board

# Sử dụng stack thay vì recursion để tránh RecursionError
def dfs(initial_board, limit=10000):
    """Depth-First Search (tham lam, không đảm bảo ngắn nhất)."""
    visited = {initial_board.state_key()}
    stack = [(initial_board, [])]
    while stack:
        board, path = stack.pop()
        if board.is_goal():
            return path
        if len(path) >= limit:
            continue  # đạt limit độ sâu
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                # đẩy vào stack theo LIFO
                stack.append((nb, path + [(vid, move)]))
    return None