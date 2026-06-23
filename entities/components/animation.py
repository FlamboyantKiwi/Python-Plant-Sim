from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from core.types import EntityState, EntityCategory
from core.assets import ASSETS

# Type-Only Imports
if TYPE_CHECKING:
    from custom_types import Num, Direction, EntityType

class AnimationController:
    def __init__(self, category: EntityCategory, entity_name: EntityType, speed:float = 0.15) -> None:
        self.category = category
        self.name = entity_name
        
        # State
        self.current_time: float = 0.0
        self.frame_index: int = 0
        
        # Settings
        self.speed: float = speed

    def _get_state_speed(self, state: EntityState) -> float:
        """Helper to explicitly map out animation pacing configurations."""
        match state:
            case EntityState.IDLE: 
                return 0.4
            case EntityState.RUN:  
                return 0.1
            case _:                
                return self.speed

    def get_frame(self, state:EntityState, direction:Direction, dt:Num) -> pygame.Surface | None:
        """ Handles the timer logic and fetches the image from AssetLoader."""
        # Update Timer
        self.current_time += dt
        frame_duration = self._get_state_speed(state)
        
        # Handle frame switching
        if self.current_time >= frame_duration:
            # Using floor division/modulo allows us to catch up safely 
            # if a major frame-drop occurs in the main engine loop
            frames_to_advance = int(self.current_time // frame_duration)
            self.frame_index += frames_to_advance
            self.current_time %= frame_duration
            
        # Ask AssetLoader for the specific frame
        # We pass frame_index as the "tick"
        return ASSETS.sprite(
            self.category, self.name, state, direction, self.frame_index)