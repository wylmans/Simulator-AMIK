import pygame
import json
import os

class QuestManager:
    """Manager untuk tracking quest dan progress pemain"""

    def __init__(self, save_file="save_data.json"):
        self.completed_quests = 0
        self.total_quests_needed = 100
        self.current_quest = None
        self.quest_giver_name = None
        self.save_file = save_file
        self.game_completed = False

        # Load progress jika ada
        self.load_progress()

    def start_quest(self, quest_description, npc_name):
        """Mulai quest baru"""
        self.current_quest = quest_description
        self.quest_giver_name = npc_name

    def complete_quest(self):
        """Tandai quest sebagai selesai"""
        if self.current_quest:
            self.completed_quests += 1
            self.current_quest = None
            self.quest_giver_name = None
            self.save_progress()

            # Cek apakah sudah mencapai 100 quest
            if self.completed_quests >= self.total_quests_needed and not self.game_completed:
                return True  # Trigger ending choice
        return False

    def get_progress_percentage(self):
        """Hitung persentase progress"""
        return min(100, (self.completed_quests / self.total_quests_needed) * 100)

    def save_progress(self):
        """Simpan progress ke file"""
        data = {
            "completed_quests": self.completed_quests,
            "game_completed": self.game_completed
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except:
            pass  # Ignore save errors

    def load_progress(self):
        """Load progress dari file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.completed_quests = data.get("completed_quests", 0)
                    self.game_completed = data.get("game_completed", False)
            except:
                pass  # Ignore load errors

    def reset_progress(self):
        """Reset semua progress"""
        self.completed_quests = 0
        self.current_quest = None
        self.quest_giver_name = None
        self.game_completed = False
        if os.path.exists(self.save_file):
            os.remove(self.save_file)

    def mark_game_completed(self):
        """Tandai game sebagai selesai"""
        self.game_completed = True
        self.save_progress()

    def draw_progress_bar(self, screen, x=None, y=None, width=None, height=None):
        """
        Render progress bar di layar
        Jika parameter tidak diberikan, akan menggunakan nilai default:
        - x: tengah horizontal (auto-centered)
        - y: 15 pixel dari atas
        - width: 400 pixel
        - height: 30 pixel
        """
        # Set default values
        if width is None:
            width = 400
        if height is None:
            height = 30

        screen_width = screen.get_size()[0]

        # Default position: tengah atas
        if x is None:
            x = (screen_width - width) // 2
        if y is None:
            y = 15

        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))

        # Progress fill
        progress = self.get_progress_percentage()
        fill_width = int((progress / 100) * width)

        # Warna berubah sesuai progress
        if progress < 50:
            color = (255, 100, 100)  # Merah
        elif progress < 80:
            color = (255, 255, 100)  # Kuning
        else:
            color = (100, 255, 100)  # Hijau

        pygame.draw.rect(screen, color, (x, y, fill_width, height))

        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 3)

        # Text
        font = pygame.font.Font(None, 26)
        text = font.render(f"{self.completed_quests}/{self.total_quests_needed} Tugas", True, (255, 255, 255))
        text_x = x + width // 2 - text.get_width() // 2
        text_y = y + height // 2 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))

    def draw_current_quest(self, screen, x, y):
        """Tampilkan quest yang sedang aktif"""
        if self.current_quest:
            font = pygame.font.Font(None, 20)

            # Background panel
            panel_width = 400
            panel_height = 80
            panel = pygame.Surface((panel_width, panel_height))
            panel.set_alpha(200)
            panel.fill((30, 30, 30))
            screen.blit(panel, (x, y))

            # Quest title
            title = font.render("Quest Aktif:", True, (255, 255, 100))
            screen.blit(title, (x + 10, y + 10))

            # Quest description (wrap text jika terlalu panjang)
            quest_text = self.current_quest
            if len(quest_text) > 45:
                quest_text = quest_text[:45] + "..."

            desc = font.render(quest_text, True, (255, 255, 255))
            screen.blit(desc, (x + 10, y + 35))

            # Instruction
            instruction = font.render("Tekan [Q] untuk selesaikan", True, (150, 150, 150))
            screen.blit(instruction, (x + 10, y + 55))
