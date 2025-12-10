import pygame
import os

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
# Display Settings
SCREEN_WIDTH = 896
SCREEN_HEIGHT = 1152
FPS = 60
TITLE = "RPG Engine: Top-Down Physics & Rendering"

# Rendering Colors
COLOR_BG = (20, 20, 20)  # Dark grey fallback for off-map areas

# Gameplay Mechanics
MOVE_SPEED = 5           # Pixels per frame
ZOOM_FACTOR = 1.5        # Global scaling for pixel-art consistency

# File System Paths
# Using os.path ensures cross-platform compatibility (Windows/Linux/Mac)
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "sprite", "3")
MAP_PATH = os.path.join(BASE_DIR, "sale2.png")
COLLISION_PATH = os.path.join(BASE_DIR, "colision2.png")

class Game:
    """
    Main Game Class.
    Manages the game loop, asset loading, physics engine, and rendering pipeline.
    """
    def __init__(self):
        # Initialize Pygame core modules
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Pipeline initialization
        self.load_assets()
        self.init_player()

    def load_assets(self):
        """
        Loads all game assets (textures, maps, collision masks) into VRAM.
        Handles scaling and mask generation for pixel-perfect collisions.
        """
        try:
            # --- 1. Map Visual Layer ---
            # Convert() is crucial for performance (matches display format)
            raw_map = pygame.image.load(MAP_PATH).convert()
            
            # Apply global zoom factor
            self.map_width = int(raw_map.get_width() * ZOOM_FACTOR)
            self.map_height = int(raw_map.get_height() * ZOOM_FACTOR)
            self.map_image = pygame.transform.scale(raw_map, (self.map_width, self.map_height))

            # --- 2. Physics Layer (Collision Mask) ---
            if os.path.exists(COLLISION_PATH):
                raw_col = pygame.image.load(COLLISION_PATH).convert()
                self.collision_image = pygame.transform.scale(raw_col, (self.map_width, self.map_height))
                
                # Thresholding: Creates a binary mask from the image.
                # Logic: Only pixels close to Pure Black (0,0,0) are considered Walls (1).
                # Tolerance (2,2,2) handles potential JPEG/PNG compression artifacts.
                self.collision_mask = pygame.mask.from_threshold(
                    self.collision_image,
                    (0, 0, 0),       # Target: Black walls
                    (2, 2, 2)        # Tolerance: Strict
                )
                self.has_collision_map = True
                print("[INFO] Collision mask generated successfully.")
            else:
                self.has_collision_map = False
                print(f"[WARNING] Collision map not found at {COLLISION_PATH}. Physics disabled.")

            # --- 3. Entity Sprites ---
            # Loading spritesheets. convert_alpha() is required for transparency.
            idle_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Angry.png")).convert_alpha()
            self.frames_idle_r = self.split_sheet(idle_sheet, 6)
            self.frames_idle_l = self.flip_frames(self.frames_idle_r)

            run_sheet = pygame.image.load(os.path.join(SPRITE_DIR, "Walk.png")).convert_alpha()
            self.frames_run_r = self.split_sheet(run_sheet, 6)
            self.frames_run_l = self.flip_frames(self.frames_run_r)

        except FileNotFoundError as e:
            print(f"[CRITICAL] Asset loading failed: {e}")
            self.running = False

    def init_player(self):
        """Initializes player state, position, and camera."""
        # Spawn Point Calculation:
        # Center X, and slightly above the bottom boundary (to avoid spawning inside the south wall)
        self.player_x = self.map_width // 2
        self.player_y = self.map_height - 230 
        
        # State Machine
        self.facing_right = True
        self.state = 'idle'
        
        # Animation
        self.current_frame = 0
        self.animation_speed = 0.2
        
        # Camera (Viewport)
        self.camera_x = 0
        self.camera_y = 0

    def split_sheet(self, sheet, frame_count):
        """Utility: Slices a spritesheet into a list of scaled surfaces."""
        frames = []
        fw = sheet.get_width() // frame_count
        fh = sheet.get_height()
        for i in range(frame_count):
            rect = pygame.Rect(i * fw, 0, fw, fh)
            frame = sheet.subsurface(rect)
            # Scaling applied here to match map zoom
            frame = pygame.transform.scale(frame, (int(fw * 2 * ZOOM_FACTOR), int(fh * 2 * ZOOM_FACTOR)))
            frames.append(frame)
        return frames

    def flip_frames(self, frames_list):
        """Utility: Creates mirrored versions of sprites (Horizontal flip)."""
        return [pygame.transform.flip(f, True, False) for f in frames_list]

    def run(self):
        """Core Game Loop."""
        while self.running:
            # 1. Input Polling
            self.handle_input()
            
            # 2. Physics & Logic Update
            self.update_physics()
            self.update_camera()
            self.update_animation()
            
            # 3. Rendering
            self.draw()
            
            # 4. Frame Pacing (VSync equivalent)
            self.clock.tick(FPS)
        pygame.quit()

    def handle_input(self):
        """Processes raw hardware input into game actions."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Continuous keyboard polling for smooth movement
        keys = pygame.key.get_pressed()
        
        self.input_x = 0
        self.input_y = 0

        # Normalization vector (Diagonal movement handling is simplified here)
        if keys[pygame.K_LEFT]:  self.input_x = -MOVE_SPEED
        if keys[pygame.K_RIGHT]: self.input_x = MOVE_SPEED
        if keys[pygame.K_UP]:    self.input_y = -MOVE_SPEED
        if keys[pygame.K_DOWN]:  self.input_y = MOVE_SPEED
            
        # Update facing direction state
        if self.input_x > 0: self.facing_right = True
        elif self.input_x < 0: self.facing_right = False

    def check_wall(self, x, y):
        """
        Performs a pixel-perfect collision check against the collision mask.
        Returns True if the coordinate (x, y) overlaps with a wall bit.
        """
        if not self.has_collision_map:
            return False
            
        # 1. Bounds Checking: Prevent querying outside mask memory
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
            return True

        # 2. Bitmask Lookup
        try:
            # get_at() returns 1 (True) if the pixel matches the threshold (Wall)
            if self.collision_mask.get_at((int(x), int(y))):
                return True
        except IndexError:
            return True

        return False

    def update_physics(self):
        """
        Applies movement with 'Sliding Collision' logic.
        We check X and Y axes independently to allow sliding along walls.
        """
        # Axis X check
        new_x = self.player_x + self.input_x
        if not self.check_wall(new_x, self.player_y):
            self.player_x = new_x

        # Axis Y check
        new_y = self.player_y + self.input_y
        if not self.check_wall(self.player_x, new_y):
            self.player_y = new_y

        # State update for animation system
        if self.input_x != 0 or self.input_y != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

    def update_camera(self):
        """
        Calculates viewport position to keep player centered.
        Includes clamping to ensure the camera never shows out-of-bounds areas.
        """
        # Target: Player center minus half screen size
        target_x = self.player_x - (SCREEN_WIDTH // 2)
        target_y = self.player_y - (SCREEN_HEIGHT // 2)
        
        # Clamp: Keep camera within Map Bounds (0 to MapSize - ScreenSize)
        target_x = max(0, min(target_x, self.map_width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.map_height - SCREEN_HEIGHT))
        
        # Centering fallback: If map is smaller than screen, center it
        if self.map_width < SCREEN_WIDTH: 
            target_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map_height < SCREEN_HEIGHT: 
            target_y = -(SCREEN_HEIGHT - self.map_height) // 2

        self.camera_x = target_x
        self.camera_y = target_y

    def update_animation(self):
        """Cycles through sprite frames based on delta time and state."""
        self.current_frame += self.animation_speed
        
        if self.state == 'idle': 
            limit = len(self.frames_idle_r)
        else: 
            limit = len(self.frames_run_r)
            
        if self.current_frame >= limit: 
            self.current_frame = 0

    def draw(self):
        """Render pass: Clears screen and draws layers in Z-order."""
        self.screen.fill(COLOR_BG)
        
        # Layer 0: Background Map (Offset by camera)
        self.screen.blit(self.map_image, (-self.camera_x, -self.camera_y))
        
        # Layer 1: Player Entity
        # Select appropriate sprite based on State and Direction
        frames = self.frames_run_r if self.state == 'running' else self.frames_idle_r
        if not self.facing_right: 
            frames = self.frames_idle_l if self.state == 'idle' else self.frames_run_l
        
        image = frames[int(self.current_frame)]
        rect = image.get_rect()
        
        # Coordinate Space Transformation: World Space -> Screen Space
        screen_x = self.player_x - self.camera_x
        screen_y = self.player_y - self.camera_y
        
        # Pivot point: Mid-Bottom (Feet) for correct depth perception
        rect.midbottom = (screen_x, screen_y)
        
        self.screen.blit(image, rect)
        
        # Buffer Swap
        pygame.display.flip()

if __name__ == '__main__':
    Game().run()