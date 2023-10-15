import pygame

# 初始化pygame
pygame.mixer.init()

# 播放音乐
def play_alarm_music(music_file='D:/share/yizhidao.mp3'):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play()

# 停止播放音乐
def stop_alarm_music():
    pygame.mixer.music.stop()
