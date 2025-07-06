from collections import deque
from utils import Board
from statistics import Statistics

def bfs(initial_board, stats=None):
    """Breadth-First Search: tìm đường ngắn nhất theo số bước."""
    if stats is None:
        stats = Statistics()
    
    stats.start_tracking("BFS")
    
    start_key = initial_board.state_key()
    frontier = deque([(initial_board, [])])
    visited = {start_key}
    
    while frontier:
        # Update statistics
        stats.increment_expanded_nodes()
        
        board, path = frontier.popleft()
        
        if board.is_goal():
            stats.stop_tracking()
            stats.set_solution(path)
            return path, stats
            
        for vid, move, nb in board.successors():
            key = nb.state_key()
            if key not in visited:
                visited.add(key)
                frontier.append((nb, path + [(vid, move)]))
    stats.stop_tracking()
    return None, stats  # không tìm được
