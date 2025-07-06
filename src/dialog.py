import pygame
import math

class StatsDialog:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.stats_data = {}
        
        # Dialog dimensions
        self.dialog_width = 450
        self.dialog_height = 330
        self.dialog_x = (screen_width - self.dialog_width) // 2
        self.dialog_y = (screen_height - self.dialog_height) // 2
        
        # Colors
        self.overlay_color = (0, 0, 0, 128)  # Semi-transparent black
        self.dialog_bg_color = (45, 45, 45)  # Dark gray
        self.border_color = (100, 200, 255)  # Light blue
        self.title_color = (255, 255, 255)   # White
        self.text_color = (220, 220, 220)    # Light gray
        self.accent_color = (100, 200, 255)  # Light blue
        self.button_color = (70, 130, 180)   # Steel blue
        self.button_hover_color = (100, 150, 200)  # Lighter blue
        
        # Fonts (will be initialized lazily)
        self.title_font = None
        self.header_font = None
        self.text_font = None
        self.small_font = None
        
        # Button
        self.button_width = 100
        self.button_height = 40
        self.button_x = self.dialog_x + (self.dialog_width - self.button_width) // 2
        self.button_y = self.dialog_y + self.dialog_height - 55
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_hovered = False
        
        # Animation
        self.animation_progress = 0.0
        self.animation_speed = 0.1
        
    def _init_fonts(self):
        if self.title_font is None:
            self.title_font = pygame.font.Font(None, 32)
            self.header_font = pygame.font.Font(None, 24)
            self.text_font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 18)
    
    def show(self, stats_data):
        self.stats_data = stats_data
        self.visible = True
        self.animation_progress = 0.0
        
    def hide(self):
        self.visible = False
        
    def update(self, mouse_pos):
        if not self.visible:
            return
            
        # Update animation
        if self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            
        # Update button hover state
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
        
    def handle_click(self, mouse_pos):
        if not self.visible:
            return False
            
        # Check if clicked on OK button
        if self.button_rect.collidepoint(mouse_pos):
            self.hide()
            return True
            
        # Check if clicked outside dialog (close dialog)
        dialog_rect = pygame.Rect(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height)
        if not dialog_rect.collidepoint(mouse_pos):
            self.hide()
            return True
            
        return False
        
    def draw(self, screen):
        if not self.visible:
            return
            
        # Initialize fonts if needed
        self._init_fonts()
            
        # Create overlay surface
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Animation easing
        ease_progress = self._ease_out_back(self.animation_progress)
        
        # Calculate animated dialog position
        anim_dialog_y = self.dialog_y + (1 - ease_progress) * 50
        
        # Draw dialog background with rounded corners
        dialog_rect = pygame.Rect(self.dialog_x, anim_dialog_y, self.dialog_width, self.dialog_height)
        self._draw_rounded_rect(screen, dialog_rect, self.dialog_bg_color, 15)
        
        # Draw border
        border_rect = pygame.Rect(self.dialog_x - 2, anim_dialog_y - 2, self.dialog_width + 4, self.dialog_height + 4)
        self._draw_rounded_rect(screen, border_rect, self.border_color, 15, 2)
        
        # Draw title
        title_text = self.title_font.render("Algorithm Performance Statistics", True, self.title_color)
        title_x = self.dialog_x + (self.dialog_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, anim_dialog_y + 20))
        
        # Draw separator line
        line_y = anim_dialog_y + 60
        pygame.draw.line(screen, self.accent_color, 
                        (self.dialog_x + 20, line_y), 
                        (self.dialog_x + self.dialog_width - 20, line_y), 2)
        
        # Draw statistics
        self._draw_stats(screen, anim_dialog_y + 80)
        
        # Draw OK button
        button_color = self.button_hover_color if self.button_hovered else self.button_color
        button_rect = pygame.Rect(self.button_x, anim_dialog_y + self.dialog_height - 55, 
                                 self.button_width, self.button_height)
        self._draw_rounded_rect(screen, button_rect, button_color, 8)
        
        # Draw button text
        button_text = self.header_font.render("OK", True, self.title_color)
        button_text_x = button_rect.x + (button_rect.width - button_text.get_width()) // 2
        button_text_y = button_rect.y + (button_rect.height - button_text.get_height()) // 2
        screen.blit(button_text, (button_text_x, button_text_y))
        
    def _draw_stats(self, screen, start_y):
        if not self.stats_data:
            return
            
        # Single column layout with better spacing
        col_x = self.dialog_x + 40
        row_height = 28
        
        # Only essential statistics
        all_stats = [
            ("Algorithm:", self.stats_data.get('algorithm', 'N/A')),
            ("Status:", self.stats_data.get('status', 'N/A')),
            ("Search Time:", self.stats_data.get('time', 'N/A')),
            ("Memory Usage:", self.stats_data.get('memory', 'N/A')),
            ("Expanded Nodes:", self.stats_data.get('expanded_nodes', 'N/A')),
            ("Solution Length:", self.stats_data.get('solution_length', 'N/A')),
        ]
        
        # Draw stats in a clean single column format
        for i, (label, value) in enumerate(all_stats):
            y_pos = start_y + 20 + i * row_height
            
            # Draw label
            label_text = self.text_font.render(label, True, self.text_color)
            screen.blit(label_text, (col_x, y_pos))
            
            # Draw value (aligned to the right side)
            value_text = self.text_font.render(str(value), True, self.title_color)
            value_x = col_x + 150
            screen.blit(value_text, (value_x, y_pos))
            
    def _draw_rounded_rect(self, screen, rect, color, radius, width=0):
        """Draw a rectangle."""
        if width == 0:
            pygame.draw.rect(screen, color, rect)
            # Draw corner circles
            pygame.draw.circle(screen, color, (rect.left + radius, rect.top + radius), radius)
            pygame.draw.circle(screen, color, (rect.right - radius, rect.top + radius), radius)
            pygame.draw.circle(screen, color, (rect.left + radius, rect.bottom - radius), radius)
            pygame.draw.circle(screen, color, (rect.right - radius, rect.bottom - radius), radius)
        else:
            pygame.draw.rect(screen, color, rect, width)
            
    def _ease_out_back(self, t):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2) 
