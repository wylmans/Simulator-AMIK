import pygame
from core import input as Input
from core.player import Player
from core.sprite import sprites
from core.map import TileKinds, Map
from core.camera import create_screen
from core.music import MusicManager
# Import sistem NPC baru
from core.npc import NPCManager, create_sample_npcs
from core.quest import QuestManager
from core.dialog import DialogueBox, EndingChoice
from core.ending import EndingScreen

# OPTIONAL: Import coordinate helper untuk cari posisi NPC
# Uncomment baris di bawah jika ingin melihat koordinat player
# from coordinate_helper import show_coordinates

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

# Setup musik
playlist = [
	"music/Caffeine.mp3",
	"music/Dorm.mp3"
]

# PENTING: Turunkan volume musik agar sound effect terdengar jelas!
music_manager = MusicManager(playlist, volume=0.3, fade_duration=2000)  # Volume 30% (turun dari 50%)
music_manager.play()

# ==================== SISTEM NPC & QUEST ====================
# Inisialisasi NPC Manager
npc_manager = NPCManager()

# Tambahkan sample NPCs (SESUAIKAN POSISI DENGAN MAP ANDA!)
sample_npcs = create_sample_npcs()
for npc in sample_npcs:
	npc_manager.add_npc(npc)

# Inisialisasi Quest Manager
quest_manager = QuestManager()

# Inisialisasi Dialogue System
dialogue_box = DialogueBox()
ending_choice = EndingChoice()
ending_screen = EndingScreen()

# Game state
game_state = "playing"  # "playing", "ending_choice", "ending_screen"

print("=== KONTROL GAME ===")
print("Arrow Keys: Gerak")
print("E atau SPACE: Bicara dengan dosen (saat dekat)")
print("Q: Selesaikan quest aktif")
print("N: Next music track")
print("P: Previous music track")
print("M: Mute/Unmute music")
print("==================")

#game loop
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.KEYDOWN:
			Input.keys_down.add(event.key)

			# ====== KONTROL BERDASARKAN GAME STATE ======

			if game_state == "ending_choice":
				# Kontrol untuk ending choice
				if event.key == pygame.K_UP:
					ending_choice.move_selection(-1)
				elif event.key == pygame.K_DOWN:
					ending_choice.move_selection(1)
				elif event.key == pygame.K_RETURN:
					choice = ending_choice.get_choice()
					ending_choice.hide()
					if choice == 0:  # Lanjutkan bermain
						game_state = "playing"
					else:  # Lihat ending
						quest_manager.mark_game_completed()
						ending_screen.show()
						game_state = "ending_screen"

			elif game_state == "ending_screen":
				# Kontrol untuk ending screen
				if event.key == pygame.K_ESCAPE:
					running = False
				elif event.key == pygame.K_r:
					# Reset dan main lagi
					quest_manager.reset_progress()
					ending_screen.hide()
					game_state = "playing"

			elif game_state == "playing":
				# Kontrol musik
				if event.key == pygame.K_n:
					music_manager.next_track()
				elif event.key == pygame.K_p:
					music_manager.previous_track()
				elif event.key == pygame.K_m:
					if music_manager.volume > 0:
						music_manager.set_volume(0)
					else:
						music_manager.set_volume(0.5)

				# Interaksi dengan NPC (E atau SPACE)
				elif event.key in [pygame.K_e, pygame.K_SPACE]:
					if dialogue_box.active:
						# Jika dialog aktif dan typing selesai, tutup dialog
						if dialogue_box.is_typing_complete():
							dialogue_box.hide()
						else:
							# Skip typing animation
							dialogue_box.skip_typing()
					else:
						# Cek apakah ada NPC terdekat
						nearby_npc = npc_manager.get_nearby_npc(player)
						if nearby_npc:
							# Tampilkan dialog dan mulai quest
							quest_text = nearby_npc.get_random_dialogue()
							# Pass music_manager agar volume musik bisa diturunkan
							dialogue_box.show(nearby_npc.name, quest_text, music_manager)
							quest_manager.start_quest(quest_text, nearby_npc.name)

				# Complete quest (Q) - hanya jika dialog tidak aktif
				elif event.key == pygame.K_q and not dialogue_box.active:
					if quest_manager.current_quest:
						reached_100 = quest_manager.complete_quest()
						if reached_100:
							# Tampilkan ending choice
							game_state = "ending_choice"
							ending_choice.show()

		elif event.type == pygame.KEYUP:
			Input.keys_down.remove(event.key)

		# Handle musik selesai
		music_manager.handle_music_end(event)

	# ====== UPDATE CODE ======
	if game_state == "playing":
		# Player hanya bisa bergerak jika dialog TIDAK aktif
		if not dialogue_box.active:
			player.update()
		dialogue_box.update()
	elif game_state == "ending_screen":
		ending_screen.update()

	# ====== DRAW CODE ======
	screen.fill(clear_color)

	if game_state == "ending_screen":
		# Hanya tampilkan ending screen
		ending_screen.draw(screen, quest_manager.completed_quests)
	else:
		# Render game normal
		map.draw(screen)

		# Draw NPCs
		npc_manager.draw_all(screen, player)

		# Draw sprites (termasuk player)
		for s in sprites:
			s.draw(screen)

		# Draw UI
		if game_state == "playing":
			# Progress bar di TENGAH ATAS (posisi otomatis)
			quest_manager.draw_progress_bar(screen)

			# Current quest di kiri atas (jika ada)
			quest_manager.draw_current_quest(screen, 10, 60)

			# Dialogue box
			dialogue_box.draw(screen)

			# OPTIONAL: Tampilkan koordinat player (untuk cari posisi NPC)
			# Uncomment baris di bawah untuk melihat koordinat
			# show_coordinates(screen, player)

		elif game_state == "ending_choice":
			# Tampilkan ending choice overlay
			ending_choice.draw(screen)

	pygame.display.flip()
	pygame.time.delay(8)

# Stop musik dengan fade out saat keluar
music_manager.stop()
pygame.quit()
