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

        # Variable pour le debug visuel de l'attaque (carré rouge)
        self.debug_attack_rect = None 

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.trigger_attack()
                    ### NOUVEAU : On vérifie si on touche l'ennemi ###
                    self.check_attack_hit()

    ### NOUVEAU : FONCTION DE COMBAT ###
    def check_attack_hit(self):
        # 1. On crée une zone d'attaque basée sur la hitbox du joueur
        attack_rect = self.player.hitbox.copy()
        range_attack = 50 # Portée de l'épée en pixels

        # 2. On déplace cette zone selon la direction du joueur
        if self.player.facing == 'right':
            attack_rect.x += range_attack
        elif self.player.facing == 'left':
            attack_rect.x -= range_attack
        elif self.player.facing == 'down':
            attack_rect.y += range_attack
        elif self.player.facing == 'up':
            attack_rect.y -= range_attack

        # 3. Stockage pour le dessin debug (carré rouge)
        if DEBUG_MODE:
            self.debug_attack_rect = attack_rect

        # 4. Vérification de collision avec le mob
        # On vérifie si le mob est vivant (pv > 0) et si les rectangles se touchent
        if self.mob.health > 0:
            if attack_rect.colliderect(self.mob.hitbox):
                # On inflige les dégâts
                self.mob.take_damage(self.player.damage)

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        target_x = max(0, min(target_x, self.map.width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map.height - SCREEN_HEIGHT))
        
        # Centrage si la carte est plus petite que l'écran
        if self.map.width < SCREEN_WIDTH: 
            target_x = -(SCREEN_WIDTH - self.map.width) // 2
        if self.map.height < SCREEN_HEIGHT: 
            target_y = -(SCREEN_HEIGHT - self.map.height) // 2
            
        self.camera_x = target_x
        self.camera_y = target_y

    def run(self):
        while self.running:
            self.handle_events()
            
            self.player.update(self.map)
            
            # On update le mob seulement s'il est vivant (ou pour jouer l'anim de mort)
            if self.mob.health > 0:
                self.mob.update(self.player, self.map)
            
            self.update_camera()
            
            # --- DESSIN ---
            self.screen.fill(COLOR_BG)
            self.screen.blit(self.map.image, (-self.camera_x, -self.camera_y))
            
            if DEBUG_MODE and self.map.has_collisions:
                self.screen.blit(self.map.debug_surface, (-self.camera_x, -self.camera_y))
            
            # DESSIN JOUEUR
            draw_rect_player = self.player.rect.copy()
            draw_rect_player.x -= self.camera_x
            draw_rect_player.y -= self.camera_y
            self.screen.blit(self.player.image, draw_rect_player)
            
            # DESSIN MOB (Seulement s'il a de la vie)
            if self.mob.health > 0:
                draw_rect_mob = self.mob.rect.copy()
                draw_rect_mob.x -= self.camera_x
                draw_rect_mob.y -= self.camera_y
                self.screen.blit(self.mob.image, draw_rect_mob)
            
            # --- DEBUG VISUEL ---
            if DEBUG_MODE:
                # Hitbox Player (Bleu)
                hb_player = self.player.hitbox.copy()
                hb_player.x -= self.camera_x
                hb_player.y -= self.camera_y
                pygame.draw.rect(self.screen, (0, 0, 255), hb_player, 2)
                
                # Hitbox Mob (Rouge si touché, Bleu sinon) - Seulement si vivant
                if self.mob.health > 0:
                    hb_mob = self.mob.hitbox.copy()
                    hb_mob.x -= self.camera_x
                    hb_mob.y -= self.camera_y
                    pygame.draw.rect(self.screen, (0, 0, 255), hb_mob, 2)

                # Zone d'attaque (Carré Rouge clignotant quand on tape)
                if self.debug_attack_rect:
                    draw_att = self.debug_attack_rect.copy()
                    draw_att.x -= self.camera_x
                    draw_att.y -= self.camera_y
                    pygame.draw.rect(self.screen, (255, 0, 0), draw_att, 2)
                    # On efface le rect après l'avoir dessiné une fois (effet flash)
                    self.debug_attack_rect = None

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()