# game.py
import pygame, random, os
from config import WIDTH, HEIGHT, FPS, CELL_SIZE, WHITE, RED, BLUE, GREEN, YELLOW, BLACK
from resources import load_image, load_music, play_music, stop_music
from sprites import Player, Bullet, Enemy, VariedObstacle
from ai import (create_specific_map, generate_coins, condition_player_close, 
                chase_action, patrol_action, SelectorNode, SequenceNode, ConditionNode, ActionNode)
                
def fade_in(screen, color=(0, 0, 0), speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(color)
    for alpha in range(255, -1, -speed):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def fade_out(screen, color=(0, 0, 0), speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(color)
    for alpha in range(0, 256, speed):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def draw_text(screen, text, x, y, color=BLACK):
    font = pygame.font.Font(None, 36)
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def draw_health_bar(surface, x, y, health, max_health, flash=False):
    BAR_WIDTH = 150
    BAR_HEIGHT = 20
    fill = (health / max_health) * BAR_WIDTH
    bar_color = YELLOW if flash and (pygame.time.get_ticks() // 100) % 2 == 0 else GREEN
    pygame.draw.rect(surface, RED, (x, y, BAR_WIDTH, BAR_HEIGHT))
    pygame.draw.rect(surface, bar_color, (x, y, fill, BAR_HEIGHT))
    pygame.draw.rect(surface, BLACK, (x, y, BAR_WIDTH, BAR_HEIGHT), 2)

def get_combined_keys(joystick):
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

def show_story(screen):
    try:
        story_bg = load_image("story background.jpg", size=(WIDTH, HEIGHT))
    except pygame.error:
        story_bg = pygame.Surface((WIDTH, HEIGHT))
        story_bg.fill(WHITE)
    font = pygame.font.Font(None, 36)
    story_text = [
        "Bienvenido a New Rally X",
        "",
        "La tierra ha sido invadida por enemigos misteriosos",
        "y la unica esperanza es recolectar monedas magicas",
        "y derrotar a los invasores.",
        "",
        "Tu mision: Explora, combate y recoge monedas",
        "para restaurar la paz en tu mundo.",
        "",
        "Presiona ENTER para comenzar..."
    ]
    line_height = 40
    total_text_height = len(story_text) * line_height
    start_y = (HEIGHT - total_text_height) // 2
    waiting = True
    while waiting:
        screen.blit(story_bg, (0, 0))
        for idx, line in enumerate(story_text):
            text_surface = font.render(line, True, BLUE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, start_y + idx * line_height + line_height // 2))
            screen.blit(text_surface, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                fade_out(screen)
                waiting = False

def get_level_data(level):
    if level == 1:
        grid_width, grid_height = 20, 15
        num_coins = 10
        enemy_count = 5
        num_obstacles = 10
    elif level == 2:
        grid_width, grid_height = 25, 20
        num_coins = 15
        enemy_count = 7
        num_obstacles = 15
    elif level == 3:
        grid_width, grid_height = 30, 25
        num_coins = 20
        enemy_count = 10
        num_obstacles = 20
    else:
        return None, None, 0

    safe_zone = {(x, y) for x in range(4) for y in range(4)}
    goal_rect = pygame.Rect(WIDTH - 100, HEIGHT - 100, 50, 50)
    goal_zone = {(x, y) for y in range(grid_height) for x in range(grid_width)
                 if pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE).colliderect(goal_rect)}
    forbidden = safe_zone.union(goal_zone)
    obstacles = set()
    while len(obstacles) < num_obstacles:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)
        if (x, y) not in forbidden:
            obstacles.add((x, y))
    obstacles = list(obstacles)
    grid = create_specific_map(grid_width, grid_height, obstacles)
    coin_positions = generate_coins(grid, num_coins)
    from sprites import Coin
    coins = [Coin(pos[0] * CELL_SIZE + (CELL_SIZE - 45) // 2,
                  pos[1] * CELL_SIZE + (CELL_SIZE - 45) // 2) for pos in coin_positions]
    return grid, coins, enemy_count

def main_menu(screen, sound_enabled, joystick):
    menu_running = True
    menu_options = ["Empezar Juego", f"Sonido: {'ON' if sound_enabled else 'OFF'}", "Salir"]
    selected_option = 0
    try:
        background = load_image("fondo_menu.jpg", size=(WIDTH, HEIGHT))
    except pygame.error:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(WHITE)
    fade_in(screen)
    font = pygame.font.Font(None, 36)
    while menu_running:
        screen.blit(background, (0, 0))
        for i, option in enumerate(menu_options):
            color = RED if i == selected_option else BLACK
            text_surface = font.render(option, True, color)
            screen.blit(text_surface, (300, 200 + i * 50))
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
                        fade_out(screen)
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

def game_loop(screen, sound_enabled, joystick):
    clock = pygame.time.Clock()
    level = 1
    try:
        bg_image = load_image("background.jpg", size=(WIDTH, HEIGHT))
    except pygame.error:
        bg_image = pygame.Surface((WIDTH, HEIGHT))
        bg_image.fill(WHITE)
    running = True
    while running:
        grid, coins_list, enemy_count = get_level_data(level)
        all_sprites = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        coin_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()
        obstacle_group = pygame.sprite.Group()
        # Obstáculos del grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x].blocked:
                    obs = pygame.sprite.Sprite()
                    obs.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
                    obs.image.fill(BLACK)
                    obs.rect = obs.image.get_rect(topleft=(x * CELL_SIZE, y * CELL_SIZE))
                    obstacle_group.add(obs)
                    all_sprites.add(obs)
        # Obstáculos personalizados
        for _ in range(2):
            w = random.randint(60, 120)
            h = random.randint(40, 100)
            x = random.randint(150, WIDTH - w - 10)
            y = random.randint(150, HEIGHT - h - 10)
            shape = random.choice(["rectangle", "square"])
            from sprites import VariedObstacle
            custom_obs = VariedObstacle(x, y, w, h, shape)
            obstacle_group.add(custom_obs)
            all_sprites.add(custom_obs)
        player = Player()
        all_sprites.add(player)
        for coin in coins_list:
            coin_group.add(coin)
            all_sprites.add(coin)
        ai_tree = SelectorNode([
            SequenceNode([
                ConditionNode(condition_player_close),
                ActionNode(chase_action)
            ]),
            ActionNode(patrol_action)
        ])
        for _ in range(enemy_count):
            ex = random.randint(5, 20) * CELL_SIZE
            ey = random.randint(5, 15) * CELL_SIZE
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    now = pygame.time.get_ticks()
                    if now - player.last_shot_time > player.shoot_cooldown:
                        bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                        bullet_group.add(bullet)
                        all_sprites.add(bullet)
                        player.last_shot_time = now
            keys = get_combined_keys(joystick)
            player.move(keys, obstacle_group)
            for bullet in bullet_group:
                bullet.update()
                if (bullet.rect.right < 0 or bullet.rect.left > WIDTH or 
                    bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT):
                    bullet.kill()
            for enemy in enemy_group:
                enemy.move(player, grid, len(grid[0]), len(grid))
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
            screen.blit(bg_image, (0, 0))
            pygame.draw.rect(screen, GREEN, goal_rect)
            all_sprites.draw(screen)
            draw_text(screen, f"Monedas: {player.coins_collected}", 10, 10, RED)
            draw_health_bar(screen, WIDTH - 170, 10, player.health, 100, flash=player.is_flashing)
            draw_text(screen, f"Nivel: {level}", WIDTH - 150, 50, RED)
            draw_text(screen, f"Puntos: {player.score}", 10, 50, BLUE)
            pygame.display.flip()
            clock.tick(FPS)
            if player.health <= 0:
                game_over = True
        try:
            results_bg = load_image("results background.jpg", size=(WIDTH, HEIGHT))
        except pygame.error:
            results_bg = pygame.Surface((WIDTH, HEIGHT))
            results_bg.fill(WHITE)
        if win:
            if player.score >= 2000:
                achievement = "¡Medalla de Oro!"
            elif player.score >= 1000:
                achievement = "¡Medalla de Plata!"
            elif player.score >= 500:
                achievement = "¡Medalla de Bronce!"
            else:
                achievement = "Sin logros"
            end_message = "¡Ganaste el nivel!"
        else:
            end_message = "¡Perdiste!"
            achievement = "Sin logros"
        results_text = [
            (end_message, RED),
            (f"Puntuación: {player.score}", BLUE),
            (f"Logro: {achievement}", GREEN)
        ]
        line_height = 60
        total_text_height = len(results_text) * line_height
        start_y = (HEIGHT - total_text_height) // 2
        screen.blit(results_bg, (0, 0))
        font = pygame.font.Font(None, 36)
        for idx, (line, color) in enumerate(results_text):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, start_y + idx * line_height + line_height // 2))
            screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        if win:
            fade_out(screen)
            level += 1
            if level > 3:
                screen.fill(WHITE)
                draw_text(screen, "¡Has completado todos los niveles!", WIDTH // 2 - 200, HEIGHT // 2, RED)
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
        if game_over:
            return

def run_game():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print("Error al iniciar audio:", e)
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("New Rally X")
    sound_enabled = True
    if sound_enabled and load_music("musica.mp3", volume=0.5):
        play_music()
    show_story(screen)
    while True:
        choice, sound_enabled = main_menu(screen, sound_enabled, joystick)
        if choice == "start":
            game_loop(screen, sound_enabled, joystick)
        else:
            continue
