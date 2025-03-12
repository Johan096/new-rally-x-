# resources.py
import os
import pygame
from src.settings import RED

_image_cache = {}

def load_image(path, size=None, fallback_size=(50, 50)):
    """Carga una imagen y la escala si se especifica. Utiliza caché para mejorar el rendimiento."""
    if path in _image_cache:
        image = _image_cache[path]
    else:
        try:
            image = pygame.image.load(path).convert_alpha()
            _image_cache[path] = image
        except pygame.error:
            print(f"No se pudo cargar {path}. Usando imagen de reemplazo.")
            image = pygame.Surface(fallback_size)
            image.fill(RED)
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_music(path, volume=0.5):
    """Carga la música de fondo."""
    if not os.path.exists(path):
        print(f"Archivo de música no encontrado: {path}")
        return False
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        return True
    except pygame.error as e:
        print(f"Error al cargar música: {path}. Error: {e}")
        return False

def play_music(loop=-1):
    pygame.mixer.music.play(loop)

def stop_music():
    pygame.mixer.music.stop()
