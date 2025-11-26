import pygame

keys_down = set()

def process_input(event):
    if event.type == pygame.KEYDOWN:
        keys_down.add(event.key)
    elif event.type == pygame.KEYUP:
        if event.key in keys_down:
            keys_down.remove(event.key)

def is_key_pressed(key):
    return key in keys_down
