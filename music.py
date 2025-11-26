import pygame
import os

class MusicManager:
    def __init__(self, playlist, volume=0.7, fade_duration=2000):
        """
        Inisialisasi Music Manager

        Args:
            playlist: List berisi path file musik
            volume: Volume musik (0.0 - 1.0)
            fade_duration: Durasi fade in/out dalam milidetik
        """
        pygame.mixer.init()
        self.playlist = playlist
        self.current_index = 0
        self.volume = volume
        self.fade_duration = fade_duration
        self.is_playing = False

        # Set event untuk musik selesai
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

    def play(self, index=0):
        """Mulai memutar musik dari index tertentu"""
        if not self.playlist:
            print("Playlist kosong!")
            return

        if index < 0 or index >= len(self.playlist):
            index = 0

        self.current_index = index
        music_path = self.playlist[self.current_index]

        # Cek apakah file ada
        if not os.path.exists(music_path):
            print(f"File musik tidak ditemukan: {music_path}")
            return

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(fade_ms=self.fade_duration)
            self.is_playing = True
            print(f"Memutar: {os.path.basename(music_path)}")
        except pygame.error as e:
            print(f"Error memutar musik: {e}")

    def next_track(self):
        """Pindah ke lagu berikutnya dengan fade out"""
        if not self.is_playing:
            return

        pygame.mixer.music.fadeout(self.fade_duration)
        self.current_index = (self.current_index + 1) % len(self.playlist)

        # Tunggu fade out selesai
        pygame.time.wait(self.fade_duration)
        self.play(self.current_index)

    def previous_track(self):
        """Pindah ke lagu sebelumnya dengan fade out"""
        if not self.is_playing:
            return

        pygame.mixer.music.fadeout(self.fade_duration)
        self.current_index = (self.current_index - 1) % len(self.playlist)

        # Tunggu fade out selesai
        pygame.time.wait(self.fade_duration)
        self.play(self.current_index)

    def handle_music_end(self, event):
        """Handle event ketika musik selesai (untuk auto-play lagu berikutnya)"""
        if event.type == pygame.USEREVENT + 1:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play(self.current_index)

    def pause(self):
        """Pause musik"""
        if self.is_playing:
            pygame.mixer.music.pause()

    def unpause(self):
        """Resume musik yang di-pause"""
        pygame.mixer.music.unpause()

    def stop(self):
        """Stop musik dengan fade out"""
        if self.is_playing:
            pygame.mixer.music.fadeout(self.fade_duration)
            self.is_playing = False

    def set_volume(self, volume):
        """Set volume musik (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def get_current_track(self):
        """Dapatkan info lagu yang sedang diputar"""
        if self.playlist and 0 <= self.current_index < len(self.playlist):
            return os.path.basename(self.playlist[self.current_index])
        return None


# Contoh penggunaan
if __name__ == "__main__":
    # Contoh playlist
    playlist = [
        "music/Caffeine.mp3",
        "music/Dorm.mp3",
    ]

    music_manager = MusicManager(playlist, volume=0.5, fade_duration=2000)
    music_manager.play()
