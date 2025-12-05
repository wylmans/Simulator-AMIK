"""
Game Simulasi Mahasiswa - Complete Version
With Menu System, Save/Load, and Settings
"""

import pygame
import sys
from core import input as Input
from core.player import Player
from core.camera import create_screen, camera
from core.music import MusicManager
from core.npc import NPCManager, create_sample_npcs
from core.quest import QuestManager, CodeChallengeBox
from core.dialog import DialogueBox, EndingChoice
from core.ending import EndingScreen
from core.menu import MainMenu, PauseMenu, SettingsButton
from core.save_system import SaveSystem, GameSettings

# Map imports
from core.map import TileKinds, Map
from core.collision import MapCollision

USE_TILED = True
try:
    from core.tiled_map import TiledMap, TiledMapCollision
except ImportError:
    print("[WARNING] Tiled map tidak tersedia")
    USE_TILED = False

pygame.init()

# Initial screen setup
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, "Simulasi AMIK")
clock = pygame.time.Clock()

# Game systems
save_system = SaveSystem()
settings = GameSettings()

# Apply settings
is_fullscreen = settings.get("fullscreen", False)
if is_fullscreen:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    camera.width = SCREEN_WIDTH
    camera.height = SCREEN_HEIGHT

# Main menu
main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
main_menu.music_slider.value = settings.get("music_volume", 0.3) * 100
main_menu.sound_slider.value = settings.get("sound_volume", 0.6) * 100
main_menu.is_fullscreen = is_fullscreen
main_menu.fullscreen_toggle.text = f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}"

# Pause menu
pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_menu.music_slider.value = main_menu.music_slider.value
pause_menu.sound_slider.value = main_menu.sound_slider.value
pause_menu.is_fullscreen = main_menu.is_fullscreen
pause_menu.fullscreen_toggle.text = main_menu.fullscreen_toggle.text

# Settings button (gear icon) for in-game
settings_button = SettingsButton(SCREEN_WIDTH - 60, 20, size=50)

# Game state management
current_screen = "main_menu"  # "main_menu", "game", "ending"
game_state = "playing"
debug_mode = False

# Game objects (will be initialized when game starts)
player = None
npc_manager = None
quest_manager = None
dialogue_box = None
code_challenge_box = None
ending_choice = None
ending_screen = None
music_manager = None
map_collision = None
tiled_map = None
map_obj = None

current_challenge_quest_index = -1

print("=" * 60)
print("[GAME] SIMULASI MAHASISWA - AMIK")
print("=" * 60)


def initialize_game(player_name, load_save_data=None):
    """Initialize atau reset game"""
    global player, npc_manager, quest_manager, dialogue_box, code_challenge_box
    global ending_choice, ending_screen, music_manager, map_collision
    global tiled_map, map_obj, game_state, USE_TILED

    print("\n[GAME] Initializing game...")

    # Map setup
    if USE_TILED:
        print("Loading Tiled map...")
        try:
            tiled_map = TiledMap("maps/campus.tmx")
            map_collision = TiledMapCollision(tiled_map)
            spawns = tiled_map.get_spawn_points()
            player_spawn = spawns.get('player', (200, 100))
            print("[OK] Tiled map loaded!")
        except Exception as e:
            print(f"[ERROR] {e}")
            print("Falling back to old map...")
            USE_TILED = False

    if not USE_TILED:
        tile_kinds = [
            TileKinds("dirt", "images/dirt.png", False),
            TileKinds("grass", "images/grass.png", False),
            TileKinds("wood", "images/wood.png", False),
            TileKinds("water", "images/water.png", True),
            TileKinds("rock", "images/rock.png", True)
        ]
        map_obj = Map("maps/start.map", tile_kinds, 32)
        map_collision = MapCollision(map_obj)
        player_spawn = (200, 100)

    # Player setup
    if load_save_data:
        # Load from save
        player_data = load_save_data["player"]
        player_name = player_data["name"]
        spawn_x = player_data["x"]
        spawn_y = player_data["y"]
    else:
        spawn_x, spawn_y = player_spawn

    player = Player(
        "karakter/Kang_azhar.png",
        "karakter/Kang_azhar.json",
        spawn_x, spawn_y,
        player_name
    )

    # Load directional sprites
    try:
        player.set_directional_sprite("left", "karakter/Kang_azhar_kiri.png", "karakter/Kang_azhar_kiri.json")
        player.set_directional_sprite("right", "karakter/Kang_azhar_kanan.png", "karakter/Kang_azhar_kanan.json")
        player.set_directional_sprite("up", "karakter/Kang_azhar_atas.png", "karakter/Kang_azhar_atas.json")
        player.set_directional_sprite("down", "karakter/Kang_azhar_bawah.png", "karakter/Kang_azhar_bawah.json")
        player.set_idle_directional_sprite("left", "karakter/Kang_azhar_idle_kiri.png", "karakter/Kang_azhar_idle_kiri.json")
        player.set_idle_directional_sprite("right", "karakter/Kang_azhar_idle_kanan.png", "karakter/Kang_azhar_idle_kanan.json")
    except Exception as e:
        print(f"[WARNING] Some sprites not loaded: {e}")

    # Music
    playlist = ["music/Caffeine.mp3", "music/Dorm.mp3"]
    music_volume = settings.get("music_volume", 0.3)
    music_manager = MusicManager(playlist, volume=music_volume, fade_duration=2000)
    music_manager.play()

    # NPCs
    npc_manager = NPCManager()
    sample_npcs = create_sample_npcs()

    if USE_TILED and tiled_map:
        spawns = tiled_map.get_spawn_points()
        for npc in sample_npcs:
            npc_spawn_key = f"npc_{npc.name.lower().replace(' ', '_')}"
            if npc_spawn_key in spawns:
                npc.x, npc.y = spawns[npc_spawn_key]
            npc_manager.add_npc(npc)
    else:
        for npc in sample_npcs:
            npc_manager.add_npc(npc)

    # Quest system
    quest_manager = QuestManager()

    # Load quest progress if from save
    if load_save_data:
        quest_data = load_save_data.get("quest", {})
        quest_manager.total_progress = quest_data.get("total_progress", 0)
        # Note: Active quests tidak di-restore untuk simplicity
        # Bisa ditambahkan nanti jika dibutuhkan

    dialogue_box = DialogueBox()
    code_challenge_box = CodeChallengeBox()
    ending_choice = EndingChoice()
    ending_screen = EndingScreen()

    game_state = "playing"

    print("[OK] Game initialized!")
    print(f"[OK] Player: {player_name}")
    print(f"[OK] Position: ({spawn_x}, {spawn_y})")
    print("=" * 60)


def toggle_fullscreen():
    """Toggle fullscreen mode"""
    global screen, is_fullscreen

    is_fullscreen = not is_fullscreen
    settings.set("fullscreen", is_fullscreen)

    if is_fullscreen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    camera.width = SCREEN_WIDTH
    camera.height = SCREEN_HEIGHT

    # Update menu toggles
    main_menu.is_fullscreen = is_fullscreen
    main_menu.fullscreen_toggle.text = f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}"
    pause_menu.is_fullscreen = is_fullscreen
    pause_menu.fullscreen_toggle.text = main_menu.fullscreen_toggle.text


def start_quest_challenge(quest_index):
    """Start code challenge untuk quest"""
    global game_state, current_challenge_quest_index

    if game_state == "playing" and not dialogue_box.active:
        quests = quest_manager.get_quest_list()
        if 0 <= quest_index < len(quests):
            quest = quests[quest_index]
            if quest.code_challenge:
                code_challenge_box.show(quest.code_challenge)
                game_state = "code_challenge"
                current_challenge_quest_index = quest_index


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== MAIN MENU =====
        if current_screen == "main_menu":
            result = main_menu.handle_event(event)

            if result == "exit":
                running = False

            elif result == "start_game":
                player_name = main_menu.player_name

                # Check if load save
                if save_system.save_exists():
                    save_data = save_system.load_game()
                    if save_data:
                        initialize_game(player_name, save_data)
                    else:
                        initialize_game(player_name)
                else:
                    initialize_game(player_name)

                current_screen = "game"

            elif result == "toggle_fullscreen":
                toggle_fullscreen()

            # Update settings from menu
            settings.set("music_volume", main_menu.music_slider.get_value())
            settings.set("sound_volume", main_menu.sound_slider.get_value())

        # ===== IN-GAME =====
        elif current_screen == "game":
            # Pause menu
            if pause_menu.active:
                result = pause_menu.handle_event(event)

                if result == "resume":
                    pause_menu.hide()

                elif result == "save":
                    success = save_system.save_game(player, quest_manager, game_state)
                    pause_menu.show_save_notification(success)

                elif result == "load":
                    # Load game from save
                    if save_system.save_exists():
                        save_data = save_system.load_game()
                        if save_data:
                            initialize_game(player.name, save_data)
                            pause_menu.hide()
                            pause_menu.show_save_notification(True)
                    else:
                        pause_menu.show_save_notification(False)

                elif result == "main_menu":
                    # Return to main menu
                    pause_menu.hide()
                    current_screen = "main_menu"
                    main_menu.state = "main"
                    if music_manager:
                        music_manager.stop()

                elif result == "exit":
                    # Exit game
                    running = False

                elif result == "toggle_fullscreen":
                    toggle_fullscreen()

                # Update settings
                settings.set("music_volume", pause_menu.music_slider.get_value())
                settings.set("sound_volume", pause_menu.sound_slider.get_value())
                if music_manager:
                    music_manager.set_volume(pause_menu.music_slider.get_value())

            # Settings button click (when not in pause menu)
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
                if settings_button.is_clicked(event):
                    pause_menu.show()
                    pause_menu.music_slider.value = settings.get("music_volume", 0.3) * 100
                    pause_menu.sound_slider.value = settings.get("sound_volume", 0.6) * 100

            # Game controls
            elif event.type == pygame.KEYDOWN:
                Input.keys_down.add(event.key)

                # ESC to pause
                if event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        pause_menu.show()
                        pause_menu.music_slider.value = settings.get("music_volume", 0.3) * 100
                        pause_menu.sound_slider.value = settings.get("sound_volume", 0.6) * 100
                    elif game_state == "code_challenge":
                        code_challenge_box.hide()
                        game_state = "playing"
                        current_challenge_quest_index = -1

                # F3 for debug
                if event.key == pygame.K_F3:
                    debug_mode = not debug_mode

                # Code challenge controls
                if game_state == "code_challenge":
                    if event.key == pygame.K_UP:
                        code_challenge_box.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        code_challenge_box.move_selection(1)
                    elif event.key == pygame.K_PAGEUP:
                        code_challenge_box.scroll_code(-1)
                    elif event.key == pygame.K_PAGEDOWN:
                        code_challenge_box.scroll_code(1)
                    elif event.key == pygame.K_RETURN:
                        code_challenge_box.submit_answer()

                # Ending choice
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

                # Ending screen
                elif game_state == "ending_screen":
                    if event.key == pygame.K_ESCAPE:
                        current_screen = "main_menu"
                        music_manager.stop()
                    elif event.key == pygame.K_r:
                        quest_manager.reset_progress()
                        ending_screen.hide()
                        game_state = "playing"

                # Playing state
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
                            music_manager.set_volume(settings.get("music_volume", 0.3))

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
                                    quest_manager.start_quest(quest_text, nearby_npc.name)
                                else:
                                    warning = f"Kamu sudah punya {quest_manager.MAX_QUESTS} quest!"
                                    dialogue_box.show(nearby_npc.name, warning, music_manager)

                    # Quest hotkeys
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

            if music_manager:
                music_manager.handle_music_end(event)

    # ===== UPDATE =====
    if current_screen == "main_menu":
        main_menu.update()

    elif current_screen == "game":
        if pause_menu.active:
            pause_menu.update()
        else:
            dt = clock.get_time()

            if game_state == "playing":
                if not dialogue_box.active:
                    player.update(map_collision, dt)
                else:
                    player.sprite.update(dt)
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

    # ===== DRAW =====
    if current_screen == "main_menu":
        main_menu.draw(screen)

    elif current_screen == "game":
        screen.fill((30, 150, 50))

        if game_state == "ending_screen":
            ending_screen.draw(screen, quest_manager.completed_quests)
        else:
            # Draw map
            if USE_TILED and tiled_map:
                tiled_map.draw(screen)
            elif map_obj:
                map_obj.draw(screen)

            # Draw NPCs & player
            npc_manager.draw_all(screen, player)
            player.draw(screen)

            # UI
            if game_state in ["playing", "code_challenge"]:
                quest_manager.draw_progress_bar(screen)
                quest_manager.draw_quest_list(screen, 10, 60)
                dialogue_box.draw(screen)

                if game_state == "code_challenge":
                    code_challenge_box.draw(screen)

            elif game_state == "ending_choice":
                ending_choice.draw(screen)

            # Debug
            if debug_mode:
                map_collision.draw_debug(screen)
                player.draw_debug(screen)

                if USE_TILED and tiled_map:
                    tiled_map.draw_spawns_debug(screen)

                font = pygame.font.Font(None, 20)
                fps = int(clock.get_fps())
                debug_texts = [
                    f"FPS: {fps}",
                    f"Player: ({int(player.x)}, {int(player.y)})",
                    f"Quests: {len(quest_manager.active_quests)}/5",
                    f"Progress: {quest_manager.total_progress}/100"
                ]

                for i, text in enumerate(debug_texts):
                    surf = font.render(text, True, (255, 255, 0))
                    screen.blit(surf, (SCREEN_WIDTH - 200, 10 + i * 20))

        # Pause menu overlay
        pause_menu.draw(screen)

        # Settings button (when not paused)
        if not pause_menu.active and game_state == "playing":
            mouse_pos = pygame.mouse.get_pos()
            settings_button.update(mouse_pos)
            settings_button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Cleanup
print("\n[GAME] Shutting down...")
if music_manager:
    music_manager.stop()
pygame.quit()
sys.exit()
