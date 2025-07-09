import pygame
import math

class StatsDialog:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.stats_data = {}
        
        self.dialog_width = 450
        self.dialog_height = 330
        self.dialog_x = (screen_width - self.dialog_width) // 2
        self.dialog_y = (screen_height - self.dialog_height) // 2
        
        self.overlay_color = (0, 0, 0, 128)
        self.dialog_bg_color = (45, 45, 45)
        self.border_color = (100, 200, 255)
        self.title_color = (255, 255, 255)
        self.text_color = (220, 220, 220)
        self.accent_color = (100, 200, 255)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 150, 200)
        
        self.title_font = None
        self.header_font = None
        self.text_font = None
        
        self.button_width = 100
        self.button_height = 40
        self.button_x = self.dialog_x + (self.dialog_width - self.button_width) // 2
        self.button_y = self.dialog_y + self.dialog_height - 55
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_hovered = False
        
        self.animation_progress = 0.0
        self.animation_speed = 0.1
        
    def _init_fonts(self):
        if self.title_font is None:
            self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
            self.header_font = pygame.font.SysFont("Arial", 22, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 20)

    def show(self, stats_data):
        self.stats_data = stats_data
        self.visible = True
        self.animation_progress = 0.0
        
    def hide(self):
        self.visible = False
        
    def update(self, mouse_pos):
        if not self.visible:
            return
            
        if self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
        
    def handle_click(self, mouse_pos):
        if not self.visible:
            return False
            
        if self.button_rect.collidepoint(mouse_pos):
            self.hide()
            return True
            
        dialog_rect = pygame.Rect(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height)
        if not dialog_rect.collidepoint(mouse_pos):
            self.hide()
            return True
            
        return False
        
    def draw(self, screen):
        if not self.visible:
            return
            
        self._init_fonts()
        
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        screen.blit(overlay, (0, 0))
        
        ease_progress = self._ease_out_back(self.animation_progress)
        anim_dialog_y = self.dialog_y + (1 - ease_progress) * 50
        
        dialog_rect = pygame.Rect(self.dialog_x, anim_dialog_y, self.dialog_width, self.dialog_height)
        border_rect = pygame.Rect(self.dialog_x - 2, anim_dialog_y - 2, self.dialog_width + 4, self.dialog_height + 4)
        
        self._draw_rounded_rect(screen, border_rect, self.border_color, 15)
        self._draw_rounded_rect(screen, dialog_rect, self.dialog_bg_color, 15)
        
        title_text = self.title_font.render("Algorithm Performance Statistics", True, self.title_color)
        title_x = self.dialog_x + (self.dialog_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, anim_dialog_y + 20))
        
        line_y = anim_dialog_y + 60
        pygame.draw.line(screen, self.accent_color, 
                         (self.dialog_x + 20, line_y), 
                         (self.dialog_x + self.dialog_width - 20, line_y), 2)
        
        self._draw_stats(screen, anim_dialog_y + 80)
        
        button_color = self.button_hover_color if self.button_hovered else self.button_color
        button_rect = pygame.Rect(self.button_x, anim_dialog_y + self.dialog_height - 55, 
                                  self.button_width, self.button_height)
        self._draw_rounded_rect(screen, button_rect, button_color, 8)
        
        button_text = self.header_font.render("OK", True, self.title_color)
        text_x = button_rect.x + (button_rect.width - button_text.get_width()) // 2
        text_y = button_rect.y + (button_rect.height - button_text.get_height()) // 2
        screen.blit(button_text, (text_x, text_y))
        
        self.button_rect = button_rect
        
    def _draw_stats(self, screen, start_y):
        if not self.stats_data:
            return
            
        col_x = self.dialog_x + 40
        row_height = 28
        
        rows = [
            ("Algorithm:", self.stats_data.get('algorithm', 'N/A')),
            ("Status:", self.stats_data.get('status', 'N/A')),
            ("Search Time:", self.stats_data.get('time', 'N/A')),
            ("Memory Usage:", self.stats_data.get('memory', 'N/A')),
            ("Expanded Nodes:", self.stats_data.get('expanded_nodes', 'N/A')),
            ("Solution Length:", self.stats_data.get('solution_length', 'N/A')),
        ]
        
        for i, (label, value) in enumerate(rows):
            y = start_y + i * row_height
            label_text = self.text_font.render(label, True, self.text_color)
            value_text = self.text_font.render(str(value), True, self.title_color)
            screen.blit(label_text, (col_x, y))
            screen.blit(value_text, (col_x + 180, y))
        
    def _draw_rounded_rect(self, surface, rect, color, radius):
        """Vẽ hình chữ nhật bo góc."""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        
    def _ease_out_back(self, t):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

class PauseDialog:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.dialog_width = 400
        self.dialog_height = 200
        self.dialog_x = (screen_width - self.dialog_width) // 2
        self.dialog_y = (screen_height - self.dialog_height) // 2

        self.overlay_color = (0, 0, 0, 150)
        self.dialog_bg_color = (30, 30, 30)
        self.border_color = (255, 255, 255)
        self.title_color = (255, 255, 255)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 150, 220)

        self.title_font = None
        self.button_font = None

        self.button_width = 120
        self.button_height = 50
        self.button_x = self.dialog_x + (self.dialog_width - self.button_width) // 2
        self.button_y = self.dialog_y + self.dialog_height - 70
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_hovered = False

    def _init_fonts(self):
        if self.title_font is None:
            self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
            self.button_font = pygame.font.SysFont("Arial", 28)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def update(self, mouse_pos):
        if not self.visible:
            return
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        if not self.visible:
            return False
        if self.button_rect.collidepoint(mouse_pos):
            self.hide()
            return True
        return False

    def draw(self, screen):
        if not self.visible:
            return

        self._init_fonts()

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        screen.blit(overlay, (0, 0))

        dialog_rect = pygame.Rect(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height)
        pygame.draw.rect(screen, self.dialog_bg_color, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, self.border_color, dialog_rect, 3, border_radius=15)

        title_text = self.title_font.render("Game Paused", True, self.title_color)
        title_x = self.dialog_x + (self.dialog_width - title_text.get_width()) // 2
        title_y = self.dialog_y + 40
        screen.blit(title_text, (title_x, title_y))

        button_color = self.button_hover_color if self.button_hovered else self.button_color
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=12)
        button_text = self.button_font.render("Resume", True, (255, 255, 255))
        text_x = self.button_rect.x + (self.button_width - button_text.get_width()) // 2
        text_y = self.button_rect.y + (self.button_height - button_text.get_height()) // 2
        screen.blit(button_text, (text_x, text_y))
