import pygame
from settings import *

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("Arial", UI_FONT_SIZE, bold=True)
        
        # Rectangle Vie
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, UI_BAR_HEIGHT)
        # Rectangle XP (Juste en dessous)
        self.xp_bar_rect = pygame.Rect(10, 35, HEALTH_BAR_WIDTH, 15)

    def show_bar(self, current, max_amount, bg_rect, color):
        # Fond
        pygame.draw.rect(self.display_surface, HEALTH_BG_COLOR, bg_rect)
        
        # Partie remplie
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width
        
        # Dessin
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 2)

    def display(self, player):
        # 1. Barre de Vie
        self.show_bar(player.health, player.max_health, self.health_bar_rect, HEALTH_COLOR)
        txt_hp = self.font.render(f"{int(player.health)}/{player.max_health}", True, UI_BORDER_COLOR)
        self.display_surface.blit(txt_hp, (self.health_bar_rect.right + 10, 10))

        # 2. Barre d'XP
        self.show_bar(player.current_xp, player.max_xp, self.xp_bar_rect, XP_COLOR)
        
        # 3. Texte du Niveau
        txt_lvl = self.font.render(f"Lvl {player.level}", True, LEVEL_TEXT_COLOR)
        self.display_surface.blit(txt_lvl, (self.xp_bar_rect.right + 10, 32))