import pygame
import random

class Quest:
    """Single quest dengan informasi lengkap"""

    def __init__(self, description, giver_name, code_challenge=None):
        self.description = description
        self.giver_name = giver_name
        self.code_challenge = code_challenge  # Dictionary dengan info challenge
        self.completed = False

    def __str__(self):
        return f"{self.giver_name}: {self.description[:30]}..."


class CodeChallenge:
    """Mini-game untuk menyelesaikan quest dengan mencari bug dalam code"""

    # Database soal-soal debugging
    CHALLENGES = [
        {
            "code": [
                "def hitung_nilai(tugas, uts, uas):",
                "    total = tugas + uts + uas",
                "    rata = total / 3",
                "    return total  # Bug disini!"
            ],
            "question": "Apa yang salah dengan kode di atas?",
            "options": [
                "A. return total seharusnya return rata",
                "B. total / 3 seharusnya total * 3",
                "C. def seharusnya function",
                "D. Tidak ada yang salah"
            ],
            "correct": 0,
            "explanation": "Fungsi seharusnya return rata, bukan total!"
        },
        {
            "code": [
                "mahasiswa = ['Budi', 'Ani', 'Citra']",
                "for i in range(len(mahasiswa)):",
                "    print(mahasiswa[i+1])  # Bug!"
            ],
            "question": "Mengapa kode ini error?",
            "options": [
                "A. range() tidak boleh digunakan",
                "B. i+1 akan IndexError pada elemen terakhir",
                "C. mahasiswa seharusnya tuple",
                "D. print() salah sintaks"
            ],
            "correct": 1,
            "explanation": "i+1 akan error saat i mencapai panjang list!"
        },
        {
            "code": [
                "nilai = input('Masukkan nilai: ')",
                "if nilai >= 80:",
                "    print('Lulus')  # Bug!"
            ],
            "question": "Apa masalahnya?",
            "options": [
                "A. input() return string, harus dikonversi ke int",
                "B. >= seharusnya <=",
                "C. if seharusnya while",
                "D. print seharusnya return"
            ],
            "correct": 0,
            "explanation": "input() selalu return string, perlu int() atau float()!"
        },
        {
            "code": [
                "def tambah(a, b):",
                "    hasil = a + b",
                "    # Bug: tidak ada return!",
                "",
                "total = tambah(5, 3)",
                "print(total)"
            ],
            "question": "Kenapa print(total) akan cetak None?",
            "options": [
                "A. Fungsi tidak ada return statement",
                "B. Parameter a dan b salah",
                "C. print() tidak boleh di luar fungsi",
                "D. total seharusnya global"
            ],
            "correct": 0,
            "explanation": "Fungsi tanpa return akan menghasilkan None!"
        },
        {
            "code": [
                "daftar = [1, 2, 3, 4, 5]",
                "for item in daftar:",
                "    daftar.remove(item)  # Bug!"
            ],
            "question": "Mengapa loop ini berbahaya?",
            "options": [
                "A. Memodifikasi list saat iterasi akan skip item",
                "B. remove() tidak boleh dalam loop",
                "C. item seharusnya i",
                "D. daftar seharusnya tuple"
            ],
            "correct": 0,
            "explanation": "Mengubah list saat iterasi akan melewatkan elemen!"
        },
        {
            "code": [
                "x = 10",
                "if x = 5:  # Bug!",
                "    print('Lima')"
            ],
            "question": "Apa yang salah?",
            "options": [
                "A. Menggunakan = (assignment) bukan == (comparison)",
                "B. x harus string",
                "C. if seharusnya for",
                "D. print seharusnya return"
            ],
            "correct": 0,
            "explanation": "Gunakan == untuk comparison, bukan =!"
        },
        {
            "code": [
                "def kali(x, y):",
                "    return x * y",
                "",
                "hasil = kali(3)  # Bug!"
            ],
            "question": "Kenapa ini error?",
            "options": [
                "A. Fungsi butuh 2 argument, hanya diberi 1",
                "B. return salah sintaks",
                "C. x dan y harus global",
                "D. kali() seharusnya multiply()"
            ],
            "correct": 0,
            "explanation": "Missing required positional argument: y!"
        },
        {
            "code": [
                "nama = 'Budi'",
                "nama[0] = 'J'  # Bug!",
                "print(nama)"
            ],
            "question": "Mengapa kode ini error?",
            "options": [
                "A. String immutable, tidak bisa diubah per-karakter",
                "B. Index 0 tidak ada",
                "C. nama seharusnya list",
                "D. print() salah"
            ],
            "correct": 0,
            "explanation": "String di Python immutable (tidak bisa diubah)!"
        }
    ]

    @staticmethod
    def get_random_challenge():
        """Return random code challenge"""
        return random.choice(CodeChallenge.CHALLENGES).copy()


class CodeChallengeBox:
    """UI untuk menampilkan dan menyelesaikan code challenge"""

    def __init__(self):
        self.active = False
        self.challenge = None
        self.selected_option = 0
        self.wrong_attempts = 0
        self.max_attempts = 3
        self.result = None  # "correct", "wrong", atau None
        self.show_result = False
        self.result_timer = 0

        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_code = pygame.font.Font(None, 22)
        self.font_option = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # Sound effects
        self.correct_sound = None
        self.wrong_sound = None
        self.fail_sound = None

        self._load_sounds()

    def _load_sounds(self):
        """Load sound effects"""
        try:
            self.correct_sound = pygame.mixer.Sound("sounds/correct.wav")
            self.correct_sound.set_volume(0.6)
        except:
            print("⚠️  sounds/correct.wav tidak ditemukan")

        try:
            self.wrong_sound = pygame.mixer.Sound("sounds/wrong.wav")
            self.wrong_sound.set_volume(0.6)
        except:
            print("⚠️  sounds/wrong.wav tidak ditemukan")

        try:
            self.fail_sound = pygame.mixer.Sound("sounds/fail.wav")
            self.fail_sound.set_volume(0.7)
        except:
            print("⚠️  sounds/fail.wav tidak ditemukan")

    def show(self, challenge):
        """Tampilkan code challenge"""
        self.active = True
        self.challenge = challenge
        self.selected_option = 0
        self.wrong_attempts = 0
        self.result = None
        self.show_result = False
        self.result_timer = 0

    def hide(self):
        """Sembunyikan challenge"""
        self.active = False
        self.challenge = None
        self.result = None
        self.show_result = False

    def move_selection(self, direction):
        """Gerakkan selection"""
        if not self.show_result:
            num_options = len(self.challenge["options"])
            self.selected_option = (self.selected_option + direction) % num_options

    def submit_answer(self):
        """Submit jawaban yang dipilih"""
        if self.show_result:
            return None

        correct_index = self.challenge["correct"]

        if self.selected_option == correct_index:
            # Jawaban benar!
            self.result = "correct"
            self.show_result = True
            self.result_timer = 120  # Show result for 2 seconds (120 frames)
            if self.correct_sound:
                self.correct_sound.play()
            return "correct"
        else:
            # Jawaban salah
            self.wrong_attempts += 1

            if self.wrong_attempts >= self.max_attempts:
                # Gagal total setelah 3x salah
                self.result = "failed"
                self.show_result = True
                self.result_timer = 180  # 3 seconds
                if self.fail_sound:
                    self.fail_sound.play()
                return "failed"
            else:
                # Masih ada kesempatan
                self.result = "wrong"
                self.show_result = True
                self.result_timer = 60  # 1 second
                if self.wrong_sound:
                    self.wrong_sound.play()
                return "wrong"

    def update(self):
        """Update timer untuk result display"""
        if self.show_result and self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer <= 0:
                if self.result in ["correct", "failed"]:
                    # Auto close setelah correct atau failed
                    return self.result  # Signal untuk close
                else:
                    # Wrong attempt, reset untuk coba lagi
                    self.show_result = False
                    self.result = None
        return None

    def draw(self, screen):
        """Render code challenge box"""
        if not self.active:
            return

        screen_width, screen_height = screen.get_size()

        # Dark overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main box
        box_width = 700
        box_height = 500
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2

        # Draw box
        pygame.draw.rect(screen, (30, 30, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 255), (box_x, box_y, box_width, box_height), 4)

        y_offset = box_y + 20

        # Title
        title = self.font_title.render("🐛 DEBUG CHALLENGE - Temukan Bug!", True, (255, 200, 100))
        screen.blit(title, (box_x + box_width // 2 - title.get_width() // 2, y_offset))
        y_offset += 40

        # Attempts remaining
        attempts_left = self.max_attempts - self.wrong_attempts
        attempts_color = (100, 255, 100) if attempts_left > 1 else (255, 100, 100)
        attempts_text = self.font_small.render(
            f"Kesempatan: {attempts_left}/{self.max_attempts}",
            True, attempts_color
        )
        screen.blit(attempts_text, (box_x + 20, y_offset))
        y_offset += 30

        # Code box
        code_box_height = 120
        pygame.draw.rect(screen, (20, 20, 30),
                        (box_x + 20, y_offset, box_width - 40, code_box_height))
        pygame.draw.rect(screen, (80, 80, 120),
                        (box_x + 20, y_offset, box_width - 40, code_box_height), 2)

        # Draw code lines
        for i, line in enumerate(self.challenge["code"]):
            line_num = self.font_code.render(f"{i+1}", True, (100, 100, 100))
            code_line = self.font_code.render(line, True, (200, 255, 200))
            screen.blit(line_num, (box_x + 30, y_offset + 10 + i * 25))
            screen.blit(code_line, (box_x + 60, y_offset + 10 + i * 25))

        y_offset += code_box_height + 20

        # Question
        question = self.font_option.render(self.challenge["question"], True, (255, 255, 255))
        screen.blit(question, (box_x + 20, y_offset))
        y_offset += 40

        # Options
        for i, option in enumerate(self.challenge["options"]):
            option_y = y_offset + i * 35

            # Highlight selected
            if i == self.selected_option and not self.show_result:
                pygame.draw.rect(screen, (70, 70, 120),
                               (box_x + 20, option_y - 5, box_width - 40, 32))
                color = (255, 255, 100)
            else:
                color = (200, 200, 200)

            option_text = self.font_option.render(option, True, color)
            screen.blit(option_text, (box_x + 30, option_y))

        # Show result overlay
        if self.show_result:
            self._draw_result_overlay(screen, box_x, box_y, box_width, box_height)
        else:
            # Instructions
            instruction = self.font_small.render(
                "↑/↓: Pilih  |  ENTER: Submit  |  ESC: Batalkan",
                True, (150, 150, 150)
            )
            screen.blit(instruction,
                       (box_x + box_width // 2 - instruction.get_width() // 2,
                        box_y + box_height - 25))

    def _draw_result_overlay(self, screen, box_x, box_y, box_width, box_height):
        """Draw result overlay (correct/wrong/failed)"""
        overlay_height = 150
        overlay_y = box_y + box_height // 2 - overlay_height // 2

        if self.result == "correct":
            color = (50, 150, 50)
            border_color = (100, 255, 100)
            title = "✅ BENAR!"
            message = self.challenge["explanation"]
            sub_message = "+1 Progress Quest Selesai!"
        elif self.result == "failed":
            color = (150, 50, 50)
            border_color = (255, 100, 100)
            title = "❌ GAGAL!"
            message = "Kamu gagal 3x! Tugas dibatalkan."
            sub_message = "-2 Progress sebagai hukuman!"
        else:  # wrong
            color = (150, 100, 50)
            border_color = (255, 200, 100)
            title = "❌ SALAH!"
            message = f"Coba lagi! Kesempatan: {self.max_attempts - self.wrong_attempts}"
            sub_message = ""

        # Draw overlay box
        pygame.draw.rect(screen, color, (box_x + 50, overlay_y, box_width - 100, overlay_height))
        pygame.draw.rect(screen, border_color,
                        (box_x + 50, overlay_y, box_width - 100, overlay_height), 4)

        # Title
        title_surf = self.font_title.render(title, True, (255, 255, 255))
        screen.blit(title_surf,
                   (box_x + box_width // 2 - title_surf.get_width() // 2, overlay_y + 20))

        # Message (word wrap)
        self._draw_wrapped_text(screen, message,
                               box_x + 70, overlay_y + 60,
                               box_width - 140, self.font_small, (255, 255, 255))

        # Sub message
        if sub_message:
            sub_surf = self.font_small.render(sub_message, True, (255, 255, 100))
            screen.blit(sub_surf,
                       (box_x + box_width // 2 - sub_surf.get_width() // 2,
                        overlay_y + overlay_height - 30))

    def _draw_wrapped_text(self, screen, text, x, y, max_width, font, color):
        """Helper untuk word wrap"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.render(test_line, True, color).get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            screen.blit(line_surf, (x, y + i * 22))


class QuestManager:
    """Manager untuk handle multiple active quests"""

    MAX_QUESTS = 5  # Maksimal 5 quest aktif

    def __init__(self):
        self.active_quests = []  # List of Quest objects
        self.completed_quests = []
        self.total_progress = 0
        self.game_completed = False
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

    def can_accept_quest(self):
        """Cek apakah bisa menerima quest baru"""
        return len(self.active_quests) < self.MAX_QUESTS

    def start_quest(self, description, giver_name):
        """Tambah quest baru"""
        if not self.can_accept_quest():
            return False  # Quest penuh

        # Create quest dengan code challenge
        challenge = CodeChallenge.get_random_challenge()
        quest = Quest(description, giver_name, challenge)
        self.active_quests.append(quest)
        return True

    def complete_quest(self, quest_index):
        """Selesaikan quest tertentu (dipanggil setelah challenge berhasil)"""
        if 0 <= quest_index < len(self.active_quests):
            quest = self.active_quests.pop(quest_index)
            self.completed_quests.append(quest)
            self.total_progress += 1

            # Check if reached 100
            if self.total_progress >= 100:
                self.game_completed = True
                return True
        return False

    def fail_quest(self, quest_index):
        """Gagal menyelesaikan quest (pengurangan progress)"""
        if 0 <= quest_index < len(self.active_quests):
            # Remove quest
            self.active_quests.pop(quest_index)

            # Kurangi progress sebanyak 2
            self.total_progress = max(0, self.total_progress - 2)

    def get_quest_list(self):
        """Return list quest aktif untuk display"""
        return self.active_quests

    def mark_game_completed(self):
        """Mark game sebagai completed"""
        self.game_completed = True

    def reset_progress(self):
        """Reset semua progress (untuk main ulang)"""
        self.active_quests = []
        self.completed_quests = []
        self.total_progress = 0
        self.game_completed = False

    def draw_progress_bar(self, screen):
        """Draw progress bar di tengah atas"""
        screen_width = screen.get_size()[0]
        bar_width = 400
        bar_height = 30
        bar_x = (screen_width - bar_width) // 2
        bar_y = 10

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Progress fill
        fill_width = int((self.total_progress / 100) * bar_width)

        # Color gradient based on progress
        if self.total_progress < 30:
            color = (255, 100, 100)  # Red
        elif self.total_progress < 70:
            color = (255, 200, 100)  # Orange
        else:
            color = (100, 255, 100)  # Green

        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Text
        progress_text = f"{self.total_progress} / 100 Tugas"
        text_surface = self.font.render(progress_text, True, (255, 255, 255))
        screen.blit(text_surface,
                   (bar_x + bar_width // 2 - text_surface.get_width() // 2,
                    bar_y + bar_height // 2 - text_surface.get_height() // 2))

    def draw_quest_list(self, screen, x, y):
        """Draw daftar quest aktif"""
        if not self.active_quests:
            no_quest = self.font_small.render("Tidak ada quest aktif", True, (150, 150, 150))
            screen.blit(no_quest, (x, y))
            return

        # Title
        title = self.font.render(f"Quest Aktif ({len(self.active_quests)}/{self.MAX_QUESTS}):",
                                True, (255, 255, 100))
        screen.blit(title, (x, y))
        y += 30

        # List quests
        for i, quest in enumerate(self.active_quests):
            # Quest box background
            box_width = 300
            box_height = 50
            pygame.draw.rect(screen, (40, 40, 60), (x, y, box_width, box_height))
            pygame.draw.rect(screen, (100, 100, 150), (x, y, box_width, box_height), 2)

            # Quest number
            num_text = self.font.render(f"{i+1}.", True, (200, 200, 200))
            screen.blit(num_text, (x + 10, y + 5))

            # Giver name
            giver = self.font_small.render(quest.giver_name, True, (100, 200, 255))
            screen.blit(giver, (x + 10, y + 28))

            # Short description
            desc = quest.description[:25] + "..." if len(quest.description) > 25 else quest.description
            desc_surf = self.font_small.render(desc, True, (200, 200, 200))
            screen.blit(desc_surf, (x + 40, y + 8))

            # Hint
            hint = self.font_small.render(f"[Tekan {i+1}]", True, (150, 150, 150))
            screen.blit(hint, (x + box_width - hint.get_width() - 10, y + 28))

            y += box_height + 10
