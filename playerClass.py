import pygame, inventory, tile, item
from helper import calc_pos_rect, get_grid_pos, get_colour
from settings import BLOCK_SIZE, WIDTH, HEIGHT
class Player(pygame.sprite.Sprite):
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
    INV_SIZE = 8 # will be a single row
    INV_PADDING = 5
    SLOT_SIZE = 50
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE/2, BLOCK_SIZE * 0.75)) # slighly taller than block
        self.image.fill(get_colour("PLAYER"))
        self.rect = self.image.get_rect(x=x, y=y) 
        self.direction = None
        self.speed = 5
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
        self.inventory = inventory.Inventory(max_size=self.INV_SIZE, 
                                   columns=self.INV_SIZE, 
                                   rect = inv_rect,
                                   slot_size=self.SLOT_SIZE,
                                   padding=self.INV_PADDING)
        self.inventory.add_item(item.Tool("GOLD_SCYTHE"))
        self.inventory.add_item(item.Seed())
        self.inventory.add_item(item.Fruit("Melon"))

    def key_down(self, key, all_tiles=None):
        if key in self.direction_keys:
            x, y = self.direction_keys[key]
            if x != 0:
                self.dx = x * self.speed
            if y != 0:
                self.dy = y * self.speed
        if key is self.interact_key:
            self.interact(all_tiles)
        # --- Inventory Selection Logic ---
        if key in self.SLOT_KEY_MAP:
            index = self.SLOT_KEY_MAP[key]
            self.inventory.set_active_slot(index)
            #print(f"Active slot set to: {index + 1}")
    def key_up(self, key):
        if key in self.direction_keys:
            x, y = self.direction_keys[key]
            if x != 0 and ((x < 0 and self.dx < 0) or (x > 0 and self.dx > 0)):
                    self.dx = 0
            if y != 0 and ((y < 0 and self.dy < 0) or (y > 0 and self.dy > 0)):
                    self.dy = 0
    def collision_check(self, all_tiles):
        # Get a list of all tiles the player is colliding with
        collided_tiles = pygame.sprite.spritecollide(self, all_tiles, False)
        for tile in collided_tiles:
            if hasattr(tile, "obstructed") and tile.obstructed:
                return True
        return False
    def update(self, all_tiles, tick = 0):
        # --- Horizontal Collision Check ---
        if self.dx != 0:
            original_x = self.rect.x
            self.rect.x += self.dx
            # Get a list of all tiles the player is colliding with
            if self.collision_check(all_tiles):
                self.rect.x = original_x # undo movement
                self.dx = 0 # Stop horizontal momentum
                

        if self.dy != 0:
            original_y = self.rect.y        
            self.rect.y += self.dy
            if self.collision_check(all_tiles):
                self.rect.y = original_y
                self.dy = 0

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


        
