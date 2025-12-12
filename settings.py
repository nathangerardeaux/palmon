import os

# --- AFFICHAGE ---
SCREEN_WIDTH = 896
SCREEN_HEIGHT = 900
FPS = 60
TITLE = "RPG Engine: Modular Structure"
COLOR_BG = (20, 20, 20)

# --- GAMEPLAY ---
MOVE_SPEED = 5
ZOOM_FACTOR = 1.5      # Zoom de la carte
PLAYER_SCALE = 2.5     # Zoom du joueur (Gros personnage)

# --- CHEMINS ---
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")

# Noms de fichiers
MAP_FILE = "sale3.png"
COLLISION_FILE = "colision3.png"
DEBUG_MODE = True
WALK_SPRITE = "lvl1Walk.png"
ATTACK_SPRITE = "lvl1Attack.png"
# --- ENNEMIS ---
MOB_SPEED = 3.5