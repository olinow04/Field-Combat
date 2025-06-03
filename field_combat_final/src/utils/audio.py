# # utils/audio.py
# import pygame
# import os
#
# class AudioManager:
#     def __init__(self):
#         pygame.mixer.init()
#         self.effects = {}
#
#     def load_effect(self, name, rel_path):
#         # build full path under assets/
#         full = os.path.join(ASSETS_DIR, rel_path)
#         self.effects[name] = pygame.mixer.Sound(full)
#
#     def play_effect(self, name):
#         if name in self.effects:
#             self.effects[name].play()
#
#     def play_music(self, rel_path, loops=-1):
#         full = os.path.join(ASSETS_DIR, rel_path)
#         pygame.mixer.music.load(full)
#         pygame.mixer.music.play(loops)
#
#     def stop_music(self):
#         pygame.mixer.music.stop()
