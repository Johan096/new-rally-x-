import pygame

def get_combined_keys(joystick=None):
    kb = pygame.key.get_pressed()
    keys_combined = {
        pygame.K_LEFT: kb[pygame.K_LEFT],
        pygame.K_RIGHT: kb[pygame.K_RIGHT],
        pygame.K_UP: kb[pygame.K_UP],
        pygame.K_DOWN: kb[pygame.K_DOWN]
    }
    if joystick:
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)
        threshold = 0.3
        if axis_x < -threshold:
            keys_combined[pygame.K_LEFT] = True
        if axis_x > threshold:
            keys_combined[pygame.K_RIGHT] = True
        if axis_y < -threshold:
            keys_combined[pygame.K_UP] = True
        if axis_y > threshold:
            keys_combined[pygame.K_DOWN] = True
    return keys_combined
