import pygame

class EndingScreen:
    """Layar ending game"""

    def __init__(self):
        self.active = False
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.scroll_y = 0
        self.scroll_speed = 1

    def show(self):
        """Tampilkan ending screen"""
        self.active = True
        self.scroll_y = 0

    def hide(self):
        """Sembunyikan ending screen"""
        self.active = False

    def update(self):
        """Update scroll credits"""
        if self.active:
            self.scroll_y += self.scroll_speed

    def draw(self, screen, completed_quests):
        """Render ending screen"""
        if not self.active:
            return

        screen_width, screen_height = screen.get_size()
        screen.fill((10, 10, 30))

        # Starting Y position
        y = screen_height - self.scroll_y

        # Title
        title = self.font_title.render("TAMAT", True, (255, 255, 100))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, y))
        y += 100

        # Ending text
        ending_lines = [
            "Selamat!",
            "",
            "Kamu telah berhasil menyelesaikan",
            f"{completed_quests} tugas selama masa kuliah!",
            "",
            "Perjalanan sebagai mahasiswa penuh dengan",
            "tantangan, begadang mengerjakan tugas,",
            "deadline yang mepet, dan dosen yang galak.",
            "",
            "Tapi kamu berhasil melewati semuanya!",
            "",
            "Ini adalah awal dari petualangan baru.",
            "Dunia kerja menunggumu!",
            "",
            "Ingat, ilmu yang kamu dapat di kampus",
            "adalah bekal untuk masa depan.",
            "",
            "Selamat wisuda! 🎓",
            "",
            "",
            "--- CREDITS ---",
            "",
            "Game Design & Programming",
            "[Your Name]",
            "",
            "Special Thanks",
            "Semua Dosen & Teman-teman",
            "",
            "Terimakasih telah bermain!",
            "",
            "",
            "Tekan [ESC] untuk keluar",
            "Tekan [R] untuk main lagi"
        ]

        for line in ending_lines:
            if y > -50 and y < screen_height:
                if line.startswith("---"):
                    text = self.font_title.render(line, True, (100, 255, 255))
                elif line in ["Selamat!", "Selamat wisuda! 🎓", "Terimakasih telah bermain!"]:
                    text = self.font_title.render(line, True, (255, 255, 100))
                else:
                    text = self.font_text.render(line, True, (255, 255, 255))
                screen.blit(text, (screen_width // 2 - text.get_width() // 2, y))
            y += 40

        # Fade in/out berdasarkan posisi
        if self.scroll_y < 100:
            # Fade in di awal
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(255 - int(self.scroll_y * 2.55))
            overlay.fill((10, 10, 30))
            screen.blit(overlay, (0, 0))
