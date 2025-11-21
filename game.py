import pygame
import input
from player import Player
from sprite import sprites

pygame.init()

#setup
pygame.display.set_caption("Simulasi - AMIK")
screen = pygame.display.set_mode((800,600))
clear_color = (30, 150, 50)
running = True
player= Player("models/image.png", 0, 0)

#game loop
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			input.keys_down.add(event.key)
		elif event.type == pygame.KEYUP:
			input.keys_down.remove(event.key)

	#Update code
	player.update()

	#Draw Code
	screen.fill(clear_color)
	for s in sprites:
		s.draw(screen)

	pygame.display.flip()

pygame.quit()