import pygame
import os

# ==========================================
# CONFIGURATION
# ==========================================
SCREEN_WIDTH = 896
SCREEN_HEIGHT = 1152
FPS = 60
TITLE = "RPG : Collisions Strictes"

COLOR_BG = (20, 20, 20)
MOVE_SPEED = 5
ZOOM_FACTOR = 1.5

BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")
MAP_PATH = os.path.join(BASE_DIR, "sale2.png")

# Assure-toi que cette image existe bien !
COLLISION_PATH = os.path.join(BASE_DIR, "colision2.png") 

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.load_assets()
        self.init_player()

    def load_assets(self):
        try:
            # --- 1. CHARGEMENT DE LA CARTE VISUELLE ---
            raw_map = pygame.image.load(MAP_PATH).convert()
            new_w = int(raw_map.get_width() * ZOOM_FACTOR)
            new_h = int(raw_map.get_height() * ZOOM_FACTOR)
            self.map_image = pygame.transform.scale(raw_map, (new_w, new_h))
            self.map_width = new_w
            self.map_height = new_h

            # --- 2. CHARGEMENT DU MASQUE DE COLLISION ---
            if os.path.exists(COLLISION_PATH):
                raw_col = pygame.image.load(COLLISION_PATH).convert()
                self.collision_image = pygame.transform.scale(raw_col, (new_w, new_h))
                
                # --- MODIFICATION ICI : TOLÉRANCE STRICTE ---
                # On ne bloque que si le pixel est STRICTEMENT NOIR (ou presque)
                # Tolérance (2, 2, 2) permet d'éviter les micro-erreurs de compression JPG/PNG
                # mais laissera passer le gris foncé.
                self.collision_mask = pygame.mask.from_threshold(
                    self.collision_image,
                    (0, 0, 0),       # Couleur cible : NOIR
                    (2, 2, 2)        # Tolérance minime (Strictement Noir)
                )
                
                self.has_collision_map = True
                print("Succès : Masque chargé (Seul le Noir pur bloque) !")
            else:
                self.has_collision_map = False
                print("ATTENTION : 'colision1.png' manquant. Tu traverses les murs !")

            # --- 3. SPRITES ---
            idle_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Angry.png")).convert_alpha()
            self.frames_idle_r = self.split_sheet(idle_sheet, 6)
            self.frames_idle_l = self.flip_frames(self.frames_idle_r)

            run_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Walk.png")).convert_alpha()
            self.frames_run_r = self.split_sheet(run_sheet, 6)
            self.frames_run_l = self.flip_frames(self.frames_run_r)

        except FileNotFoundError as e:
            print(f"[ERROR] {e}")
            self.running = False

    def init_player(self):
        # Position X : Au milieu de la largeur de la map
        self.player_x = self.map_width // 2
        
        # Position Y : TOUT EN BAS (Hauteur totale - 150 pixels de marge)
        self.player_y = self.map_height - 250 
        
        self.facing_right = True
        self.state = 'idle'
        self.current_frame = 0
        self.animation_speed = 0.2
        self.camera_x = 0
        self.camera_y = 0
        
        # Hitbox (pieds)
        self.hitbox_radius = 15

    def split_sheet(self, sheet, frame_count):
        frames = []
        fw = sheet.get_width() // frame_count
        fh = sheet.get_height()
        for i in range(frame_count):
            rect = pygame.Rect(i * fw, 0, fw, fh)
            frame = sheet.subsurface(rect)
            frame = pygame.transform.scale(frame, (int(fw * 2 * ZOOM_FACTOR), int(fh * 2 * ZOOM_FACTOR)))
            frames.append(frame)
        return frames

    def flip_frames(self, frames_list):
        return [pygame.transform.flip(f, True, False) for f in frames_list]

    def run(self):
        while self.running:
            self.handle_input()
            self.update_physics()
            self.update_camera()
            self.update_animation()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False

        keys = pygame.key.get_pressed()
        
        self.input_x = 0
        self.input_y = 0

        if keys[pygame.K_LEFT]:  self.input_x = -MOVE_SPEED
        if keys[pygame.K_RIGHT]: self.input_x = MOVE_SPEED
        if keys[pygame.K_UP]:    self.input_y = -MOVE_SPEED
        if keys[pygame.K_DOWN]:  self.input_y = MOVE_SPEED
            
        if self.input_x > 0: self.facing_right = True
        elif self.input_x < 0: self.facing_right = False

    def check_wall(self, x, y):
        """Retourne Vrai si la position (x,y) touche un mur."""
        
        if not self.has_collision_map:
            return False
            
        # Hors map
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
            return True

        # Masque de collision
        try:
            if self.collision_mask.get_at((int(x), int(y))):
                return True
        except IndexError:
            return True

        return False

    def update_physics(self):
        # 1. Test Mouvement Horizontal (X)
        new_x = self.player_x + self.input_x
        if not self.check_wall(new_x, self.player_y):
            self.player_x = new_x

        # 2. Test Mouvement Vertical (Y)
        new_y = self.player_y + self.input_y
        if not self.check_wall(self.player_x, new_y):
            self.player_y = new_y

        if self.input_x != 0 or self.input_y != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

    def update_camera(self):
        target_x = self.player_x - (SCREEN_WIDTH // 2)
        target_y = self.player_y - (SCREEN_HEIGHT // 2)
        
        target_x = max(0, min(target_x, self.map_width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map_height - SCREEN_HEIGHT))
        
        if self.map_width < SCREEN_WIDTH: target_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map_height < SCREEN_HEIGHT: target_y = -(SCREEN_HEIGHT - self.map_height) // 2

        self.camera_x = target_x
        self.camera_y = target_y

    def update_animation(self):
        self.current_frame += self.animation_speed
        if self.state == 'idle': limit = len(self.frames_idle_r)
        else: limit = len(self.frames_run_r)
        if self.current_frame >= limit: self.current_frame = 0

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 1. Map
        self.screen.blit(self.map_image, (-self.camera_x, -self.camera_y))
        
        # 2. Joueur
        frames = self.frames_run_r if self.state == 'running' else self.frames_idle_r
        if not self.facing_right: frames = self.frames_idle_l if self.state == 'idle' else self.frames_run_l
        
        image = frames[int(self.current_frame)]
        rect = image.get_rect()
        
        screen_x = self.player_x - self.camera_x
        screen_y = self.player_y - self.camera_y
        rect.midbottom = (screen_x, screen_y)
        
        self.screen.blit(image, rect)
        pygame.display.flip()

if __name__ == '__main__':
    Game().run()