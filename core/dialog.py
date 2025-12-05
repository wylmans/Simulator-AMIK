import pygame

class DialogueBox:
    """Text box untuk menampilkan dialog NPC"""

    def __init__(self):
        self.active = False
        self.text = ""
        self.speaker_name = ""
        self.char_index = 0  # Untuk efek typing
        self.typing_speed = 1  # Karakter per frame (lebih lambat = lebih jelas sound)
        self.full_text = ""
        self.char_counter = 0  # Counter untuk sound effect

        # Setup mixer untuk sound effect yang lebih loud
        # Ini penting agar sound effect tidak tertimpa music!
        pygame.mixer.set_num_channels(16)  # Lebih banyak channel

        # Load sound effect (bubble/text sound) - UNDERTALE STYLE
        self.text_sound = None
        sound_loaded = False

        # Try multiple sound file locations
        sound_paths = [
            "sounds/bubble.mp3",
            "sounds/bubble.wav",
            "sounds/text.mp3",
            "sounds/text.wav",
            "sounds/blip.mp3",
            "sounds/blip.wav"
        ]

        for sound_path in sound_paths:
            try:
                self.text_sound = pygame.mixer.Sound(sound_path)
                # PENTING: Volume sound effect lebih keras dari music!
                self.text_sound.set_volume(0.8)  # 80% volume (lebih keras!)
                print(f"[OK] Sound loaded: {sound_path}")
                print(f"   Volume: 80% (music background akan diturunkan)")
                sound_loaded = True
                break
            except:
                continue

        if not sound_loaded:
            print("[WARNING] WARNING: Tidak ada sound effect ditemukan!")
            print("   Letakkan file sound di salah satu lokasi:")
            for path in sound_paths:
                print(f"   - {path}")
            print("   Atau generate dengan: python generate_sound.py")

        # Font
        self.font_name = pygame.font.Font(None, 28)
        self.font_text = pygame.font.Font(None, 24)

        # Box dimensions
        self.box_width = 700
        self.box_height = 150
        self.padding = 20

    def show(self, speaker_name, text, music_manager=None):
        """
        Tampilkan dialog baru

        Args:
            speaker_name: Nama NPC yang bicara
            text: Text dialog
            music_manager: (Optional) MusicManager untuk lower volume musik
        """
        self.active = True
        self.speaker_name = speaker_name
        self.full_text = text
        self.text = ""
        self.char_index = 0
        self.char_counter = 0
        self.music_manager = music_manager

        # Lower music volume saat dialog muncul (agar sound effect jelas)
        if self.music_manager:
            self.original_music_volume = self.music_manager.volume
            self.music_manager.set_volume(self.original_music_volume * 0.4)  # 40% dari volume asli

    def hide(self):
        """Sembunyikan dialog"""
        self.active = False
        self.text = ""
        self.full_text = ""
        self.char_index = 0
        self.char_counter = 0

        # Restore music volume ke semula
        if hasattr(self, 'music_manager') and self.music_manager:
            if hasattr(self, 'original_music_volume'):
                self.music_manager.set_volume(self.original_music_volume)

    def update(self):
        """Update efek typing - UNDERTALE STYLE"""
        if not self.active:
            return

        if self.char_index < len(self.full_text):
            # Tambah karakter secara bertahap
            for _ in range(self.typing_speed):
                if self.char_index < len(self.full_text):
                    current_char = self.full_text[self.char_index]
                    self.char_index += 1
                    self.text = self.full_text[:self.char_index]

                    # Play sound untuk setiap karakter (kecuali spasi)
                    # UNDERTALE STYLE: Sound bunyi untuk SETIAP huruf/karakter
                    if self.text_sound and current_char not in [' ', '\n', '\t']:
                        # Play sound dengan random pitch variation (seperti Undertale)
                        self.text_sound.play()
                        self.char_counter += 1

    def skip_typing(self):
        """Skip efek typing, langsung tampilkan semua text"""
        if self.active and self.char_index < len(self.full_text):
            self.char_index = len(self.full_text)
            self.text = self.full_text

    def is_typing_complete(self):
        """Cek apakah typing sudah selesai"""
        return self.char_index >= len(self.full_text)

    def draw(self, screen):
        """Render dialog box ke layar"""
        if not self.active:
            return

        screen_width, screen_height = screen.get_size()

        # Posisi box di bagian bawah layar
        box_x = (screen_width - self.box_width) // 2
        box_y = screen_height - self.box_height - 20

        # Draw shadow
        shadow_offset = 5
        shadow_surface = pygame.Surface((self.box_width, self.box_height))
        shadow_surface.set_alpha(100)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, (box_x + shadow_offset, box_y + shadow_offset))

        # Draw main box
        box_surface = pygame.Surface((self.box_width, self.box_height))
        box_surface.fill((20, 20, 40))
        screen.blit(box_surface, (box_x, box_y))

        # Draw border
        pygame.draw.rect(screen, (255, 255, 255),
                        (box_x, box_y, self.box_width, self.box_height), 3)

        # Draw speaker name background
        name_bg_height = 35
        name_bg = pygame.Surface((250, name_bg_height))
        name_bg.fill((100, 100, 200))
        screen.blit(name_bg, (box_x + self.padding, box_y - name_bg_height // 2))
        pygame.draw.rect(screen, (255, 255, 255),
                        (box_x + self.padding, box_y - name_bg_height // 2, 250, name_bg_height), 2)

        # Draw speaker name
        name_surface = self.font_name.render(self.speaker_name, True, (255, 255, 255))
        screen.blit(name_surface,
                   (box_x + self.padding + 10, box_y - name_bg_height // 2 + 5))

        # Draw text (word wrap)
        self.draw_wrapped_text(screen, self.text,
                              box_x + self.padding,
                              box_y + self.padding,
                              self.box_width - self.padding * 2)

        # Draw continue indicator jika typing selesai
        if self.is_typing_complete():
            indicator_text = "Tekan [SPACE] atau [E]"
            indicator_surface = self.font_text.render(indicator_text, True, (200, 200, 200))
            screen.blit(indicator_surface,
                       (box_x + self.box_width - indicator_surface.get_width() - self.padding,
                        box_y + self.box_height - 30))

    def draw_wrapped_text(self, screen, text, x, y, max_width):
        """Render text dengan word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font_text.render(test_line, True, (255, 255, 255))

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw each line
        line_height = 30
        for i, line in enumerate(lines[:3]):  # Maksimal 3 baris
            line_surface = self.font_text.render(line, True, (255, 255, 255))
            screen.blit(line_surface, (x, y + i * line_height))


class EndingChoice:
    """Dialog untuk pilihan ending"""

    def __init__(self):
        self.active = False
        self.selected_option = 0  # 0 = Continue, 1 = Ending
        self.font_title = pygame.font.Font(None, 36)
        self.font_option = pygame.font.Font(None, 28)

    def show(self):
        """Tampilkan pilihan ending"""
        self.active = True
        self.selected_option = 0

    def hide(self):
        """Sembunyikan pilihan"""
        self.active = False

    def move_selection(self, direction):
        """Gerakkan selection (1 = bawah, -1 = atas)"""
        self.selected_option = (self.selected_option + direction) % 2

    def get_choice(self):
        """Return pilihan yang dipilih (0 = Continue, 1 = Ending)"""
        return self.selected_option

    def draw(self, screen):
        """Render ending choice dialog"""
        if not self.active:
            return

        screen_width, screen_height = screen.get_size()

        # Overlay gelap
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_width = 500
        box_height = 250
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2

        # Draw box
        pygame.draw.rect(screen, (30, 30, 60), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 255, 100), (box_x, box_y, box_width, box_height), 4)

        # Title
        title = self.font_title.render("Selamat! 100 Tugas Selesai!", True, (255, 255, 100))
        screen.blit(title, (box_x + box_width // 2 - title.get_width() // 2, box_y + 30))

        # Subtitle
        subtitle = self.font_option.render("Apa yang ingin kamu lakukan?", True, (255, 255, 255))
        screen.blit(subtitle, (box_x + box_width // 2 - subtitle.get_width() // 2, box_y + 80))

        # Options
        options = ["Lanjutkan Bermain", "Lihat Ending"]
        for i, option in enumerate(options):
            y_pos = box_y + 130 + i * 40

            # Highlight selected
            if i == self.selected_option:
                pygame.draw.rect(screen, (100, 100, 200),
                               (box_x + 50, y_pos - 5, box_width - 100, 35))
                color = (255, 255, 255)
            else:
                color = (180, 180, 180)

            option_text = self.font_option.render(f"> {option}", True, color)
            screen.blit(option_text, (box_x + 60, y_pos))

        # Instructions
        instruction = self.font_option.render("↑/↓: Pilih  |  ENTER: Konfirmasi", True, (150, 150, 150))
        screen.blit(instruction, (box_x + box_width // 2 - instruction.get_width() // 2,
                                  box_y + box_height - 30))
