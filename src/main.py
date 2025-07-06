import pygame
from pygame.locals import *
from gui import main_menu, level_select, settings
from gameplay import gameplay, quit_game, get_state

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1100, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush Hour")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

    if get_state() == "main_menu":
        main_menu(screen)
    elif get_state() == "level_select":
        level_select(screen)
    elif get_state() == "gameplay":
        gameplay(screen)
    elif get_state() == "settings":
        settings(screen)

    pygame.display.flip()
    clock.tick(60)
