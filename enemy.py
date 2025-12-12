import pygame
import os
import math
from settings import *

class Enemy(pygame.sprite.Sprite):
    # ON AJOUTE max_health et damage DANS LES PARAMETRES
    def __init__(self, start_x, start_y, max_health=100, damage=10):
        super().__init__()
        self.x = start_x
        self.y = start_y
        
        # --- STATS DYNAMIQUES ---
        self.max_health = max_health
        self.health = self.max_health
        self.damage = damage
        # ------------------------

        self.attack_range = 30
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        
        self.facing = 'down'
        self.state = 'idle'
        self.is_attacking = False
        self.frame_index = 0
        self.animation_speed = 0.2
        
        self.load_sprites()
        
        self.image = self.anims_walk['down'][0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.x, self.y)
        self.hitbox = self.rect.inflate(-100, -95)


    def load_sprites(self):
        # (Identique à avant)
        path_walk = os.path.join(SPRITE_DIR, WALK_SPRITE)
        sheet_walk = pygame.image.load(path_walk).convert_alpha()
        self.anims_walk = self.cut_sheet(sheet_walk, 4, 6)
        
        path_attack = os.path.join(SPRITE_DIR, ATTACK_SPRITE)
        sheet_attack = pygame.image.load(path_attack).convert_alpha()
        if sheet_attack.get_width() % 8 != 0:
            new_w = (sheet_attack.get_width() // 8 + 1) * 8
            sheet_attack = pygame.transform.scale(sheet_attack, (new_w, sheet_attack.get_height()))
        self.anims_attack = self.cut_sheet(sheet_attack, 4, 8)

    def cut_sheet(self, sheet, rows, cols):
        w = sheet.get_width() // cols
        h = sheet.get_height() // rows
        anims = {}
        dirs = ['down', 'left', 'right', 'up']
        for r in range(rows):
            d = dirs[r]
            frames = []
            for c in range(cols):
                rect = pygame.Rect(c*w, r*h, w, h)
                sub = sheet.subsurface(rect)
                scaled = pygame.transform.scale(sub, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
                frames.append(scaled)
            anims[d] = frames
        return anims

    def update(self, player, game_map):
        if self.is_attacking:
            self.animate()
            return 

        dx_val = player.x - self.rect.centerx
        dy_val = player.y - self.rect.centery
        dist = math.hypot(dx_val, dy_val)

        if dist > 20: 
            # --- MOUVEMENT (Si loin) ---
            move_x = (dx_val / dist) * MOB_SPEED
            move_y = (dy_val / dist) * MOB_SPEED
            
            self.hitbox.x += move_x
            if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery):
                self.hitbox.x -= move_x
            self.hitbox.y += move_y
            if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery):
                self.hitbox.y -= move_y
                
            self.rect.center = self.hitbox.center
            self.x = self.rect.midbottom[0]
            self.y = self.rect.midbottom[1]

            self.state = 'running'
            
            # Mise à jour direction mouvement
            if abs(move_x) > abs(move_y):
                self.facing = 'right' if move_x > 0 else 'left'
            else:
                self.facing = 'down' if move_y > 0 else 'up'

        else:
            # --- COMBAT (Si proche) ---
            self.state = 'idle'
            
            # NOUVEAU : On force le calcul de la direction même à l'arrêt
            # dx_val > 0 veut dire que le joueur est à Droite
            # dy_val > 0 veut dire que le joueur est en Bas
            if abs(dx_val) > abs(dy_val):
                self.facing = 'right' if dx_val > 0 else 'left'
            else:
                self.facing = 'down' if dy_val > 0 else 'up'

            self.check_attack(player)

        self.animate()

    def check_attack(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.is_attacking = True
            self.state = 'attacking'
            self.frame_index = 0
            self.last_attack_time = current_time
            player.take_damage(self.damage)

    def animate(self):
        # (Identique à avant)
        current_list = []
        speed = 0.2
        if self.state == 'attacking':
            current_list = self.anims_attack[self.facing]
            speed = 0.35 
        elif self.state == 'running':
            current_list = self.anims_walk[self.facing]
            speed = self.animation_speed
        else:
            current_list = [self.anims_walk[self.facing][0]]
            speed = 0

        self.frame_index += speed
        if self.frame_index >= len(current_list):
            if self.state == 'attacking':
                self.is_attacking = False
                self.state = 'idle'
                self.frame_index = 0
            else:
                self.frame_index = 0

        idx = int(self.frame_index)
        if idx >= len(current_list): idx = 0
        self.image = current_list[idx]
        
        old_center = self.hitbox.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        if self.state == 'attacking':
            offset = 30
            if self.facing == 'right': self.rect.x -= offset
            elif self.facing == 'left': self.rect.x += offset

    def take_damage(self, amount):
        self.health -= amount
        print(f"L'ennemi a pris {amount} dégâts. Vie restante : {self.health}")
        if self.health <= 0:
            self.kill()
            print("L'ennemi est mort !")