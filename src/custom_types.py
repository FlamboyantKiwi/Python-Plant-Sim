from __future__ import annotations
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol

import pygame

# Safe Runtime Imports 
# Base classes that don't import anything else - safe to load at runtime.
from src.entities.base_entity import Entity
from src.world.tiles.base_tile import Tile
from src.core.types.generated_enums import PlayerType, FarmAnimalType

#  Runtime Aliases
Num = int | float
Group = pygame.sprite.AbstractGroup
Pos = tuple[int, int]
NodeMap = list[list[int]]
Interactables = Sequence[Tile | Entity]
EntityType = PlayerType | FarmAnimalType | str
Colour = str | tuple[int, int, int] | pygame.Color

# Type Hub
# Everything here is ONLY loaded by the IDE/Linter, preventing circular crashes.
if TYPE_CHECKING:
    from main import Game
    
    # Core
    from src.core.types import (
        EntityState, Direction, ItemCategory, ToolType, Quality, 
        TextConfig, ShopData, PlantData, ItemData
    )
    from src.core.states import GameState, BaseUIState
    from src.entities.inventory_data import Inventory
    # UI
    from src.ui import (
        InventoryUI, UIElement, Button, Slot, BaseWrapper, 
        ShopMenu, TooltipWrapper, ProgressBar
    )
    
    # Entities & Components
    from src.entities import Item, ToolItem, SeedItem, MovingEntity, Player, Plant, Animal
    from src.entities.components import (
        AnimationController, InteractionController, 
        InventoryController, DragController, InventoryManager
    )
    
    # Groups
    from src.groups import PlantGroup, CameraGroup, UIGroup
    
    # World
    from src.world import Level, GroundTile, WaterTile