from __future__ import annotations
import pygame
import os
import inspect
from enum import Enum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Sequence, Optional, Union, Dict, Set

# Runtime Imports
from core.spritesheet import SpriteSheet
from core.types import EntityState, Direction, EntityCategory
from core.assets.asset_data import  GAME_ENTITIES
from core.assets.base import SpriteGroup

# Type-Only Imports
if TYPE_CHECKING:
    from custom_types import EntityType

class EntityGroup(SpriteGroup):
    def load(self) -> None:
        for category, config in GAME_ENTITIES.items():
            self.storage[category] = {}
            for name in config.sheets:
                self.storage[category][name] = {}
                folder_name = category.value if isinstance(category, Enum) else category
                path = self.manager.get_asset_path(f"{name}.png", folder=folder_name)
                sheet = SpriteSheet(path)
                
                for state, anim_grid in config.animations.items():
                    s_key = state.value if isinstance(state, Enum) else state
                    self.storage[category][name][s_key] = {}
                    for direction, rect in anim_grid.items():
                        d_key = direction.value if isinstance(direction, Enum) else direction
                        frames = []
                        f_size = config.frame_size 
                        cols, rows = rect.w // f_size, rect.h // f_size
                        for r in range(rows):
                            for c in range(cols):
                               frames.append(sheet.get_image(
                                    rect.x + (c * f_size), rect.y + (r * f_size), 
                                    f_size, f_size, (64, 64)))
                        self.storage[category][name][s_key][d_key] = frames

    def get_sprite(self, cat: EntityCategory, name: EntityType, state: EntityState, direction: Direction, frame: int) -> pygame.Surface | None:
        """Safely fetches a specific frame of animation."""
        try:
            frames = self.storage[cat][name][state.value][direction.value]
            return frames[int(frame) % len(frames)]
        except (KeyError, IndexError):
            return None
