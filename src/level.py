import heapq
from src.settings import CELL_SIZE

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.blocked = False  # Se actualizará con obstáculos
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None
    def __lt__(self, other):
        return self.f < other.f
    def __hash__(self):
        return hash((self.x, self.y))

def create_empty_grid(width, height):
    return [[Node(x, y) for x in range(width)] for y in range(height)]

def copy_grid(grid):
    new_grid = []
    for row in grid:
        new_row = []
        for node in row:
            new_node = Node(node.x, node.y)
            new_node.blocked = node.blocked
            new_row.append(new_node)
        new_grid.append(new_row)
    return new_grid

def a_star(start, goal, grid, width, height):
    open_list = []
    closed_set = set()
    start.g = 0
    start.h = abs(start.x - goal.x) + abs(start.y - goal.y)
    start.f = start.g + start.h
    heapq.heappush(open_list, (start.f, start))
    while open_list:
        current = heapq.heappop(open_list)[1]
        if current.x == goal.x and current.y == goal.y:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]
        closed_set.add(current)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current.x + dx, current.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbor = grid[ny][nx]
                if neighbor.blocked or neighbor in closed_set:
                    continue
                tentative_g = current.g + 1
                if tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.h = abs(neighbor.x - goal.x) + abs(neighbor.y - goal.y)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current
                    heapq.heappush(open_list, (neighbor.f, neighbor))
    return None

def get_level_data(level):
    # Ejemplo simple: según nivel, definir cantidad de enemigos.
    if level == 1:
        enemy_count = 5
    elif level == 2:
        enemy_count = 7
    elif level == 3:
        enemy_count = 10
    else:
        return None, None, 0
    grid_width, grid_height = 20, 15
    grid = create_empty_grid(grid_width, grid_height)
    coins = []  # Las monedas se agregarán como decoración
    return grid, coins, enemy_count
