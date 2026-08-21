from __future__ import annotations
from typing import TYPE_CHECKING
from src.core import Log
from src.world import Tile

if TYPE_CHECKING:
    from src.entities import Player
    from src.custom_types import Interactables, CameraGroup

class InteractionHandler:
    """Manages what happens when a player interacts with world tiles or entities."""
    def __init__(self, player: Player, camera_group: CameraGroup) -> None:
        self.player = player
        self.camera_group = camera_group

    def handle_interaction(self, interactables: Interactables) -> None:
        """Interacts with the tile or entity directly under the player's target offset."""
        hit_objects = self.player.targeter.get_target_objects(interactables)

        if not hit_objects:
            return  # Looking at nothing

        target_obj = hit_objects[0]
        active_item = self.player.inventory.get_active_item()

        # 1. Active Item Interaction
        if active_item:
            used = active_item.use(self.player, target_obj, interactables, self.camera_group)
            if used:
                self.player.inventory.consume_active_item()
            return

        # 2. Empty Hand Interaction (Prioritize non-tiles like Plants, NPCs, etc.)
        for target_obj in hit_objects:
            if not isinstance(target_obj, Tile):
                if target_obj.on_interact(self.player):
                    return  # Action complete!

        Log.whisper(f"Nothing happened when interacting with {type(target_obj).__name__}.")