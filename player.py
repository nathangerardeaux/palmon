import pygame
import os
import sys
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.x = start_x
        self.y = start_y
        
        # --- STATS ---
        self.max_health = 100
        self.health = self.max_health
        self.damage = 25
        
        # --- XP & NIVEAUX ---
        self.level = 1
        self.current_xp = 0
        self.max_xp = 100
        # --------------------

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

    def handle_input(self):
        if self.is_attacking: return 0, 0
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:  dx = -MOVE_SPEED; self.facing = 'left'
        elif keys[pygame.K_RIGHT]: dx = MOVE_SPEED; self.facing = 'right'
        if keys[pygame.K_UP]:    dy = -MOVE_SPEED; self.facing = 'up'
        elif keys[pygame.K_DOWN]:  dy = MOVE_SPEED; self.facing = 'down'
        if dx != 0 and dy != 0:
            if keys[pygame.K_DOWN]: self.facing = 'down'
            elif keys[pygame.K_UP]: self.facing = 'up'
        return dx, dy

    def trigger_attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.state = 'attacking'
            self.frame_index = 0

    # --- GESTION XP ---
    def gain_xp(self, amount):
        self.current_xp += amount
        while self.current_xp >= self.max_xp:
            self.current_xp -= self.max_xp
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.damage += 5
        self.health = self.max_health
        self.max_xp = int(self.max_xp * 1.2)
        print(f"NIVEAU {self.level} ! PV: {self.max_health}, DMG: {self.damage}")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def update(self, game_map):
        dx, dy = self.handle_input()

        self.hitbox.x += dx
        if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery) or \
           game_map.check_wall(self.hitbox.left, self.hitbox.centery) or \
           game_map.check_wall(self.hitbox.right, self.hitbox.centery):
            self.hitbox.x -= dx
        
        self.hitbox.y += dy
        if game_map.check_wall(self.hitbox.centerx, self.hitbox.centery) or \
           game_map.check_wall(self.hitbox.centerx, self.hitbox.top) or \
           game_map.check_wall(self.hitbox.centerx, self.hitbox.bottom):
            self.hitbox.y -= dy

        self.rect.center = self.hitbox.center
        self.x = self.rect.midbottom[0]
        self.y = self.rect.midbottom[1]

        if self.is_attacking: self.state = 'attacking'
        elif dx != 0 or dy != 0: self.state = 'running'
        else: self.state = 'idle'

        self.animate()

    def animate(self):
        current_list = []
        speed = 0.2
        if self.state == 'attacking':
            current_list = self.anims_attack[self.facing]
            speed = 0.35
        elif self.state == 'running':
            current_list = self.anims_walk[self.facing]
        else:
            current_list = [self.anims_walk[self.facing][0]]

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