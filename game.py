"""
Game Simulasi Mahasiswa - Complete Version
With Menu System, Save/Load, and Settings
FIXED: Fullscreen & Resolution bugs
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
from core.menu import MainMenu, PauseMenu
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

# Get available display modes from system
def get_available_resolutions():
    """Get list of supported resolutions from the display"""
    modes = pygame.display.list_modes()
    if modes == -1:  # All resolutions supported
        # Return common 16:9 resolutions
        return [
            (1920, 1080),
            (1680, 1050),
            (1600, 900),
            (1440, 900),
            (1366, 768),
            (1280, 720),
            (1080, 720),
            (960, 540)
        ]
    else:
        # Filter for 16:9 and 16:10 aspect ratios
        filtered = []
        for width, height in modes:
            aspect = width / height
            # Accept 16:9 (1.777) and 16:10 (1.6)
            if 1.5 <= aspect <= 1.8:
                filtered.append((width, height))
        return filtered if filtered else modes

# Get system's current resolution
info = pygame.display.Info()
SYSTEM_WIDTH = info.current_w
SYSTEM_HEIGHT = info.current_h

# Initial screen setup
save_system = SaveSystem()
settings = GameSettings()

# Load saved resolution or use default
SCREEN_WIDTH = settings.get("resolution_width", 1080)
SCREEN_HEIGHT = settings.get("resolution_height", 720)

# Ensure resolution is valid
available_resolutions = get_available_resolutions()
if (SCREEN_WIDTH, SCREEN_HEIGHT) not in available_resolutions:
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 720

screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, "Simulasi AMIK")
clock = pygame.time.Clock()

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

# Add available resolutions to menu if it has resolution support
if hasattr(main_menu, 'available_resolutions'):
    main_menu.available_resolutions = available_resolutions
    main_menu.current_resolution_index = 0
    # Find current resolution in list
    for i, (w, h) in enumerate(available_resolutions):
        if w == SCREEN_WIDTH and h == SCREEN_HEIGHT:
            main_menu.current_resolution_index = i
            break
    if hasattr(main_menu, 'update_resolution_text'):
        main_menu.update_resolution_text()

# Pause menu
pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_menu.music_slider.value = main_menu.music_slider.value
pause_menu.sound_slider.value = main_menu.sound_slider.value
pause_menu.is_fullscreen = main_menu.is_fullscreen
pause_menu.fullscreen_toggle.text = main_menu.fullscreen_toggle.text

# Game state management
current_screen = "main_menu"  # "main_menu", "game", "ending"
game_state = "playing"
debug_mode = False

# New-game warning modal state
newgame_warning_active = False
newgame_warning_seconds = 3
newgame_warning_timer = 0
newgame_pending_player_name = ""

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
print(f"[INFO] System Resolution: {SYSTEM_WIDTH}x{SYSTEM_HEIGHT}")
print(f"[INFO] Game Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"[INFO] Available Resolutions: {len(available_resolutions)}")
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
        "karakter/mahasiswa.png",
        "karakter/mahasiswa.json",
        spawn_x, spawn_y,
        player_name
    )

    # Load directional sprites
    try:
        player.set_directional_sprite("left", "karakter/mahasiswa_kiri.png", "karakter/mahasiswa_kiri.json")
        player.set_directional_sprite("right", "karakter/mahasiswa_kanan.png", "karakter/mahasiswa_kanan.json")
        player.set_directional_sprite("up", "karakter/mahasiswa_atas.png", "karakter/mahasiswa_atas.json")
        player.set_directional_sprite("down", "karakter/mahasiswa_bawah.png", "karakter/mahasiswa_bawah.json")
        player.set_idle_directional_sprite("left", "karakter/mahasiswa_idle_kiri.png", "karakter/mahasiswa_idle_kiri.json")
        player.set_idle_directional_sprite("right", "karakter/mahasiswa_idle_kanan.png", "karakter/Kang_azhar_idle_kanan.json")
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


def apply_settings(new_width, new_height, new_fullscreen):
    """Apply new settings and recreate screen"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, is_fullscreen
    global main_menu, pause_menu

    print(f"\n[SETTINGS] Applying new settings...")
    print(f"[SETTINGS] Resolution: {new_width}x{new_height}")
    print(f"[SETTINGS] Fullscreen: {new_fullscreen}")

    # Save old values
    old_music_volume = settings.get("music_volume", 0.3)
    old_sound_volume = settings.get("sound_volume", 0.6)
    if main_menu:
        old_music_volume = main_menu.music_slider.value / 100
        old_sound_volume = main_menu.sound_slider.value / 100

    # Update globals
    SCREEN_WIDTH = new_width
    SCREEN_HEIGHT = new_height
    is_fullscreen = new_fullscreen

    # Save to settings
    settings.set("resolution_width", SCREEN_WIDTH)
    settings.set("resolution_height", SCREEN_HEIGHT)
    settings.set("fullscreen", is_fullscreen)

    # Recreate screen with new settings
    flags = 0
    if is_fullscreen:
        flags = pygame.FULLSCREEN

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    except Exception:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Simulasi AMIK")

    # Use actual surface size (handles DPI/scaling / compositor differences)
    real_w, real_h = screen.get_size()
    SCREEN_WIDTH = real_w
    SCREEN_HEIGHT = real_h

    # Update camera
    camera.width = SCREEN_WIDTH
    camera.height = SCREEN_HEIGHT

    # Recreate menus with new resolution - this ensures they're centered correctly
    main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    main_menu.music_slider.value = old_music_volume * 100
    main_menu.sound_slider.value = old_sound_volume * 100
    main_menu.is_fullscreen = is_fullscreen
    main_menu.fullscreen_toggle.text = f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}"

    # Update available resolutions in menu (if supported)
    if hasattr(main_menu, 'available_resolutions'):
        main_menu.available_resolutions = available_resolutions
        main_menu.current_resolution_index = 0
        for i, (w, h) in enumerate(available_resolutions):
            if w == SCREEN_WIDTH and h == SCREEN_HEIGHT:
                main_menu.current_resolution_index = i
                break
        if hasattr(main_menu, 'update_resolution_text'):
            try:
                main_menu.update_resolution_text()
            except Exception:
                pass

    pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    pause_menu.music_slider.value = old_music_volume * 100
    pause_menu.sound_slider.value = old_sound_volume * 100
    pause_menu.is_fullscreen = is_fullscreen
    pause_menu.fullscreen_toggle.text = f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}"

    print("[OK] Settings applied!")
    print(f"[OK] Screen recreated: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"[OK] Menus recreated and centered")


def toggle_fullscreen():
    """Toggle fullscreen mode (legacy function, use apply_settings instead)"""
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
    pause_menu.fullscreen_toggle.text = f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}"


def start_quest_challenge(quest_index):
    """Start code challenge for a quest"""
    global game_state, current_challenge_quest_index

    if not quest_manager:
        return

    if 0 <= quest_index < len(quest_manager.active_quests):
        quest = quest_manager.active_quests[quest_index]
        # Quest is a `Quest` object; show its code_challenge payload
        try:
            code_challenge_box.show(quest.code_challenge)
        except Exception:
            # Fallback if attribute missing
            try:
                code_challenge_box.show(quest["code_challenge"])
            except Exception:
                pass
        game_state = "code_challenge"
        current_challenge_quest_index = quest_index


# ===== MAIN LOOP =====
running = True
while running:
    # ===== EVENTS =====
    for event in pygame.event.get():
        # Keep input state consistent
        try:
            Input.process_input(event)
        except Exception:
            pass
        if event.type == pygame.QUIT:
            running = False

        # Main menu events
        if current_screen == "main_menu":
            # Handle modal events FIRST (before main menu)
            if newgame_warning_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    modal_w, modal_h = 700, 220
                    modal_x = (SCREEN_WIDTH - modal_w) // 2
                    modal_y = (SCREEN_HEIGHT - modal_h) // 2

                    btn_w, btn_h = 140, 48
                    gap = 20
                    ok_x = modal_x + modal_w - btn_w * 2 - gap * 2
                    ok_y = modal_y + modal_h - btn_h - gap
                    cancel_x = modal_x + modal_w - btn_w - gap
                    cancel_y = ok_y

                    # Check OK button (only if countdown finished)
                    if newgame_warning_timer == 0:
                        if ok_x <= mx <= ok_x + btn_w and ok_y <= my <= ok_y + btn_h:
                            newgame_warning_active = False
                            initialize_game(newgame_pending_player_name)
                            current_screen = "game"

                    # Check Cancel button
                    if cancel_x <= mx <= cancel_x + btn_w and cancel_y <= my <= cancel_y + btn_h:
                        newgame_warning_active = False
                        newgame_pending_player_name = ""
                # Don't process other events when modal is active
                continue

            # Process main menu events when modal is not active
            result = main_menu.handle_event(event)

            if result in ("new_game", "start_game"):
                # Get player name from menu
                player_name = "Player"
                if hasattr(main_menu, 'player_name') and main_menu.player_name:
                    player_name = main_menu.player_name
                elif hasattr(main_menu, 'name_input') and hasattr(main_menu.name_input, 'text'):
                    player_name = main_menu.name_input.text or "Player"

                # Fallback: check for input field text directly
                if hasattr(main_menu, 'name_input'):
                    input_text = main_menu.name_input.text if hasattr(main_menu.name_input, 'text') else ""
                    if input_text and input_text.strip():
                        player_name = input_text.strip()

                print(f"[DEBUG] New game - Player name: '{player_name}'")

                # Show new-game warning modal if save exists
                if save_system.save_exists():
                    print("[DEBUG] Save exists, showing modal")
                    newgame_warning_active = True
                    newgame_warning_timer = newgame_warning_seconds * 60
                    newgame_pending_player_name = player_name
                else:
                    # No save exists, start directly
                    print("[DEBUG] No save, starting game directly")
                    initialize_game(player_name)
                    current_screen = "game"

            elif result == "load_game":
                save_data = save_system.load_game()
                if save_data:
                    player_name = save_data["player"]["name"]
                    initialize_game(player_name, save_data)
                    current_screen = "game"
                    print("[OK] Game loaded!")

            elif result in ("quit", "exit"):
                running = False

            elif result == "toggle_fullscreen":
                # Use new apply_settings instead
                new_fullscreen = main_menu.is_fullscreen
                apply_settings(SCREEN_WIDTH, SCREEN_HEIGHT, new_fullscreen)

            elif result == "apply_settings":
                # Apply ALL settings at once
                new_music_volume = main_menu.music_slider.value / 100
                new_sound_volume = main_menu.sound_slider.value / 100
                new_fullscreen = main_menu.is_fullscreen

                # Get resolution from menu if available
                new_width = SCREEN_WIDTH
                new_height = SCREEN_HEIGHT
                if hasattr(main_menu, 'current_resolution_index') and hasattr(main_menu, 'available_resolutions'):
                    res_idx = main_menu.current_resolution_index
                    if 0 <= res_idx < len(main_menu.available_resolutions):
                        new_width, new_height = main_menu.available_resolutions[res_idx]

                # Save audio settings
                settings.set("music_volume", new_music_volume)
                settings.set("sound_volume", new_sound_volume)

                # Apply display settings (resolution + fullscreen)
                apply_settings(new_width, new_height, new_fullscreen)

                # Update music volume if game is running
                if music_manager:
                    music_manager.set_volume(new_music_volume)

                print("[OK] All settings applied!")

        # Game events
        elif current_screen == "game":
            if game_state == "ending_choice":
                choice = ending_choice.handle_event(event)
                if choice:
                    ending_screen.set_ending(choice, quest_manager.completed_quests)
                    game_state = "ending_screen"
                    ending_choice.hide()

            elif game_state == "ending_screen":
                action = ending_screen.handle_event(event)
                if action == "main_menu":
                    current_screen = "main_menu"
                    if music_manager:
                        music_manager.stop()

            # Pause menu events
            if pause_menu.active:
                result = pause_menu.handle_event(event)

                if result == "resume":
                    pause_menu.active = False

                elif result == "save":
                    if player and quest_manager:
                        # Save using SaveSystem API (player, quest_manager, game_state)
                        success = save_system.save_game(player, quest_manager, game_state)
                        # Show in-game save notification box
                        try:
                            pause_menu.show_save_notification(success)
                        except Exception:
                            pass
                        if success:
                            print("[OK] Game saved!")
                        else:
                            print("[SAVE] Failed to save game.")

                elif result == "load":
                    # Load existing save and resume game
                    if save_system.save_exists():
                        save_data = save_system.load_game()
                        if save_data:
                            saved_name = save_data.get("player", {}).get("name", "Player")
                            initialize_game(saved_name, save_data)
                            pause_menu.active = False
                            current_screen = "game"
                            print("[OK] Game loaded from pause menu!")
                        else:
                            pause_menu.show_save_notification(False)
                    else:
                        pause_menu.show_save_notification(False)

                elif result == "main_menu":
                    pause_menu.active = False
                    current_screen = "main_menu"
                    # Ensure main menu shows the main panel, not name input
                    try:
                        main_menu.state = "main"
                        main_menu.name_input.active = False
                    except Exception:
                        pass
                    if music_manager:
                        music_manager.stop()

                elif result == "toggle_fullscreen":
                    # Use new apply_settings instead
                    new_fullscreen = pause_menu.is_fullscreen
                    apply_settings(SCREEN_WIDTH, SCREEN_HEIGHT, new_fullscreen)

                elif result == "apply_settings":
                    # Apply ALL settings at once from pause menu
                    new_music_volume = pause_menu.music_slider.value / 100
                    new_sound_volume = pause_menu.sound_slider.value / 100
                    new_fullscreen = pause_menu.is_fullscreen

                    # Get resolution from menu if available
                    new_width = SCREEN_WIDTH
                    new_height = SCREEN_HEIGHT
                    if hasattr(pause_menu, 'current_resolution_index') and hasattr(pause_menu, 'available_resolutions'):
                        res_idx = pause_menu.current_resolution_index
                        if 0 <= res_idx < len(pause_menu.available_resolutions):
                            new_width, new_height = pause_menu.available_resolutions[res_idx]

                    # Save audio settings
                    settings.set("music_volume", new_music_volume)
                    settings.set("sound_volume", new_sound_volume)

                    # Apply display settings
                    apply_settings(new_width, new_height, new_fullscreen)

                    # Update music volume
                    if music_manager:
                        music_manager.set_volume(new_music_volume)

                    print("[OK] All settings applied from pause menu!")

            # Game input
            else:
                if event.type == pygame.KEYDOWN:
                    # If in code challenge mode, route keys to the challenge UI
                    if game_state == "code_challenge" and code_challenge_box and code_challenge_box.active:
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
                        # don't fall through to other handlers for these keys
                        continue
                    # Pause menu
                    if event.key == pygame.K_ESCAPE:
                        if game_state in ["playing", "code_challenge"]:
                            pause_menu.active = True
                            pause_menu.current_tab = "main"

                    # Debug toggle
                    elif event.key == pygame.K_F3:
                        debug_mode = not debug_mode
                        print(f"Debug mode: {debug_mode}")

                    # Music mute
                    elif event.key == pygame.K_m:
                        if music_manager:
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
                    pass

            if music_manager:
                music_manager.handle_music_end(event)

    # ===== UPDATE =====
    if current_screen == "main_menu":
        main_menu.update()
        # Update new-game warning countdown if active
        if newgame_warning_active:
            if newgame_warning_timer > 0:
                newgame_warning_timer -= 1

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

        # Draw new-game warning modal if active
        if newgame_warning_active:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # Modal box
            modal_w, modal_h = 700, 220
            modal_x = (SCREEN_WIDTH - modal_w) // 2
            modal_y = (SCREEN_HEIGHT - modal_h) // 2

            pygame.draw.rect(screen, (20, 20, 40), (modal_x, modal_y, modal_w, modal_h))
            pygame.draw.rect(screen, (200, 200, 200), (modal_x, modal_y, modal_w, modal_h), 2)

            # Warning text (Indonesian)
            font = pygame.font.Font(None, 28)
            warning = "Jika Kamu Memulai Permainan Baru Maka saat melakukan Save game saat permainan berjalan, save game lama kamu akan di hilang"

            # Simple word-wrap
            words = warning.split(' ')
            lines = []
            cur = ''
            max_w = modal_w - 40
            for w in words:
                test = (cur + ' ' + w).strip()
                if font.size(test)[0] <= max_w:
                    cur = test
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)

            for i, line in enumerate(lines):
                surf = font.render(line, True, (255, 255, 255))
                screen.blit(surf, (modal_x + 20, modal_y + 20 + i * 30))

            # Buttons
            btn_w, btn_h = 140, 48
            gap = 20
            ok_x = modal_x + modal_w - btn_w * 2 - gap * 2
            ok_y = modal_y + modal_h - btn_h - gap
            cancel_x = modal_x + modal_w - btn_w - gap
            cancel_y = ok_y

            # OK button shows countdown
            seconds_left = max(0, (newgame_warning_timer + 59) // 60)
            ok_label = f"OK ({seconds_left})" if newgame_warning_timer > 0 else "OK"

            # OK button appearance depends on enabled state
            ok_color = (100, 100, 100) if newgame_warning_timer > 0 else (50, 150, 50)
            pygame.draw.rect(screen, ok_color, (ok_x, ok_y, btn_w, btn_h))
            pygame.draw.rect(screen, (255, 255, 255), (ok_x, ok_y, btn_w, btn_h), 2)
            ok_surf = font.render(ok_label, True, (255, 255, 255))
            ok_rect = ok_surf.get_rect(center=(ok_x + btn_w // 2, ok_y + btn_h // 2))
            screen.blit(ok_surf, ok_rect)

            # Cancel button
            pygame.draw.rect(screen, (150, 50, 50), (cancel_x, cancel_y, btn_w, btn_h))
            pygame.draw.rect(screen, (255, 255, 255), (cancel_x, cancel_y, btn_w, btn_h), 2)
            cancel_surf = font.render("Cancel", True, (255, 255, 255))
            cancel_rect = cancel_surf.get_rect(center=(cancel_x + btn_w // 2, cancel_y + btn_h // 2))
            screen.blit(cancel_surf, cancel_rect)

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

    pygame.display.flip()
    clock.tick(60)

# Cleanup
print("\n[GAME] Shutting down...")
if music_manager:
    music_manager.stop()
pygame.quit()
sys.exit()
