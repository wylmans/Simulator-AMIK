import pygame
import input
from player import Player
from sprite import sprites
from map import TileKinds, Map
from camera import create_screen
from music import MusicManager  # Import music manager

pygame.init()

#setup
screen = create_screen(800, 600, "Simulasi AMIK")
clear_color = (30, 150, 50)
running = True
player = Player("models/image.png", 200, 100)
tile_kinds = [
	TileKinds("dirt", "images/dirt.png", False),
	TileKinds("grass", "images/grass.png", False),
	TileKinds("wood", "images/wood.png", False),
	TileKinds("water", "images/water.png", False),
	TileKinds("rock", "images/rock.png", False)
]

map = Map("maps/start.map", tile_kinds, 32)

# Setup musik - Ganti dengan path lagu Anda
playlist = [
	"music/Caffeine.mp3",
	"music/Dorm.mp3"
]

# Inisialisasi music manager (volume 0.5, fade 2 detik)
music_manager = MusicManager(playlist, volume=0.5, fade_duration=2000)
music_manager.play()  # Mulai memutar musik

#game loop
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			input.keys_down.add(event.key)

			# Kontrol musik (opsional)
			if event.key == pygame.K_n:  # N untuk next track
				music_manager.next_track()
			elif event.key == pygame.K_p:  # P untuk previous track
				music_manager.previous_track()
			elif event.key == pygame.K_m:  # M untuk mute/unmute
				if music_manager.volume > 0:
					music_manager.set_volume(0)
				else:
					music_manager.set_volume(0.5)

		elif event.type == pygame.KEYUP:
			input.keys_down.remove(event.key)

		# Handle musik selesai (auto-play lagu berikutnya)
		music_manager.handle_music_end(event)

	#Update code
	player.update()

	#Draw Code
	screen.fill(clear_color)
	map.draw(screen)
	for s in sprites:
		s.draw(screen)

	pygame.display.flip()
	pygame.time.delay(8)

# Stop musik dengan fade out saat keluar
music_manager.stop()
pygame.quit()
