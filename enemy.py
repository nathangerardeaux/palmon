import pygame
import os
import math
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.x = start_x
        self.y = start_y
        self.facing = 'down'
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2
        
        self.load_sprites()
        
        self.image = self.anims_walk['down'][0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.x, self.y)
        
        # --- HITBOX DU MOB ---
        self.hitbox = self.rect.inflate(-100, -95)

    def load_sprites(self):
        # (Identique au joueur pour l'instant)
        path_walk = os.path.join(SPRITE_DIR, WALK_SPRITE)
        sheet_walk = pygame.image.load(path_walk).convert_alpha()
        self.anims_walk = self.cut_sheet(sheet_walk, 4, 6)

    def cut_sheet(self, sheet, rows, cols):
        # (Identique à Player)
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
        # Calcul direction
        dx_val = player.x - self.rect.centerx
        dy_val = player.y - self.rect.centery
        dist = math.hypot(dx_val, dy_val)

        if dist > 20: # S'arrête un peu avant de coller le joueur
            move_x = (dx_val / dist) * MOB_SPEED
            move_y = (dy_val / dist) * MOB_SPEED
            
            # --- PHYSIQUE HITBOX MOB ---
            self.hitbox.x += move_x
            if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery):
                self.hitbox.x -= move_x
                
            self.hitbox.y += move_y
            if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery):
                self.hitbox.y -= move_y
                
            # Synchro
            self.rect.center = self.hitbox.center
            self.x = self.rect.midbottom[0]
            self.y = self.rect.midbottom[1]

            self.state = 'running'
            
            # Regard
            if abs(move_x) > abs(move_y):
                self.facing = 'right' if move_x > 0 else 'left'
            else:
                self.facing = 'down' if move_y > 0 else 'up'
        else:
            self.state = 'idle'

        self.animate()

    def animate(self):
        current_list = self.anims_walk[self.facing]
        if self.state == 'running':
            self.frame_index += self.animation_speed
            if self.frame_index >= len(current_list):
                self.frame_index = 0
        else:
            self.frame_index = 0

        idx = int(self.frame_index)
        self.image = current_list[idx]
        
        # Mise à jour rect et resynchro hitbox
        old_center = self.hitbox.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center