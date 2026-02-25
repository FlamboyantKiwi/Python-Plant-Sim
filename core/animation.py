from core.types import EntityState, Direction
from core.asset_loader import ASSETS

class AnimationController:
    def __init__(self, category, entity_name):
        self.category = category
        self.name = entity_name
        
        # State
        self.current_time = 0.0
        self.frame_index = 0
        
        # Settings
        self.speed = 0.15 # Default speed

    def get_frame(self, state:EntityState, direction:Direction, dt:int):
        """ Handles the timer logic and fetches the image from AssetLoader."""
        # 1. Update Timer
        self.current_time += dt
        
        # Adjust speed for different states if needed
        current_speed = self.speed
        if state == EntityState.IDLE: 
            current_speed = 0.4
        elif state == EntityState.RUN: 
            current_speed = 0.1

        # 2. Advance Frame
        if self.current_time >= current_speed:
            self.current_time = 0
            self.frame_index += 1
            
        # 3. Ask AssetLoader for the specific frame
        # We pass frame_index as the "tick"
        return ASSETS.get_animated_sprite(
            self.category, self.name, state, direction, self.frame_index)