from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, cast
from entities.plant import Plant

if TYPE_CHECKING:
    from custom_types import Num



class PlantGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    @property
    def plants(self) -> list[Plant]:
        """Returns a strictly-typed list of Plant objects."""
        return cast(list[Plant], self.sprites())

    def add(self, *sprites:pygame.sprite.Sprite) -> None:
        """Overridden to ensure only Plant instances are added."""
        for sprite in sprites:
            if isinstance(sprite, Plant):
                super().add(sprite)
            else:
                raise TypeError(f"PlantGroup only accepts 'Plant' objects, not {type(sprite).__name__}")
    
    def grow_all(self, amount: Num) -> None:
        """Ticks the growth logic for every plant in this group."""
        for plant in self.plants:
            plant.grow(amount)

    def get_plant_at_grid(self, grid_x: int, grid_y: int) -> Plant | None:
        """Helper to find a specific plant instance by its coordinates."""
        for plant in self.plants:
            if plant.grid_x == grid_x and plant.grid_y == grid_y:
                return plant
        return None
