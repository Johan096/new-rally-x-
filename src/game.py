import pygame
import random
from src.settings import WIDTH, HEIGHT, CELL_SIZE, WHITE, GREEN, RED, BLUE
from src.transitions import fade_in_nonblocking, fade_out_nonblocking
from src.music import load_music, play_music, stop_music
from src.ui import draw_text, draw_health_bar
from src.input import get_combined_keys
from src.level import get_level_data
from src.behavior import SelectorNode, SequenceNode, ConditionNode, ActionNode, condition_player_close, chase_action, patrol_action
from src.entities import Player, Bullet, Enemy, Coin, ImageObstacle

def show_story():
    try:
        story_bg = pygame.image.load("assets/story background.jpg").convert()
        story_bg = pygame.transform.scale(story_bg, (WIDTH, HEIGHT))
    except pygame.error:
        story_bg = pygame.Surface((WIDTH, HEIGHT))
        story_bg.fill(WHITE)
    story_text = [
        "Bienvenido a New Rally X",
        "",
        "La tierra ha sido invadida por enemigos misteriosos",
        "y la única esperanza es recolectar monedas mágicas",
        "y derrotar a los invasores.",
        "",
        "Tu misión: Explora, combate y recoge monedas",
        "para restaurar la paz en tu mundo.",
        "",
        "Presiona ENTER para comenzar..."
    ]
    line_height = 40
    total_text_height = len(story_text) * line_height
    start_y = (HEIGHT - total_text_height) // 2
    waiting = True
    while waiting:
        pygame.display.get_surface().blit(story_bg, (0, 0))
        for idx, line in enumerate(story_text):
            text_surface = pygame.font.Font(None,36).render(line, True, BLUE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, start_y + idx * line_height + line_height // 2))
            pygame.display.get_surface().blit(text_surface, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    fade_out_nonblocking(pygame.display.get_surface())
                    waiting = False

def main_menu(sound_enabled):
    menu_options = ["Empezar Juego", f"Sonido: {'ON' if sound_enabled else 'OFF'}", "Salir"]
    selected_option = 0
    try:
        background = pygame.image.load("assets/fondo_menu.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except pygame.error:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(WHITE)
    fade_in_nonblocking(pygame.display.get_surface())
    running = True
    while running:
        pygame.display.get_surface().blit(background, (0, 0))
        for i, option in enumerate(menu_options):
            color = RED if i == selected_option else BLUE
            draw_text(option, 300, 200 + i * 50, color)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        fade_out_nonblocking(pygame.display.get_surface())
                        return "start", sound_enabled
                    elif selected_option == 1:
                        sound_enabled = not sound_enabled
                        menu_options[1] = f"Sonido: {'ON' if sound_enabled else 'OFF'}"
                        if sound_enabled:
                            play_music()
                        else:
                            stop_music()
                    elif selected_option == 2:
                        pygame.quit(); exit()

def game_loop():
    clock = pygame.time.Clock()
    level = 1
    try:
        bg_image = pygame.image.load("assets/background.jpg").convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except pygame.error:
        bg_image = pygame.Surface((WIDTH, HEIGHT))
        bg_image.fill(WHITE)
    running = True
    while running:
        grid, _, enemy_count = get_level_data(level)
        all_sprites = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        coin_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()
        deco_obstacles, deco_coins = generate_decorations()  # Usando la función de generación en entities
        # Actualizar grid con obstáculos
        for obs in deco_obstacles:
            cell_x = obs.rect.x // CELL_SIZE
            cell_y = obs.rect.y // CELL_SIZE
            if 0 <= cell_x < len(grid[0]) and 0 <= cell_y < len(grid):
                grid[cell_y][cell_x].blocked = True
        obstacles_group = pygame.sprite.Group(deco_obstacles)
        for obs in deco_obstacles:
            all_sprites.add(obs)
        for coin in deco_coins:
            coin_group.add(coin)
            all_sprites.add(coin)
        player = Player()
        all_sprites.add(player)
        ai_tree = SelectorNode([
            SequenceNode([ConditionNode(condition_player_close), ActionNode(chase_action)]),
            ActionNode(patrol_action)
        ])
        # Generar enemigos evitando colisiones con obstáculos
        for _ in range(enemy_count):
            valid = False
            attempts = 0
            while not valid and attempts < 100:
                ex = random.randint(5, 20) * CELL_SIZE
                ey = random.randint(5, 15) * CELL_SIZE
                enemy_rect = pygame.Rect(ex, ey, 50, 50)
                collision = False
                for obs in obstacles_group:
                    if enemy_rect.colliderect(obs.rect):
                        collision = True
                        break
                if not collision:
                    valid = True
                attempts += 1
            if valid:
                enemy = Enemy(ex, ey, ai_tree)
                enemy_group.add(enemy)
                all_sprites.add(enemy)
        goal_rect = pygame.Rect(WIDTH - 100, HEIGHT - 100, 50, 50)
        game_over = False
        win = False
        while not game_over and not win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        now = pygame.time.get_ticks()
                        if now - player.last_shot_time > player.shoot_cooldown:
                            bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                            bullet_group.add(bullet)
                            all_sprites.add(bullet)
                            player.last_shot_time = now
            keys = get_combined_keys()
            player.move(keys, obstacles_group)
            for bullet in bullet_group:
                bullet.update()
                if (bullet.rect.right < 0 or bullet.rect.left > WIDTH or 
                    bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT):
                    bullet.kill()
            for enemy in enemy_group:
                enemy.move(player, grid, len(grid[0]), len(grid), obstacles_group)
                if enemy.rect.colliderect(player.rect):
                    player.health -= 1
                    player.is_flashing = True
                    player.flash_timer = pygame.time.get_ticks()
                if pygame.sprite.spritecollide(enemy, bullet_group, True):
                    enemy.kill()
                    player.score += 100
            coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
            player.coins_collected += len(coins_collected)
            player.score += 50 * len(coins_collected)
            if player.is_flashing and pygame.time.get_ticks() - player.flash_timer > 300:
                player.is_flashing = False
            if player.rect.colliderect(goal_rect) or len(coin_group) == 0:
                win = True
                player.score += 500
            pygame.display.get_surface().blit(bg_image, (0, 0))
            pygame.draw.rect(pygame.display.get_surface(), GREEN, goal_rect)
            all_sprites.draw(pygame.display.get_surface())
            draw_text(f"Monedas: {player.coins_collected}", 10, 10, RED)
            draw_health_bar(pygame.display.get_surface(), WIDTH - 170, 10, player.health, 100, flash=player.is_flashing)
            draw_text(f"Nivel: {level}", WIDTH - 150, 50, RED)
            draw_text(f"Puntos: {player.score}", 10, 50, BLUE)
            pygame.display.flip()
            clock.tick(60)
            if player.health <= 0:
                game_over = True
        # (Aquí agregarías la pantalla de resultados y progresión de nivel)
        running = False  # Para finalizar el juego en este ejemplo

def generate_decorations(num_obstacles=10, num_coins=10, min_distance=15):
    # Función similar a la definida en entities.py o level.py
    # Puedes mover esta función a otro módulo si lo prefieres
    import random
    from src.entities import ImageObstacle, Coin
    deco_obstacles = []
    deco_coins = []
    margin = 20
    full_rect = pygame.Rect(margin, margin, WIDTH - 2 * margin, HEIGHT - 2 * margin)
    start_rect = pygame.Rect(100, 100, 55, 55)
    goal_rect = pygame.Rect(WIDTH - 100, HEIGHT - 100, 50, 50)
    attempts = 0
    while len(deco_obstacles) < num_obstacles and attempts < 1000:
        x = random.randint(full_rect.left, full_rect.right - CELL_SIZE)
        y = random.randint(full_rect.top, full_rect.bottom - CELL_SIZE)
        new_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        if new_rect.colliderect(start_rect) or new_rect.colliderect(goal_rect):
            attempts += 1; continue
        collision = False
        for obs in deco_obstacles:
            if new_rect.colliderect(obs.rect.inflate(min_distance, min_distance)):
                collision = True; break
        if not collision:
            obs = ImageObstacle(x, y, CELL_SIZE)
            deco_obstacles.append(obs)
        attempts += 1
    attempts = 0
    coin_size = 45
    while len(deco_coins) < num_coins and attempts < 1000:
        x = random.randint(full_rect.left, full_rect.right - coin_size)
        y = random.randint(full_rect.top, full_rect.bottom - coin_size)
        new_rect = pygame.Rect(x, y, coin_size, coin_size)
        collision = False
        for coin in deco_coins:
            if new_rect.colliderect(coin.rect.inflate(min_distance, min_distance)):
                collision = True; break
        if not collision:
            coin = Coin(x, y)
            deco_coins.append(coin)
        attempts += 1
    return deco_obstacles, deco_coins

