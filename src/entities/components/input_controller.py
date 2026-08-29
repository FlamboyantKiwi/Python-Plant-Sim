from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.config import key_binds
from src.core import EntityState

if TYPE_CHECKING:
    from src.custom_types import MovingEntity, Num

class InputController:
    """Handles keyboard polling, movement vectors, run multipliers, and facing directions."""
    def __init__(self, entity: MovingEntity, base_speed: Num, run_multiplier: float = 1.5) -> None:
        self.entity = entity
        self.base_speed = base_speed
        self.run_multiplier = run_multiplier

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        
        input_x = 0
        input_y = 0
        for key, (x, y) in key_binds.direction_keys.items():
            if keys[key]:
                input_x += x
                input_y += y
                
        # Update Entity Direction Vector
        self.entity.direction.x = input_x
        self.entity.direction.y = input_y
        
        # Update Facing Direction
        lookup_key = (input_x, input_y)
        if lookup_key in key_binds.facing_map:
            self.entity.facing = key_binds.facing_map[lookup_key]
            
        # Normalization (Fixes diagonal speed boost)
        if self.entity.direction.magnitude_squared() > 0:
            self.entity.direction = self.entity.direction.normalize()
            self.entity.state = EntityState.RUN if keys[key_binds.run] else EntityState.WALK
        else:
            self.entity.state = EntityState.IDLE                      

        # Running Speed Calculation
        if keys[key_binds.run]:
            self.entity.current_speed = self.base_speed * self.run_multiplier
        else:
            self.entity.current_speed = self.base_speed