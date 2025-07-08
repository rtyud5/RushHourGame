import pygame
from pygame.locals import *
from gameplay import go_to_level_select, go_to_main_menu, go_to_gameplay, go_to_settings, quit_game, go_back, set_state

pygame.mixer.init()

WHITE = (255, 255, 255)

main_menu_img = None
level_select_img = None
settings_img = None

pygame.mixer.music.load("./sound/sound.mp3")
pygame.mixer.music.play(-1)

click_sound = pygame.mixer.Sound('./sound/click.wav')
click_sound.set_volume(0.3)

volume = 0.5
volume_dragging = False

BACK_BUTTON = pygame.Rect(40, 40, 60, 60)
HELP_BUTTON = pygame.Rect(120, 470, 150, 186)
ABOUT_US_BUTTON = pygame.Rect(470, 470, 150, 186)
LEAVE_BUTTON = pygame.Rect(820, 470, 150, 186)

level_rects = [
    pygame.Rect(140, 180, 130, 130),  # Level 1
    pygame.Rect(370, 180, 130, 130),  # Level 2
    pygame.Rect(600, 180, 130, 130),  # Level 3
    pygame.Rect(830, 180, 130, 130),  # Level 4
    pygame.Rect(140, 360, 130, 130),  # Level 5
    pygame.Rect(370, 360, 130, 130),  # Level 6
    pygame.Rect(600, 360, 130, 130),  # Level 7
    pygame.Rect(830, 360, 130, 130),  # Level 8
    pygame.Rect(140, 560, 130, 130),  # Level 9
    pygame.Rect(370, 560, 130, 130),  # Level 10
]


def main_menu(screen):
    global main_menu_img
    if main_menu_img is None and pygame.display.get_init():
        main_menu_img = pygame.image.load('./images/gui/mainmenu.png').convert()

    if main_menu_img:
        screen.blit(main_menu_img, (0, 0))
    else:
        screen.fill((30, 30, 30))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    settings_button = pygame.Rect(990, 20, 90, 92)
    play_button = pygame.Rect(400, 415, 300, 96)

    if settings_button.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        go_to_settings()

    if play_button.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        go_to_level_select()


def level_select(screen):
    global level_select_img
    if level_select_img is None and pygame.display.get_init():
        level_select_img = pygame.image.load('./images/gui/levelselect.png').convert()

    if level_select_img:
        screen.blit(level_select_img, (0, 0))
    else:
        screen.fill((30, 30, 30))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if BACK_BUTTON.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        go_to_main_menu()

    for i, rect in enumerate(level_rects):
        if rect.collidepoint(mouse) and click[0] == 1:
            click_sound.play()
            pygame.time.delay(150)
            go_to_gameplay(i + 1)


def settings(screen):
    global settings_img, volume, volume_dragging
    if settings_img is None and pygame.display.get_init():
        settings_img = pygame.image.load('./images/gui/settings.png').convert()

    if settings_img:
        screen.blit(settings_img, (0, 0))
    else:
        screen.fill((30, 30, 30))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    bar_x, bar_y = 350, 270
    bar_width, bar_height = 500, 20
    handle_radius = 18
    corner_radius = bar_height // 2

    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=corner_radius)
    handle_x = bar_x + int(volume * bar_width)
    handle_y = bar_y + bar_height // 2
    pygame.draw.circle(screen, (100, 175, 250), (handle_x, handle_y), handle_radius)

    if click[0] and abs(mouse[0] - handle_x) < handle_radius + 5 and abs(mouse[1] - handle_y) < handle_radius + 5:
        volume_dragging = True
    if not click[0]:
        volume_dragging = False
    if volume_dragging:
        volume = (mouse[0] - bar_x) / bar_width
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)

    font = pygame.font.SysFont("Comic Sans MS", 50)
    percent_text = f"{int(volume * 100)}%"
    text_surface = font.render(percent_text, True, (255, 255, 255))
    screen.blit(text_surface, (320, 350))

    if HELP_BUTTON.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        settings_img_help = None
        if settings_img_help is None and pygame.display.get_init():
            settings_img_help = pygame.image.load('./images/gui/help.png').convert()

        if settings_img_help:
            screen.blit(settings_img_help, (0, 0))
        else:
            screen.fill((30, 30, 30))

        pygame.display.update()

        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.collidepoint(event.pos):
                        click_sound.play()
                        pygame.time.delay(150)
                        running = False

    if ABOUT_US_BUTTON.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        settings_img_about_us = None
        if settings_img_about_us is None and pygame.display.get_init():
            settings_img_about_us = pygame.image.load('./images/gui/aboutus.png').convert()

        if settings_img_about_us:
            screen.blit(settings_img_about_us, (0, 0))
        else:
            screen.fill((30, 30, 30))

        pygame.display.update()

        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.collidepoint(event.pos):
                        click_sound.play()
                        pygame.time.delay(150)
                        running = False

    if LEAVE_BUTTON.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        quit_game()

    if BACK_BUTTON.collidepoint(mouse) and click[0] == 1:
        click_sound.play()
        pygame.time.delay(150)
        go_back()
