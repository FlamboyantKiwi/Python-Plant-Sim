from __future__ import annotations
import pygame
from src.core.assets.asset_data import CROPS_ORDER, TREES_ORDER, TREE_FRAME_SLICES
from .sprite_group import SpriteGroup

class PlantGroup(SpriteGroup):
    def load(self) -> None:
        def extract_plants(sheet_key: str, order_list: list, world_x: int, world_w: int, is_tree: bool):
            sheet = self.get_sheet(sheet_key)
            if not sheet or not order_list:
                return
            row_h = sheet.sheet.get_height() // len(order_list)
            for i, name in enumerate(order_list):
                current_y = i * row_h
                padded_strip = sheet.get_image(world_x, current_y, world_w, row_h)
                bounds = padded_strip.get_bounding_rect()
                if bounds.h <= 0:
                    continue
                tight_strip = padded_strip.subsurface((0, bounds.y, world_w, bounds.h))
                if is_tree:
                    slices = TREE_FRAME_SLICES
                else:
                    frame_w = world_w // 4
                    slices = [(idx * frame_w, frame_w) for idx in range(4)]
                for frame_idx, (offset, width) in enumerate(slices):
                    frame_img = tight_strip.subsurface((offset, 0, width, bounds.h))
                    scaled_size = (width * self.SCALE_FACTOR, bounds.h * self.SCALE_FACTOR)
                    self.storage[f"{name}_{frame_idx}"] = pygame.transform.scale(frame_img, scaled_size)

        extract_plants("crops", CROPS_ORDER, world_x=80, world_w=128, is_tree=False)
        extract_plants("trees", TREES_ORDER, world_x=80, world_w=255, is_tree=True)