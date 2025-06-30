from utils import Board

# Sử dụng stack thay vì recursion để tránh RecursionError
def dfs(initial_board, limit=500):
    """Depth-First Search (tham lam, không đảm bảo ngắn nhất)."""
    visited = {initial_board.state_key()}
    stack = [(initial_board, [])]

    # Statistics tracking
    nodes_explored = 0
    max_stack_size = 1
    
    while stack:
        current_stack_size = len(stack)
        max_stack_size = max(max_stack_size, current_stack_size)
        
        board, path = stack.pop()
        nodes_explored += 1
        
        if board.is_goal():
            return {
                'path': path,
                'nodes_explored': nodes_explored,
                'max_queue_size': max_stack_size
            }
        if len(path) >= limit:
            continue  # đạt limit độ sâu
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                # đẩy vào stack theo LIFO
                stack.append((nb, path + [(vid, move)]))
    return {
        'path': None,
        'nodes_explored': nodes_explored,
        'max_queue_size': max_stack_size
    }
