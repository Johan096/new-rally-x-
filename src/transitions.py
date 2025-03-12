import pygame
from src.settings import FPS

class FadeTransition:
    def __init__(self, screen, direction="in", color=(0, 0, 0), duration=500):
        self.screen = screen
        self.direction = direction
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.surface = pygame.Surface(screen.get_size())
        self.surface.fill(color)
        self.done = False

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1, elapsed / self.duration)
        alpha = 255 * (1 - progress) if self.direction == "in" else 255 * progress
        self.surface.set_alpha(alpha)
        self.screen.blit(self.surface, (0, 0))
        if progress >= 1:
            self.done = True

def fade_in_nonblocking(screen, duration=500, color=(0, 0, 0)):
    fade = FadeTransition(screen, direction="in", color=color, duration=duration)
    clock = pygame.time.Clock()
    while not fade.done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
        fade.update()
        pygame.display.flip()
        clock.tick(FPS)

def fade_out_nonblocking(screen, duration=500, color=(0, 0, 0)):
    fade = FadeTransition(screen, direction="out", color=color, duration=duration)
    clock = pygame.time.Clock()
    while not fade.done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
        fade.update()
        pygame.display.flip()
        clock.tick(FPS)
