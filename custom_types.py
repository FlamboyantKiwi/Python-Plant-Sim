from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, Protocol, Any, Sequence
import pygame

from entities.entity import Entity
from world.tile import Tile
from core.types import PlayerType, FarmAnimalType

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
    from entities.components.animation import AnimationController
    from core.types import EntityState, Direction, ItemCategory, ToolType, Quality, TextConfig
    # UI
    from ui.InventoryUI import InventoryUI, Inventory
    from ui.ui_elements import UIElement, Button
    from ui.wrappers import BaseWrapper
    Element: TypeAlias = UIElement | BaseWrapper
    # Entities
    from entities.items import Item, ToolItem, SeedItem
    from entities.entity import MovingEntity
    # Groups
    from groups.plant_group import PlantGroup
    from groups.camera import CameraGroup
    from groups.ui_group import UIGroup
    
