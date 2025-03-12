import math
import pygame
from .level import copy_grid, a_star
from .settings import CELL_SIZE

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
    current_time = pygame.time.get_ticks()
    enemy_cell = (enemy.rect.centerx // CELL_SIZE, enemy.rect.centery // CELL_SIZE)
    player_cell = (player.rect.centerx // CELL_SIZE, player.rect.centery // CELL_SIZE)
    recalc_needed = False
    if current_time - enemy.last_path_calc_time > enemy.path_recalc_interval:
        recalc_needed = True
    if enemy.last_target_position is None:
        recalc_needed = True
    else:
        if abs(player_cell[0] - enemy.last_target_position[0]) > 1 or abs(player_cell[1] - enemy.last_target_position[1]) > 1:
            recalc_needed = True
    if recalc_needed:
        grid_copy = copy_grid(grid)
        start = grid_copy[enemy_cell[1]][enemy_cell[0]]
        goal = grid_copy[player_cell[1]][player_cell[0]]
        path = a_star(start, goal, grid_copy, grid_width, grid_height)
        enemy.cached_path = path if path is not None else []
        enemy.last_path_calc_time = current_time
        enemy.last_target_position = player_cell
    else:
        path = enemy.cached_path
    if path and len(path) > 1:
        next_cell = path[1]
        target_vector = pygame.math.Vector2(next_cell[0] * CELL_SIZE + CELL_SIZE // 2,
                                            next_cell[1] * CELL_SIZE + CELL_SIZE // 2)
        move_vector = target_vector - enemy.pos
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
