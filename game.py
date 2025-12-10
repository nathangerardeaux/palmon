import pygame
import os

# ==============================================================================
# CONFIGURATION GLOBALE & CONSTANTES
# ==============================================================================
# Paramètres d'affichage et de boucle de jeu
SCREEN_WIDTH = 896
SCREEN_HEIGHT = 900
FPS = 60
TITLE = "RPG Engine: Big Player, Normal Map"
COLOR_BG = (20, 20, 20)

# Paramètres de gameplay
MOVE_SPEED = 5 

# --- GESTION DES ÉCHELLES D'AFFICHAGE (SCALING) ---
# ZOOM_FACTOR  : Appliqué à l'environnement (Carte, Collisions).
# PLAYER_SCALE : Appliqué aux entités (Joueur).
# Note : Une échelle joueur plus élevée crée un effet de "géant" ou de gros plan.
ZOOM_FACTOR = 1.5   
PLAYER_SCALE = 2.5  

# --- GESTION DES CHEMINS DE FICHIERS ---
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")
MAP_PATH = os.path.join(BASE_DIR, "sale3.png")
COLLISION_PATH = os.path.join(BASE_DIR, "colision3.png")

# Noms des fichiers de spritesheets
WALK_SPRITESHEET = "lvl1Walk.png" 
ATTACK_SPRITESHEET = "lvl1Attack.png"

# ==============================================================================
# CLASSE PRINCIPALE DU JEU
# ==============================================================================
class Game:
    """
    Classe principale gérant l'initialisation, la boucle de jeu, 
    la gestion des événements et le rendu graphique.
    """

    def __init__(self):
        """Initialisation des modules Pygame, de la fenêtre et des variables d'état."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Chargement des ressources graphiques et initialisation du joueur
        self.load_assets()
        self.init_player()

    def load_assets(self):
        """
        Charge les images, cartes et sprites en mémoire.
        Gère le redimensionnement distinct pour la carte (ZOOM_FACTOR) 
        et le joueur (PLAYER_SCALE).
        """
        try:
            # --- 1. CHARGEMENT DE LA CARTE ---
            raw_map = pygame.image.load(MAP_PATH).convert()
            self.map_width = int(raw_map.get_width() * ZOOM_FACTOR)
            self.map_height = int(raw_map.get_height() * ZOOM_FACTOR)
            self.map_image = pygame.transform.scale(raw_map, (self.map_width, self.map_height))

            # --- 2. GESTION DES COLLISIONS ---
            # Charge le masque de collision s'il existe, sinon désactive la physique des murs.
            if os.path.exists(COLLISION_PATH):
                raw_col = pygame.image.load(COLLISION_PATH).convert()
                self.collision_image = pygame.transform.scale(raw_col, (self.map_width, self.map_height))
                
                # Création d'un masque binaire basé sur la couleur noire (seuillage)
                self.collision_mask = pygame.mask.from_threshold(
                    self.collision_image, (0, 0, 0), (2, 2, 2)
                )
                self.has_collision_map = True
            else:
                self.has_collision_map = False

            # --- 3. CHARGEMENT ET DÉCOUPAGE DES SPRITES ---
            
            # -> Animation de MARCHE
            walk_sheet = pygame.image.load(os.path.join(SPRITE_DIR, WALK_SPRITESHEET)).convert_alpha()
            self.animations_walk = self.cut_grid_sheet(walk_sheet, rows=4, cols=6, scale=PLAYER_SCALE)
            
            # -> Animation d'ATTAQUE
            attack_sheet = pygame.image.load(os.path.join(SPRITE_DIR, ATTACK_SPRITESHEET)).convert_alpha()
            
            # Hack : Correction de la largeur de la feuille de sprite si elle n'est pas multiple de 8
            # Cela évite des artefacts lors du découpage automatique.
            if attack_sheet.get_width() % 8 != 0:
                 new_w = (attack_sheet.get_width() // 8 + 1) * 8
                 attack_sheet = pygame.transform.scale(attack_sheet, (new_w, attack_sheet.get_height()))
            
            self.animations_attack = self.cut_grid_sheet(attack_sheet, rows=4, cols=8, scale=PLAYER_SCALE)

        except FileNotFoundError as e:
            print(f"[CRITICAL] Erreur lors du chargement des assets : {e}")
            self.running = False

    def cut_grid_sheet(self, sheet, rows, cols, scale):
        """
        Découpe une feuille de sprites (spritesheet) en une grille d'images individuelles.
        
        Args:
            sheet (Surface): L'image source complète.
            rows (int): Nombre de lignes (directions).
            cols (int): Nombre de colonnes (frames d'animation).
            scale (float): Facteur de redimensionnement à appliquer à chaque frame.
            
        Returns:
            dict: Dictionnaire {direction: [liste_de_frames]}.
        """
        frame_width = sheet.get_width() // cols
        frame_height = sheet.get_height() // rows
        animations = {}
        directions = ['down', 'left', 'right', 'up'] # Ordre standard des RPG Maker/LPC
        
        for row_index in range(rows):
            direction = directions[row_index]
            frames = []
            for col_index in range(cols):
                # Extraction du rectangle correspondant à la frame
                rect = pygame.Rect(col_index * frame_width, row_index * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect)
                
                # Application de l'échelle spécifique (PLAYER_SCALE)
                scaled = pygame.transform.scale(frame, (int(frame_width * scale), int(frame_height * scale)))
                frames.append(scaled)
            animations[direction] = frames
        return animations

    def init_player(self):
        """Initialise la position, l'état et les variables d'animation du joueur."""
        # Positionnement initial (centré horizontalement, décalé vers le bas)
        self.player_x = self.map_width // 2
        self.player_y = self.map_height - 330 
        
        # États
        self.facing_direction = 'down'
        self.state = 'idle'
        self.is_attacking = False
        
        # Animation & Caméra
        self.current_frame = 0
        self.animation_speed = 0.2
        self.camera_x = 0
        self.camera_y = 0

    def run(self):
        """Boucle principale du jeu (Game Loop)."""
        while self.running:
            self.handle_input()      # 1. Entrées utilisateur
            self.update_physics()    # 2. Mouvement et collisions
            self.update_camera()     # 3. Positionnement caméra
            self.update_animation()  # 4. Calcul de la frame actuelle
            self.draw()              # 5. Rendu à l'écran
            self.clock.tick(FPS)     # Régulation des FPS
        pygame.quit()

    def handle_input(self):
        """Gestion des événements Pygame (clavier, fermeture fenêtre)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Gestion des actions ponctuelles (Attaque)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    if not self.is_attacking:
                        self.is_attacking = True
                        self.state = 'attacking'
                        self.current_frame = 0

        # Si le joueur attaque, on bloque les mouvements
        if self.is_attacking:
            self.input_x = 0
            self.input_y = 0
            return

        # Gestion des mouvements continus (Déplacement)
        keys = pygame.key.get_pressed()
        self.input_x = 0
        self.input_y = 0

        if keys[pygame.K_LEFT]:
            self.input_x = -MOVE_SPEED
            self.facing_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            self.input_x = MOVE_SPEED
            self.facing_direction = 'right'
            
        if keys[pygame.K_UP]:
            self.input_y = -MOVE_SPEED
            self.facing_direction = 'up'
        elif keys[pygame.K_DOWN]:
            self.input_y = MOVE_SPEED
            self.facing_direction = 'down'
        
        # Mise à jour de la direction prioritaire en cas de mouvement diagonal
        if self.input_x != 0 and self.input_y != 0:
             if keys[pygame.K_DOWN]: self.facing_direction = 'down'
             elif keys[pygame.K_UP]: self.facing_direction = 'up'
             elif keys[pygame.K_LEFT]: self.facing_direction = 'left'
             elif keys[pygame.K_RIGHT]: self.facing_direction = 'right'

        # Mise à jour de l'état (Course ou Repos)
        if self.input_x != 0 or self.input_y != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

    def check_wall(self, x, y):
        """
        Vérifie la collision avec les murs via le masque de collision.
        Retourne True si une collision est détectée ou si on sort de la carte.
        """
        if not self.has_collision_map: return False
        
        # Vérification des limites de la carte
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height: 
            return True
        
        try:
            # Vérification pixel-perfect sur le masque
            if self.collision_mask.get_at((int(x), int(y))): 
                return True
        except IndexError:
            return True # Sécurité en cas de débordement d'index
        return False

    def update_physics(self):
        """Applique le mouvement sur les axes X et Y séparément pour gérer le glissement contre les murs."""
        if self.is_attacking: return

        # Mouvement Axe X
        new_x = self.player_x + self.input_x
        if not self.check_wall(new_x, self.player_y):
            self.player_x = new_x

        # Mouvement Axe Y
        new_y = self.player_y + self.input_y
        if not self.check_wall(self.player_x, new_y):
            self.player_y = new_y

    def update_camera(self):
        """
        Calcule la position de la caméra pour centrer le joueur.
        La caméra est 'clampée' (restreinte) aux bords de la carte.
        """
        target_x = self.player_x - (SCREEN_WIDTH // 2)
        target_y = self.player_y - (SCREEN_HEIGHT // 2)
        
        # Restriction aux dimensions de la carte
        target_x = max(0, min(target_x, self.map_width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map_height - SCREEN_HEIGHT))
        
        # Centrage spécial si la carte est plus petite que l'écran
        if self.map_width < SCREEN_WIDTH: 
            target_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map_height < SCREEN_HEIGHT: 
            target_y = -(SCREEN_HEIGHT - self.map_height) // 2
            
        self.camera_x = target_x
        self.camera_y = target_y

    def update_animation(self):
        """Gère la progression des frames d'animation selon l'état du joueur."""
        current_anim_list = []
        
        if self.state == 'attacking':
            self.animation_speed = 0.35
            current_anim_list = self.animations_attack[self.facing_direction]
            
        elif self.state == 'running':
            self.animation_speed = 0.2
            current_anim_list = self.animations_walk[self.facing_direction]
            
        else: # state == 'idle'
            # En idle, on affiche simplement la première frame de marche
            current_anim_list = [self.animations_walk[self.facing_direction][0]]

        self.current_frame += self.animation_speed
        
        # Gestion de la fin de l'animation
        if self.current_frame >= len(current_anim_list):
            if self.state == 'attacking':
                self.is_attacking = False
                self.state = 'idle'
                self.current_frame = 0
            else:
                self.current_frame = 0 # Boucle l'animation
            
        frame_index = int(self.current_frame)
        
        # Sécurité pour éviter l'index out of bounds
        if frame_index >= len(current_anim_list): frame_index = 0
        
        self.image_to_draw = current_anim_list[frame_index]

    def draw(self):
        """Rendu graphique des couches (Background -> Map -> Player)."""
        self.screen.fill(COLOR_BG)
        
        # Rendu de la carte avec décalage caméra
        self.screen.blit(self.map_image, (-self.camera_x, -self.camera_y))
        
        # Calcul de la position écran du joueur
        rect = self.image_to_draw.get_rect()
        screen_x = self.player_x - self.camera_x
        screen_y = self.player_y - self.camera_y
        
        # Le point de pivot est 'midbottom' (les pieds du personnage)
        rect.midbottom = (screen_x, screen_y)
        
        # Correction visuelle spécifique pour l'attaque (à cause de la taille de l'épée/effet)
        if self.state == 'attacking':
            offset = 30 
            if self.facing_direction == 'right': rect.x -= offset 
            elif self.facing_direction == 'left': rect.x += offset
        
        self.screen.blit(self.image_to_draw, rect)
        
        pygame.display.flip()

if __name__ == '__main__':
    Game().run()