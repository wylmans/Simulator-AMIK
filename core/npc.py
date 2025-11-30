import pygame
import random
from core.camera import camera  # Import camera untuk posisi relatif

class NPC(pygame.sprite.Sprite):
    """Base class untuk NPC (Dosen)"""

    def __init__(self, name, x, y, sprite_path, dialogue_lines):
        super().__init__()
        self.name = name
        self.x = x  # Posisi absolute di map
        self.y = y  # Posisi absolute di map
        self.sprite_path = sprite_path
        self.dialogue_lines = dialogue_lines  # List dialog yang akan ditampilkan

        # Load sprite
        try:
            self.image = pygame.image.load(sprite_path)
            self.image = pygame.transform.scale(self.image, (48, 48))
        except:
            # Fallback jika gambar tidak ada
            self.image = pygame.Surface((48, 48))
            self.image.fill((100, 100, 200))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Interaction range
        self.interaction_range = 80  # Pixel radius untuk interaksi

    def is_in_range(self, player):
        """Cek apakah player dalam jangkauan interaksi"""
        dx = self.x - player.x
        dy = self.y - player.y
        distance = (dx**2 + dy**2)**0.5
        return distance <= self.interaction_range

    def get_random_dialogue(self):
        """Ambil dialog random dari list"""
        return random.choice(self.dialogue_lines)

    def draw(self, screen):
        """Render NPC ke layar dengan camera offset"""
        # Gunakan camera offset seperti di sprite.py
        screen.blit(self.image, (self.x - camera.x, self.y - camera.y))

    def draw_indicator(self, screen, player):
        """Tampilkan indikator jika player dalam range"""
        if self.is_in_range(player):
            # Gambar tanda seru di atas NPC (dengan camera offset)
            font = pygame.font.Font(None, 36)
            text = font.render("!", True, (255, 255, 0))
            screen.blit(text, (self.x - camera.x + 16, self.y - camera.y - 30))


class NPCManager:
    """Manager untuk mengelola semua NPC"""

    def __init__(self):
        self.npcs = []

    def add_npc(self, npc):
        """Tambah NPC ke manager"""
        self.npcs.append(npc)

    def get_nearby_npc(self, player):
        """Cari NPC terdekat yang dalam range"""
        for npc in self.npcs:
            if npc.is_in_range(player):
                return npc
        return None

    def draw_all(self, screen, player):
        """Render semua NPC dan indikator"""
        for npc in self.npcs:
            npc.draw(screen)
            npc.draw_indicator(screen, player)


# Template dialog untuk berbagai dosen
DOSEN_DIALOGUES = {
    "pemrograman": [
        "Kerjakan tugas coding tentang algoritma sorting!",
        "Buat program kalkulator sederhana sebagai tugas!",
        "Debug code ini dan temukan errornya!",
        "Implementasikan struktur data linked list!",
        "Optimasi kode yang telah kamu buat!"
    ],
    "database": [
        "Buat ERD untuk sistem perpustakaan!",
        "Tulis query SQL untuk join 3 tabel!",
        "Normalisasi database sampai 3NF!",
        "Design schema untuk e-commerce!",
        "Optimasi query yang lambat ini!"
    ],
    "jaringan": [
        "Konfigurasi router untuk subnet ini!",
        "Analisis traffic jaringan dengan Wireshark!",
        "Setup VPN untuk kantor cabang!",
        "Troubleshoot masalah koneksi ini!",
        "Design topologi jaringan untuk kampus!"
    ],
    "matematika": [
        "Selesaikan integral parsial ini!",
        "Hitung determinan matriks 4x4!",
        "Buktikan teorema ini dengan induksi!",
        "Optimasi fungsi dengan turunan!",
        "Selesaikan sistem persamaan linear!"
    ],
    "umum": [
        "Kerjakan tugas tepat waktu ya!",
        "Baca materi untuk pertemuan berikutnya!",
        "Jangan lupa kumpulkan laporan!",
        "Pelajari konsep yang sudah dijelaskan!",
        "Latihan soal-soal di buku!"
    ]
}


def create_sample_npcs():
    """
    Fungsi helper untuk membuat contoh NPC dosen

    ⭐ SESUAIKAN POSISI X dan Y DENGAN MAP ANDA! ⭐

    Koordinat adalah posisi ABSOLUTE di map (bukan screen)
    Contoh: Jika map 1000x1000, gunakan koordinat 0-1000
    """
    npcs = []

    # ═══════════════════════════════════════════════════════
    # ⭐⭐⭐ UBAH KOORDINAT X, Y DI SINI! ⭐⭐⭐
    # ═══════════════════════════════════════════════════════

    # Contoh NPC 1 - Dosen Pemrograman
    npc1 = NPC(
        name="Prof. Budi",
        x=250,        # ← UBAH KOORDINAT X (posisi horizontal di map)
        y=150,        # ← UBAH KOORDINAT Y (posisi vertikal di map)
        sprite_path="images/dosen1.png",
        dialogue_lines=DOSEN_DIALOGUES["pemrograman"]
    )
    npcs.append(npc1)

    # Contoh NPC 2 - Dosen Database
    npc2 = NPC(
        name="Dr. Siti",
        x=400,        # ← UBAH KOORDINAT X
        y=300,        # ← UBAH KOORDINAT Y
        sprite_path="images/dosen2.png",
        dialogue_lines=DOSEN_DIALOGUES["database"]
    )
    npcs.append(npc2)

    # Contoh NPC 3 - Dosen Jaringan
    npc3 = NPC(
        name="Pak Ahmad",
        x=600,        # ← UBAH KOORDINAT X
        y=200,        # ← UBAH KOORDINAT Y
        sprite_path="images/dosen3.png",
        dialogue_lines=DOSEN_DIALOGUES["jaringan"]
    )
    npcs.append(npc3)

    # Contoh NPC 4 - Dosen Matematika
    npc4 = NPC(
        name="Bu Rina",
        x=300,        # ← UBAH KOORDINAT X
        y=450,        # ← UBAH KOORDINAT Y
        sprite_path="images/dosen4.png",
        dialogue_lines=DOSEN_DIALOGUES["matematika"]
    )
    npcs.append(npc4)

    # Contoh NPC 5 - Dosen Umum
    npc5 = NPC(
        name="Pak Dedi",
        x=150,        # ← UBAH KOORDINAT X
        y=350,        # ← UBAH KOORDINAT Y
        sprite_path="images/dosen5.png",
        dialogue_lines=DOSEN_DIALOGUES["umum"]
    )
    npcs.append(npc5)

    # ═══════════════════════════════════════════════════════
    # TIPS: Untuk cari koordinat yang tepat:
    # 1. Jalankan game dan gerakkan player ke lokasi yg diinginkan
    # 2. Print koordinat player: print(f"X: {player.x}, Y: {player.y}")
    # 3. Gunakan koordinat tersebut untuk NPC
    # ═══════════════════════════════════════════════════════

    return npcs
