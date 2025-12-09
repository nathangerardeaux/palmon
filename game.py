import pygame
import os

# ==========================================
# CONSTANTES & CONFIGURATION
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Mon Jeu de Plateforme"

# Couleurs
COLOR_BG = (50, 50, 50)
COLOR_FLOOR = (255, 255, 255)

# Physique
GRAVITY = 0.8
JUMP_FORCE = -18
MOVE_SPEED = 5
FLOOR_Y = 500

# Chemins : On utilise os.path pour que ça marche partout
# __file__ désigne ce fichier "game.py", on cherche le dossier "sprite" à côté.
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")


class Game:
    def __init__(self):
        # Initialisation
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Chargement des ressources
        self.load_assets()

        # Initialisation du joueur
        self.init_player()

    def load_assets(self):
        """Charge les images et prépare les listes Droite/Gauche."""
        try:
            # 1. IDLE
            idle_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Walk_attack.png")).convert_alpha()
            self.frames_idle_r = self.split_sheet(idle_sheet, 6)
            self.frames_idle_l = self.flip_frames(self.frames_idle_r)

            # 2. RUN
            run_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Walk.png")).convert_alpha()
            self.frames_run_r = self.split_sheet(run_sheet, 6)
            self.frames_run_l = self.flip_frames(self.frames_run_r)

            # 3. JUMP
            jump_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Pullup.png")).convert_alpha()
            self.frames_jump_r = self.split_sheet(jump_sheet, 6)
            self.frames_jump_l = self.flip_frames(self.frames_jump_r)

        except FileNotFoundError as e:
            print(f"ERREUR : Impossible de trouver les images dans {SPRITE_DIR}")
            print(e)
            self.running = False

    def init_player(self):
        self.player_x = 300
        self.player_y = FLOOR_Y
        self.velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.state = 'idle'

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.2

    def split_sheet(self, sheet, frame_count):
        """Découpe la sprite sheet."""
        frames = []
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        for i in range(frame_count):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = sheet.subsurface(rect)
            frame = pygame.transform.scale(frame, (frame_width * 2, frame_height * 2))
            frames.append(frame)
        return frames

    def flip_frames(self, frames_list):
        """Crée le miroir des images pour la gauche."""
        return [pygame.transform.flip(f, True, False) for f in frames_list]

    def run(self):
        """Boucle principale."""
        while self.running:
            self.handle_input()
            self.update_physics()
            self.update_animation()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.is_jumping:
                    self.velocity_y = JUMP_FORCE
                    self.is_jumping = True
                    self.current_frame = 0

        keys = pygame.key.get_pressed()
        self.dx = 0

        if keys[pygame.K_LEFT]:
            self.dx = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.dx = MOVE_SPEED
            self.facing_right = True

    def update_physics(self):
        # Horizontal
        self.player_x += self.dx

        # Vertical (Gravité)
        self.velocity_y += GRAVITY
        self.player_y += self.velocity_y

        # Sol
        if self.player_y >= FLOOR_Y:
            self.player_y = FLOOR_Y
            self.velocity_y = 0
            self.is_jumping = False

        # État
        if self.is_jumping:
            self.state = 'jumping'
        elif self.dx != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

    def update_animation(self):
        self.current_frame += self.animation_speed

        # On détermine la liste cible juste pour savoir sa longueur
        if self.state == 'idle':
            count = len(self.frames_idle_r)
        elif self.state == 'running':
            count = len(self.frames_run_r)
        else:
            count = len(self.frames_jump_r)

        if self.current_frame >= count:
            self.current_frame = 0

    def draw(self):
        self.screen.fill(COLOR_BG)
        pygame.draw.line(self.screen, COLOR_FLOOR, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 5)

        # 1. Sélection de la bonne liste d'images
        frames_target = None
        if self.facing_right:
            if self.state == 'idle':
                frames_target = self.frames_idle_r
            elif self.state == 'running':
                frames_target = self.frames_run_r
            elif self.state == 'jumping':
                frames_target = self.frames_jump_r
        else:
            if self.state == 'idle':
                frames_target = self.frames_idle_l
            elif self.state == 'running':
                frames_target = self.frames_run_l
            elif self.state == 'jumping':
                frames_target = self.frames_jump_l

        # 2. Récupération de l'image
        image_to_draw = frames_target[int(self.current_frame)]

        # 3. Ancrage MidBottom (Les pieds sur le sol)
        rect = image_to_draw.get_rect()
        rect.midbottom = (self.player_x, self.player_y)

        self.screen.blit(image_to_draw, rect)
        pygame.display.flip()