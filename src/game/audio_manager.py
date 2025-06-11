import pygame
import os


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.5
        self.background_music = None
        self.is_background_playing = False

    def load_sound(self, name, filepath):
        """Ładuje dźwięk do pamięci"""
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

    def play_sound(self, name):
        """Odtwarza dźwięk jednorazowo"""
        if name in self.sounds:
            self.sounds[name].play()

    def play_background_music(self, name):
        """Odtwarza muzykę w tle w pętli"""
        if name in self.sounds and not self.is_background_playing:
            self.sounds[name].play(-1)  # -1 = nieskończona pętla
            self.is_background_playing = True

    def stop_background_music(self):
        """Zatrzymuje muzykę w tle"""
        pygame.mixer.stop()
        self.is_background_playing = False

    def load_all_game_sounds(self, sounds_dir):
        """Ładuje wszystkie dźwięki gry"""
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


# Singleton pattern
_audio_manager = None


def get_audio_manager():
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
