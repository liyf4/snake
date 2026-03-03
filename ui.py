import pygame
import math
from config import COLOR_BLUE, COLOR_WHITE

class Button:
    def __init__(self, anchor_x, anchor_y, width, height, text_key, font, color=COLOR_BLUE, text_color=COLOR_WHITE, icon=None, is_toggle=False):
        self.anchor_x = anchor_x # 0.0 to 1.0
        self.anchor_y = anchor_y # 0.0 to 1.0
        self.base_width = width
        self.base_height = height
        self.text_key = text_key
        self.font = font
        self.color = color
        self.text_color = text_color
        self.icon = icon
        self.is_toggle = is_toggle
        self.hovered = False
        self.animation_scale = 1.0
        self.rect = pygame.Rect(0, 0, width, height)

    def draw(self, screen, window_size, scale_factor, lang_dict):
        target_scale = 1.05 if self.hovered else 1.0
        self.animation_scale += (target_scale - self.animation_scale) * 0.2
        
        w = self.base_width * scale_factor * self.animation_scale
        h = self.base_height * scale_factor * self.animation_scale
        cx = window_size * self.anchor_x
        cy = window_size * self.anchor_y
        
        self.rect = pygame.Rect(0, 0, max(w, 44*scale_factor), max(h, 44*scale_factor))
        self.rect.center = (cx, cy)

        draw_color = [min(255, c + 30) if self.hovered else c for c in self.color]
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=int(5 * scale_factor))
        
        if self.icon == 'gear':
            self._draw_gear(screen, self.rect, scale_factor)
        elif self.text_key:
            text = lang_dict.get(self.text_key, self.text_key)
            if hasattr(self, 'text_suffix'): text += self.text_suffix
            
            text_surf = self.font.render(text, True, self.text_color)
            if scale_factor != 1.0:
                new_size = (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor))
                text_surf = pygame.transform.smoothscale(text_surf, new_size)
            screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def _draw_gear(self, screen, rect, scale):
        cx, cy = rect.center
        r = rect.width * 0.3
        pygame.draw.circle(screen, self.text_color, (cx, cy), r, int(2*scale))
        for i in range(8):
            angle = math.radians(i * 45)
            x1, y1 = cx + math.cos(angle)*r, cy + math.sin(angle)*r
            x2, y2 = cx + math.cos(angle)*(r+5*scale), cy + math.sin(angle)*(r+5*scale)
            pygame.draw.line(screen, self.text_color, (x1, y1), (x2, y2), int(2*scale))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
