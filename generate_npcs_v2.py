#!/usr/bin/env python3
"""
NPC Generator V2 - WITH AUTO TMX SPAWN POINT GENERATION
Otomatis tambah spawn points ke file campus.tmx!

Usage:
    python generate_npcs_v2.py

Features:
    - Interactive input untuk data NPC
    - Input koordinat X, Y untuk setiap NPC
    - Auto-generate spawn points di TMX file
    - Generate Python code untuk npc.py
    - Backup TMX file otomatis
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil

# Template untuk berbagai tipe dialogue
DIALOGUE_TEMPLATES = {
    "pemrograman": [
        "Kerjakan tugas coding tentang {topic}!",
        "Buat program {task} sebagai latihan!",
        "Debug code ini dan temukan errornya!",
        "Implementasikan {concept} dengan Python!",
        "Optimasi kode yang telah kamu buat!"
    ],
    "database": [
        "Buat ERD untuk sistem {system}!",
        "Tulis query SQL untuk {task}!",
        "Normalisasi database sampai 3NF!",
        "Design schema untuk {project}!",
        "Optimasi query yang lambat ini!"
    ],
    "jaringan": [
        "Konfigurasi {device} untuk {purpose}!",
        "Analisis traffic jaringan dengan Wireshark!",
        "Setup {tech} untuk koneksi aman!",
        "Troubleshoot masalah {problem}!",
        "Design topologi jaringan untuk {location}!"
    ],
    "matematika": [
        "Selesaikan {topic} ini!",
        "Hitung {calculation}!",
        "Buktikan teorema ini dengan {method}!",
        "Optimasi fungsi dengan turunan!",
        "Selesaikan sistem persamaan linear!"
    ],
    "umum": [
        "Kerjakan tugas tepat waktu ya!",
        "Baca materi untuk pertemuan berikutnya!",
        "Jangan lupa kumpulkan laporan!",
        "Pelajari konsep yang sudah dijelaskan!",
        "Latihan soal-soal di buku!"
    ],
    "custom": []
}


class TMXEditor:
    """Helper class untuk edit TMX file"""
    
    def __init__(self, tmx_path):
        self.tmx_path = tmx_path
        self.tree = None
        self.root = None
        self.spawns_layer = None
        self.next_object_id = 1
        self.ns = ''
        
    def load(self):
        """Load TMX file"""
        if not os.path.exists(self.tmx_path):
            raise FileNotFoundError(f"TMX file not found: {self.tmx_path}")
        
        self.tree = ET.parse(self.tmx_path)
        self.root = self.tree.getroot()
        # Determine XML namespace if present (e.g. '{http://mapeditor.org}map')
        if '}' in self.root.tag:
            self.ns = self.root.tag.split('}')[0].strip('{')
        else:
            self.ns = ''
        
        # Get next object ID
        next_id = self.root.get('nextobjectid', '1')
        self.next_object_id = int(next_id)
        
        # Find or create Spawns objectgroup
        self._find_or_create_spawns_layer()
        
        print(f"✅ TMX file loaded: {self.tmx_path}")
        print(f"   Next object ID: {self.next_object_id}")
    
    def _find_or_create_spawns_layer(self):
        """Find Spawns objectgroup or create if not exists"""
        # Helper to strip namespace from tag
        def _local(tag):
            return tag.split('}', 1)[-1] if '}' in tag else tag

        # Try to find "Spawns" or "Spawnner" in any namespace
        for element in self.root.findall('.//*'):
            if _local(element.tag) == 'objectgroup':
                name = element.get('name', '')
                if name and name.lower() in ['spawns', 'spawnner']:
                    self.spawns_layer = element
                    print(f"   Found object layer: {name}")
                    return
        
        # Create new objectgroup if not found
        print("   Creating new 'Spawns' object layer...")

        # Find highest layer ID by checking any element with 'id' attribute
        max_id = 0
        for element in self.root.findall('.//*'):
            id_val = element.get('id')
            if id_val and id_val.isdigit():
                layer_id = int(id_val)
                if layer_id > max_id:
                    max_id = layer_id

        # Use namespace-aware tag when creating
        tag = f'{{{self.ns}}}objectgroup' if self.ns else 'objectgroup'
        self.spawns_layer = ET.SubElement(self.root, tag)
        self.spawns_layer.set('id', str(max_id + 1))
        self.spawns_layer.set('name', 'Spawns')

        print(f"   Created 'Spawns' layer (id: {max_id + 1})")
    
    def add_spawn_point(self, name, x, y):
        """Add spawn point object to TMX"""
        # Create object element (namespace-aware)
        tag_obj = f'{{{self.ns}}}object' if self.ns else 'object'
        obj = ET.SubElement(self.spawns_layer, tag_obj)
        obj.set('id', str(self.next_object_id))
        obj.set('name', name)
        obj.set('x', str(x))
        obj.set('y', str(y))

        # Add point element (namespace-aware)
        tag_point = f'{{{self.ns}}}point' if self.ns else 'point'
        ET.SubElement(obj, tag_point)
        
        print(f"   ✅ Added spawn: {name} at ({x}, {y})")
        
        self.next_object_id += 1
    
    def save(self, backup=True):
        """Save TMX file with optional backup"""
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.tmx_path}.backup_{timestamp}"
            shutil.copy2(self.tmx_path, backup_path)
            print(f"\n💾 Backup created: {backup_path}")
        
        # Update nextobjectid
        self.root.set('nextobjectid', str(self.next_object_id))
        
        # Write to file
        self.tree.write(self.tmx_path, encoding='UTF-8', xml_declaration=True)
        print(f"✅ TMX file saved: {self.tmx_path}")
    
    def get_existing_spawns(self):
        """Get list of existing spawn point names"""
        spawns = []
        if self.spawns_layer is not None:
            # Use namespace-agnostic search
            for element in self.spawns_layer.findall('.//*'):
                tag = element.tag.split('}', 1)[-1] if '}' in element.tag else element.tag
                if tag == 'object':
                    name = element.get('name', '')
                    if name:
                        spawns.append(name)
        return spawns


class NPCGenerator:
    def __init__(self, tmx_path="maps/campus.tmx"):
        self.npcs = []
        self.tmx_path = tmx_path
        self.tmx_editor = None
        
    def initialize_tmx(self):
        """Initialize TMX editor"""
        try:
            self.tmx_editor = TMXEditor(self.tmx_path)
            self.tmx_editor.load()
            return True
        except Exception as e:
            print(f"⚠️  Error loading TMX: {e}")
            print(f"   TMX path: {self.tmx_path}")
            print(f"   Spawn points akan di-generate tapi tidak otomatis ditambahkan ke TMX")
            return False
    
    def add_npc_interactive(self):
        """Tambah NPC dengan input interaktif + koordinat"""
        print("\n" + "="*60)
        print("🎓 TAMBAH NPC BARU")
        print("="*60)
        
        # Basic info
        name = input("📝 Nama NPC (contoh: Pak Aldo): ").strip()
        if not name:
            print("⚠️  Nama tidak boleh kosong!")
            return None
        
        role = input("👔 Role/Jabatan (contoh: Dosen Pemrograman): ").strip()
        
        # Location
        print("\n📍 LOKASI NPC DI MAP")
        print("💡 Tips: Buka Tiled untuk lihat koordinat map")
        print("   - Hover mouse di map untuk lihat koordinat di status bar")
        print("   - Atau letakkan temporary object untuk cek koordinat")
        
        while True:
            try:
                x_input = input("   X coordinate (contoh: 800): ").strip()
                y_input = input("   Y coordinate (contoh: 600): ").strip()
                
                x = float(x_input) if x_input else 100
                y = float(y_input) if y_input else 100
                
                print(f"   ✅ Koordinat: ({x}, {y})")
                break
            except ValueError:
                print("   ⚠️  Koordinat harus angka! Coba lagi.")
        
        # Sprite config
        print("\n🎨 SPRITE CONFIGURATION")
        print("Pilih tipe sprite:")
        print("1. Aseprite (punya file .png + .json dari Aseprite)")
        print("2. Simple strip (sprite horizontal strip)")
        print("3. Fallback (kotak warna - untuk prototype)")
        
        sprite_choice = input("Pilih (1/2/3) [default: 3]: ").strip() or "3"
        sprite_config = self._get_sprite_config(sprite_choice, name)
        
        # Dialogue
        print("\n💬 DIALOGUE LINES")
        print("Pilih kategori dialogue:")
        for i, cat in enumerate(DIALOGUE_TEMPLATES.keys(), 1):
            print(f"{i}. {cat.capitalize()}")
        
        categories = list(DIALOGUE_TEMPLATES.keys())
        cat_choice = input(f"Pilih (1-{len(categories)}) [default: 5-umum]: ").strip()
        
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            category = categories[int(cat_choice) - 1]
        else:
            category = "umum"
        
        if category == "custom":
            dialogues = self._get_custom_dialogues()
        else:
            dialogues = DIALOGUE_TEMPLATES[category].copy()
        
        # Create NPC data
        spawn_key = f"npc_{name.lower().replace(' ', '_')}"
        
        npc_data = {
            "name": name,
            "role": role,
            "x": x,
            "y": y,
            "sprite_config": sprite_config,
            "dialogues": dialogues,
            "spawn_key": spawn_key
        }
        
        self.npcs.append(npc_data)
        
        print(f"\n✅ NPC '{name}' berhasil ditambahkan!")
        print(f"   Spawn key: {spawn_key}")
        print(f"   Lokasi: ({x}, {y})")
        
        return npc_data
    
    def _get_sprite_config(self, choice, name):
        """Generate sprite config berdasarkan pilihan"""
        if choice == "1":
            print("\n📁 File Aseprite sprite:")
            sprite_path = input("   Path ke .png (contoh: sprites/pak_aldo.png): ").strip()
            json_path = input("   Path ke .json (contoh: sprites/pak_aldo.json): ").strip()
            
            return {
                'type': 'aseprite',
                'spritesheet': sprite_path or f'sprites/{name.lower().replace(" ", "_")}.png',
                'json': json_path or f'sprites/{name.lower().replace(" ", "_")}.json'
            }
        
        elif choice == "2":
            print("\n📁 Simple sprite strip:")
            sprite_path = input("   Path ke .png (contoh: sprites/dosen.png): ").strip()
            frame_w = input("   Frame width [48]: ").strip() or "48"
            frame_h = input("   Frame height [48]: ").strip() or "48"
            num_frames = input("   Jumlah frames [4]: ").strip() or "4"
            
            return {
                'type': 'simple',
                'sprite': sprite_path or 'sprites/dosen.png',
                'frame_width': int(frame_w),
                'frame_height': int(frame_h),
                'num_frames': int(num_frames),
                'frame_duration': 150
            }
        
        else:
            print("\n🎨 Fallback color (RGB):")
            print("   Preset:")
            print("   1. Merah (200,100,100)")
            print("   2. Hijau (100,200,100)")
            print("   3. Biru (100,100,200)")
            print("   4. Kuning (200,200,100)")
            print("   5. Ungu (150,100,200)")
            print("   6. Custom")
            
            color_choice = input("   Pilih (1-6) [3]: ").strip() or "3"
            
            color_presets = {
                "1": (200, 100, 100),
                "2": (100, 200, 100),
                "3": (100, 100, 200),
                "4": (200, 200, 100),
                "5": (150, 100, 200)
            }
            
            if color_choice in color_presets:
                color = color_presets[color_choice]
            elif color_choice == "6":
                color_input = input("   RGB (format: 200,100,100): ").strip()
                try:
                    r, g, b = map(int, color_input.split(','))
                    color = (r, g, b)
                except:
                    color = (100, 100, 200)
            else:
                color = (100, 100, 200)
            
            return {
                'type': 'fallback',
                'color': color,
                'size': (48, 48)
            }
    
    def _get_custom_dialogues(self):
        """Input custom dialogue lines"""
        dialogues = []
        print("\n💬 Masukkan dialogue lines (ketik 'done' untuk selesai):")
        
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
        """Add all NPC spawn points to TMX file"""
        if not self.tmx_editor:
            print("\n⚠️  TMX editor not initialized")
            return False
        
        print("\n" + "="*60)
        print("📍 MENAMBAHKAN SPAWN POINTS KE TMX")
        print("="*60)
        
        # Get existing spawns
        existing = self.tmx_editor.get_existing_spawns()
        print(f"   Existing spawn points: {len(existing)}")
        
        added = 0
        skipped = 0
        
        for npc in self.npcs:
            spawn_key = npc['spawn_key']
            
            if spawn_key in existing:
                print(f"   ⏭️  Skip: {spawn_key} (already exists)")
                skipped += 1
            else:
                self.tmx_editor.add_spawn_point(
                    spawn_key,
                    npc['x'],
                    npc['y']
                )
                added += 1
        
        print(f"\n📊 Summary:")
        print(f"   Added: {added}")
        print(f"   Skipped: {skipped}")
        
        if added > 0:
            self.tmx_editor.save(backup=True)
            return True
        else:
            print("   No changes to TMX file")
            return False
    
    def generate_code(self):
        """Generate Python code untuk semua NPC"""
        if not self.npcs:
            return "# Tidak ada NPC yang dibuat\n"
        
        code_lines = []
        code_lines.append("    # ═══════════════════════════════════════════════════════")
        code_lines.append("    # ⭐ NPC BARU - GENERATED CODE")
        code_lines.append("    # ═══════════════════════════════════════════════════════\n")
        
        for i, npc in enumerate(self.npcs, 1):
            code_lines.append(f"    # NPC {i}: {npc['name']} - {npc['role']}")
            code_lines.append(f"    # Lokasi: ({npc['x']}, {npc['y']})")
            code_lines.append(f"    # Spawn key: {npc['spawn_key']}\n")
            
            # Sprite config
            code_lines.append(f"    npc{i}_sprite_config = {{")
            for key, value in npc['sprite_config'].items():
                if isinstance(value, str):
                    code_lines.append(f"        '{key}': '{value}',")
                elif isinstance(value, tuple):
                    code_lines.append(f"        '{key}': {value},")
                else:
                    code_lines.append(f"        '{key}': {value},")
            code_lines.append("    }\n")
            
            # Dialogue lines
            code_lines.append(f"    npc{i}_dialogues = [")
            for dialogue in npc['dialogues']:
                code_lines.append(f'        "{dialogue}",')
            code_lines.append("    ]\n")
            
            # NPC creation
            code_lines.append(f"    npc{i} = NPC(")
            code_lines.append(f'        name="{npc["name"]}",')
            code_lines.append(f"        x={npc['x']},  # Akan di-override jika ada spawn point di Tiled")
            code_lines.append(f"        y={npc['y']},  # Koordinat default")
            code_lines.append(f"        sprite_config=npc{i}_sprite_config,")
            code_lines.append(f"        dialogue_lines=npc{i}_dialogues")
            code_lines.append("    )")
            code_lines.append(f"    npcs.append(npc{i})\n")
        
        code_lines.append("    # ═══════════════════════════════════════════════════════\n")
        
        return "\n".join(code_lines)
    
    def save_to_file(self, filename="new_npcs_code.txt"):
        """Save generated code ke file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# ═══════════════════════════════════════════════════════\n")
            f.write("# GENERATED NPC CODE\n")
            f.write("# ═══════════════════════════════════════════════════════\n\n")
            f.write("# INSTRUKSI:\n")
            f.write("# 1. Copy code di bawah ini\n")
            f.write("# 2. Paste ke dalam fungsi create_sample_npcs() di core/npc.py\n")
            f.write("# 3. Paste SEBELUM baris 'return npcs'\n")
            f.write("# 4. Spawn points sudah otomatis ditambahkan ke campus.tmx!\n")
            f.write("# 5. Jalankan game - NPC akan muncul di lokasi yang ditentukan\n\n")
            f.write(self.generate_code())
            
            # Add spawn points summary
            f.write("\n\n# ═══════════════════════════════════════════════════════\n")
            f.write("# SPAWN POINTS SUMMARY\n")
            f.write("# ═══════════════════════════════════════════════════════\n\n")
            
            for npc in self.npcs:
                f.write(f"# {npc['name']} ({npc['role']})\n")
                f.write(f"#   Spawn key: {npc['spawn_key']}\n")
                f.write(f"#   Koordinat: ({npc['x']}, {npc['y']})\n\n")
        
        print(f"\n💾 Code tersimpan di: {filename}")
    
    def export_json(self, filename="npcs_config.json"):
        """Export NPC data sebagai JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.npcs, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON config tersimpan di: {filename}")


def main():
    """Main interactive program"""
    print("\n" + "🎓"*30)
    print("NPC GENERATOR V2 - WITH AUTO TMX SPAWN POINTS")
    print("🎓"*30 + "\n")
    
    # Ask for TMX path
    print("📂 TMX File Location")
    tmx_path = input("   Path to campus.tmx [maps/campus.tmx]: ").strip()
    if not tmx_path:
        tmx_path = "maps/campus.tmx"
    
    generator = NPCGenerator(tmx_path)
    
    # Try to initialize TMX editor
    tmx_available = generator.initialize_tmx()
    
    if not tmx_available:
        print("\n⚠️  WARNING: TMX file tidak bisa dibuka")
        print("   Generator tetap bisa digunakan, tapi spawn points")
        print("   harus ditambahkan manual ke Tiled nanti.")
        cont = input("\n   Lanjut? (y/n) [y]: ").strip().lower()
        if cont == 'n':
            return
    
    while True:
        print("\n" + "─"*60)
        print("MENU:")
        print("1. Tambah NPC baru (dengan koordinat)")
        print("2. Lihat NPC yang sudah dibuat")
        print("3. Generate code dan save")
        if tmx_available:
            print("4. ⭐ Add spawn points to TMX file")
            print("5. Exit")
        else:
            print("4. Exit")
        print("─"*60)
        
        choice = input("Pilih menu: ").strip()
        
        if choice == "1":
            generator.add_npc_interactive()
        
        elif choice == "2":
            if not generator.npcs:
                print("\n⚠️  Belum ada NPC yang dibuat")
            else:
                print(f"\n📋 NPC yang sudah dibuat ({len(generator.npcs)}):")
                for i, npc in enumerate(generator.npcs, 1):
                    print(f"   {i}. {npc['name']} - {npc['role']}")
                    print(f"      Lokasi: ({npc['x']}, {npc['y']})")
                    print(f"      Spawn: {npc['spawn_key']}")
        
        elif choice == "3":
            if not generator.npcs:
                print("\n⚠️  Belum ada NPC yang dibuat!")
            else:
                print("\n" + generator.generate_code())
                
                save = input("\n💾 Save ke file? (y/n) [y]: ").strip().lower()
                if save != 'n':
                    generator.save_to_file()
                    generator.export_json()
                    
                    print("\n✅ Code saved!")
        
        elif choice == "4" and tmx_available:
            if not generator.npcs:
                print("\n⚠️  Belum ada NPC yang dibuat!")
            else:
                confirm = input("\n⚠️  Ini akan mengedit file TMX! Lanjut? (y/n) [y]: ").strip().lower()
                if confirm != 'n':
                    success = generator.add_spawns_to_tmx()
                    if success:
                        print("\n✅ Spawn points berhasil ditambahkan ke TMX!")
                        print("   Buka Tiled untuk verifikasi")
        
        elif choice == ("5" if tmx_available else "4"):
            if generator.npcs:
                print("\n📝 LANGKAH SELANJUTNYA:")
                print("   1. Copy code dari 'new_npcs_code.txt'")
                print("   2. Paste ke 'core/npc.py' di create_sample_npcs()")
                if tmx_available:
                    print("   3. Spawn points sudah ditambahkan ke TMX (cek di Tiled)")
                    print("   4. Jalankan game!")
                else:
                    print("   3. Tambahkan spawn points manual di Tiled")
                    print("   4. Jalankan game!")
            
            print("\n👋 Terima kasih! Happy coding!\n")
            break
        
        else:
            print("\n⚠️  Pilihan tidak valid!")


if __name__ == '__main__':
    main()
