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
    while frontier:
        f, g, _, board, path = heapq.heappop(frontier)
        key = board.state_key()
        if key in visited and visited[key] <= g:
            continue
        visited[key] = g
        if board.is_goal():
            return path
        for vid, move, nb in board.successors():
            step = nb.vehicles[vid].length
            ng = g + step
            h = blocking_cars(nb)
            heapq.heappush(
                frontier,
                (ng + h, ng, next(counter), nb, path + [(vid, move)])
            )
    return None