import pygame
import random
from .settings import WIDTH, HEIGHT, CELL_SIZE, WHITE, RED, BLUE, GREEN, YELLOW, BLACK

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.original_image = pygame.image.load("assets/player01_.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (55, 55))
        except pygame.error:
            self.original_image = pygame.Surface((55, 55))
            self.original_image.fill(RED)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(100, 100))
        self.speed = 4
        self.angle = 0
        self.coins_collected = 0
        self.health = 100
        self.shoot_cooldown = 200  
        self.last_shot_time = 0
        self.score = 0
        self.flash_timer = 0
        self.is_flashing = False

    def move(self, keys, obstacles):
        original_rect = self.rect.copy()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed; self.angle = 180
        if keys[pygame.K_RIGHT]:
            dx = self.speed; self.angle = 0
        if keys[pygame.K_UP]:
            dy = -self.speed; self.angle = 270
        if keys[pygame.K_DOWN]:
            dy = self.speed; self.angle = 90
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if any(ob.rect.colliderect(self.rect) for ob in obstacles):
            self.rect.x = original_rect.x
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if any(ob.rect.colliderect(self.rect) for ob in obstacles):
            self.rect.y = original_rect.y
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.speed = 6
        self.angle = angle
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        if self.angle == 0:
            self.rect.x += self.speed
        elif self.angle == 180:
            self.rect.x -= self.speed
        elif self.angle == 90:
            self.rect.y -= self.speed
        elif self.angle == 270:
            self.rect.y += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, ai_tree):
        super().__init__()
        try:
            self.original_image = pygame.image.load("assets/enemigos01.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        except pygame.error:
            self.original_image = pygame.Surface((50, 50))
            self.original_image.fill(BLUE)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 1.5  # Velocidad moderada
        self.patrol_points = [
            pygame.math.Vector2(x, y),
            pygame.math.Vector2(random.randint(200, WIDTH - 200), random.randint(200, HEIGHT - 200))
        ]
        self.current_patrol_point = 1
        self.behavior_tree = ai_tree
        self.last_path_calc_time = 0
        self.path_recalc_interval = 500  # en milisegundos
        self.cached_path = []
        self.last_target_position = None

    def move(self, player, grid, grid_width, grid_height, obstacles):
        old_position = self.pos.copy()
        self.behavior_tree.run(self, player, grid, grid_width, grid_height)
        new_position = self.pos.copy()
        move_vector = new_position - old_position
        old_x = self.pos.x; old_y = self.pos.y
        self.pos.x = old_x + move_vector.x
        self.rect.centerx = int(self.pos.x)
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.pos.x = old_x
            self.rect.centerx = int(old_x)
        self.pos.y = old_y + move_vector.y
        self.rect.centery = int(self.pos.y)
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.pos.y = old_y
            self.rect.centery = int(old_y)
        if self.pos == old_position:
            self.last_path_calc_time = 0

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/moneda.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 45))
        except pygame.error:
            self.image = pygame.Surface((45, 45))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

class ImageObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/obstaculo.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except pygame.error:
            self.image = pygame.Surface((size, size))
            self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))
