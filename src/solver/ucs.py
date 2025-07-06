import heapq
from utils import Board
from itertools import count

# Uniform-Cost Search: tìm đường chi phí nhỏ nhất (cost = length của xe)
def ucs(initial_board):
    frontier = []
    counter = count()  # để tie-breaker nếu cost bằng nhau
    # frontier element: (total_cost, tie_id, board, path)
    heapq.heappush(frontier, (0, next(counter), initial_board, []))
    visited = {}
    while frontier:
        cost, _, board, path = heapq.heappop(frontier)
        key = board.state_key()
        if key in visited and visited[key] <= cost:
            continue
        visited[key] = cost
        if board.is_goal():
            return path
        for vid, move, nb in board.successors():
            step_cost = nb.vehicles[vid].length
            heapq.heappush(
                frontier,
                (cost + step_cost, next(counter), nb, path + [(vid, move)])
            )
    return None