from collections import deque
from utils import Board

def bfs(initial_board):
    """Breadth-First Search: tìm đường ngắn nhất theo số bước."""
    start_key = initial_board.state_key()
    frontier = deque([(initial_board, [])])
    visited = {start_key}

    # Statistics tracking
    nodes_explored = 0
    max_queue_size = 1
    
    while frontier:
        current_queue_size = len(frontier)
        max_queue_size = max(max_queue_size, current_queue_size)
        
        board, path = frontier.popleft()
        nodes_explored += 1
        
        if board.is_goal():
            # Return path and statistics
            return {
                'path': path,
                'nodes_explored': nodes_explored,
                'max_queue_size': max_queue_size
            }
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                frontier.append((nb, path + [(vid, move)]))
    # No solution found
    return {
        'path': None,
        'nodes_explored': nodes_explored,
        'max_queue_size': max_queue_size
    }
