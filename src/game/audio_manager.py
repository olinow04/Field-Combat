import pygame
import os


class AudioManager:
    # Inicjalizuje mikser pygame i ustawia głośności
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.background_music = None
        self.is_background_playing = False

    # Ładuje dźwięk z pliku i ustawia głośność efektów
    def load_sound(self, name, filepath):
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
                print(f"✓ Załadowano dźwięk: {name}")
            else:
                print(f"✗ Nie znaleziono pliku: {filepath}")
        except pygame.error as e:
            print(f"✗ Błąd ładowania dźwięku {name}: {e}")

    # Odtwarza dźwięk efektu o podanej nazwie
    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # Odtwarza muzykę w tle w pętli, jeśli nie jest już odtwarzana
    def play_background_music(self, name):
        if name in self.sounds and not self.is_background_playing:
            self.sounds[name].play(-1)
            self.is_background_playing = True

    # Zatrzymuje wszystkie dźwięki i muzykę w tle
    def stop_background_music(self):
        pygame.mixer.stop()
        self.is_background_playing = False

    # Ładuje wszystkie pliki dźwiękowe gry z podanego katalogu
    def load_all_game_sounds(self, sounds_dir):
        sound_files = {
            'background_audio': 'background_audio.wav',
            'end_game_audio': 'end_game_audio.wav',
            'explosion_audio': 'explosion_audio.mp3',
            'game_over_audio': 'game_over_audio.wav',
            'levelup_audio': 'levelup_audio.mp3',
            'player_die': 'player_die.wav',
            'shoot_effect': 'shoot_effect.mp3'
        }

        for name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            self.load_sound(name, filepath)


_audio_manager = None

# Zwraca instancję AudioManager (singleton)
def get_audio_manager():
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
