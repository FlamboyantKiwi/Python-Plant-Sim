import pygame
from settings import WIDTH, HEIGHT, PLAYER_START_INVENTORY, INTERACTION_DISTANCE

# 1. Core Imports
from core.helper import calc_pos_rect
from core.types import EntityState, DOWN
from core.controls import controls
from core.animation import AnimationController
# 2. Entity Imports
from entities.items import ItemFactory
from entities.physicsEntity import MovingEntity

from ui.InventoryUI import InventoryUI, Inventory

# 3. World Imports
from world.tile import Tile

class Player(MovingEntity):
    #Inventory Variables
    INV_SIZE = 8 # will be a single row
    INV_PADDING = 5
    SLOT_SIZE = 50
    def __init__(self, x:int|float, y:int|float, group, type="Racoon"):
       # 1. Figure out the unique player visuals and sizes first
        initial_image = pygame.Surface((32, 64))
        start_rect = initial_image.get_rect(topleft=(x, y))
        
        start_hitbox = pygame.Rect(0, 0, 20, 10)
        start_hitbox.midbottom = start_rect.midbottom
        
        # 2. Hand them to the PhysicsEntity to do the rest!
        super().__init__(initial_image, start_rect, start_hitbox, 200, group)
        
        self.player_type = type
        self.state = EntityState.IDLE
        self.facing = DOWN # start looking down
        self.animator = AnimationController("PLAYER", type)
        
        # Interaction Offsets
        self.interaction_offsets = {}
        self.generate_interaction_offsets(INTERACTION_DISTANCE)

        self.run_multiplier = 1.5  
        
        #Inventory + Stats
        self.money = 500
        self.setup_inventory()
        
    def generate_interaction_offsets(self, distance:int):
        for (dx, dy), direction in controls.facing_map.items():
            # Only use Pure Cardinals (ignore diagonal keys for the math)
            if dx == 0 or dy == 0:
                self.interaction_offsets[direction] = pygame.math.Vector2(dx * distance, dy * distance)
        
    def setup_inventory(self):
        """Calculates and initializes the UI rect for the inventory."""
        required_width = self.INV_SIZE * (self.SLOT_SIZE + self.INV_PADDING) + self.INV_PADDING
        required_height = self.SLOT_SIZE + self.INV_PADDING * 2

        inv_rect = calc_pos_rect(
            required_width, required_height, WIDTH, HEIGHT,
           y_offset= ((HEIGHT - required_height) // 2) - 10)
        
        self.inventory = Inventory(max_size=self.INV_SIZE)
        
        self.active_slot_index = 0 
        
        # 3. Visual UI Component
        self.inventory_ui = InventoryUI(
            rect=inv_rect,
            inventory_data=self.inventory,
            columns=self.INV_SIZE,
            slot_size=self.SLOT_SIZE,
            padding=self.INV_PADDING
        )
        
        # Tell the UI to visually highlight the first slot
        self.inventory_ui.slots[self.active_slot_index].is_active = True
        
        # Populate initial items into the data layer
        for item_id, count in PLAYER_START_INVENTORY:
            self.inventory.add_item(ItemFactory.create(item_id, count))
    
    def set_active_slot(self, index: int):
        """Safely updates the active slot and handles UI highlighting."""
        if 0 <= index < self.INV_SIZE:
            # Visually turn off the old slot
            self.inventory_ui.slots[self.active_slot_index].is_active = False
            
            # Update data
            self.active_slot_index = index
            
            # Visually turn on the new slot
            self.inventory_ui.slots[self.active_slot_index].is_active = True
        
    def handle_event(self, event, all_tiles):
        """Handles discrete inputs (clicks). Call this from Game Loop."""
        if event.type == pygame.KEYDOWN:
            # Interact
            if event.key == controls.interact:
                self.interact(all_tiles)
            
            # 2. Hotbar Selection (1-8 keys)
            if event.key in controls.slots:
                new_index = controls.slots[event.key]
                self.set_active_slot(new_index)
                
    def handle_click(self, pos):
        """Checks if the player's UI was clicked."""
        clicked_index = self.inventory_ui.click(pos)
        
        if clicked_index is not None:
            self.set_active_slot(clicked_index)
            print(f"Clicked hotbar slot: {clicked_index}")
            return True
            
        return False
    
    def input(self):
        keys = pygame.key.get_pressed()
       
        input_x = 0
        input_y = 0

        for key, (x, y) in controls.direction_keys.items():
            if keys[key]:
                input_x += x
                input_y += y

        # Update Direction Vector (for physics)
        self.direction.x = input_x
        self.direction.y = input_y

        # Update direction player is facing
        lookup_key = (input_x, input_y)
        if lookup_key in controls.facing_map:
            self.facing = controls.facing_map[lookup_key]

        # Normalization (Fixes diagonal speed boost)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            self.state = EntityState.RUN if keys[controls.run] else EntityState.WALK
        else:
            self.state = EntityState.IDLE
            
        # Running Logic
        if keys[controls.run]:
            self.current_speed = self.base_speed * self.run_multiplier
        else:
            self.current_speed = self.base_speed

    def update(self, dt, all_tiles):
        """Main update loop. 
            Requires dt (delta time) for smooth vector movement."""
        self.input()
        
        
        frame = self.animator.get_frame(self.state, self.facing, dt)
        if frame: 
            self.image = frame
            self.rect = self.image.get_rect()
        
        self.move(dt, all_tiles)

    def interact(self, all_tiles:list[Tile]):
        """Interacts with the tile directly under the player's feet."""
        # Grab the item directly from the data array
        active_item = self.inventory.items[self.active_slot_index]
        
        if not active_item: 
            print("Inventory Slot Empty!")
            return

        offset = self.interaction_offsets.get(self.facing, (0,0))
        target_point = self.hitbox.midbottom + offset
        
        # Create a 1x1 invisible rect at the target point
        target_rect = pygame.Rect(target_point[0], target_point[1], 1, 1)
        
        # Use Pygame's built-in collision loop (massively faster)
        hit_tiles = [t for t in all_tiles if target_rect.colliderect(t.rect)]
        
        for tile in hit_tiles:
            print(f"Interacting with tile at {target_point}")
            used = active_item.use(self, tile, all_tiles, self.groups()[0])
            
            if used and active_item.count <= 0:
                self.inventory.items[self.active_slot_index] = None
                print("Item consumed entirely.")
            break # Stop after interacting with the first valid tile

        
