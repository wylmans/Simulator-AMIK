#!/usr/bin/env python3
"""
NPC Generator V2 - FINAL COMPLETE VERSION
Generate NPCs dengan animated sprites, quests, dan auto-implementation

Features:
- ✅ Animated sprite support (PNG + JSON roll film style)
- ✅ Quest assignment untuk setiap NPC
- ✅ Extensive debug (file verification, sprite loading, etc)
- ✅ Auto-edit campus.tmx (spawn points)
- ✅ Auto-edit npc.py (insert NPC code)
- ✅ Verification & testing

Usage:
    python generate_npcs_v2.py
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil
import re
import sys

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PROJECT_PATH = "."
TMX_FILE = "maps/campus.tmx"
NPC_FILE = "core/npc.py"
SPRITES_DIR = "sprites"  # Directory untuk sprite files

# ═══════════════════════════════════════════════════════════════

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def debug_print(message, level="INFO"):
    """Print debug message dengan warna"""
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "DEBUG": Colors.OKCYAN
    }
    color = colors.get(level, Colors.ENDC)

    prefix = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }

    print(f"{color}{prefix.get(level, '')} {message}{Colors.ENDC}")


# Quest templates
QUEST_TEMPLATES = {
    "pemrograman": [
        "Buat program sorting dengan algoritma bubble sort",
        "Implementasikan linked list dengan Python",
        "Debug program yang error IndexError",
        "Buat kalkulator sederhana dengan GUI",
        "Optimasi code yang lambat dengan big O notation"
    ],
    "database": [
        "Buat ERD untuk sistem perpustakaan digital",
        "Tulis query SQL dengan 3 tabel join",
        "Normalisasi database sampai bentuk 3NF",
        "Design schema database untuk e-commerce",
        "Optimasi query yang memakan waktu lama"
    ],
    "jaringan": [
        "Konfigurasi router untuk subnet 192.168.1.0/24",
        "Analisis packet dengan Wireshark",
        "Setup VPN untuk remote access",
        "Troubleshoot masalah koneksi WiFi",
        "Design topologi jaringan untuk lab komputer"
    ],
    "matematika": [
        "Selesaikan integral parsial",
        "Hitung determinan matriks 4x4",
        "Buktikan teorema dengan induksi matematika",
        "Optimasi fungsi dengan turunan",
        "Selesaikan sistem persamaan linear"
    ],
    "umum": [
        "Kumpulkan laporan akhir semester",
        "Presentasi hasil project kelompok",
        "Pelajari materi untuk ujian tengah semester",
        "Revisi proposal skripsi",
        "Lengkapi form registrasi semester depan"
    ]
}

# Dialogue templates
DIALOGUE_TEMPLATES = {
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


def verify_sprite_files(png_path, json_path=None):
    """Verify sprite files exist dan readable"""
    debug_print(f"Verifying sprite files...", "DEBUG")

    issues = []

    # Check PNG
    if png_path and png_path != '__fallback__':
        full_png = os.path.join(PROJECT_PATH, png_path)
        debug_print(f"  Checking PNG: {full_png}", "DEBUG")

        if os.path.exists(full_png):
            size = os.path.getsize(full_png)
            debug_print(f"  ✓ PNG found ({size} bytes)", "SUCCESS")

            # Try to get image dimensions (optional)
            try:
                import pygame
                pygame.init()
                img = pygame.image.load(full_png)
                w, h = img.get_size()
                debug_print(f"  ✓ Image size: {w}×{h} pixels", "DEBUG")
            except:
                pass
        else:
            debug_print(f"  ✗ PNG NOT FOUND: {full_png}", "WARNING")
            issues.append(f"PNG not found: {png_path}")

    # Check JSON
    if json_path:
        full_json = os.path.join(PROJECT_PATH, json_path)
        debug_print(f"  Checking JSON: {full_json}", "DEBUG")

        if os.path.exists(full_json):
            try:
                with open(full_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Verify JSON structure
                if 'frames' in data:
                    frame_count = len(data['frames'])
                    debug_print(f"  ✓ JSON found ({frame_count} frames)", "SUCCESS")

                    # Show first few frame names
                    if frame_count > 0:
                        frames = list(data['frames'].keys())[:3]
                        debug_print(f"  ✓ Sample frames: {', '.join(frames)}", "DEBUG")
                else:
                    debug_print(f"  ⚠️  JSON structure unusual (no 'frames' key)", "WARNING")

            except json.JSONDecodeError as e:
                debug_print(f"  ✗ JSON parse error: {e}", "ERROR")
                issues.append(f"JSON invalid: {json_path}")
            except Exception as e:
                debug_print(f"  ✗ Error reading JSON: {e}", "ERROR")
                issues.append(f"JSON error: {json_path}")
        else:
            debug_print(f"  ✗ JSON NOT FOUND: {full_json}", "WARNING")
            issues.append(f"JSON not found: {json_path}")

    return issues


def verify_file_paths():
    """Verify all required file paths"""
    debug_print("═══════════════════════════════════════════════════════════════", "INFO")
    debug_print("FILE PATHS VERIFICATION", "INFO")
    debug_print("═══════════════════════════════════════════════════════════════", "INFO")

    tmx_full = os.path.join(PROJECT_PATH, TMX_FILE)
    npc_full = os.path.join(PROJECT_PATH, NPC_FILE)
    sprites_full = os.path.join(PROJECT_PATH, SPRITES_DIR)

    issues = []

    # Check TMX
    debug_print(f"1. Checking TMX: {tmx_full}", "INFO")
    if not os.path.exists(tmx_full):
        debug_print(f"   TMX NOT FOUND", "ERROR")
        issues.append("TMX file tidak ditemukan")
    else:
        debug_print(f"   ✓ TMX exists ({os.path.getsize(tmx_full)} bytes)", "SUCCESS")

        if not os.access(tmx_full, os.W_OK):
            debug_print("   ⚠️  TMX read-only", "WARNING")
            issues.append("TMX read-only (tidak bisa diedit)")
        else:
            debug_print("   ✓ TMX writable", "SUCCESS")

    # Check npc.py
    debug_print(f"\n2. Checking npc.py: {npc_full}", "INFO")
    if not os.path.exists(npc_full):
        debug_print(f"   npc.py NOT FOUND", "ERROR")
        issues.append("npc.py tidak ditemukan")
    else:
        debug_print(f"   ✓ npc.py exists ({os.path.getsize(npc_full)} bytes)", "SUCCESS")

        try:
            with open(npc_full, 'r', encoding='utf-8') as f:
                content = f.read()

            if "def create_sample_npcs" in content:
                debug_print("   ✓ Found create_sample_npcs() function", "SUCCESS")
            else:
                debug_print("   ⚠️  create_sample_npcs() NOT FOUND", "WARNING")

            if "return npcs" in content:
                debug_print("   ✓ Found 'return npcs' statement", "SUCCESS")
            else:
                debug_print("   ⚠️  'return npcs' NOT FOUND", "WARNING")
                issues.append("'return npcs' tidak ditemukan")

        except Exception as e:
            debug_print(f"   ✗ Error reading npc.py: {e}", "ERROR")
            issues.append("npc.py tidak bisa dibaca")

    # Check sprites directory
    debug_print(f"\n3. Checking sprites directory: {sprites_full}", "INFO")
    if not os.path.exists(sprites_full):
        debug_print(f"   ⚠️  Sprites directory not found (will be created if needed)", "WARNING")
    else:
        sprite_files = [f for f in os.listdir(sprites_full) if f.endswith(('.png', '.json'))]
        debug_print(f"   ✓ Sprites directory exists ({len(sprite_files)} files)", "SUCCESS")

        # List some sprite files
        if sprite_files:
            debug_print(f"   Files: {', '.join(sprite_files[:5])}", "DEBUG")

    print()
    if issues:
        debug_print("ISSUES FOUND:", "ERROR")
        for issue in issues:
            print(f"   - {issue}")
        print()
        return False
    else:
        debug_print("✅ All file paths verified!", "SUCCESS")
        print()
        return True


class TMXEditor:
    """TMX file editor dengan extensive debugging"""

    def __init__(self, tmx_path):
        self.tmx_path = tmx_path
        self.tree = None
        self.root = None
        self.spawns_layer = None
        self.next_object_id = 1

    def load(self):
        """Load TMX file dengan validation"""
        debug_print(f"Loading TMX: {self.tmx_path}", "INFO")

        if not os.path.exists(self.tmx_path):
            debug_print(f"TMX file tidak ditemukan", "ERROR")
            return False

        try:
            self.tree = ET.parse(self.tmx_path)
            self.root = self.tree.getroot()
            debug_print("TMX parsed successfully", "SUCCESS")
        except ET.ParseError as e:
            debug_print(f"TMX parse error: {e}", "ERROR")
            return False
        except Exception as e:
            debug_print(f"Error loading TMX: {e}", "ERROR")
            return False

        # Get map info
        map_width = self.root.get('width', 'inf')
        map_height = self.root.get('height', 'inf')
        tile_width = self.root.get('tilewidth', '32')
        tile_height = self.root.get('tileheight', '32')

        debug_print(f"Map: {map_width}×{map_height} tiles ({tile_width}×{tile_height} px)", "DEBUG")

        # Get next object ID
        next_id = self.root.get('nextobjectid', '1')
        self.next_object_id = int(next_id)
        debug_print(f"Next object ID: {self.next_object_id}", "DEBUG")

        # Find or create Spawns layer
        self._find_or_create_spawns_layer()

        return True

    def _find_or_create_spawns_layer(self):
        """Find or create Spawns objectgroup"""
        debug_print("Looking for Spawns layer...", "DEBUG")

        objectgroups = self.root.findall('objectgroup')
        debug_print(f"Found {len(objectgroups)} object layer(s)", "DEBUG")

        for og in objectgroups:
            name = og.get('name', 'unnamed')
            obj_count = len(og.findall('object'))
            debug_print(f"  Layer: '{name}' ({obj_count} objects)", "DEBUG")

            if name.lower() in ['spawns', 'spawnner', 'spawn']:
                self.spawns_layer = og
                debug_print(f"✓ Found Spawns layer: '{name}'", "SUCCESS")
                return

        # Create new
        debug_print("Creating new 'Spawns' layer...", "WARNING")

        max_id = 1
        for elem in self.root.findall('.//*[@id]'):
            try:
                elem_id = int(elem.get('id', 0))
                max_id = max(max_id, elem_id)
            except:
                pass

        self.spawns_layer = ET.SubElement(self.root, 'objectgroup')
        self.spawns_layer.set('id', str(max_id + 1))
        self.spawns_layer.set('name', 'Spawns')

        debug_print(f"✓ Created 'Spawns' layer (id: {max_id + 1})", "SUCCESS")

    def add_spawn_point(self, name, x, y):
        """Add spawn point dengan validation"""
        debug_print(f"Adding spawn: {name} at ({x}, {y})", "DEBUG")

        # Check if exists
        existing = self.get_existing_spawns()
        if name in existing:
            debug_print(f"Spawn '{name}' already exists, skipping", "WARNING")
            return False

        obj = ET.SubElement(self.spawns_layer, 'object')
        obj.set('id', str(self.next_object_id))
        obj.set('name', name)
        obj.set('x', str(x))
        obj.set('y', str(y))

        point = ET.SubElement(obj, 'point')

        debug_print(f"✓ Spawn added (id: {self.next_object_id})", "SUCCESS")
        self.next_object_id += 1
        return True

    def get_existing_spawns(self):
        """Get existing spawn names"""
        spawns = []
        if self.spawns_layer is not None:
            for obj in self.spawns_layer.findall('object'):
                name = obj.get('name', '')
                if name:
                    spawns.append(name)
        return spawns

    def save(self, backup=True):
        """Save TMX dengan backup"""
        debug_print(f"Saving TMX...", "INFO")

        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.tmx_path}.backup_{timestamp}"

            try:
                shutil.copy2(self.tmx_path, backup_path)
                debug_print(f"✓ Backup: {backup_path}", "SUCCESS")
            except Exception as e:
                debug_print(f"Backup failed: {e}", "WARNING")

        self.root.set('nextobjectid', str(self.next_object_id))

        try:
            self.tree.write(self.tmx_path, encoding='UTF-8', xml_declaration=True)
            debug_print(f"✓ TMX saved successfully", "SUCCESS")
            return True
        except Exception as e:
            debug_print(f"Save failed: {e}", "ERROR")
            return False


class NPCCodeGenerator:
    """Generate Python code untuk npc.py"""

    def __init__(self, npcs):
        self.npcs = npcs

    def generate_code(self):
        """Generate complete code block"""
        if not self.npcs:
            debug_print("No NPCs to generate", "WARNING")
            return ""

        debug_print(f"Generating code for {len(self.npcs)} NPC(s)", "INFO")

        lines = []
        lines.append("    # ═══════════════════════════════════════════════════════")
        lines.append("    # ⭐ GENERATED NPCs - AUTO-CREATED")
        lines.append(f"    # Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"    # Total NPCs: {len(self.npcs)}")
        lines.append("    # ═══════════════════════════════════════════════════════\n")

        for i, npc in enumerate(self.npcs, 1):
            lines.append(f"    # NPC {i}: {npc['name']} - {npc['role']}")
            lines.append(f"    # Location: ({npc['x']}, {npc['y']})")
            lines.append(f"    # Spawn key: {npc['spawn_key']}")
            if npc.get('quest'):
                lines.append(f"    # Quest: {npc['quest']}")
            lines.append("")

            # Sprite config
            lines.append(f"    npc{i}_sprite = {{")
            for key, value in npc['sprite_config'].items():
                if isinstance(value, str):
                    lines.append(f"        '{key}': '{value}',")
                elif isinstance(value, tuple):
                    lines.append(f"        '{key}': {value},")
                else:
                    lines.append(f"        '{key}': {value},")
            lines.append("    }")
            lines.append("")

            # Dialogue
            lines.append(f"    npc{i}_dialogues = [")
            for dialogue in npc['dialogues']:
                dialogue_escaped = dialogue.replace('"', '\\"')
                lines.append(f'        "{dialogue_escaped}",')
            lines.append("    ]")
            lines.append("")

            # NPC instance
            lines.append(f"    npc{i} = NPC(")
            lines.append(f'        name="{npc["name"]}",')
            lines.append(f"        x={npc['x']},")
            lines.append(f"        y={npc['y']},")
            lines.append(f"        sprite_config=npc{i}_sprite,")
            lines.append(f"        dialogue_lines=npc{i}_dialogues")
            lines.append("    )")
            lines.append(f"    npcs.append(npc{i})")
            lines.append("")

        lines.append("    # ═══════════════════════════════════════════════════════\n")

        return "\n".join(lines)


class NPCFileUpdater:
    """Update npc.py file"""

    def __init__(self, npc_file_path):
        self.npc_file_path = npc_file_path

    def insert_code(self, generated_code):
        """Insert code ke npc.py"""
        debug_print(f"Updating npc.py...", "INFO")

        if not os.path.exists(self.npc_file_path):
            debug_print(f"npc.py not found", "ERROR")
            return False

        try:
            with open(self.npc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            debug_print(f"Read {len(content)} characters", "DEBUG")
        except Exception as e:
            debug_print(f"Failed to read npc.py: {e}", "ERROR")
            return False

        # Find insertion point
        pattern = r'(\s+)(return npcs)'
        match = re.search(pattern, content)

        if not match:
            debug_print("Could not find 'return npcs'", "ERROR")
            debug_print("Saving to new_npcs_code.txt instead", "WARNING")

            try:
                with open("new_npcs_code.txt", 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                debug_print("✓ Code saved to: new_npcs_code.txt", "SUCCESS")
                debug_print("Manually copy to npc.py before 'return npcs'", "INFO")
            except Exception as e:
                debug_print(f"Save failed: {e}", "ERROR")

            return False

        debug_print("✓ Found insertion point", "SUCCESS")

        # Backup
        backup_path = f"{self.npc_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(self.npc_file_path, backup_path)
            debug_print(f"✓ Backup: {backup_path}", "SUCCESS")
        except Exception as e:
            debug_print(f"Backup failed: {e}", "WARNING")

        # Insert
        insert_pos = match.start()
        new_content = content[:insert_pos] + generated_code + "\n" + content[insert_pos:]

        try:
            with open(self.npc_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            debug_print(f"✓ npc.py updated successfully", "SUCCESS")
            return True
        except Exception as e:
            debug_print(f"Write failed: {e}", "ERROR")
            return False


class NPCGenerator:
    """Main NPC generator"""

    def __init__(self):
        self.npcs = []
        self.tmx_path = os.path.join(PROJECT_PATH, TMX_FILE)
        self.npc_file = os.path.join(PROJECT_PATH, NPC_FILE)
        self.tmx_editor = None

        # Auto-load existing config if available
        self._load_existing_config()

    def _load_existing_config(self):
        """Load existing NPCs from config file"""
        config_file = "npcs_config.json"

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.npcs = json.load(f)

                if self.npcs:
                    debug_print(f"✓ Loaded {len(self.npcs)} NPC(s) from {config_file}", "SUCCESS")
                    for npc in self.npcs:
                        debug_print(f"  - {npc['name']} at ({npc['x']}, {npc['y']})", "DEBUG")
            except Exception as e:
                debug_print(f"Warning: Could not load config: {e}", "WARNING")

    def initialize(self):
        """Initialize dengan verification"""
        debug_print("═══════════════════════════════════════════════════════════════", "INFO")
        debug_print("INITIALIZING NPC GENERATOR", "INFO")
        debug_print("═══════════════════════════════════════════════════════════════", "INFO")

        try:
            self.tmx_editor = TMXEditor(self.tmx_path)
            if self.tmx_editor.load():
                debug_print("✅ TMX Editor initialized", "SUCCESS")
                print()
                return True
            else:
                debug_print("TMX Editor initialization failed", "ERROR")
                print()
                return False
        except Exception as e:
            debug_print(f"Initialization error: {e}", "ERROR")
            print()
            return False

    def add_npc_interactive(self):
        """Add NPC interactively"""
        print("\n" + "="*60)
        print("🎓 TAMBAH NPC BARU")
        print("="*60)

        # Basic info
        name = input("\n📝 Nama NPC: ").strip()
        if not name:
            debug_print("Nama tidak boleh kosong!", "ERROR")
            return None

        role = input("👔 Role/Jabatan: ").strip() or "Staff"

        # Coordinates
        print("\n📍 KOORDINAT NPC")
        print("💡 Tips mendapatkan koordinat:")
        print("   1. Buka Tiled → Hover mouse → Lihat status bar")
        print("   2. Atau lihat player position di game (tekan F3)")
        print("   3. Map kampus biasanya: 0-1920 (X), 0-1280 (Y)")
        print()
        print("⚠️  PENTING: Koordinat harus dalam map bounds!")
        print("   Player spawn: (494, 557)")
        print("   Example locations:")
        print("   - Lab Komputer: (800, 600)")
        print("   - Ruang Dosen: (1200, 400)")
        print("   - Dekat player: (600, 500)")

        while True:
            try:
                x_input = input("\n   X coordinate: ").strip()
                y_input = input("   Y coordinate: ").strip()

                x = float(x_input) if x_input else 500
                y = float(y_input) if y_input else 500

                # Validate coordinates
                if x > 2000 or y > 1500:
                    debug_print(f"⚠️  Koordinat sangat jauh: ({x}, {y})", "WARNING")
                    debug_print(f"   Map biasanya max ~1920×1280", "WARNING")
                    debug_print(f"   NPC mungkin di luar map!", "WARNING")

                    confirm = input("   Lanjut dengan koordinat ini? (y/n) [n]: ").strip().lower()
                    if confirm != 'y':
                        continue

                debug_print(f"Koordinat: ({x}, {y})", "SUCCESS")
                break
            except ValueError:
                debug_print("Koordinat harus angka!", "ERROR")

        # Sprite
        sprite_config = self._get_sprite_config_interactive(name)

        # Quest (optional)
        quest = self._get_quest_interactive(role)

        # Dialogue
        dialogues = self._get_dialogues_interactive(role)

        # Create spawn key
        spawn_key = f"npc_{name.lower().replace(' ', '_')}"

        npc_data = {
            "name": name,
            "role": role,
            "x": x,
            "y": y,
            "sprite_config": sprite_config,
            "quest": quest,
            "dialogues": dialogues,
            "spawn_key": spawn_key
        }

        self.npcs.append(npc_data)

        print()
        debug_print(f"NPC '{name}' berhasil ditambahkan!", "SUCCESS")
        debug_print(f"Spawn key: {spawn_key}", "INFO")
        debug_print(f"Lokasi: ({x}, {y})", "INFO")
        if quest:
            debug_print(f"Quest: {quest[:50]}...", "INFO")

        return npc_data

    def _get_sprite_config_interactive(self, npc_name):
        """Get sprite configuration"""
        print("\n🎨 SPRITE CONFIGURATION")
        print("1. Aseprite (PNG + JSON animasi roll film) ⭐ RECOMMENDED")
        print("2. Simple sprite strip (horizontal)")
        print("3. Fallback (kotak warna)")

        choice = input("Pilih (1/2/3) [1]: ").strip() or "1"

        if choice == "1":
            # Aseprite
            print("\n📁 Aseprite Sprite Files (roll film animation):")
            print("   Contoh: sprites/dosen1.png, sprites/dosen1.json")

            default_png = f'sprites/{npc_name.lower().replace(" ", "_")}.png'
            default_json = f'sprites/{npc_name.lower().replace(" ", "_")}.json'

            png_path = input(f"   PNG path [{default_png}]: ").strip() or default_png
            json_path = input(f"   JSON path [{default_json}]: ").strip() or default_json

            # Verify files
            issues = verify_sprite_files(png_path, json_path)

            if issues:
                print()
                debug_print("⚠️  Sprite file issues detected:", "WARNING")
                for issue in issues:
                    print(f"      - {issue}")
                print()

                use_anyway = input("   Continue anyway? (y/n) [y]: ").strip().lower()
                if use_anyway == 'n':
                    debug_print("Using fallback instead", "INFO")
                    return {
                        'type': 'fallback',
                        'color': (100, 100, 200),
                        'size': (48, 48)
                    }

            return {
                'type': 'aseprite',
                'spritesheet': png_path,
                'json': json_path
            }

        elif choice == "2":
            # Simple strip
            print("\n📁 Simple Sprite Strip:")
            sprite_path = input("   PNG path [sprites/dosen.png]: ").strip() or "sprites/dosen.png"

            # Verify
            issues = verify_sprite_files(sprite_path)
            if issues:
                debug_print(f"⚠️  {issues[0]}", "WARNING")

            frame_w = int(input("   Frame width [48]: ").strip() or "48")
            frame_h = int(input("   Frame height [48]: ").strip() or "48")
            num_frames = int(input("   Jumlah frames [4]: ").strip() or "4")

            return {
                'type': 'simple',
                'sprite': sprite_path,
                'frame_width': frame_w,
                'frame_height': frame_h,
                'num_frames': num_frames,
                'frame_duration': 150
            }

        else:
            # Fallback
            print("\n🎨 Pilih warna:")
            print("1. Merah   (200,100,100)")
            print("2. Hijau   (100,200,100)")
            print("3. Biru    (100,100,200)")
            print("4. Kuning  (200,200,100)")
            print("5. Ungu    (150,100,200)")

            color_choice = input("Pilih (1-5) [3]: ").strip() or "3"

            colors = {
                "1": (200, 100, 100),
                "2": (100, 200, 100),
                "3": (100, 100, 200),
                "4": (200, 200, 100),
                "5": (150, 100, 200)
            }

            return {
                'type': 'fallback',
                'color': colors.get(color_choice, (100, 100, 200)),
                'size': (48, 48)
            }

    def _get_quest_interactive(self, role):
        """Get quest for NPC"""
        print("\n🎯 QUEST (Optional)")
        print("Assign quest untuk NPC ini?")

        assign = input("Assign quest? (y/n) [y]: ").strip().lower()
        if assign == 'n':
            return None

        # Determine category from role
        role_lower = role.lower()
        category = "umum"

        if "program" in role_lower or "coding" in role_lower:
            category = "pemrograman"
        elif "database" in role_lower or "basis data" in role_lower:
            category = "database"
        elif "jaringan" in role_lower or "network" in role_lower:
            category = "jaringan"
        elif "matemat" in role_lower:
            category = "matematika"

        print(f"\n💡 Suggested category: {category}")
        print("Pilih kategori quest:")
        categories = list(QUEST_TEMPLATES.keys())
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.capitalize()}")
        print(f"{len(categories)+1}. Custom (input manual)")

        choice = input(f"Pilih (1-{len(categories)+1}): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                selected_category = categories[idx]
                quests = QUEST_TEMPLATES[selected_category]

                print(f"\nPilih quest dari {selected_category}:")
                for i, q in enumerate(quests, 1):
                    print(f"{i}. {q}")

                quest_choice = input(f"Pilih (1-{len(quests)}) [1]: ").strip() or "1"
                try:
                    quest_idx = int(quest_choice) - 1
                    if 0 <= quest_idx < len(quests):
                        return quests[quest_idx]
                except:
                    pass

                return quests[0]
        except:
            pass

        # Custom quest
        custom_quest = input("\n📝 Input quest description: ").strip()
        return custom_quest if custom_quest else None

    def _get_dialogues_interactive(self, role):
        """Get dialogues"""
        print("\n💬 DIALOGUE LINES")

        # Auto-suggest based on role
        role_lower = role.lower()
        category = "umum"

        if "program" in role_lower:
            category = "pemrograman"
        elif "database" in role_lower:
            category = "database"
        elif "jaringan" in role_lower:
            category = "jaringan"
        elif "matemat" in role_lower:
            category = "matematika"

        print(f"💡 Suggested: {category}")
        print("Pilih kategori dialogue:")

        categories = list(DIALOGUE_TEMPLATES.keys())
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.capitalize()}")
        print(f"{len(categories)+1}. Custom")

        choice = input(f"Pilih (1-{len(categories)+1}): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return DIALOGUE_TEMPLATES[categories[idx]].copy()
        except:
            pass

        # Custom
        print("\n💬 Input dialogue lines (ketik 'done' untuk selesai):")
        dialogues = []
        i = 1
        while True:
            line = input(f"   Line {i}: ").strip()
            if line.lower() == 'done':
                break
            if line:
                dialogues.append(line)
                i += 1

        return dialogues if dialogues else DIALOGUE_TEMPLATES["umum"]

    def add_spawns_to_tmx(self):
        """Add spawns to TMX"""
        print("\n" + "="*60)
        debug_print("ADDING SPAWN POINTS TO TMX", "INFO")
        print("="*60 + "\n")

        if not self.tmx_editor:
            debug_print("TMX Editor not initialized", "ERROR")
            return False

        existing = self.tmx_editor.get_existing_spawns()
        debug_print(f"Existing spawns: {len(existing)}", "INFO")

        added = 0
        skipped = 0

        for npc in self.npcs:
            spawn_key = npc['spawn_key']

            if spawn_key in existing:
                debug_print(f"⏭️  Skip (exists): {spawn_key}", "WARNING")
                skipped += 1
            else:
                if self.tmx_editor.add_spawn_point(spawn_key, npc['x'], npc['y']):
                    added += 1

        print()
        debug_print(f"Summary: Added {added}, Skipped {skipped}", "INFO")

        if added > 0:
            if self.tmx_editor.save(backup=True):
                debug_print("✅ TMX updated successfully!", "SUCCESS")
                return True
            else:
                debug_print("Failed to save TMX", "ERROR")
                return False
        elif skipped > 0:
            # Spawns already exist - not an error!
            debug_print("All spawns already exist in TMX", "INFO")
            return True  # Changed from False - this is OK!
        else:
            debug_print("No spawns to process", "WARNING")
            return False

    def update_npc_file(self):
        """Update npc.py"""
        print("\n" + "="*60)
        debug_print("UPDATING NPC.PY FILE", "INFO")
        print("="*60 + "\n")

        code_gen = NPCCodeGenerator(self.npcs)
        generated_code = code_gen.generate_code()

        if not generated_code:
            debug_print("No code generated", "ERROR")
            return False

        updater = NPCFileUpdater(self.npc_file)
        success = updater.insert_code(generated_code)

        if success:
            debug_print("✅ npc.py updated!", "SUCCESS")
        else:
            debug_print("Failed to update npc.py", "ERROR")

        return success

    def save_config(self):
        """Save config JSON"""
        try:
            with open("npcs_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.npcs, f, indent=2, ensure_ascii=False)
            debug_print("✓ Config saved: npcs_config.json", "SUCCESS")
            return True
        except Exception as e:
            debug_print(f"Save config failed: {e}", "ERROR")
            return False

    def verify_implementation(self):
        """Verify implementation"""
        print("\n" + "="*60)
        debug_print("VERIFICATION REPORT", "INFO")
        print("="*60 + "\n")

        all_good = True

        # Check TMX
        debug_print("1. Checking TMX spawns...", "INFO")
        if os.path.exists(self.tmx_path):
            try:
                tree = ET.parse(self.tmx_path)
                root = tree.getroot()

                spawns_found = []
                for og in root.findall('objectgroup'):
                    if og.get('name', '').lower() in ['spawns', 'spawn', 'spawnner']:
                        for obj in og.findall('object'):
                            spawns_found.append(obj.get('name', ''))

                debug_print(f"   Spawns in TMX: {len(spawns_found)}", "INFO")

                for npc in self.npcs:
                    if npc['spawn_key'] in spawns_found:
                        debug_print(f"   ✓ {npc['spawn_key']}", "SUCCESS")
                    else:
                        debug_print(f"   ✗ {npc['spawn_key']} NOT FOUND", "ERROR")
                        all_good = False

            except Exception as e:
                debug_print(f"   Error: {e}", "ERROR")
                all_good = False
        else:
            debug_print("   TMX not found", "ERROR")
            all_good = False

        # Check npc.py
        print()
        debug_print("2. Checking npc.py code...", "INFO")
        if os.path.exists(self.npc_file):
            try:
                with open(self.npc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if "# ⭐ GENERATED NPCs" in content:
                    debug_print("   ✓ Generated code found", "SUCCESS")
                else:
                    debug_print("   ✗ Generated code NOT found", "ERROR")
                    all_good = False

                for npc in self.npcs:
                    if f'name="{npc["name"]}"' in content:
                        debug_print(f"   ✓ {npc['name']} in code", "SUCCESS")
                    else:
                        debug_print(f"   ✗ {npc['name']} NOT in code", "ERROR")
                        all_good = False

            except Exception as e:
                debug_print(f"   Error: {e}", "ERROR")
                all_good = False
        else:
            debug_print("   npc.py not found", "ERROR")
            all_good = False

        # Check game.py flag
        print()
        debug_print("3. Checking game.py...", "INFO")
        game_py = os.path.join(PROJECT_PATH, "game.py")
        if os.path.exists(game_py):
            try:
                with open(game_py, 'r', encoding='utf-8') as f:
                    content = f.read()

                if "ENABLE_SAMPLE_NPCS = False" in content:
                    debug_print("   ✓ ENABLE_SAMPLE_NPCS = False", "SUCCESS")
                elif "ENABLE_SAMPLE_NPCS = True" in content:
                    debug_print("   ⚠️  ENABLE_SAMPLE_NPCS = True", "WARNING")
                    debug_print("      Set to False to use generated NPCs", "INFO")
                else:
                    debug_print("   ⚠️  Flag not found", "WARNING")

            except Exception as e:
                debug_print(f"   Warning: {e}", "WARNING")

        print()
        if all_good:
            debug_print("✅ ALL VERIFICATION PASSED!", "SUCCESS")
        else:
            debug_print("⚠️  SOME VERIFICATION FAILED", "WARNING")

        return all_good


def main():
    """Main program"""
    print("\n" + "🎓"*30)
    print("NPC GENERATOR V2 - FINAL COMPLETE VERSION")
    print("With Animated Sprites, Quests, and Auto-Implementation")
    print("🎓"*30 + "\n")

    # Verify paths
    if not verify_file_paths():
        debug_print("Fix file path issues first!", "ERROR")
        input("\nPress Enter to exit...")
        return

    generator = NPCGenerator()

    if not generator.initialize():
        debug_print("Initialization failed", "ERROR")
        input("\nPress Enter to exit...")
        return

    # Main loop
    while True:
        print("─"*60)
        print("MENU:")
        print("1. 🎓 Tambah NPC baru")
        print("2. 📋 Lihat NPCs yang sudah dibuat")
        print("3. ⭐ IMPLEMENT ke game (TMX + npc.py)")
        print("4. 🔍 VERIFY implementation")
        print("5. 💾 Save config only (no implementation)")
        print("6. 🗑️  Clear all NPCs (reset)")
        print("7. ❌ Exit")
        print("─"*60)

        choice = input("Pilih (1-7): ").strip()

        if choice == "1":
            generator.add_npc_interactive()

        elif choice == "2":
            if not generator.npcs:
                debug_print("Belum ada NPC", "WARNING")
            else:
                print(f"\n📋 NPCs ({len(generator.npcs)}):")
                for i, npc in enumerate(generator.npcs, 1):
                    print(f"   {i}. {npc['name']} - {npc['role']}")
                    print(f"      Location: ({npc['x']}, {npc['y']})")
                    print(f"      Spawn: {npc['spawn_key']}")
                    print(f"      Sprite: {npc['sprite_config']['type']}")
                    if npc.get('quest'):
                        print(f"      Quest: {npc['quest'][:40]}...")

        elif choice == "3":
            if not generator.npcs:
                debug_print("Belum ada NPC untuk di-implement", "ERROR")
            else:
                print("\n⚠️  IMPLEMENT TO GAME")
                print("   This will:")
                print("   1. Edit campus.tmx (add spawn points)")
                print("   2. Edit npc.py (insert NPC code)")
                print("   3. Backup both files")

                confirm = input("\nContinue? (y/n) [y]: ").strip().lower()

                if confirm != 'n':
                    # Implement
                    print()
                    tmx_success = generator.add_spawns_to_tmx()
                    npc_success = generator.update_npc_file()
                    generator.save_config()

                    print("\n" + "="*60)
                    if tmx_success and npc_success:
                        debug_print("✅ IMPLEMENTATION COMPLETE!", "SUCCESS")
                        print("="*60)
                        debug_print("Use Menu 4 to verify", "INFO")
                    else:
                        debug_print("⚠️  Implementation completed with warnings", "WARNING")
                        print("="*60)

                        # Show details
                        if not tmx_success:
                            debug_print("  - TMX: Spawns already exist or error", "DEBUG")
                        else:
                            debug_print("  - TMX: ✓ OK", "DEBUG")

                        if not npc_success:
                            debug_print("  - npc.py: Error updating", "DEBUG")
                        else:
                            debug_print("  - npc.py: ✓ OK", "DEBUG")

                        print()
                        debug_print("Run Menu 4 to verify implementation", "INFO")

        elif choice == "4":
            generator.verify_implementation()

            print("\n📝 NEXT STEPS:")
            print("   1. Set ENABLE_SAMPLE_NPCS = False in game.py")
            print("   2. Run: python game.py")
            print("   3. Press F3 to see spawn points")
            print("   4. NPCs should appear with animations!")

        elif choice == "5":
            generator.save_config()
            debug_print("Config saved (no implementation)", "SUCCESS")

        elif choice == "6":
            # Clear all NPCs
            if not generator.npcs:
                debug_print("Tidak ada NPC untuk dihapus", "WARNING")
            else:
                print(f"\n⚠️  CLEAR ALL NPCs ({len(generator.npcs)} NPCs)")
                print("   This will delete all NPCs from memory")
                print("   (TMX and npc.py will NOT be modified)")

                confirm = input("\nAre you sure? (yes/no): ").strip().lower()

                if confirm == 'yes':
                    generator.npcs = []

                    # Delete config file
                    if os.path.exists("npcs_config.json"):
                        os.remove("npcs_config.json")
                        debug_print("✓ npcs_config.json deleted", "SUCCESS")

                    debug_print("✓ All NPCs cleared from memory", "SUCCESS")
                    debug_print("Re-run script untuk start fresh", "INFO")
                else:
                    debug_print("Clear cancelled", "INFO")

        elif choice == "7":
            print("\n👋 Goodbye!\n")
            break

        else:
            debug_print("Invalid choice", "WARNING")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted\n")
    except Exception as e:
        debug_print(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
