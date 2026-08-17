from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, Protocol, Any, Sequence
import pygame

from src.entities.entity import Entity
from src.world.tile import Tile
from src.core.types import PlayerType, FarmAnimalType

Num = int|float
Group = pygame.sprite.AbstractGroup
Pos = tuple[int,int]
NodeMap = list[list[int]]
Interactables = Sequence[Tile | Entity]
EntityType = PlayerType | FarmAnimalType | str
Colour = str | tuple[int, int, int] | pygame.Color
if TYPE_CHECKING:
    from main import Game
    # Core Logic
    from src.entities.components.animation import AnimationController
    from src.core.types import EntityState, Direction, ItemCategory, ToolType, Quality, TextConfig
    # UI
    from src.ui.InventoryUI import InventoryUI, Inventory
    from src.ui.ui_elements import UIElement, Button, Slot
    from src.ui.wrappers import BaseWrapper
    # Entities
    from src.entities.items import Item, ToolItem, SeedItem
    from src.entities.entity import MovingEntity
    # Groups
    from src.groups.plant_group import PlantGroup
    from src.groups.camera import CameraGroup
    from src.groups.ui_group import UIGroup
    
