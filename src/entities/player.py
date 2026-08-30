from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pygame

from src.config import INTERACTION_DISTANCE, PLAYER_START_INVENTORY

# Runtime Imports (Needed for logic/inheritance)
from src.core import EntityCategory, PlayerType, ToolType
from src.groups import CameraGroup
from src.utils import Log

from .base.moving_entity import MovingEntity
from .components import (
    AnimationController,
    InputController,
    InteractionController,
    InteractionHandler,
)
from .inventory import (
    InventoryController,
    InventoryManager,
)
from .items import ItemFactory

# Type-Only Imports (Prevents Circular Imports)
if TYPE_CHECKING:
    from src.custom_types import Group, Interactables, Item, Num, Pos

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

        self.camera_group: CameraGroup = cast(CameraGroup, group)
        self.player_type:PlayerType = type
        self.animator:AnimationController = AnimationController(EntityCategory.PLAYER, type) 
        
        self.targeter:InteractionController = InteractionController(self, INTERACTION_DISTANCE)
        self.interaction_handler:InteractionHandler = InteractionHandler(self, self.camera_group)
        self.input_controller:InputController = InputController(self, base_speed=200, run_multiplier=1.5)
        
        #Inventory + Stats
        self.money:int = 500
        self.setup_inventory()
        
    def setup_inventory(self) -> None:
        """Initializes the InventoryController and the Drag/Drop Manager."""
        # Create the all-in-one Controller for the Player
        self.inventory:InventoryController = InventoryController(
            size=self.INV_SIZE, 
            slot_size=self.SLOT_SIZE, 
            padding=self.INV_PADDING
        )
        
        # Create the Manager and 'open' the player's hotbar permanently
        self.inventory_manager:InventoryManager = InventoryManager()
        self.inventory_manager.open_inventory(self.inventory)
        
        # Populate initial items into the data layer
        for item_id, count in PLAYER_START_INVENTORY:
            self.inventory.data.add_item(ItemFactory.create(item_id, count))
    
    @property
    def active_item(self) -> Item | None:
        """Convenience property to access the player's currently selected item."""
        return self.inventory.get_active_item()
    
    def refill_active_watering_can(self) -> None:
        ### WILL BE RMOVED LATER - when water / water sources are added
        """Refills the currently equipped watering can to max capacity."""
        active_item = self.inventory.get_active_item()
        if active_item and getattr(active_item, 'tool_type', None) == ToolType.WATER:
            active_item.water_level = active_item.max_water
            Log.success(f"Refilled {active_item.name}! Water level: {active_item.water_level}/{active_item.max_water}")
        else:
            Log.info("Equip a watering can to refill it.")
   
    def update(self, dt:Num, interactables:Interactables, mouse_pos:Pos|None=None):
        """Main update loop. 
            Requires dt (delta time) for smooth vector movement."""
        self.input_controller.update()
        
        frame = self.animator.get_frame(self.state, self.facing, dt)
        if frame: 
            self.image = frame
            self.rect.size = self.image.get_size()
            self.sync_rect_to_hitbox()
        
        self.move(dt, interactables)
        self.inventory.update(mouse_pos)

    def interact(self, interactables: Interactables) -> None:
        """Interacts with the tile or entity directly under the player's target offset."""
        self.interaction_handler.handle_interaction(interactables)

    def receive_item(self, item_id: str, count: int = 1) -> bool:
        """The Logic Middle Man: Instantiates an item and adds it to the inventory."""
        new_item = ItemFactory.create(item_id, count)
        
        if self.inventory.data.add_item(new_item):
            Log.success(f"Received {new_item.name}!")
            return True
        else:
            Log.error("Inventory is full! Cannot receive item.")
            return False
