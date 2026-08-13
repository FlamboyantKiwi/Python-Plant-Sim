from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports (Needed for logic/inheritance)
from settings import WIDTH, HEIGHT, PLAYER_START_INVENTORY, INTERACTION_DISTANCE
from core.ui_utils import calc_pos_rect
from core.types import EntityState, PlayerType, EntityCategory
from core.controls import controls
from entities.components.animation import AnimationController
from entities.items import create_item
from entities.entity import MovingEntity
from entities.components.interaction import InteractionController
from entities.components.inventoryComponent import InventoryController, InventoryManager
# Type-Only Imports (Prevents Circular Imports)
if TYPE_CHECKING:
    from custom_types import Tile, Direction, Item, Group, Pos, Interactables, Num

class Player(MovingEntity):
    #Inventory Variables
    INV_SIZE = 8 # will be a single row
    INV_PADDING = 5
    SLOT_SIZE = 50
    def __init__(self, x:Num, y:Num, group: Group, type:PlayerType=PlayerType.RACOON) -> None:
       # Figure out the unique player visuals and sizes first
        initial_image = pygame.Surface((32, 64))
        start_rect = initial_image.get_rect(topleft=(x, y))
        
        start_hitbox = pygame.Rect(0, 0, 20, 10)
        start_hitbox.midbottom = start_rect.midbottom
        
        # Hand them to the PhysicsEntity to do the rest!
        super().__init__(initial_image, start_rect, start_hitbox, 200, group)
        
        self.player_type = type
        self.animator = AnimationController(EntityCategory.PLAYER, type) 
        
        self.targeter = InteractionController(self, INTERACTION_DISTANCE)

        self.run_multiplier = 1.5  
        
        #Inventory + Stats
        self.money = 500
        self.setup_inventory()
        
    def setup_inventory(self) -> None:
        """Initializes the InventoryController and the Drag/Drop Manager."""
        # Create the all-in-one Controller for the Player
        self.inventory = InventoryController(
            size=self.INV_SIZE, 
            slot_size=self.SLOT_SIZE, 
            padding=self.INV_PADDING
        )
        
        # Create the Manager and 'open' the player's hotbar permanently
        self.inventory_manager = InventoryManager()
        self.inventory_manager.open_inventory(self.inventory)
        
        # Populate initial items into the data layer
        for item_id, count in PLAYER_START_INVENTORY:
            self.inventory.data.add_item(create_item(item_id, count))
       
    def handle_event(self, event: pygame.event.Event, interactables:Interactables) -> None:
        """Handles discrete inputs (clicks). Call this from Game Loop."""
        if event.type == pygame.KEYDOWN:
            # Interact
            if event.key == controls.interact:
                self.interact(interactables)
            
        #  Hotbar Selection (handled by controller) (1-8 keys)
        self.inventory.handle_event(event, controls)
                
    def handle_click(self, pos:Pos) -> bool:
        """Passes mouse clicks to the Drag & Drop Manager."""
        return self.inventory_manager.handle_click(pos)
    
    def input(self) -> None:
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

    def update(self, dt:Num, interactables:Interactables, mouse_pos:Pos|None=None):
        """Main update loop. 
            Requires dt (delta time) for smooth vector movement."""
        self.input()
        
        frame = self.animator.get_frame(self.state, self.facing, dt)
        if frame: 
            self.image = frame
            self.rect.size = self.image.get_size()
            self.sync_rect_to_hitbox()
        
        self.move(dt, interactables)
        self.inventory.update(mouse_pos)

    def interact(self, interactables:Interactables) -> None:
        """Interacts with the tile or entity directly under the player's target offset."""
        # Ask the Component what we are looking at!
        hit_objects = self.targeter.get_target_objects(interactables)
        
        if not hit_objects:
            return # Looking at nothing
            
        # Check Inventory
        active_item = self.inventory.get_active_item()
        if not active_item: 
            print("Inventory Slot Empty! (Maybe talk to an NPC or open a chest here later?)")
            return

        # Use the item on the first object we hit
        target_obj = hit_objects[0]
        print(f"Interacting with {type(target_obj).__name__}")
        
        used = active_item.use(self, target_obj, interactables, self.groups()[0])
        
        if used: # clean up if consumed
            self.inventory.consume_active_item()
            print("Item consumed entirely.")
        
