from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from core.controls import controls

# Type-Only Imports
if TYPE_CHECKING:
    from custom_types import Interactables
    from world.tile import Tile
    from entities.entity import MovingEntity, Entity
    from core.types import Direction

class InteractionController:
    """A component attached to a player or NPC that handles targeting."""
    def __init__(self, entity: MovingEntity, interaction_distance: int) -> None:
        self.entity = entity
        self.distance = interaction_distance
        
        self.offsets: dict[Direction, pygame.math.Vector2] = {}
        self._generate_offsets()

    def _generate_offsets(self) -> None:
        """Creates directional vectors for the interaction raycast."""
        for (dx, dy), direction in controls.facing_map.items():
            # Only use Pure Cardinals (ignore diagonal keys for the math)
            if dx == 0 or dy == 0:
                self.offsets[direction] = pygame.math.Vector2(dx * self.distance, dy * self.distance)

    def get_target_objects(self, interactables: Interactables) -> list[Tile | Entity]:
        """Casts a short 'ray' to find what the entity is looking at."""
        # Get the offset based on the entity's current facing direction
        offset = self.offsets.get(self.entity.facing, pygame.math.Vector2(0, 0))
        
        # Calculate the exact pixel point in the world
        target_point = self.entity.hitbox.midbottom + offset
        
        # Create a 1x1 invisible rect at the target point
        target_rect = pygame.Rect(int(target_point.x), int(target_point.y), 1, 1)
        
        # Return all solid and non-solid interactables that touch this point
        return [obj for obj in interactables if target_rect.colliderect(obj.rect)]