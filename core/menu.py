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


class SettingsButton:
    """Hamburger menu icon button for in-game menu"""

    def __init__(self, x, y, size=40):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.is_hovered = False

    def update(self, mouse_pos):
        """Update hover state"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draw hamburger menu icon"""
        # Draw background circle
        color = (150, 150, 255) if self.is_hovered else (100, 100, 200)
        pygame.draw.circle(screen, color, self.rect.center, self.size // 2)
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.size // 2, 2)

        # Draw hamburger menu (3 horizontal lines)
        center_x, center_y = self.rect.center
        line_width = self.size // 2
        line_height = 2
        line_spacing = self.size // 6

        # Top line
        pygame.draw.line(screen, (255, 255, 255),
                        (center_x - line_width // 2, center_y - line_spacing),
                        (center_x + line_width // 2, center_y - line_spacing), line_height)

        # Middle line
        pygame.draw.line(screen, (255, 255, 255),
                        (center_x - line_width // 2, center_y),
                        (center_x + line_width // 2, center_y), line_height)

        # Bottom line
        pygame.draw.line(screen, (255, 255, 255),
                        (center_x - line_width // 2, center_y + line_spacing),
                        (center_x + line_width // 2, center_y + line_spacing), line_height)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class Slider:
    """Slider untuk volume control"""

    def __init__(self, x, y, width, label, min_val=0, max_val=100, initial_val=50):
        self.rect = pygame.Rect(x, y, width, 20)
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
        # Update position from rect
        self.x = self.rect.x
        self.y = self.rect.y

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
        self.settings_button = Button(button_x, start_y + 80, button_width, button_height, "Settings")
        self.exit_button = Button(button_x, start_y + 160, button_width, button_height, "Exit")

        # Name input
        input_width = 400
        input_height = 50
        input_x = (screen_width - input_width) // 2
        input_y = screen_height // 2

        self.name_input = TextInput(input_x, input_y, input_width, input_height)
        self.name_submit_button = Button(input_x, input_y + 80, input_width, 50, "Continue")

        # Settings
        self.music_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 50,
                                   400, "Music Volume", initial_val=30)
        self.sound_slider = Slider(screen_width // 2 - 200, screen_height // 2 + 50,
                                   400, "Sound Effects", initial_val=60)

        self.fullscreen_toggle = Button(screen_width // 2 - 150, screen_height // 2 + 130,
                                       300, 50, "Fullscreen: OFF")
        self.back_button = Button(screen_width // 2 - 150, screen_height // 2 + 200,
                                 300, 50, "Back")

        self.is_fullscreen = False

        # Player name
        self.player_name = ""

    def handle_event(self, event):
        """Handle menu events"""
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "main":
            self.start_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.exit_button.update(mouse_pos)

            if self.start_button.is_clicked(event):
                self.state = "name_input"
                self.name_input.active = True
                return None

            if self.settings_button.is_clicked(event):
                self.state = "settings"
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
            self.fullscreen_toggle.update(mouse_pos)
            self.back_button.update(mouse_pos)

            if self.fullscreen_toggle.is_clicked(event):
                self.is_fullscreen = not self.is_fullscreen
                self.fullscreen_toggle.text = f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}"
                return "toggle_fullscreen"

            if self.back_button.is_clicked(event):
                self.state = "main"

        return None

    def update(self):
        """Update menu"""
        if self.state == "name_input":
            self.name_input.update()

    def draw(self, screen):
        """Draw menu"""
        # Get actual screen dimensions
        actual_width = screen.get_width()
        actual_height = screen.get_height()

        # Background gradient
        for y in range(actual_height):
            color_value = int(30 + (y / actual_height) * 50)
            pygame.draw.line(screen, (color_value, color_value // 2, color_value),
                           (0, y), (actual_width, y))

        if self.state == "main":
            self._draw_main_menu(screen, actual_width, actual_height)
        elif self.state == "name_input":
            self._draw_name_input(screen, actual_width, actual_height)
        elif self.state == "settings":
            self._draw_settings(screen, actual_width, actual_height)

    def _draw_main_menu(self, screen, width, height):
        """Draw main menu screen"""
        # Title
        title = self.title_font.render("Simulasi AMIK", True, (255, 255, 100))
        title_rect = title.get_rect(center=(width // 2, 150))
        screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render("Kehidupan Mahasiswa Informatika", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(width // 2, 200))
        screen.blit(subtitle, subtitle_rect)

        # Buttons - recalculate positions for current screen size
        button_width = 300
        button_height = 60
        button_x = (width - button_width) // 2
        start_y = height // 2

        # Update button positions
        self.start_button.rect.x = button_x
        self.start_button.rect.y = start_y
        self.settings_button.rect.x = button_x
        self.settings_button.rect.y = start_y + 80
        self.exit_button.rect.x = button_x
        self.exit_button.rect.y = start_y + 160

        self.start_button.draw(screen)
        self.settings_button.draw(screen)
        self.exit_button.draw(screen)

        # Version
        version = self.subtitle_font.render("v1.0", True, (100, 100, 100))
        screen.blit(version, (10, height - 30))

    def _draw_name_input(self, screen, width, height):
        """Draw name input screen"""
        # Title
        title = self.title_font.render("Masukkan Nama", True, (255, 255, 100))
        title_rect = title.get_rect(center=(width // 2, 150))
        screen.blit(title, title_rect)

        # Instruction
        instruction = self.subtitle_font.render("Siapa nama kamu?", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(width // 2, 250))
        screen.blit(instruction, instruction_rect)

        # Input box - recalculate position
        input_width = 400
        input_height = 50
        input_x = (width - input_width) // 2
        input_y = height // 2

        self.name_input.rect.x = input_x
        self.name_input.rect.y = input_y
        self.name_input.draw(screen)

        # Submit button
        self.name_submit_button.rect.x = input_x
        self.name_submit_button.rect.y = input_y + 80
        self.name_submit_button.draw(screen)

        # Hint
        hint = self.subtitle_font.render("Tekan ENTER atau klik Continue", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(width // 2, height - 100))
        screen.blit(hint, hint_rect)

    def _draw_settings(self, screen, width, height):
        """Draw settings screen"""
        # Title
        title = self.title_font.render("Settings", True, (255, 255, 100))
        title_rect = title.get_rect(center=(width // 2, 100))
        screen.blit(title, title_rect)

        # Sliders - recalculate positions
        self.music_slider.rect.x = width // 2 - 200
        self.music_slider.rect.y = height // 2 - 50
        self.sound_slider.rect.x = width // 2 - 200
        self.sound_slider.rect.y = height // 2 + 50
        self.fullscreen_toggle.rect.x = width // 2 - 150
        self.fullscreen_toggle.rect.y = height // 2 + 130
        self.back_button.rect.x = width // 2 - 150
        self.back_button.rect.y = height // 2 + 200

        self.music_slider.draw(screen)
        self.sound_slider.draw(screen)

        # Buttons
        self.fullscreen_toggle.draw(screen)
        self.back_button.draw(screen)


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
        self.exit_button = Button(button_x, start_y + 400, button_width, button_height, "Exit Game")

        # Settings (same as main menu)
        self.music_slider = Slider(screen_width // 2 - 200, screen_height // 2 - 50,
                                   400, "Music Volume", initial_val=30)
        self.sound_slider = Slider(screen_width // 2 - 200, screen_height // 2 + 50,
                                   400, "Sound Effects", initial_val=60)
        self.fullscreen_toggle = Button(screen_width // 2 - 150, screen_height // 2 + 130,
                                       300, 50, "Fullscreen: OFF")
        self.back_button = Button(screen_width // 2 - 150, screen_height // 2 + 200,
                                 300, 50, "Back")

        self.is_fullscreen = False

        # Save notification
        self.save_notification = ""
        self.save_notification_timer = 0

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
            self.exit_button.update(mouse_pos)

            if self.resume_button.is_clicked(event):
                return "resume"

            if self.save_button.is_clicked(event):
                return "save"

            if self.load_button.is_clicked(event):
                return "load"

            if self.settings_button.is_clicked(event):
                self.state = "settings"
                return None

            if self.menu_button.is_clicked(event):
                return "main_menu"

            if self.exit_button.is_clicked(event):
                return "exit"

        elif self.state == "settings":
            self.music_slider.handle_event(event)
            self.sound_slider.handle_event(event)
            self.fullscreen_toggle.update(mouse_pos)
            self.back_button.update(mouse_pos)

            if self.fullscreen_toggle.is_clicked(event):
                self.is_fullscreen = not self.is_fullscreen
                self.fullscreen_toggle.text = f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}"
                return "toggle_fullscreen"

            if self.back_button.is_clicked(event):
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

        # Get actual screen dimensions
        actual_width = screen.get_width()
        actual_height = screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((actual_width, actual_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        if self.state == "pause":
            self._draw_pause_menu(screen, actual_width, actual_height)
        elif self.state == "settings":
            self._draw_settings(screen, actual_width, actual_height)

        # Save notification
        if self.save_notification_timer > 0:
            notif_font = pygame.font.Font(None, 28)
            notif_surface = notif_font.render(self.save_notification, True, (100, 255, 100))
            notif_rect = notif_surface.get_rect(center=(actual_width // 2, 50))

            # Background
            bg_rect = notif_rect.inflate(20, 10)
            pygame.draw.rect(screen, (20, 20, 40), bg_rect)
            pygame.draw.rect(screen, (100, 255, 100), bg_rect, 2)

            screen.blit(notif_surface, notif_rect)

    def _draw_pause_menu(self, screen, width, height):
        """Draw pause menu"""
        # Title
        title = self.title_font.render("PAUSED", True, (255, 255, 100))
        title_rect = title.get_rect(center=(width // 2, 80))
        screen.blit(title, title_rect)

        # Update button positions
        button_width = 300
        button_height = 50
        button_x = (width - button_width) // 2
        start_y = height // 2 - 120

        self.resume_button.rect.x = button_x
        self.resume_button.rect.y = start_y
        self.resume_button.rect.height = button_height

        self.save_button.rect.x = button_x
        self.save_button.rect.y = start_y + 60
        self.save_button.rect.height = button_height

        self.load_button.rect.x = button_x
        self.load_button.rect.y = start_y + 120
        self.load_button.rect.height = button_height

        self.settings_button.rect.x = button_x
        self.settings_button.rect.y = start_y + 180
        self.settings_button.rect.height = button_height

        self.menu_button.rect.x = button_x
        self.menu_button.rect.y = start_y + 240
        self.menu_button.rect.height = button_height

        self.exit_button.rect.x = button_x
        self.exit_button.rect.y = start_y + 300
        self.exit_button.rect.height = button_height

        # Buttons
        self.resume_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.settings_button.draw(screen)
        self.menu_button.draw(screen)
        self.exit_button.draw(screen)

    def _draw_settings(self, screen, width, height):
        """Draw settings in pause menu"""
        # Title
        title = self.title_font.render("Settings", True, (255, 255, 100))
        title_rect = title.get_rect(center=(width // 2, 100))
        screen.blit(title, title_rect)

        # Update slider positions
        self.music_slider.rect.x = width // 2 - 200
        self.music_slider.rect.y = height // 2 - 50
        self.sound_slider.rect.x = width // 2 - 200
        self.sound_slider.rect.y = height // 2 + 50
        self.fullscreen_toggle.rect.x = width // 2 - 150
        self.fullscreen_toggle.rect.y = height // 2 + 130
        self.back_button.rect.x = width // 2 - 150
        self.back_button.rect.y = height // 2 + 200

        # Sliders
        self.music_slider.draw(screen)
        self.sound_slider.draw(screen)

        # Buttons
        self.fullscreen_toggle.draw(screen)
        self.back_button.draw(screen)
