from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from core.types import EntityState
from core.asset_loader import ASSETS

# Type-Only Imports
if TYPE_CHECKING:
    from custom_types import Num, Direction

class AnimationController:
    def __init__(self, category: str, entity_name: str, speed:float = 0.15) -> None:
        self.category = category
        self.name = entity_name
        
        # State
        self.current_time: float = 0.0
        self.frame_index: int = 0
        
        # Settings
        self.speed: float = speed

    def get_frame(self, state:EntityState, direction:Direction, dt:Num) -> pygame.Surface | None:
        """ Handles the timer logic and fetches the image from AssetLoader."""
        # Update Timer
        self.current_time += dt
        
        # Adjust speed for different states if needed
        current_speed = self.speed
        if state == EntityState.IDLE: 
            current_speed = 0.4
        elif state == EntityState.RUN: 
            current_speed = 0.1

        # Advance Frame
        if self.current_time >= current_speed:
            self.current_time = 0
            self.frame_index += 1
            
        # Ask AssetLoader for the specific frame
        # We pass frame_index as the "tick"
        return ASSETS.get_animated_sprite(
            self.category, self.name, state, direction, self.frame_index)