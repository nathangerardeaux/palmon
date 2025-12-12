import pygame
import sys
from settings import *
from game_map import GameMap
from player import Player
from enemy import Enemy

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.map = GameMap()
        start_x = self.map.width // 2
        start_y = self.map.height - 330
        self.player = Player(start_x, start_y)
        self.mob = Enemy(444, 328)
        
        self.camera_x = 0
        self.camera_y = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.trigger_attack()

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        target_x = max(0, min(target_x, self.map.width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map.height - SCREEN_HEIGHT))
        if self.map.width < SCREEN_WIDTH: target_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map.height < SCREEN_HEIGHT: target_y = -(SCREEN_HEIGHT - self.map.height) // 2
        self.camera_x = target_x
        self.camera_y = target_y

    def run(self):
        while self.running:
            self.handle_events()
            
            self.player.update(self.map)
            self.mob.update(self.player, self.map)
            self.update_camera()
            
            self.screen.fill(COLOR_BG)
            self.screen.blit(self.map.image, (-self.camera_x, -self.camera_y))
            
            if DEBUG_MODE and self.map.has_collisions:
                self.screen.blit(self.map.debug_surface, (-self.camera_x, -self.camera_y))
            
            # --- DESSIN JOUEUR ---
            draw_rect_player = self.player.rect.copy()
            draw_rect_player.x -= self.camera_x
            draw_rect_player.y -= self.camera_y
            self.screen.blit(self.player.image, draw_rect_player)
            
            # --- DESSIN MOB ---
            draw_rect_mob = self.mob.rect.copy()
            draw_rect_mob.x -= self.camera_x
            draw_rect_mob.y -= self.camera_y
            self.screen.blit(self.mob.image, draw_rect_mob)
            
            # --- DEBUG HITBOXES (Carrés bleus) ---
            if DEBUG_MODE:
                # Hitbox Player
                hb_player = self.player.hitbox.copy()
                hb_player.x -= self.camera_x
                hb_player.y -= self.camera_y
                pygame.draw.rect(self.screen, (0, 0, 255), hb_player, 2)
                
                # Hitbox Mob
                hb_mob = self.mob.hitbox.copy()
                hb_mob.x -= self.camera_x
                hb_mob.y -= self.camera_y
                pygame.draw.rect(self.screen, (0, 0, 255), hb_mob, 2)

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()