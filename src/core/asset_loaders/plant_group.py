from __future__ import annotations

import pygame

from .sprite_group import SpriteGroup


class PlantGroup(SpriteGroup):
    def load(self) -> None:
        crops_order = self.raw_data.get("crops", [])
        trees_order = self.raw_data.get("trees", [])
        
        self._extract_plants("crops", crops_order, world_x=80, world_w=128, is_tree=False)
        self._extract_plants("trees", trees_order, world_x=80, world_w=255, is_tree=True)
        
    def _extract_plants(self, sheet_key: str, order_list: list, world_x: int, world_w: int, is_tree: bool) -> None:
        """Processes a plant spritesheet using the shared row iterator."""
        tree_slices = self.raw_data.get("tree_slices", [])
        
        # Use the parent class's row generator
        for name, current_y, row_h, sheet in self._iter_rows(sheet_key, order_list):
            
            # Use the parent class's cropping math
            tight_strip, bounds = self._get_tight_strip(sheet, world_x, current_y, world_w, row_h)
            if not tight_strip or not bounds:
                continue
                
            # Handle slicing logic
            if is_tree:
                slices = tree_slices
            else:
                frame_w = world_w // 4
                slices = [(idx * frame_w, frame_w) for idx in range(4)]
                
            for frame_idx, (offset, width) in enumerate(slices):
                frame_img = tight_strip.subsurface((offset, 0, width, bounds.h))
                scaled_size = (width * self.SCALE_FACTOR, bounds.h * self.SCALE_FACTOR)
                self.storage[f"{name}_{frame_idx}"] = pygame.transform.scale(frame_img, scaled_size)