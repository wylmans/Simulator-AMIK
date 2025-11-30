import pygame
from core.sprite import Sprite
from core.input import is_key_pressed
from core.camera import camera

class Player(Sprite):
	def __init__(self, image, x, y):
		super().__init__(image, x, y)
		self.movement_speed = 2
	def update(self):
		if is_key_pressed(pygame.K_w):
			self.y -= self.movement_speed
		if is_key_pressed(pygame.K_a):
			self.x -= self.movement_speed
		if is_key_pressed(pygame.K_s):
			self.y += self.movement_speed
		if is_key_pressed(pygame.K_d):
			self.x += self.movement_speed
		camera.x = self.x - camera.width / 2 + self.image.get_width()/2
		camera.y = self.y - camera.height / 2 + self.image.get_height()/2
