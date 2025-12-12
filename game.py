import pygame
import sys
from settings import *
from game_map import GameMap
from player import Player
from enemy import Enemy
from ui import UI  # IMPORT UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = 'menu'
        self.font = pygame.font.SysFont("Arial", FONT_SIZE, bold=True)
        self.font_gameover = pygame.font.SysFont("Arial", 80, bold=True)
        self.ui = UI() # UI INSTANCE
        
        btn_w, btn_h = 200, 80
        self.play_button = pygame.Rect(
            (SCREEN_WIDTH // 2 - btn_w // 2),
            (SCREEN_HEIGHT // 2 - btn_h // 2),
            btn_w, btn_h
        )

        self.menu_cam_x = 0
        self.menu_cam_y = 0
        self.menu_cam_speed_x = 2
        self.menu_cam_speed_y = 1
        
        self.map = GameMap()
        self.all_enemies = pygame.sprite.Group()
        
        self.camera_x = 0
        self.camera_y = 0
        self.debug_attack_rect = None
        
        self.start_game()

    def start_game(self):
        start_x = self.map.width // 2
        start_y = self.map.height - 330
        self.player = Player(start_x, start_y)
        self.all_enemies.empty()
        self.wave = 1
        self.spawn_wave()

    def spawn_wave(self):
        if self.wave == 1:
            # XP REWARD AJOUTÉ (20)
            for i in range(3):
                mob = Enemy(400 + (i * 40), 328, max_health=100, damage=5, xp_reward=20)
                self.all_enemies.add(mob)
        elif self.wave == 2:
            # XP REWARD AJOUTÉ (40)
            for i in range(5):
                mob = Enemy(350 + (i * 40), 328, max_health=150, damage=10, xp_reward=40)
                self.all_enemies.add(mob)
        elif self.wave == 3:
            # XP REWARD BOSS (500)
            boss = Enemy(444, 328, max_health=500, damage=20, xp_reward=500)
            self.all_enemies.add(boss)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.state == 'menu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button.collidepoint(event.pos):
                        self.state = 'game'
                        self.update_camera() 

            elif self.state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.player.trigger_attack()
                        self.check_attack_hit()
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'

            elif self.state == 'game_over':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.start_game()
                        self.state = 'game'
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'

    def check_attack_hit(self):
        attack_rect = self.player.hitbox.copy()
        range_attack = 50 
        if self.player.facing == 'right': attack_rect.x += range_attack
        elif self.player.facing == 'left': attack_rect.x -= range_attack
        elif self.player.facing == 'down': attack_rect.y += range_attack
        elif self.player.facing == 'up': attack_rect.y -= range_attack

        if DEBUG_MODE: self.debug_attack_rect = attack_rect

        for mob in self.all_enemies:
            if attack_rect.colliderect(mob.hitbox):
                mob.take_damage(self.player.damage)
                # DONNER XP SI MORT
                if mob.health <= 0:
                    self.player.gain_xp(mob.xp_reward)

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        target_x = max(0, min(target_x, self.map.width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map.height - SCREEN_HEIGHT))
        if self.map.width < SCREEN_WIDTH: target_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map.height < SCREEN_HEIGHT: target_y = -(SCREEN_HEIGHT - self.map_height) // 2
        self.camera_x = target_x
        self.camera_y = target_y

    def update_menu_camera(self):
        self.menu_cam_x += self.menu_cam_speed_x
        self.menu_cam_y += self.menu_cam_speed_y
        if self.menu_cam_x <= 0 or self.menu_cam_x >= self.map.width - SCREEN_WIDTH: self.menu_cam_speed_x *= -1
        if self.menu_cam_y <= 0 or self.menu_cam_y >= self.map.height - SCREEN_HEIGHT: self.menu_cam_speed_y *= -1

    def draw_game_world(self, cam_x, cam_y):
        self.screen.blit(self.map.image, (-cam_x, -cam_y))
        if DEBUG_MODE and self.map.has_collisions: self.screen.blit(self.map.debug_surface, (-cam_x, -cam_y))

        draw_rect_player = self.player.rect.copy()
        draw_rect_player.x -= cam_x
        draw_rect_player.y -= cam_y
        self.screen.blit(self.player.image, draw_rect_player)
        
        for mob in self.all_enemies:
            draw_rect_mob = mob.rect.copy()
            draw_rect_mob.x -= cam_x
            draw_rect_mob.y -= cam_y
            self.screen.blit(mob.image, draw_rect_mob)
            # Barre vie mob
            mob.draw_health(self.screen, cam_x, cam_y)

            if DEBUG_MODE:
                hb_mob = mob.hitbox.copy()
                hb_mob.x -= cam_x
                hb_mob.y -= cam_y
                pygame.draw.rect(self.screen, (0, 0, 255), hb_mob, 2)

        if DEBUG_MODE:
            hb_player = self.player.hitbox.copy()
            hb_player.x -= cam_x
            hb_player.y -= cam_y
            pygame.draw.rect(self.screen, (0, 0, 255), hb_player, 2)
            if self.debug_attack_rect:
                draw_att = self.debug_attack_rect.copy()
                draw_att.x -= cam_x
                draw_att.y -= cam_y
                pygame.draw.rect(self.screen, (255, 0, 0), draw_att, 2)
                self.debug_attack_rect = None

    def run(self):
        while self.running:
            self.handle_events()
            
            if self.state == 'menu':
                self.update_menu_camera()
                self.draw_game_world(self.menu_cam_x, self.menu_cam_y)
                
                small_w = SCREEN_WIDTH // 10
                small_h = SCREEN_HEIGHT // 10
                current = self.screen.copy()
                small = pygame.transform.smoothscale(current, (small_w, small_h))
                blurred = pygame.transform.smoothscale(small, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(blurred, (0, 0))
                
                mouse_pos = pygame.mouse.get_pos()
                btn_color = COLOR_BUTTON_HOVER if self.play_button.collidepoint(mouse_pos) else COLOR_BUTTON
                pygame.draw.rect(self.screen, btn_color, self.play_button, border_radius=12)
                pygame.draw.rect(self.screen, (255,255,255), self.play_button, 2, border_radius=12)
                
                txt = self.font.render("JOUER", True, COLOR_TEXT)
                self.screen.blit(txt, txt.get_rect(center=self.play_button.center))

            elif self.state == 'game':
                self.player.update(self.map)
                
                if self.player.health <= 0:
                    self.state = 'game_over'
                
                for mob in self.all_enemies:
                    mob.update(self.player, self.map)
                
                if len(self.all_enemies) == 0 and self.wave < 4:
                    self.wave += 1
                    self.spawn_wave()
                
                self.update_camera()
                self.screen.fill(COLOR_BG)
                self.draw_game_world(self.camera_x, self.camera_y)
                
                # AFFICHER L'UI
                self.ui.display(self.player)

            elif self.state == 'game_over':
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((50, 0, 0))
                overlay.set_alpha(180)
                self.screen.blit(overlay, (0,0))
                
                txt_go = self.font_gameover.render("GAME OVER", True, (255, 0, 0))
                self.screen.blit(txt_go, txt_go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
                
                txt_restart = self.font.render("Appuie sur 'R' pour Recommencer", True, (255, 255, 255))
                self.screen.blit(txt_restart, txt_restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()