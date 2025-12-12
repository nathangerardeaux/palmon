import os

# --- AFFICHAGE ---
SCREEN_WIDTH = 896
SCREEN_HEIGHT = 900
FPS = 60
TITLE = "RPG Engine: Leveling & UI"
COLOR_BG = (20, 20, 20)

# --- UI / MENU ---
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (50, 50, 50)
COLOR_BUTTON_HOVER = (100, 100, 100)
FONT_SIZE = 60
BLUR_INTENSITY = 10 

# --- UI BARRES (NOUVEAU) ---
UI_BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
UI_FONT_SIZE = 18

# Couleurs Vie
HEALTH_COLOR = (255, 0, 0)
HEALTH_BG_COLOR = (60, 60, 60)
UI_BORDER_COLOR = (255, 255, 255)

# Couleurs XP (NOUVEAU)
XP_COLOR = (255, 215, 0)        # Or/Jaune
XP_BG_COLOR = (60, 60, 60)      
LEVEL_TEXT_COLOR = (255, 255, 255)

# --- GAME OVER ---
COLOR_GAMEOVER = (200, 0, 0)

# --- GAMEPLAY ---
MOVE_SPEED = 5
ZOOM_FACTOR = 1.5
PLAYER_SCALE = 2.5

# --- ENNEMIS ---
MOB_SPEED = 3.5

# --- CHEMINS ---
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")

# Noms de fichiers
MAP_FILE = "sale3.png"
COLLISION_FILE = "colision3.png"
DEBUG_MODE = True # Mets False pour cacher les hitboxes
WALK_SPRITE = "lvl1Walk.png"
ATTACK_SPRITE = "lvl1Attack.png"