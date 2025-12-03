import pygame
from core import input as Input
from core.player import Player
from core.sprite import sprites
from core.map import TileKinds, Map
from core.camera import create_screen
from core.collision import MapCollision
from core.music import MusicManager
from core.npc import NPCManager, create_sample_npcs
from core.quest import QuestManager, CodeChallengeBox
from core.dialog import DialogueBox, EndingChoice
from core.ending import EndingScreen

pygame.init()

# Setup
screen = create_screen(800, 600, "Simulasi AMIK")
clear_color = (30, 150, 50)
running = True
clock = pygame.time.Clock()

# Player
player = Player("models/image.png", 200, 100)

# Map
tile_kinds = [
    TileKinds("dirt", "images/dirt.png", False),
    TileKinds("grass", "images/grass.png", False),
    TileKinds("wood", "images/wood.png", False),
    TileKinds("water", "images/water.png", True),
    TileKinds("rock", "images/rock.png", True)
]

map_obj = Map("maps/start.map", tile_kinds, 32)
map_collision = MapCollision(map_obj)

# Setup musik
playlist = [
    "music/Caffeine.mp3",
    "music/Dorm.mp3"
]

music_manager = MusicManager(playlist, volume=0.3, fade_duration=2000)
music_manager.play()

# ==================== SISTEM NPC & QUEST ====================
npc_manager = NPCManager()
sample_npcs = create_sample_npcs()
for npc in sample_npcs:
    npc_manager.add_npc(npc)

quest_manager = QuestManager()
dialogue_box = DialogueBox()
code_challenge_box = CodeChallengeBox()
ending_choice = EndingChoice()
ending_screen = EndingScreen()

# Game state
game_state = "playing"
current_challenge_quest_index = -1

# Helper function (must be defined before the main loop since the loop can call it)
def start_quest_challenge(quest_index):
    """Start code challenge untuk quest dengan index tertentu"""
    global game_state, current_challenge_quest_index

    if game_state == "playing" and not dialogue_box.active:
        quests = quest_manager.get_quest_list()
        if 0 <= quest_index < len(quests):
            quest = quests[quest_index]
            if quest.code_challenge:
                code_challenge_box.show(quest.code_challenge)
                # switch into code_challenge state
                # note: current_challenge_quest_index tracks which quest we're working on
                game_state = "code_challenge"
                current_challenge_quest_index = quest_index
                print(f"🐛 Debug challenge: Quest {quest_index + 1}")

print("=== KONTROL GAME ===")
print("WASD: Gerak")
print("E atau SPACE: Bicara dengan dosen")
print("1-5: Kerjakan quest (tekan angka sesuai nomor quest)")
print("N/P: Next/Previous music")
print("M: Mute/Unmute")
print("==================")

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            Input.keys_down.add(event.key)

            # ====== CODE CHALLENGE STATE ======
            if game_state == "code_challenge":
                if event.key == pygame.K_ESCAPE:
                    code_challenge_box.hide()
                    game_state = "playing"
                    current_challenge_quest_index = -1

                elif event.key == pygame.K_UP:
                    code_challenge_box.move_selection(-1)

                elif event.key == pygame.K_DOWN:
                    code_challenge_box.move_selection(1)

                elif event.key == pygame.K_RETURN:
                    code_challenge_box.submit_answer()

            # ====== ENDING CHOICE STATE ======
            elif game_state == "ending_choice":
                if event.key == pygame.K_UP:
                    ending_choice.move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    ending_choice.move_selection(1)
                elif event.key == pygame.K_RETURN:
                    choice = ending_choice.get_choice()
                    ending_choice.hide()
                    if choice == 0:
                        game_state = "playing"
                    else:
                        quest_manager.mark_game_completed()
                        ending_screen.show()
                        game_state = "ending_screen"

            # ====== ENDING SCREEN STATE ======
            elif game_state == "ending_screen":
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    quest_manager.reset_progress()
                    ending_screen.hide()
                    game_state = "playing"

            # ====== PLAYING STATE ======
            elif game_state == "playing":
                # Music controls
                if event.key == pygame.K_n:
                    music_manager.next_track()
                elif event.key == pygame.K_p:
                    music_manager.previous_track()
                elif event.key == pygame.K_m:
                    if music_manager.volume > 0:
                        music_manager.set_volume(0)
                    else:
                        music_manager.set_volume(0.3)

                # NPC interaction
                elif event.key in [pygame.K_e, pygame.K_SPACE]:
                    if dialogue_box.active:
                        if dialogue_box.is_typing_complete():
                            dialogue_box.hide()
                        else:
                            dialogue_box.skip_typing()
                    else:
                        nearby_npc = npc_manager.get_nearby_npc(player)
                        if nearby_npc:
                            if quest_manager.can_accept_quest():
                                quest_text = nearby_npc.get_random_dialogue()
                                dialogue_box.show(nearby_npc.name, quest_text, music_manager)
                                success = quest_manager.start_quest(quest_text, nearby_npc.name)
                                if success:
                                    print(f"✅ Quest diterima: {nearby_npc.name}")
                            else:
                                warning = f"Kamu sudah punya {quest_manager.MAX_QUESTS} quest! Selesaikan dulu."
                                dialogue_box.show(nearby_npc.name, warning, music_manager)

                # Quest challenge hotkeys (1-5)
                elif event.key == pygame.K_1:
                    start_quest_challenge(0)
                elif event.key == pygame.K_2:
                    start_quest_challenge(1)
                elif event.key == pygame.K_3:
                    start_quest_challenge(2)
                elif event.key == pygame.K_4:
                    start_quest_challenge(3)
                elif event.key == pygame.K_5:
                    start_quest_challenge(4)

        elif event.type == pygame.KEYUP:
            if event.key in Input.keys_down:
                Input.keys_down.remove(event.key)

        music_manager.handle_music_end(event)

    # ====== UPDATE ======
    if game_state == "playing":
        if not dialogue_box.active:
            player.update(map_collision)
        dialogue_box.update()

    elif game_state == "code_challenge":
        result = code_challenge_box.update()

        if result == "correct":
            reached_100 = quest_manager.complete_quest(current_challenge_quest_index)
            code_challenge_box.hide()
            game_state = "playing"
            current_challenge_quest_index = -1

            if reached_100:
                game_state = "ending_choice"
                ending_choice.show()

        elif result == "failed":
            quest_manager.fail_quest(current_challenge_quest_index)
            code_challenge_box.hide()
            game_state = "playing"
            current_challenge_quest_index = -1

    elif game_state == "ending_screen":
        ending_screen.update()

    # ====== DRAW ======
    screen.fill(clear_color)

    if game_state == "ending_screen":
        ending_screen.draw(screen, quest_manager.completed_quests)
    else:
        map_obj.draw(screen)
        npc_manager.draw_all(screen, player)

        for s in sprites:
            s.draw(screen)

        if game_state in ["playing", "code_challenge"]:
            quest_manager.draw_progress_bar(screen)
            quest_manager.draw_quest_list(screen, 10, 60)
            dialogue_box.draw(screen)

            if game_state == "code_challenge":
                code_challenge_box.draw(screen)

        elif game_state == "ending_choice":
            ending_choice.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Helper function


music_manager.stop()
pygame.quit()
