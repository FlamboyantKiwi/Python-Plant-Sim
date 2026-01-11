import pygame
from settings import WIDTH, HEIGHT, ANIMATION_SPEED

# 1. Core Imports
from core.helper import calc_pos_rect, get_grid_pos, get_direction, get_colour
from core.asset_loader import AssetLoader

# 2. Entity Imports
from entities.inventory import Inventory
from entities import items  # Access item.Tool, item.Seed, etc.

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
    SLOT_KEY_MAP = {
        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
        pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7,
    }
    interact_key = pygame.K_SPACE
    RUN_KEY = pygame.K_LSHIFT

    #Inventory Variables
    INV_SIZE = 8 # will be a single row
    INV_PADDING = 5
    SLOT_SIZE = 50
    def __init__(self, x:int|float, y:int|float, type="Fox"):
        super().__init__()
        self.player_type = type
        self.image = AssetLoader.get_animated_sprite("PLAYER", self.player_type, "Idle", "Down", 0)
        if not self.image:
            print("Error occured loading player image")
            # Create fallback surface to prevent crash
            self.image = pygame.Surface((32, 64))
            self.image.fill(get_colour("PLAYER"))

        self.rect = self.image.get_rect(x=x, y=y) 
        self.direction = "Down" # start looking down
        self.base_speed = 5.0
        self.speed = self.base_speed
        self.run_multiplier = 1.5
        self.state = "Idle"
        self.dx = 0
        self.dy = 0      
        
        #Inventory + Resource Variables
        self.money = 500
        required_width = self.INV_SIZE * (self.SLOT_SIZE + self.INV_PADDING) + self.INV_PADDING
        required_height = self.SLOT_SIZE + self.INV_PADDING * 2

        inv_rect = calc_pos_rect(
            desired_width=required_width,
            desired_height=required_height,
            screen_width=WIDTH,
            screen_height=HEIGHT,
            x_offset=0,
            y_offset= ((HEIGHT - required_height) // 2) - 10
        )
        self.inventory = Inventory(max_size=self.INV_SIZE, 
                                   columns=self.INV_SIZE, 
                                   rect = inv_rect,
                                   slot_size=self.SLOT_SIZE,
                                   padding=self.INV_PADDING)
        self.inventory.add_item(items.Tool("Gold_Scythe"))
        self.inventory.add_item(items.Seed("Red Pepper", 50))
        self.inventory.add_item(items.Fruit("Gold_Red Pepper", 10))
        self.inventory.add_item(items.Tool("Wood_Hoe"))

    def recalculate_movement_vectors(self):
        """Adjusts self.dx and self.dy to match the current self.speed magnitude 
        while preserving the direction (sign)."""
        if self.dx != 0:
            # Set dx to -speed or +speed
            self.dx = (self.dx / abs(self.dx)) * self.speed
            
        if self.dy != 0:
            # Set dy to -speed or +speed
            self.dy = (self.dy / abs(self.dy)) * self.speed

    def key_down(self, key, all_tiles=None):
        if key in self.direction_keys:
            x, y = self.direction_keys[key]
            # Set the directional sign (-1 or 1) without speed magnitude
            if x != 0:      self.dx = x
            if y != 0:      self.dy = y
            # Apply the current speed magnitude to any non-zero vector
            self.recalculate_movement_vectors()
        if key == self.RUN_KEY:
            # Only increase speed if currently at base speed 
            if self.speed == self.base_speed: # Check against base speed to prevent repeated multiplication
                self.speed *= self.run_multiplier
            
            # Apply the new speed magnitude to existing movement vectors
            self.recalculate_movement_vectors()

        # Interaction Key Logic
        if key is self.interact_key:
            self.interact(all_tiles)

        # Inventory Selection Logic
        if key in self.SLOT_KEY_MAP:
            index = self.SLOT_KEY_MAP[key]
            self.inventory.set_active_slot(index)
    def key_up(self, key):
        # Direction Logic
        if key in self.direction_keys:
            x, y = self.direction_keys[key]
            if x != 0 and ((x < 0 and self.dx < 0) or (x > 0 and self.dx > 0)):
                self.dx = 0
            if y != 0 and ((y < 0 and self.dy < 0) or (y > 0 and self.dy > 0)):
                self.dy = 0
        # Sprint Logic
        if key == self.RUN_KEY:
            # Decrease speed magnitude
            if self.speed != self.base_speed:
                self.speed /= self.run_multiplier
            
            # Recalculate movement vectors if player is still moving
            if self.dx != 0 or self.dy != 0:
                self.recalculate_movement_vectors()

    def collision_check(self, all_tiles):
        # Get a list of all tiles the player is colliding with
        collided_tiles = pygame.sprite.spritecollide(self, all_tiles, False) # type: ignore
        for tile in collided_tiles:
            if hasattr(tile, "obstructed") and tile.obstructed:
                return True
        return False
    def update(self, all_tiles, tick):
        anim_tick = tick // ANIMATION_SPEED
        
        if (self.dx != 0 or self.dy != 0):
            # Calculate new facing direction (handles alternation tie-breaker)
            new_direction = get_direction(self.dx, self.dy, anim_tick)
            if new_direction: 
                self.direction = new_direction
            
            # Determine state based on current speed (check for float tolerance)
            if self.speed > self.base_speed + 0.001:
                self.state = "Run"
            else:
                self.state = "Walk"
        else:
            self.state = "Idle"

        self.image = AssetLoader.get_animated_sprite(
            category="PLAYER",
            name=self.player_type,      # 'Fox', 'BlueBird', etc.
            state=self.state,           # 'Walk', 'Idle', 'Run'
            direction=self.direction,   # 'Up', 'Down', etc.
            tick=anim_tick
        )
        
        # Horizontal Collision Check
        if self.dx != 0:
            original_x = self.rect.x
            self.rect.x += self.dx # type: ignore
            # Get a list of all tiles the player is colliding with
            if self.collision_check(all_tiles):
                self.rect.x = original_x # undo movement
                self.dx = 0 # Stop horizontal momentum
                
        # Vertical Collision Check
        if self.dy != 0:
            original_y = self.rect.y        
            self.rect.y += self.dy # type: ignore
            # Get a list of all tiles the player is colliding with
            if self.collision_check(all_tiles):
                self.rect.y = original_y # undo movement
                self.dy = 0 # Stop vertical momentum

        # Horizontal boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.dx = 0 # Stop movement when hitting a boundary
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.dx = 0
            
        # Vertical boundaries
        if self.rect.top < 0: #-BLOCK_SIZE /2: # fit to blocksize
            self.rect.top = 0 #-BLOCK_SIZE /2
            self.dy = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.dy = 0
    def interact(self, all_tiles):
        x, y = get_grid_pos((self.rect.centerx, self.rect.bottom))
        active_item = self.inventory.get_active_item()
        if active_item is None:
            print("Inventory Slot Empty!")
            return
        active_item.use(self, target_tile=None, all_tiles=all_tiles)
        return
        ### ** need to update interaction with tiles!!
        temp_tile = tile.Tile(x, y, "GROUND")
        colliding_tiles = pygame.sprite.spritecollide(temp_tile, all_tiles, False)
        target_tile = colliding_tiles[0] if colliding_tiles else None

        if target_tile is not None:
            active_item.use(self, target_tile, all_tiles)
            
        temp_tile.kill() # remove temporary tile


        
