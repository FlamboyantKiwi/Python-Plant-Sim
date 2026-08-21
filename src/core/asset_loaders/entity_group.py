from __future__ import annotations
import pygame
from enum import Enum
from typing import TYPE_CHECKING
from ..types import EntityState, Direction, EntityCategory
from .sprite_group import SpriteGroup
from .spritesheet import SpriteSheet

if TYPE_CHECKING:
    from src.custom_types import EntityType

class EntityGroup(SpriteGroup):
    def load(self) -> None:
        for category, config in self.raw_data.items():
            self.storage[category] = {}
            for name in config.sheets:
                self.storage[category][name] = {}
                folder_name = category.value if isinstance(category, Enum) else category
                path = self.manager.get_image_path(f"{name}.png", subfolder=folder_name)
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
        try:
            frames = self.storage[cat.lower()][name][state.value][direction.value]
            return frames[int(frame) % len(frames)]
        except (KeyError, IndexError):
            return None