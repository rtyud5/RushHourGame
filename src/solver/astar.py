import heapq
from utils import Board
from solver.heuristics import blocking_cars
from itertools import count

# A* Search: kết hợp g (cost thực) và h (heuristic)
def astar(initial_board):
    frontier = []
    counter = count()
    start_h = blocking_cars(initial_board)
    # frontier element: (f = g+h, g, tie_id, board, path)
    heapq.heappush(frontier, (start_h, 0, next(counter), initial_board, []))
    visited = {}

    # Statistics tracking
    nodes_explored = 0
    max_queue_size = 1
    
    while frontier:
        current_queue_size = len(frontier)
        max_queue_size = max(max_queue_size, current_queue_size)
        
        f, g, _, board, path = heapq.heappop(frontier)
        nodes_explored += 1
        
        key = board.state_key()
        if key in visited and visited[key] <= g:
            continue
        visited[key] = g
        
        if board.is_goal():
            return {
                'path': path,
                'nodes_explored': nodes_explored,
                'max_queue_size': max_queue_size
            }
            
        for vid, move, nb in board.successors():
            step = nb.vehicles[vid].length
            ng = g + step
            h = blocking_cars(nb)
            heapq.heappush(
                frontier,
                (ng + h, ng, next(counter), nb, path + [(vid, move)])
            )
    return {
        'path': None,
        'nodes_explored': nodes_explored,
        'max_queue_size': max_queue_size
    }
