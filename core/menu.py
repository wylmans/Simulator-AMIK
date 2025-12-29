import pygame
import json
import os


class TextInput:
    """Input box untuk nama player"""

    def __init__(self, x, y, width, height, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

        self.font = pygame.font.Font(None, 32)
        self.color_inactive = (100, 100, 120)
        self.color_active = (150, 150, 255)

    def handle_event(self, event):
        """Handle keyboard input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True  # Submit
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                if event.unicode.isprintable():
                    self.text += event.unicode

        return False

    def update(self):
        """Update cursor blink"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        """Draw input box"""
        # Background
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, (20, 20, 40), self.rect)
        pygame.draw.rect(screen, color, self.rect, 3)

        # Text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + text_surface.get_width() + 2
            pygame.draw.line(screen, (255, 255, 255),
                           (cursor_x, self.rect.y + 8),
                           (cursor_x, self.rect.y + self.rect.height - 8), 2)


class Button:
    """Simple button class"""

    def __init__(self, x, y, width, height, text, color=(100, 100, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (150, 150, 255)
        self.is_hovered = False

        self.font = pygame.font.Font(None, 32)

    def update(self, mouse_pos):
        """Update hover state"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draw button"""
        color = self.hover_color if self.is_hovered else self.color

        # Button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # Text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class Slider:
    """Slider untuk volume control"""

    def __init__(self, x, y, width, label, min_val=0, max_val=100, initial_val=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.label = label

        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val

        self.dragging = False
        self.font = pygame.font.Font(None, 24)

    def handle_event(self, event):
        """Handle mouse events"""
        slider_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if slider_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])

    def _update_value(self, mouse_x):
        """Update value based on mouse position"""
        relative_x = mouse_x - self.x
        relative_x = max(0, min(relative_x, self.width))

        ratio = relative_x / self.width
        self.value = self.min_val + (self.max_val - self.min_val) * ratio

    def get_value(self):
        """Get current value (0-1 for volume)"""
        return self.value / 100.0

    def draw(self, screen):
        """Draw slider"""
        # Label
        label_surface = self.font.render(self.label, True, (255, 255, 255))
        screen.blit(label_surface, (self.x, self.y - 25))

        # Slider track
        pygame.draw.rect(screen, (50, 50, 70),
                        (self.x, self.y, self.width, self.height))

        # Slider fill
        fill_width = int(self.width * (self.value / self.max_val))
        pygame.draw.rect(screen, (100, 150, 255),
                        (self.x, self.y, fill_width, self.height))

        # Slider handle
        handle_x = self.x + fill_width
        pygame.draw.circle(screen, (255, 255, 255),
                         (handle_x, self.y + self.height // 2), 8)

        # Value text
        value_text = f"{int(self.value)}%"
        value_surface = self.font.render(value_text, True, (255, 255, 255))
        screen.blit(value_surface, (self.x + self.width + 10, self.y - 2))


class MainMenu:
    """Main menu screen"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Get available resolutions
        self.resolutions = self._get_available_resolutions()
        self.current_resolution_index = 0

        # Menu states
        self.state = "main"  # "main", "name_input", "settings"

        # Title
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 24)

        # Main menu buttons
        button_width = 300
        button_height = 60
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2

        self.start_button = Button(button_x, start_y, button_width, button_height, "Start Game")
        self.load_button = Button(button_x, start_y + 80, button_width, button_height, "Load Game")
        self.settings_button = Button(button_x, start_y + 160, button_width, button_height, "Settings")
        self.exit_button = Button(button_x, start_y + 240, button_width, button_height, "Exit")

        # Name input
        input_width = 400
        input_height = 50
        input_x = (screen_width - input_width) // 2
        input_y = screen_height // 2

        self.name_input = TextInput(input_x, input_y, input_width, input_height)
        self.name_submit_button = Button(input_x, input_y + 80, input_width, 50, "Continue")

        # Settings
        self.music_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 120,
                                   400, "Music Volume", initial_val=30)
        self.sound_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 40,
                                   400, "Sound Effects", initial_val=60)
        # Camera zoom slider (percent)
        self.zoom_slider = Slider(screen_width // 2 - 200, screen_height // 2 + 40,
                      400, "Camera Zoom (%)", min_val=50, max_val=200, initial_val=100)

        # Resolution selector
        self.resolution_left = Button(screen_width // 2 - 200, screen_height // 2 + 50,
                                     60, 40, "<")
        self.resolution_right = Button(screen_width // 2 + 140, screen_height // 2 + 50,
                                      60, 40, ">")

        self.fullscreen_toggle = Button(screen_width // 2 - 150, screen_height // 2 + 110,
                                       300, 50, "Fullscreen: OFF")

        # Apply and Back buttons
        self.apply_button = Button(screen_width // 2 - 250, screen_height // 2 + 180,
                                  200, 50, "Apply", color=(50, 150, 50))
        self.back_button = Button(screen_width // 2 + 50, screen_height // 2 + 180,
                                 200, 50, "Back")

        self.is_fullscreen = False

        # Player name
        self.player_name = ""

        # Settings change notification
        self.settings_changed = False

        # Ensure layout is consistent (useful when resolution changes)
        self.update_layout(self.screen_width, self.screen_height)
    def _get_available_resolutions(self):
        """Get list of available screen resolutions"""
        try:
            modes = pygame.display.list_modes()
            if modes == -1:  # All resolutions supported
                return [(1920, 1080), (1600, 900), (1366, 768), (1280, 720), (1080, 720)]
            else:
                # Filter to common aspect ratios
                filtered = []
                for mode in modes:
                    if mode[0] >= 800 and mode[1] >= 600:  # Minimum size
                        filtered.append(mode)
                return filtered[:10] if filtered else [(1080, 720)]
        except:
            return [(1920, 1080), (1600, 900), (1366, 768), (1280, 720), (1080, 720)]

    def update_layout(self, screen_width, screen_height):
        """Recalculate and apply layout positions based on provided screen size."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Buttons
        button_width = 300
        button_height = 60
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2

        self.start_button.rect = pygame.Rect(button_x, start_y, button_width, button_height)
        self.load_button.rect = pygame.Rect(button_x, start_y + 80, button_width, button_height)
        self.settings_button.rect = pygame.Rect(button_x, start_y + 160, button_width, button_height)
        self.exit_button.rect = pygame.Rect(button_x, start_y + 240, button_width, button_height)

        # Name input
        input_width = 400
        input_height = 50
        input_x = (screen_width - input_width) // 2
        input_y = screen_height // 2
        self.name_input.rect = pygame.Rect(input_x, input_y, input_width, input_height)
        self.name_submit_button.rect = pygame.Rect(input_x, input_y + 80, input_width, 50)

        # Sliders
        self.music_slider.x = screen_width // 2 - 200
        self.music_slider.y = screen_height // 2 - 120
        self.sound_slider.x = screen_width // 2 - 200
        self.sound_slider.y = screen_height // 2 - 40
        self.zoom_slider.x = screen_width // 2 - 200
        self.zoom_slider.y = screen_height // 2 + 40
        self.zoom_slider.x = screen_width // 2 - 200
        self.zoom_slider.y = screen_height // 2 + 40

        # Resolution buttons
        self.resolution_left.rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 50, 60, 40)
        self.resolution_right.rect = pygame.Rect(screen_width // 2 + 140, screen_height // 2 + 50, 60, 40)

        # Fullscreen toggle and apply/back
        self.fullscreen_toggle.rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 110, 300, 50)
        self.apply_button.rect = pygame.Rect(screen_width // 2 - 250, screen_height // 2 + 180, 200, 50)
        self.back_button.rect = pygame.Rect(screen_width // 2 + 50, screen_height // 2 + 180, 200, 50)

    def get_resolution_text(self):
        """Get current resolution as text"""
        if 0 <= self.current_resolution_index < len(self.resolutions):
            w, h = self.resolutions[self.current_resolution_index]
            return f"{w} x {h}"
        return "1080 x 720"

    def handle_event(self, event):
        """Handle menu events"""
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "main":
            self.start_button.update(mouse_pos)
            self.load_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.exit_button.update(mouse_pos)

            if self.start_button.is_clicked(event):
                self.state = "name_input"
                self.name_input.active = True
                return None

            if self.load_button.is_clicked(event):
                return "load_game"

            if self.settings_button.is_clicked(event):
                self.state = "settings"
                self.settings_changed = False
                return None

            if self.exit_button.is_clicked(event):
                return "exit"

        elif self.state == "name_input":
            submitted = self.name_input.handle_event(event)
            self.name_submit_button.update(mouse_pos)

            if submitted or self.name_submit_button.is_clicked(event):
                if self.name_input.text.strip():
                    self.player_name = self.name_input.text.strip()
                    return "start_game"

        elif self.state == "settings":
            self.music_slider.handle_event(event)
            self.sound_slider.handle_event(event)
            # zoom_slider exists for both menus
            try:
                self.zoom_slider.handle_event(event)
            except Exception:
                pass
            self.fullscreen_toggle.update(mouse_pos)
            self.resolution_left.update(mouse_pos)
            self.resolution_right.update(mouse_pos)
            self.apply_button.update(mouse_pos)
            self.back_button.update(mouse_pos)

            # Mark as changed if sliders moved
            if event.type == pygame.MOUSEMOTION and (self.music_slider.dragging or self.sound_slider.dragging or self.zoom_slider.dragging):
                self.settings_changed = True

            if self.fullscreen_toggle.is_clicked(event):
                self.is_fullscreen = not self.is_fullscreen
                self.fullscreen_toggle.text = f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}"
                self.settings_changed = True

            # Resolution navigation
            if self.resolution_left.is_clicked(event):
                self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                self.settings_changed = True

            if self.resolution_right.is_clicked(event):
                self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                self.settings_changed = True

            if self.apply_button.is_clicked(event):
                self.settings_changed = False
                return "apply_settings"

            if self.back_button.is_clicked(event):
                self.settings_changed = False
                self.state = "main"

        return None

    def update(self):
        """Update menu"""
        if self.state == "name_input":
            self.name_input.update()

    def draw(self, screen):
        """Draw menu"""
        # Background gradient
        for y in range(screen.get_height()):
            color_value = int(30 + (y / screen.get_height()) * 50)
            pygame.draw.line(screen, (color_value, color_value // 2, color_value),
                           (0, y), (screen.get_width(), y))

        if self.state == "main":
            self._draw_main_menu(screen)
        elif self.state == "name_input":
            self._draw_name_input(screen)
        elif self.state == "settings":
            self._draw_settings(screen)

    def _draw_main_menu(self, screen):
        """Draw main menu screen"""
        # Title
        title = self.title_font.render("Simulasi AMIK", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render("Kehidupan Mahasiswa Informatika", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(subtitle, subtitle_rect)

        # Buttons
        self.start_button.draw(screen)
        self.load_button.draw(screen)
        self.settings_button.draw(screen)
        self.exit_button.draw(screen)

        # Version
        version = self.subtitle_font.render("v1.0", True, (100, 100, 100))
        screen.blit(version, (10, self.screen_height - 30))

    def _draw_name_input(self, screen):
        """Draw name input screen"""
        # Title
        title = self.title_font.render("Masukkan Nama", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)

        # Instruction
        instruction = self.subtitle_font.render("Siapa nama kamu?", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(instruction, instruction_rect)

        # Input box
        self.name_input.draw(screen)

        # Submit button
        self.name_submit_button.draw(screen)

        # Hint
        hint = self.subtitle_font.render("Tekan ENTER atau klik Continue", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        screen.blit(hint, hint_rect)

    def _draw_settings(self, screen):
        """Draw settings screen"""
        # Title
        title = self.title_font.render("Settings", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Sliders
        self.music_slider.draw(screen)
        self.sound_slider.draw(screen)
        self.zoom_slider.draw(screen)

        # Resolution selector
        res_label = self.subtitle_font.render("Resolution:", True, (255, 255, 255))
        screen.blit(res_label, (self.screen_width // 2 - 200, self.screen_height // 2 + 30))

        self.resolution_left.draw(screen)
        self.resolution_right.draw(screen)

        # Current resolution text
        res_text = self.subtitle_font.render(self.get_resolution_text(), True, (255, 255, 255))
        res_text_rect = res_text.get_rect(center=(self.screen_width // 2 + 40, self.screen_height // 2 + 70))
        screen.blit(res_text, res_text_rect)

        # Buttons
        self.fullscreen_toggle.draw(screen)
        self.apply_button.draw(screen)
        self.back_button.draw(screen)

        # Changes notification
        if self.settings_changed:
            notif = self.subtitle_font.render("* Click Apply to save changes", True, (255, 200, 100))
            notif_rect = notif.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 250))
            screen.blit(notif, notif_rect)


class PauseMenu:
    """In-game pause menu (ESC)"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False

        # Current state
        self.state = "pause"  # "pause" or "settings"

        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 32)
        self.subtitle_font = pygame.font.Font(None, 24)

        # Get available resolutions
        self.resolutions = self._get_available_resolutions()
        self.current_resolution_index = 0

        # Pause menu buttons
        button_width = 300
        button_height = 60
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2 - 100

        self.resume_button = Button(button_x, start_y, button_width, button_height, "Resume")
        self.save_button = Button(button_x, start_y + 80, button_width, button_height, "Save Game")
        self.load_button = Button(button_x, start_y + 160, button_width, button_height, "Load Game")
        self.settings_button = Button(button_x, start_y + 240, button_width, button_height, "Settings")
        self.menu_button = Button(button_x, start_y + 320, button_width, button_height, "Main Menu")

        # Settings (same as main menu)
        self.music_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 120,
                                   400, "Music Volume", initial_val=30)
        self.sound_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 40,
                                   400, "Sound Effects", initial_val=60)
        # Camera zoom slider (percent)
        self.zoom_slider = Slider(screen_width // 2 - 200, screen_height // 2 + 40,
                      400, "Camera Zoom (%)", min_val=50, max_val=200, initial_val=100)

        # Resolution selector
        self.resolution_left = Button(screen_width // 2 - 200, screen_height // 2 + 50,
                                     60, 40, "<")
        self.resolution_right = Button(screen_width // 2 + 140, screen_height // 2 + 50,
                                      60, 40, ">")

        self.fullscreen_toggle = Button(screen_width // 2 - 150, screen_height // 2 + 110,
                                       300, 50, "Fullscreen: OFF")

        # Apply and Back
        self.apply_button = Button(screen_width // 2 - 250, screen_height // 2 + 180,
                                  200, 50, "Apply", color=(50, 150, 50))
        self.back_button = Button(screen_width // 2 + 50, screen_height // 2 + 180,
                                 200, 50, "Back")

        self.is_fullscreen = False
        self.settings_changed = False

        # Save notification
        self.save_notification = ""
        self.save_notification_timer = 0

        # Ensure layout matches screen size
        self.update_layout(self.screen_width, self.screen_height)

    def _get_available_resolutions(self):
        """Get list of available screen resolutions"""
        try:
            modes = pygame.display.list_modes()
            if modes == -1:
                return [(1920, 1080), (1600, 900), (1366, 768), (1280, 720), (1080, 720)]
            else:
                filtered = []
                for mode in modes:
                    if mode[0] >= 800 and mode[1] >= 600:
                        filtered.append(mode)
                return filtered[:10] if filtered else [(1080, 720)]
        except:
            return [(1920, 1080), (1600, 900), (1366, 768), (1280, 720), (1080, 720)]

    def update_layout(self, screen_width, screen_height):
        """Recalculate layout for pause menu based on screen size."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        button_width = 300
        button_height = 60
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2 - 100

        # Buttons
        self.resume_button.rect = pygame.Rect(button_x, start_y, button_width, button_height)
        self.save_button.rect = pygame.Rect(button_x, start_y + 80, button_width, button_height)
        self.load_button.rect = pygame.Rect(button_x, start_y + 160, button_width, button_height)
        self.settings_button.rect = pygame.Rect(button_x, start_y + 240, button_width, button_height)
        self.menu_button.rect = pygame.Rect(button_x, start_y + 320, button_width, button_height)

        # Sliders
        self.music_slider.x = screen_width // 2 - 200
        self.music_slider.y = screen_height // 2 - 120
        self.sound_slider.x = screen_width // 2 - 200
        self.sound_slider.y = screen_height // 2 - 40

        # Resolution buttons
        self.resolution_left.rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 50, 60, 40)
        self.resolution_right.rect = pygame.Rect(screen_width // 2 + 140, screen_height // 2 + 50, 60, 40)

        # Fullscreen toggle and apply/back
        self.fullscreen_toggle.rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 110, 300, 50)
        self.apply_button.rect = pygame.Rect(screen_width // 2 - 250, screen_height // 2 + 180, 200, 50)
        self.back_button.rect = pygame.Rect(screen_width // 2 + 50, screen_height // 2 + 180, 200, 50)

    def get_resolution_text(self):
        """Get current resolution as text"""
        if 0 <= self.current_resolution_index < len(self.resolutions):
            w, h = self.resolutions[self.current_resolution_index]
            return f"{w} x {h}"
        return "1080 x 720"

    def show(self):
        """Show pause menu"""
        self.active = True
        self.state = "pause"

    def hide(self):
        """Hide pause menu"""
        self.active = False

    def handle_event(self, event):
        """Handle pause menu events"""
        if not self.active:
            return None

        mouse_pos = pygame.mouse.get_pos()

        if self.state == "pause":
            self.resume_button.update(mouse_pos)
            self.save_button.update(mouse_pos)
            self.load_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)

            if self.resume_button.is_clicked(event):
                return "resume"

            if self.save_button.is_clicked(event):
                return "save"

            if self.load_button.is_clicked(event):
                return "load"

            if self.settings_button.is_clicked(event):
                self.state = "settings"
                self.settings_changed = False
                return None

            if self.menu_button.is_clicked(event):
                return "main_menu"

        elif self.state == "settings":
            self.music_slider.handle_event(event)
            self.sound_slider.handle_event(event)
            self.zoom_slider.handle_event(event)
            self.fullscreen_toggle.update(mouse_pos)
            self.resolution_left.update(mouse_pos)
            self.resolution_right.update(mouse_pos)
            self.apply_button.update(mouse_pos)
            self.back_button.update(mouse_pos)

            # Mark as changed
            if event.type == pygame.MOUSEMOTION and (self.music_slider.dragging or self.sound_slider.dragging or self.zoom_slider.dragging):
                self.settings_changed = True

            if self.fullscreen_toggle.is_clicked(event):
                self.is_fullscreen = not self.is_fullscreen
                self.fullscreen_toggle.text = f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}"
                self.settings_changed = True

            if self.resolution_left.is_clicked(event):
                self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                self.settings_changed = True

            if self.resolution_right.is_clicked(event):
                self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                self.settings_changed = True

            if self.apply_button.is_clicked(event):
                self.settings_changed = False
                return "apply_settings"

            if self.back_button.is_clicked(event):
                self.settings_changed = False
                self.state = "pause"

        return None

    def update(self):
        """Update pause menu"""
        if self.save_notification_timer > 0:
            self.save_notification_timer -= 1

    def show_save_notification(self, success=True):
        """Show save notification"""
        if success:
            self.save_notification = "Game saved successfully!"
        else:
            self.save_notification = "Failed to save game."
        self.save_notification_timer = 120  # 2 seconds

    def draw(self, screen):
        """Draw pause menu"""
        if not self.active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Draw current pause menu state
        if self.state == "pause":
            self._draw_pause_menu(screen)
        elif self.state == "settings":
            self._draw_settings(screen)

        # Save notification
        if self.save_notification_timer > 0:
            notif_font = pygame.font.Font(None, 28)
            notif_surface = notif_font.render(self.save_notification, True, (100, 255, 100))
            notif_rect = notif_surface.get_rect(center=(self.screen_width // 2, 50))

            # Background
            bg_rect = notif_rect.inflate(20, 10)
            pygame.draw.rect(screen, (20, 20, 40), bg_rect)
            pygame.draw.rect(screen, (100, 255, 100), bg_rect, 2)

            screen.blit(notif_surface, notif_rect)

    def _draw_pause_menu(self, screen):
        """Draw pause menu"""
        # Title
        title = self.title_font.render("PAUSED", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)

        # Buttons
        self.resume_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.settings_button.draw(screen)
        self.menu_button.draw(screen)

    def _draw_settings(self, screen):
        """Draw settings in pause menu"""
        # Title
        title = self.title_font.render("Settings", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Sliders
        self.music_slider.draw(screen)
        self.sound_slider.draw(screen)
        # Camera zoom (pause menu settings)
        self.zoom_slider.draw(screen)

        # Resolution selector
        res_label = self.subtitle_font.render("Resolution:", True, (255, 255, 255))
        screen.blit(res_label, (self.screen_width // 2 - 200, self.screen_height // 2 + 30))

        self.resolution_left.draw(screen)
        self.resolution_right.draw(screen)

        # Current resolution text
        res_text = self.subtitle_font.render(self.get_resolution_text(), True, (255, 255, 255))
        res_text_rect = res_text.get_rect(center=(self.screen_width // 2 + 40, self.screen_height // 2 + 70))
        screen.blit(res_text, res_text_rect)

        # Buttons
        self.fullscreen_toggle.draw(screen)
        self.apply_button.draw(screen)
        self.back_button.draw(screen)

        # Changes notification
        if self.settings_changed:
            notif = self.subtitle_font.render("* Click Apply to save changes", True, (255, 200, 100))
            notif_rect = notif.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 250))
            screen.blit(notif, notif_rect)
