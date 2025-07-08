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

def show_loading_screen():
    loading_bg = pygame.image.load('./images/gui/intro.png').convert()
    screen.blit(loading_bg, (0, 0))
    
    bar_x, bar_y = WIDTH // 2 - 200, HEIGHT // 2 + 150
    bar_width, bar_height = 400, 20
    corner_radius = bar_height // 2

    for i in range(101):
        screen.blit(loading_bg, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), border_radius=corner_radius)
        pygame.draw.rect(screen, (100, 175, 250), (bar_x, bar_y, int(i / 100 * bar_width), bar_height), border_radius=corner_radius)
        
        font = pygame.font.SysFont("Comic Sans MS", 30)
        percent_text = f"{i}%"
        text_surface = font.render(percent_text, True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - 25, bar_y - 40))
        
        pygame.display.flip()
        pygame.time.delay(30)

show_loading_screen()

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
