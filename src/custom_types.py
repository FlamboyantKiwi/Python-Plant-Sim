# ruff: noqa: F401 # Disables "Imported but unused" error
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol

import pygame

# Safe Runtime Imports 
# Base classes that don't import anything else - safe to load at runtime.
from src.entities.base.base_entity import Entity
from src.types.generated_enums import FarmAnimalType, PlayerType
from src.world.tiles.base_tile import Tile

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
    from src.core.states import BaseUIState, GameState

    # Entities & Components
    from src.entities import Animal, Item, MovingEntity, Plant, Player
    from src.entities.components import (
        AnimationController,
        InteractionController,
    )
    from src.entities.inventory import (
        DragController,
        Inventory,
        InventoryController,
        InventoryManager,
    )
    from src.entities.items import (
        SeedItem,
        ToolItem,
    )

    # Groups
    from src.groups import CameraGroup, PlantGroup, UIGroup

    # Core
    from src.types import (
        Direction,
        EntityState,
        ItemCategory,
        ItemData,
        PlantData,
        Quality,
        ShopData,
        TextConfig,
        ToolType,
    )

    # UI
    from src.ui import (
        BaseWrapper,
        Button,
        InventoryUI,
        ProgressBar,
        ShopMenu,
        Slot,
        TooltipWrapper,
        UIElement,
    )

    # World
    from src.world import GroundTile, Level, WaterTile
