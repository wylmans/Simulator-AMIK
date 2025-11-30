import pygame
from core.camera import camera

loaded = {}
sprites = []

class Sprite:
    def __init__(self, image, x, y):
        if image in loaded:
            self.image = loaded[image]
        else:
            self.image = pygame.image.load(image)
            loaded[image] = self.image

        self.x = x
        self.y = y
        sprites.append(self)

    def draw(self, screen):
        screen.blit(self.image, (self.x - camera.x, self.y - camera.y))  # HARUS PAKAI self.x self.y

    def update(self):
        print("update berjalan")
