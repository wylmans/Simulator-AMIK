import pygame


class Camera:
	"""Simple camera container replacing use of pygame.Rect so we can add zoom."""

	def __init__(self, x=0, y=0, width=0, height=0, zoom=1.0):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.zoom = zoom


camera = Camera()


def create_screen(width, height, title):
	pygame.display.set_caption(title)

	screen = pygame.display.set_mode((width, height))
	camera.width = width
	camera.height = height
	return screen
