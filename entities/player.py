import pygame
from settings import WIDTH, HEIGHT, ANIMATION_SPEED, PLAYER_START_INVENTORY

# 1. Core Imports
from core.helper import calc_pos_rect, get_grid_pos, get_direction, get_colour
from core.asset_loader import AssetLoader
from core.types import EntityState, Direction
from core.animation import AnimationController
# 2. Entity Imports
from entities.inventory import Inventory
from entities.items import ItemFactory

# 3. World Imports (Assumes you moved tile.py to world/tile.py)
from world.tile import Tile

class Player(pygame.sprite.Sprite):
    # Input Key Variables
    direction_keys = {
        # Horizontal Movement
        pygame.K_a: (-1, 0),    # Left
        pygame.K_LEFT: (-1, 0),
        pygame.K_d: (1, 0),     # Right
        pygame.K_RIGHT: (1, 0),
        
        # Vertical Movement
        pygame.K_w: (0, -1),    # Up
        pygame.K_UP: (0, -1),
        pygame.K_s: (0, 1),     # Down
        pygame.K_DOWN: (0, 1)}
    FACING_MAP = {
        (-1, 0): Direction.LEFT,
        (1, 0):  Direction.RIGHT,
        (0, -1): Direction.UP,
        (0, 1):  Direction.DOWN}
    SLOT_KEY_MAP = {
        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
        pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7}
    INTERACT_KEY = pygame.K_SPACE
    RUN_KEY = pygame.K_LSHIFT

    #Inventory Variables
    INV_SIZE = 8 # will be a single row
    INV_PADDING = 5
    SLOT_SIZE = 50
    def __init__(self, x:int|float, y:int|float, type="Fox"):
        super().__init__()
        self.player_type = type
        self.state = EntityState.IDLE
        self.facing = Direction.DOWN # start looking down
        self.image = pygame.Surface((32, 64))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Create Hitboc
        self.hitbox = pygame.Rect(0, 0, 20, 10)
        self.hitbox.midbottom = self.rect.midbottom

        #Movement
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.direction = pygame.math.Vector2()
        self.animator = AnimationController("PLAYER", type)

        self.base_speed = 200 # pixels per second
        self.current_speed = 0
        self.run_multiplier = 1.5  
        
        #Inventory + Stats
        self.money = 500
        self.setup_inventory()

    def setup_inventory(self):
        """Calculates and initializes the UI rect for the inventory."""
        required_width = self.INV_SIZE * (self.SLOT_SIZE + self.INV_PADDING) + self.INV_PADDING
        required_height = self.SLOT_SIZE + self.INV_PADDING * 2

        inv_rect = calc_pos_rect(
            required_width, required_height, WIDTH, HEIGHT,
            x_offset=0, y_offset= ((HEIGHT - required_height) // 2) - 10)
        
        self.inventory = Inventory(
            max_size=self.INV_SIZE, 
            columns=self.INV_SIZE, 
            rect = inv_rect,
            slot_size=self.SLOT_SIZE,
            padding=self.INV_PADDING)
        
        for item_id, count in PLAYER_START_INVENTORY:
            self.inventory.add_item(ItemFactory.create(item_id, count))
    def handle_event(self, event, all_tiles):
        """Handles discrete inputs (clicks). Call this from Game Loop."""
        if event.type == pygame.KEYDOWN:
            # Interact
            if event.key == self.INTERACT_KEY:
                self.interact(all_tiles)
            
            # Inventory
            if event.key in self.SLOT_KEY_MAP:
                index = self.SLOT_KEY_MAP[event.key]
                self.inventory.set_active_slot(index)
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        # Movement
        for key, (x,y) in self.direction_keys.items():
            if keys[key]:
                self.direction.x += x
                self.direction.y += y
                if (x,y) in self.FACING_MAP:
                    self.facing = self.FACING_MAP[(x, y)]

        # Running Logic
        if keys[self.RUN_KEY]:
            self.current_speed = self.base_speed * self.run_multiplier
        else:
            self.current_speed = self.base_speed

        # Normalization (Fixes diagonal speed boost)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            self.state = EntityState.RUN if keys[self.RUN_KEY] else EntityState.WALK
        else:
            self.state = EntityState.IDLE

    def move(self, dt, tiles):
        """Applies movement to Hitbox, checks collision, then syncs Rect."""
        if self.direction.magnitude() > 0:
            # Horizontal
            self.pos.x += self.direction.x * self.current_speed * dt
            self.hitbox.centerx = round(self.pos.x)
            self.check_collision("horizontal", tiles)

            # Vertical
            self.pos.y += self.direction.y * self.current_speed * dt
            self.hitbox.centery = round(self.pos.y)
            self.check_collision("vertical", tiles)

            # Boundaries
            if self.hitbox.left < 0: 
                self.hitbox.left = 0
                self.pos.x = self.hitbox.centerx
            elif self.hitbox.right > WIDTH: 
                self.hitbox.right = WIDTH
                self.pos.x = self.hitbox.centerx
                
            if self.hitbox.top < 0: 
                self.hitbox.top = 0
                self.pos.y = self.hitbox.centery
            elif self.hitbox.bottom > HEIGHT: 
                self.hitbox.bottom = HEIGHT
                self.pos.y = self.hitbox.centery

        # 2. VISUAL SYNC (Always Run This!)
        # This ensures the sprite is pinned to the feet even when standing still.
        self.rect.centerx = self.hitbox.centerx
        self.rect.midbottom = self.hitbox.midbottom
        
        

    def check_collision(self, axis, tiles):
        """ hitbox-based collision check. 2 phases: self.rect (fast) and self.hitbox (precise)"""
        potential_hits = pygame.sprite.spritecollide(self, tiles, False) #type:ignore
        for obj in potential_hits:
            if isinstance(obj, Tile) and obj.obstructed:
                if self.hitbox.colliderect(obj.rect):
                    if axis == "horizontal":
                        if self.direction.x > 0: # Moving Right
                            self.hitbox.right = obj.rect.left
                        elif self.direction.x < 0: # Moving Left
                            self.hitbox.left = obj.rect.right
                        self.pos.x = self.hitbox.centerx

                    elif axis == "vertical":
                        if self.direction.y > 0: # Moving Down
                            self.hitbox.bottom = obj.rect.top
                        elif self.direction.y < 0: # Moving Up
                            self.hitbox.top = obj.rect.bottom
                        self.pos.y = self.hitbox.centery

    def update(self, dt, all_tiles):
        """
        Main update loop. 
        Requires dt (delta time) for smooth vector movement.
        """
        self.input()
        self.move(dt, all_tiles)

        frame = self.animator.get_frame(self.state, self.facing, dt)
        if frame: self.image = frame

    def interact(self, all_tiles:list[Tile]):
        """Interacts with the tile directly under the player's feet."""
        active_item = self.inventory.get_active_item()
        if not active_item: 
            print("Inventory Slot Empty!")
            return

        # Target Point: Bottom center of the hitbox (The feet)
        target_point = self.hitbox.midbottom
        
        # Simple loop to find what we are standing on/facing
        # (You could offset this by self.facing to interact with the tile in FRONT of you)
        for tile in all_tiles:
            if tile.rect.collidepoint(target_point):
                print(f"Interacting with tile at {target_point}")
                used = active_item.use(self, tile, all_tiles)
                if used:
                    self.inventory.remove_if_empty(active_item)
                break

        
