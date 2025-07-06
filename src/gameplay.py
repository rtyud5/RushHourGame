import pygame
import os
import glob
import time
import threading
import sys

from map_loader import load_map
from utils import Board, Vehicle
from solver.bfs import bfs
from solver.dfs import dfs
from solver.ucs import ucs
from solver.astar import astar
from statistics import Statistics
from dialog import StatsDialog

CELL_SIZE = 80
WIDTH, HEIGHT = 1100, 800
stop_event = threading.Event()

STATE = "main_menu"

def set_state(value):
    global STATE
    STATE = value

def get_state():
    return STATE

LEVELS = sorted([
    int(os.path.splitext(os.path.basename(f))[0].replace('map', ''))
    for f in glob.glob(os.path.join('maps', 'map*.json'))
])
selected_level = None
board = None
initial_board = None
algo_func = bfs

# Stats dialog
stats_dialog = StatsDialog(WIDTH, HEIGHT)
current_stats = Statistics()
current_algorithm = "BFS"

car_images = {}
current_map_folder = None
background_img = None

tick_img = None

def load_tick_image():
    global tick_img
    if tick_img is None:
        tick_img = pygame.image.load('./images/src_images/tick.png').convert_alpha()
        tick_img = pygame.transform.scale(tick_img, (40, 40))

GRID_OFFSET_X = 400
GRID_OFFSET_Y = 200

def load_car_images(map_number):
    global car_images, current_map_folder
    car_images = {}
    current_map_folder = os.path.join('.', 'images', f'map{map_number}')
    if not os.path.exists(current_map_folder):
        print(f"Folder images {current_map_folder} không tồn tại!")
        return
    for img_file in os.listdir(current_map_folder):
        if img_file.endswith('.png'):
            name, _ = os.path.splitext(img_file)
            parts = name.split('_')
            if len(parts) != 3:
                continue
            car_id, orientation, length_str = parts
            key = (car_id.lower(), orientation.lower(), int(length_str))
            path = os.path.join(current_map_folder, img_file)
            img = pygame.image.load(path).convert_alpha()
            w = CELL_SIZE if orientation == 'v' else CELL_SIZE * int(length_str)
            h = CELL_SIZE * int(length_str) if orientation == 'v' else CELL_SIZE
            car_images[key] = pygame.transform.scale(img, (w, h))

def go_to_level_select():
    global STATE
    STATE = "level_select"

def go_to_main_menu():
    global STATE
    STATE = "main_menu"

def go_to_settings():
    global STATE
    STATE = "settings"

def go_to_gameplay(level):
    global selected_level, board, initial_board, STATE, current_stats, current_algorithm
    path = os.path.join("maps", f"map{level}.json")
    vehicles = load_map(path)
    board = Board(vehicles)
    initial_board = Board({vid: v for vid, v in vehicles.items()})
    selected_level = level
    STATE = "gameplay"
    current_stats = Statistics()
    current_algorithm = algo_func.__name__.upper()
    stats_dialog.hide()
    load_car_images(level)

def quit_game():
    pygame.quit()
    sys.exit()

def select_bfs():
    global algo_func, current_algorithm
    algo_func = bfs
    current_algorithm = 'BFS'

def select_dfs():
    global algo_func, current_algorithm
    algo_func = dfs
    current_algorithm = 'DFS'

def select_ucs():
    global algo_func, current_algorithm
    algo_func = ucs
    current_algorithm = 'UCS'

def select_astar():
    global algo_func, current_algorithm
    algo_func = astar
    current_algorithm = 'A*'

def reset_game():
    global board, current_stats, current_algorithm
    stop_event.set()
    if initial_board:
        board = Board({vid: v for vid, v in initial_board.vehicles.items()})
        current_stats = Statistics()
        current_algorithm = algo_func.__name__.upper()
        stats_dialog.hide()
    go_to_gameplay(selected_level)

def draw_vehicles(screen):
    for v in board.vehicles.values():
        x = GRID_OFFSET_X + v.col * CELL_SIZE
        y = GRID_OFFSET_Y + v.row * CELL_SIZE
        key = (v.id.lower(), v.orientation.lower(), v.length)
        if key in car_images:
            screen.blit(car_images[key], (x, y))
        else:
            w = (v.length if v.orientation == 'H' else 1) * CELL_SIZE
            h = (v.length if v.orientation == 'V' else 1) * CELL_SIZE
            color = (255, 0, 0) if v.id == 'X' else (0, 102, 204)
            pygame.draw.rect(screen, color, (x, y, w, h))

def solve():
    def worker():
        global board, current_stats, stats_dialog
        stop_event.clear()
        
        # Reset and start tracking
        current_stats = Statistics()
        
        # Call the algorithm with statistics tracking
        try:
            result, stats = algo_func(initial_board)
            
            if not result:
                # Show dialog with no solution or hit limit
                stats_data = stats.get_formatted_stats()
                stats_dialog.show(stats_data)
                return
                
            # Store stats for later display
            final_stats = stats.get_formatted_stats()
            
            # Animate the solution first
            path = result
            board = Board({vid: v for vid, v in initial_board.vehicles.items()})

            def sleep_with_stop_check(total_ms, check_interval_ms=50):
                for _ in range(0, total_ms, check_interval_ms):
                    if stop_event.is_set():
                        break
                    time.sleep(check_interval_ms / 1000)

            # Run animation
            animation_completed = True
            for vid, move in path:
                if stop_event.is_set():
                    animation_completed = False
                    break
                sleep_with_stop_check(300)
                if stop_event.is_set():
                    animation_completed = False
                    break
                v = board.vehicles[vid]
                new_r, new_c = (v.row + move, v.col) if v.orientation == 'V' else (v.row, v.col + move)
                board.vehicles[vid] = Vehicle(v.id, v.orientation, new_r, new_c, v.length)
            
            # Show statistics dialog only after animation completes
            if animation_completed:
                # Add a small delay before showing dialog
                time.sleep(0.5)
                stats_dialog.show(final_stats)
                
        except Exception as e:
            # Show error dialog
            error_stats = {
                'algorithm': current_algorithm,
                'status': f'Error: {str(e)}',
                'time': '0ms',
                'memory': '0KB',
                'expanded_nodes': '0',
                'solution_length': '0'
            }
            stats_dialog.show(error_stats)
            print(f"Error during solving: {e}")

    threading.Thread(target=worker, daemon=True).start()

def gameplay(screen):
    global background_img
    if background_img is None:
        background_img = pygame.image.load('./images/gui/gameplaybg.png').convert()

    screen.blit(background_img, (0, 0))
    draw_vehicles(screen)

    load_tick_image()

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Update dialog
    stats_dialog.update(mouse)

    # Handle dialog events
    if click[0] == 1:  # Left click
        if stats_dialog.handle_click(mouse):
            pygame.time.delay(150)  # Prevent multiple clicks

    bfs_button = pygame.Rect(30, 220, 140, 140)
    dfs_button = pygame.Rect(225, 220, 140, 140)
    ucs_button = pygame.Rect(30, 420, 140, 140)
    astar_button = pygame.Rect(225, 420, 140, 140)

    def draw_tick_on_button(button):
        tick_pos = (button.x + button.width - 40, button.y + button.height - 40)
        screen.blit(tick_img, tick_pos)

    if current_algorithm == 'BFS':
        draw_tick_on_button(bfs_button)
    elif current_algorithm == 'DFS':
        draw_tick_on_button(dfs_button)
    elif current_algorithm == 'UCS':
        draw_tick_on_button(ucs_button)
    elif current_algorithm == 'A*':
        draw_tick_on_button(astar_button)

    # Only handle UI clicks if dialog is not visible
    if not stats_dialog.visible:
        if bfs_button.collidepoint(mouse) and click[0] == 1:
            pygame.time.delay(150)
            select_bfs()
        elif dfs_button.collidepoint(mouse) and click[0] == 1:
            pygame.time.delay(150)
            select_dfs()
        elif ucs_button.collidepoint(mouse) and click[0] == 1:
            pygame.time.delay(150)
            select_ucs()
        elif astar_button.collidepoint(mouse) and click[0] == 1:
            pygame.time.delay(150)
            select_astar()

        solve_button = pygame.Rect(70, 590, 90, 92)
        reset_button = pygame.Rect(230, 590, 90, 92)
        level_select_button = pygame.Rect(750, 20, 90, 92)
        home_button = pygame.Rect(870, 20, 90, 92)
        settings_button = pygame.Rect(990, 20, 90, 92)

        for button, action in [
            (solve_button, solve),
            (reset_button, reset_game),
            (level_select_button, go_to_level_select),
            (home_button, go_to_main_menu),
            (settings_button, lambda: print("Open settings"))
        ]:
            if button.collidepoint(mouse) and click[0] == 1:
                pygame.time.delay(150)
                action()

    # Draw dialog last (on top)
    stats_dialog.draw(screen)
