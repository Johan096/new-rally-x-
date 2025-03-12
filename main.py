from src import game, settings, music

def main():
    sound_enabled = True
    game.show_story()
    choice, sound_enabled = game.main_menu(sound_enabled)
    if choice == "start":
        game.game_loop()

if __name__ == "__main__":
    main()
