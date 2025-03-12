import pygame
from src.settings import WHITE, RED, GREEN, BLACK
font = pygame.font.Font(None, 36)

def draw_text(text, x, y, color=BLACK):
    render = font.render(text, True, color)
    pygame.display.get_surface().blit(render, (x, y))

def draw_health_bar(surface, x, y, health, max_health, flash=False):
    BAR_WIDTH = 150
    BAR_HEIGHT = 20
    fill = (health / max_health) * BAR_WIDTH
    bar_color = RED if flash and (pygame.time.get_ticks() // 100) % 2 == 0 else GREEN
    pygame.draw.rect(surface, RED, (x, y, BAR_WIDTH, BAR_HEIGHT))
    pygame.draw.rect(surface, bar_color, (x, y, fill, BAR_HEIGHT))
    pygame.draw.rect(surface, BLACK, (x, y, BAR_WIDTH, BAR_HEIGHT), 2)
