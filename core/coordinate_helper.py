"""
COORDINATE HELPER - Tool untuk mencari koordinat NPC

Jalankan game dengan script ini untuk melihat koordinat player real-time
Gunakan koordinat ini untuk menempatkan NPC di core/npc.py

CARA PAKAI:
1. Tambahkan import ini di game.py:
   from coordinate_helper import show_coordinates

2. Di game loop (bagian Update), tambahkan:
   show_coordinates(screen, player)

3. Jalankan game, koordinat akan muncul di layar
4. Catat koordinat lokasi yang diinginkan untuk NPC
"""

import pygame

def show_coordinates(screen, player, font_size=24):
    """
    Tampilkan koordinat player di layar

    Args:
        screen: pygame screen surface
        player: object player yang punya atribut x dan y
        font_size: ukuran font
    """
    font = pygame.font.Font(None, font_size)

    # Background panel
    panel_width = 200
    panel_height = 80
    panel = pygame.Surface((panel_width, panel_height))
    panel.set_alpha(200)
    panel.fill((0, 0, 0))
    screen.blit(panel, (10, screen.get_height() - panel_height - 10))

    # Text koordinat
    x_text = font.render(f"X: {int(player.x)}", True, (255, 255, 100))
    y_text = font.render(f"Y: {int(player.y)}", True, (255, 255, 100))
    info_text = font.render("(Pos. Player)", True, (150, 150, 150))

    screen.blit(x_text, (20, screen.get_height() - panel_height))
    screen.blit(y_text, (20, screen.get_height() - panel_height + 25))
    screen.blit(info_text, (20, screen.get_height() - 35))


def print_coordinates_on_click(player):
    """
    Print koordinat ke console saat player bergerak
    Panggil di game loop untuk debug
    """
    print(f"Player Position → X: {int(player.x)}, Y: {int(player.y)}")


# ═══════════════════════════════════════════════════════════════
# CONTOH PENGGUNAAN DI GAME.PY
# ═══════════════════════════════════════════════════════════════
"""
# Di bagian atas game.py, tambahkan import:
from coordinate_helper import show_coordinates

# Di game loop, setelah bagian Draw UI, tambahkan:
show_coordinates(screen, player)

# Sekarang saat game berjalan, koordinat akan muncul di kiri bawah!
# Gerakkan player ke lokasi yang diinginkan, catat koordinatnya,
# lalu gunakan untuk menempatkan NPC di core/npc.py
"""

# ═══════════════════════════════════════════════════════════════
# TEMPLATE COPY-PASTE UNTUK NPC
# ═══════════════════════════════════════════════════════════════
"""
Setelah dapat koordinat, copy template ini ke create_sample_npcs():

    npcX = NPC(
        name="Nama Dosen",
        x=XXX,  # ← Paste koordinat X di sini
        y=YYY,  # ← Paste koordinat Y di sini
        sprite_path="images/dosenX.png",
        dialogue_lines=DOSEN_DIALOGUES["kategori"]
    )
    npcs.append(npcX)
"""
