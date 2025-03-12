import os
import pygame

music_available = True

def load_music(path, volume=0.5):
    global music_available
    if not music_available:
        return
    if not os.path.exists(path):
        print(f"Archivo de música no encontrado: {path}")
        music_available = False
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
    except pygame.error as e:
        print(f"No se pudo cargar la música: {path}. Error: {e}")
        music_available = False

def play_music(loop=-1):
    if music_available:
        pygame.mixer.music.play(loop)

def stop_music():
    if music_available:
        pygame.mixer.music.stop()
