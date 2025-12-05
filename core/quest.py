import pygame
import random

class Quest:
    """Single quest dengan informasi lengkap"""

    def __init__(self, description, giver_name, code_challenge=None):
        self.description = description
        self.giver_name = giver_name
        self.code_challenge = code_challenge
        self.completed = False

    def __str__(self):
        return f"{self.giver_name}: {self.description[:30]}..."


class CodeChallenge:
    """Mini-game untuk menyelesaikan quest dengan mencari bug dalam code"""

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
        },
        {
            "code": [
                "def proses_data(data):",
                "    for i in range(len(data)):",
                "        data[i] = data[i] * 2",
                "    print('Selesai')",
                "    # Bug: tidak return data!",
                "",
                "angka = [1, 2, 3]",
                "hasil = proses_data(angka)",
                "print(hasil)  # None"
            ],
            "question": "Apa yang salah?",
            "options": [
                "A. Fungsi memodifikasi tapi tidak return data",
                "B. range() salah",
                "C. data[i] tidak boleh diubah",
                "D. print() seharusnya di luar fungsi"
            ],
            "correct": 0,
            "explanation": "Fungsi harus return data setelah modifikasi!"
        },
        {
            "code": [
                "def cek_genap(n):",
                "    if n % 2 == 0:",
                "        return True",
                "    # Bug: tidak ada else return False!",
                "",
                "print(cek_genap(3))  # None"
            ],
            "question": "Kenapa hasilnya None?",
            "options": [
                "A. Tidak ada return untuk kasus False",
                "B. n % 2 salah sintaks",
                "C. == seharusnya =",
                "D. print() salah posisi"
            ],
            "correct": 0,
            "explanation": "Fungsi butuh return untuk semua kondisi!"
        }
    ]

    @staticmethod
    def get_random_challenge():
        """Return random code challenge"""
        return random.choice(CodeChallenge.CHALLENGES).copy()


class CodeChallengeBox:
    """UI untuk menampilkan dan menyelesaikan code challenge dengan scrolling"""

    def __init__(self):
        self.active = False
        self.challenge = None
        self.selected_option = 0
        self.wrong_attempts = 0
        self.max_attempts = 3
        self.result = None
        self.show_result = False
        self.result_timer = 0

        # Scrolling untuk code box
        self.scroll_offset = 0
        self.max_visible_lines = 5  # Maksimal 5 baris code terlihat

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
            print("[WARNING] sounds/correct.wav tidak ditemukan")
            pass

        try:
            self.wrong_sound = pygame.mixer.Sound("sounds/wrong.wav")
            self.wrong_sound.set_volume(0.6)
        except:
            print("[WARNING] sounds/wrong.wav tidak ditemukan")
            pass

        try:
            self.fail_sound = pygame.mixer.Sound("sounds/fail.wav")
            self.fail_sound.set_volume(0.7)
        except:
            print("[WARNING] sounds/fail.wav tidak ditemukan")
            pass

    def show(self, challenge):
        """Tampilkan code challenge"""
        self.active = True
        self.challenge = challenge
        self.selected_option = 0
        self.wrong_attempts = 0
        self.result = None
        self.show_result = False
        self.result_timer = 0
        self.scroll_offset = 0  # Reset scroll

    def hide(self):
        """Sembunyikan challenge"""
        self.active = False
        self.challenge = None
        self.result = None
        self.show_result = False
        self.scroll_offset = 0

    def move_selection(self, direction):
        """Gerakkan selection"""
        if not self.show_result:
            num_options = len(self.challenge["options"])
            self.selected_option = (self.selected_option + direction) % num_options

    def scroll_code(self, direction):
        """Scroll code box"""
        if self.challenge:
            total_lines = len(self.challenge["code"])
            if total_lines > self.max_visible_lines:
                self.scroll_offset += direction
                # Clamp scroll offset
                max_scroll = total_lines - self.max_visible_lines
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def submit_answer(self):
        """Submit jawaban yang dipilih"""
        if self.show_result:
            return None

        correct_index = self.challenge["correct"]

        if self.selected_option == correct_index:
            self.result = "correct"
            self.show_result = True
            self.result_timer = 120
            if self.correct_sound:
                self.correct_sound.play()
            return "correct"
        else:
            self.wrong_attempts += 1

            if self.wrong_attempts >= self.max_attempts:
                self.result = "failed"
                self.show_result = True
                self.result_timer = 180
                if self.fail_sound:
                    self.fail_sound.play()
                return "failed"
            else:
                self.result = "wrong"
                self.show_result = True
                self.result_timer = 60
                if self.wrong_sound:
                    self.wrong_sound.play()
                return "wrong"

    def update(self):
        """Update timer untuk result display"""
        if self.show_result and self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer <= 0:
                if self.result in ["correct", "failed"]:
                    return self.result
                else:
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
        box_height = 520  # Increased height
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

        # Code box with scrolling
        code_box_height = 150  # Fixed height for scrollable area
        code_box_width = box_width - 40
        code_box_x = box_x + 20
        code_box_y = y_offset

        # Draw code box background
        pygame.draw.rect(screen, (20, 20, 30),
                        (code_box_x, code_box_y, code_box_width, code_box_height))
        pygame.draw.rect(screen, (80, 80, 120),
                        (code_box_x, code_box_y, code_box_width, code_box_height), 2)

        # Create clipping rect for code (scrollable area)
        clip_rect = pygame.Rect(code_box_x + 5, code_box_y + 5,
                                code_box_width - 10, code_box_height - 10)
        screen.set_clip(clip_rect)

        # Draw code lines with scroll offset
        total_lines = len(self.challenge["code"])
        line_height = 25
        visible_start = self.scroll_offset
        visible_end = min(visible_start + self.max_visible_lines, total_lines)

        for i in range(visible_start, visible_end):
            line = self.challenge["code"][i]
            relative_y = (i - visible_start) * line_height

            # Line number
            line_num = self.font_code.render(f"{i+1}", True, (100, 100, 100))
            screen.blit(line_num, (code_box_x + 10, code_box_y + 10 + relative_y))

            # Code line
            code_line = self.font_code.render(line, True, (200, 255, 200))
            screen.blit(code_line, (code_box_x + 40, code_box_y + 10 + relative_y))

        # Remove clipping
        screen.set_clip(None)

        # Scroll indicators
        if total_lines > self.max_visible_lines:
            # Scrollbar background
            scrollbar_x = code_box_x + code_box_width - 15
            scrollbar_y = code_box_y + 5
            scrollbar_height = code_box_height - 10
            pygame.draw.rect(screen, (50, 50, 70),
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))

            # Scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * self.max_visible_lines / total_lines))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) *
                                       self.scroll_offset / (total_lines - self.max_visible_lines))
            pygame.draw.rect(screen, (100, 150, 255),
                           (scrollbar_x, thumb_y, 10, thumb_height))

            # Scroll hint
            if self.scroll_offset > 0:
                hint_up = self.font_small.render("▲ Ada kode di atas", True, (255, 200, 100))
                screen.blit(hint_up, (code_box_x + code_box_width - hint_up.get_width() - 20,
                                     code_box_y - 20))

            if self.scroll_offset < total_lines - self.max_visible_lines:
                hint_down = self.font_small.render("▼ Ada kode di bawah", True, (255, 200, 100))
                screen.blit(hint_down, (code_box_x + code_box_width - hint_down.get_width() - 20,
                                       code_box_y + code_box_height + 5))

        y_offset += code_box_height + 25

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
            scroll_hint = ""
            if self.challenge and len(self.challenge["code"]) > self.max_visible_lines:
                scroll_hint = "PgUp/PgDn: Scroll Code  |  "

            instruction = self.font_small.render(
                f"{scroll_hint}↑/↓: Pilih  |  ENTER: Submit  |  ESC: Batal",
                True, (150, 150, 150)
            )
            screen.blit(instruction,
                       (box_x + box_width // 2 - instruction.get_width() // 2,
                        box_y + box_height - 20))

    def _draw_result_overlay(self, screen, box_x, box_y, box_width, box_height):
        """Draw result overlay"""
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
        else:
            color = (150, 100, 50)
            border_color = (255, 200, 100)
            title = "❌ SALAH!"
            message = f"Coba lagi! Kesempatan: {self.max_attempts - self.wrong_attempts}"
            sub_message = ""

        pygame.draw.rect(screen, color, (box_x + 50, overlay_y, box_width - 100, overlay_height))
        pygame.draw.rect(screen, border_color,
                        (box_x + 50, overlay_y, box_width - 100, overlay_height), 4)

        title_surf = self.font_title.render(title, True, (255, 255, 255))
        screen.blit(title_surf,
                   (box_x + box_width // 2 - title_surf.get_width() // 2, overlay_y + 20))

        self._draw_wrapped_text(screen, message,
                               box_x + 70, overlay_y + 60,
                               box_width - 140, self.font_small, (255, 255, 255))

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

    MAX_QUESTS = 5

    def __init__(self):
        self.active_quests = []
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
            return False

        challenge = CodeChallenge.get_random_challenge()
        quest = Quest(description, giver_name, challenge)
        self.active_quests.append(quest)
        return True

    def complete_quest(self, quest_index):
        """Selesaikan quest tertentu"""
        if 0 <= quest_index < len(self.active_quests):
            quest = self.active_quests.pop(quest_index)
            self.completed_quests.append(quest)
            self.total_progress += 1

            if self.total_progress >= 100:
                self.game_completed = True
                return True
        return False

    def fail_quest(self, quest_index):
        """Gagal menyelesaikan quest"""
        if 0 <= quest_index < len(self.active_quests):
            self.active_quests.pop(quest_index)
            self.total_progress = max(0, self.total_progress - 2)

    def get_quest_list(self):
        """Return list quest aktif"""
        return self.active_quests

    def mark_game_completed(self):
        """Mark game sebagai completed"""
        self.game_completed = True

    def reset_progress(self):
        """Reset semua progress"""
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

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        fill_width = int((self.total_progress / 100) * bar_width)

        if self.total_progress < 30:
            color = (255, 100, 100)
        elif self.total_progress < 70:
            color = (255, 200, 100)
        else:
            color = (100, 255, 100)

        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

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

        title = self.font.render(f"Quest Aktif ({len(self.active_quests)}/{self.MAX_QUESTS}):",
                                True, (255, 255, 100))
        screen.blit(title, (x, y))
        y += 30

        for i, quest in enumerate(self.active_quests):
            box_width = 300
            box_height = 50
            pygame.draw.rect(screen, (40, 40, 60), (x, y, box_width, box_height))
            pygame.draw.rect(screen, (100, 100, 150), (x, y, box_width, box_height), 2)

            num_text = self.font.render(f"{i+1}.", True, (200, 200, 200))
            screen.blit(num_text, (x + 10, y + 5))

            giver = self.font_small.render(quest.giver_name, True, (100, 200, 255))
            screen.blit(giver, (x + 10, y + 28))

            desc = quest.description[:25] + "..." if len(quest.description) > 25 else quest.description
            desc_surf = self.font_small.render(desc, True, (200, 200, 200))
            screen.blit(desc_surf, (x + 40, y + 8))

            hint = self.font_small.render(f"[{i+1}]", True, (150, 150, 150))
            screen.blit(hint, (x + box_width - hint.get_width() - 10, y + 28))

            y += box_height + 10
