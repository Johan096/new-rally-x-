# ai.py
import pygame
import math
import heapq
from src.settings import CELL_SIZE

# --- A* y manejo del grid ---
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.blocked = False
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash((self.x, self.y))

def create_specific_map(width, height, obstacles_coords):
    grid = [[Node(x, y) for x in range(width)] for y in range(height)]
    for (x, y) in obstacles_coords:
        if 0 <= x < width and 0 <= y < height:
            grid[y][x].blocked = True
    return grid

def reset_grid(grid):
    """
    Reinicializa los atributos de cada nodo en el grid.
    Se llama antes de cada ejecución del algoritmo A* para evitar copiar el grid.
    """
    for row in grid:
        for node in row:
            node.g = float('inf')
            node.h = 0
            node.f = float('inf')
            node.parent = None

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

def generate_coins(grid, num_coins):
    rows = len(grid)
    cols = len(grid[0])
    possible_positions = [(x, y) for y in range(rows) for x in range(cols) if not grid[y][x].blocked]
    import random
    random.shuffle(possible_positions)
    return possible_positions[:num_coins]

# --- Árbol de Comportamiento ---
class BehaviorNode:
    def run(self, enemy, player, grid, grid_width, grid_height):
        raise NotImplementedError

class ConditionNode(BehaviorNode):
    def __init__(self, condition_func):
        self.condition_func = condition_func

    def run(self, enemy, player, grid, grid_width, grid_height):
        return self.condition_func(enemy, player, grid, grid_width, grid_height)

class ActionNode(BehaviorNode):
    def __init__(self, action_func):
        self.action_func = action_func

    def run(self, enemy, player, grid, grid_width, grid_height):
        self.action_func(enemy, player, grid, grid_width, grid_height)
        return True

class SequenceNode(BehaviorNode):
    def __init__(self, children):
        self.children = children

    def run(self, enemy, player, grid, grid_width, grid_height):
        for child in self.children:
            if not child.run(enemy, player, grid, grid_width, grid_height):
                return False
        return True

class SelectorNode(BehaviorNode):
    def __init__(self, children):
        self.children = children

    def run(self, enemy, player, grid, grid_width, grid_height):
        for child in self.children:
            if child.run(enemy, player, grid, grid_width, grid_height):
                return True
        return False

def condition_player_close(enemy, player, grid, grid_width, grid_height):
    dx = player.rect.centerx - enemy.rect.centerx
    dy = player.rect.centery - enemy.rect.centery
    return math.hypot(dx, dy) < 200

def chase_action(enemy, player, grid, grid_width, grid_height):
    # En lugar de copiar el grid, reiniciamos los valores de cada nodo.
    reset_grid(grid)
    enemy_cell = (enemy.rect.centerx // CELL_SIZE, enemy.rect.centery // CELL_SIZE)
    player_cell = (player.rect.centerx // CELL_SIZE, player.rect.centery // CELL_SIZE)
    start = grid[enemy_cell[1]][enemy_cell[0]]
    goal = grid[player_cell[1]][player_cell[0]]
    path = a_star(start, goal, grid, grid_width, grid_height)
    if path and len(path) > 1:
        next_cell = path[1]
        target_vector = pygame.math.Vector2(next_cell[0] * CELL_SIZE + CELL_SIZE // 2,
                                            next_cell[1] * CELL_SIZE + CELL_SIZE // 2)
        move_vector = target_vector - pygame.math.Vector2(enemy.rect.center)
        if move_vector.length() != 0:
            enemy.pos += move_vector.normalize() * enemy.speed
    else:
        dx = player.rect.centerx - enemy.rect.centerx
        dy = player.rect.centery - enemy.rect.centery
        if dx or dy:
            enemy.pos += pygame.math.Vector2(dx, dy).normalize() * enemy.speed

def patrol_action(enemy, player, grid, grid_width, grid_height):
    target = enemy.patrol_points[enemy.current_patrol_point]
    move_vector = target - enemy.pos
    if move_vector.length() < 3:
        enemy.current_patrol_point = (enemy.current_patrol_point + 1) % len(enemy.patrol_points)
        target = enemy.patrol_points[enemy.current_patrol_point]
        move_vector = target - enemy.pos
    if move_vector.length() != 0:
        enemy.pos += move_vector.normalize() * enemy.speed
