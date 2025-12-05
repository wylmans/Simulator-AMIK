import json
import os
from datetime import datetime


class SaveSystem:
    """System untuk save dan load game state"""

    SAVE_DIR = "saves"
    SAVE_FILE = "savegame.json"

    def __init__(self):
        # Buat folder saves jika belum ada
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)
            print(f"[SAVE] Created save directory: {self.SAVE_DIR}")

    def save_game(self, player, quest_manager, game_state="playing"):
        """
        Save current game state ke file JSON

        Args:
            player: Player object
            quest_manager: QuestManager object
            game_state: Current game state string

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            save_data = {
                # Metadata
                "save_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",

                # Player data
                "player": {
                    "name": player.name,
                    "x": player.x,
                    "y": player.y,
                    "facing_direction": player.facing_direction
                },

                # Quest data
                "quest": {
                    "total_progress": quest_manager.total_progress,
                    "active_quests": [
                        {
                            "description": q.description,
                            "giver_name": q.giver_name
                        }
                        for q in quest_manager.active_quests
                    ],
                    "completed_count": len(quest_manager.completed_quests)
                },

                # Game state
                "game_state": game_state
            }

            # Write to file
            save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            print(f"[SAVE] Game saved successfully to {save_path}")
            return True

        except Exception as e:
            print(f"[SAVE] Error saving game: {e}")
            return False

    def load_game(self):
        """
        Load game state dari file JSON

        Returns:
            dict: Save data jika berhasil, None jika gagal
        """
        try:
            save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)

            if not os.path.exists(save_path):
                print("[SAVE] No save file found")
                return None

            with open(save_path, 'r') as f:
                save_data = json.load(f)

            print(f"[SAVE] Game loaded from {save_path}")
            print(f"[SAVE] Save date: {save_data.get('save_date', 'Unknown')}")

            return save_data

        except Exception as e:
            print(f"[SAVE] Error loading game: {e}")
            return None

    def save_exists(self):
        """Check apakah save file ada"""
        save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
        return os.path.exists(save_path)

    def delete_save(self):
        """Delete save file"""
        try:
            save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
            if os.path.exists(save_path):
                os.remove(save_path)
                print("[SAVE] Save file deleted")
                return True
            return False
        except Exception as e:
            print(f"[SAVE] Error deleting save: {e}")
            return False

    def get_save_info(self):
        """Get informasi tentang save file"""
        save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)

        if not os.path.exists(save_path):
            return None

        try:
            with open(save_path, 'r') as f:
                data = json.load(f)

            return {
                "player_name": data.get("player", {}).get("name", "Unknown"),
                "progress": data.get("quest", {}).get("total_progress", 0),
                "save_date": data.get("save_date", "Unknown"),
                "exists": True
            }
        except:
            return None


class GameSettings:
    """Manage game settings (volume, fullscreen, etc)"""

    SETTINGS_FILE = "settings.json"

    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings dari file"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                print("[SETTINGS] Settings loaded")
                return settings
        except Exception as e:
            print(f"[SETTINGS] Error loading: {e}")

        # Default settings
        return {
            "music_volume": 0.3,
            "sound_volume": 0.6,
            "fullscreen": False
        }

    def save_settings(self):
        """Save settings ke file"""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("[SETTINGS] Settings saved")
            return True
        except Exception as e:
            print(f"[SETTINGS] Error saving: {e}")
            return False

    def set(self, key, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()

    def get(self, key, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
