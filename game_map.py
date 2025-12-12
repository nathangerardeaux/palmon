import pygame
import os
from settings import *

class GameMap:
    def __init__(self):
        self.load_map_data()

    def load_map_data(self):
        # Chargement de l'image visuelle (LA CARTE)
        img_path = os.path.join(BASE_DIR, MAP_FILE)
        try:
            raw_image = pygame.image.load(img_path).convert()
            # Redimensionnement selon le ZOOM_FACTOR
            self.width = int(raw_image.get_width() * ZOOM_FACTOR)
            self.height = int(raw_image.get_height() * ZOOM_FACTOR)
            self.image = pygame.transform.scale(raw_image, (self.width, self.height))
        except FileNotFoundError:
            print(f"ERREUR: Impossible de trouver {MAP_FILE}")
            # Fallback (carré noir si pas d'image)
            self.image = pygame.Surface((2000, 2000))
            self.width, self.height = 2000, 2000

        # Chargement des collisions (PHYSIQUE)
        # Cette partie doit s'exécuter PEU IMPORTE le Debug Mode
        col_path = os.path.join(BASE_DIR, COLLISION_FILE)
        
        if os.path.exists(col_path):
            # A. On charge l'image
            raw_col = pygame.image.load(col_path).convert_alpha()
            scaled_col = pygame.transform.scale(raw_col, (self.width, self.height))
            
            # B. On calcule le masque (OBLIGATOIRE POUR QUE LES MURS EXISTENT)
            self.collision_mask = pygame.mask.from_threshold(
                scaled_col, (0, 0, 0), (2, 2, 2)
            )
            self.has_collisions = True
            print("Info: Collisions chargées.")

            # C. Génération visuelle (OPTIONNEL - SEULEMENT SI DEBUG EST TRUE)
            # C'est uniquement l'image rouge qui dépend du debug, pas la physique.
            if DEBUG_MODE:
                self.debug_surface = self.collision_mask.to_surface(
                    setcolor=(255, 0, 0, 100), # Rouge semi-transparent
                    unsetcolor=(0, 0, 0, 0)    # Transparent
                )
        else:
            self.collision_mask = None
            self.has_collisions = False
            print("Attention: Pas de fichier collision trouvé.")

    def check_wall(self, x, y):
        """Vérifie si un point (x, y) est dans un mur."""
        
        # 1. Vérifie les limites de la carte (Bords de l'écran)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
            
        # 2. Si pas de fichier collision, on ne vérifie pas l'intérieur
        if not self.has_collisions:
            return False
        
        # 3. Vérifie le masque
        try:
            if self.collision_mask.get_at((int(x), int(y))):
                return True
        except IndexError:
            return True
            
        return False