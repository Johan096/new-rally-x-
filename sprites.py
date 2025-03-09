# sprites.py
import pygame
import random
from resources import load_image
from config import WIDTH, HEIGHT, CELL_SIZE, RED, BLUE, GREEN, YELLOW, BLACK

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image("player01_.png", size=(55, 55))
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
            dx = -self.speed
            self.angle = 180
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.angle = 0
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.angle = 270
        if keys[pygame.K_DOWN]:
            dy = self.speed
            self.angle = 90

        # Movimiento horizontal y colisiones
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if any(ob.rect.colliderect(self.rect) for ob in obstacles):
            self.rect.x = original_rect.x

        # Movimiento vertical y colisiones
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if any(ob.rect.colliderect(self.rect) for ob in obstacles):
            self.rect.y = original_rect.y

        # Rotar imagen según la dirección
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
        self.original_image = load_image("enemigos01.png", size=(50, 50))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 2
        self.patrol_points = [
            pygame.math.Vector2(x, y),
            pygame.math.Vector2(random.randint(200, WIDTH - 200), random.randint(200, HEIGHT - 200))
        ]
        self.current_patrol_point = 1
        self.behavior_tree = ai_tree

    def move(self, player, grid, grid_width, grid_height):
        self.behavior_tree.run(self, player, grid, grid_width, grid_height)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        # Evitar salir de los límites
        if self.rect.left < 0:
            self.rect.left = 0; self.pos.x = self.rect.left
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH; self.pos.x = self.rect.right - self.rect.width
        if self.rect.top < 0:
            self.rect.top = 0; self.pos.y = self.rect.top
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT; self.pos.y = self.rect.bottom - self.rect.height

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("moneda.jpg", size=(45, 45))
        self.rect = self.image.get_rect(topleft=(x, y))

class VariedObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, shape="rectangle"):
        super().__init__()
        self.shape = shape
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        if shape in ["rectangle", "square"]:
            pygame.draw.rect(self.image, BLACK, (0, 0, width, height))
        elif shape == "ellipse":
            pygame.draw.ellipse(self.image, BLACK, (0, 0, width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
