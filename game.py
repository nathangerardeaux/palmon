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
        
        # --- NOUVEAU : GESTION DES GROUPES D'ENNEMIS ---
        self.all_enemies = pygame.sprite.Group() # Le groupe qui contient tous les méchants
        
        self.wave = 1  # On commence Vague 1
        self.spawn_wave() # On lance la première vague
        
        self.camera_x = 0
        self.camera_y = 0
        self.debug_attack_rect = None 

    # --- NOUVEAU : FONCTION POUR GERER LES VAGUES ---
    # --- REMPLACE JUSTE CETTE FONCTION DANS TON GAME.PY ---
    def spawn_wave(self):
        if self.wave == 1:
            print("--- VAGUE 1 : 3 Ennemis (100 PV) ---")
            # On crée une boucle de 3
            for i in range(3):
                # J'ajoute (i * 40) à la position X pour qu'ils ne soient pas tous collés
                mob = Enemy(400 + (i * 40), 328, max_health=100, damage=10)
                self.all_enemies.add(mob)
            
        elif self.wave == 2:
            print("--- VAGUE 2 : 5 Ennemis (200 PV) ---")
            # On crée une boucle de 5
            for i in range(5):
                # 200 HP comme demandé
                mob = Enemy(350 + (i * 40), 328, max_health=200, damage=15)
                self.all_enemies.add(mob)
            
        elif self.wave == 3:
            print("--- VAGUE 3 : LE BOSS ! ---")
            # Je garde tes stats actuelles
            boss = Enemy(444, 328, max_health=300, damage=25)
            self.all_enemies.add(boss)

        elif self.wave == 4:
            print("VICTOIRE ! TU AS GAGNÉ LE JEU !")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.trigger_attack()
                    self.check_attack_hit()

    def check_attack_hit(self):
        attack_rect = self.player.hitbox.copy()
        range_attack = 50 

        if self.player.facing == 'right': attack_rect.x += range_attack
        elif self.player.facing == 'left': attack_rect.x -= range_attack
        elif self.player.facing == 'down': attack_rect.y += range_attack
        elif self.player.facing == 'up': attack_rect.y -= range_attack

        if DEBUG_MODE: self.debug_attack_rect = attack_rect

        # --- NOUVEAU : ON VERIFIE LA COLLISION SUR TOUT LE GROUPE ---
        # On boucle sur tous les ennemis vivants
        for mob in self.all_enemies:
            if attack_rect.colliderect(mob.hitbox):
                mob.take_damage(self.player.damage)
                # Note: si mob meurt (kill), il s'enlève tout seul du groupe self.all_enemies

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        target_x = max(0, min(target_x, self.map.width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map.height - SCREEN_HEIGHT))
        if self.map.width < SCREEN_WIDTH: target_x = -(SCREEN_WIDTH - self.map.width) // 2
        if self.map.height < SCREEN_HEIGHT: target_y = -(SCREEN_HEIGHT - self.map.height) // 2
        self.camera_x = target_x
        self.camera_y = target_y

    def run(self):
        while self.running:
            self.handle_events()
            
            self.player.update(self.map)
            
            # --- UPDATE DE TOUS LES ENNEMIS ---
            for mob in self.all_enemies:
                mob.update(self.player, self.map)
            
            # --- LOGIQUE DE VAGUE ---
            # Si le groupe est vide (tout le monde est mort) ET qu'on n'a pas fini
            if len(self.all_enemies) == 0 and self.wave < 4:
                self.wave += 1 # On passe à la vague suivante
                self.spawn_wave() # On fait apparaître les nouveaux
            
            self.update_camera()
            
            # --- DESSIN ---
            self.screen.fill(COLOR_BG)
            self.screen.blit(self.map.image, (-self.camera_x, -self.camera_y))
            
            if DEBUG_MODE and self.map.has_collisions:
                self.screen.blit(self.map.debug_surface, (-self.camera_x, -self.camera_y))
            
            # Dessin Joueur
            draw_rect_player = self.player.rect.copy()
            draw_rect_player.x -= self.camera_x
            draw_rect_player.y -= self.camera_y
            self.screen.blit(self.player.image, draw_rect_player)
            
            # --- DESSIN DE TOUS LES ENNEMIS ---
            for mob in self.all_enemies:
                draw_rect_mob = mob.rect.copy()
                draw_rect_mob.x -= self.camera_x
                draw_rect_mob.y -= self.camera_y
                self.screen.blit(mob.image, draw_rect_mob)
                
                # Petite barre de vie au dessus des ennemis (Optionnel mais pratique)
                # pygame.draw.rect(self.screen, (255,0,0), (draw_rect_mob.x, draw_rect_mob.y - 10, 30, 5))
                # current_width = 30 * (mob.health / mob.max_health)
                # pygame.draw.rect(self.screen, (0,255,0), (draw_rect_mob.x, draw_rect_mob.y - 10, current_width, 5))
            
            # --- DEBUG VISUEL ---
            if DEBUG_MODE:
                hb_player = self.player.hitbox.copy()
                hb_player.x -= self.camera_x
                hb_player.y -= self.camera_y
                pygame.draw.rect(self.screen, (0, 0, 255), hb_player, 2)
                
                for mob in self.all_enemies:
                    hb_mob = mob.hitbox.copy()
                    hb_mob.x -= self.camera_x
                    hb_mob.y -= self.camera_y
                    pygame.draw.rect(self.screen, (0, 0, 255), hb_mob, 2)

                if self.debug_attack_rect:
                    draw_att = self.debug_attack_rect.copy()
                    draw_att.x -= self.camera_x
                    draw_att.y -= self.camera_y
                    pygame.draw.rect(self.screen, (255, 0, 0), draw_att, 2)
                    self.debug_attack_rect = None

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()