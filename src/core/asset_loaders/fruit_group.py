from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Any

import pygame

from src.types import Quality, SpriteRect
from src.utils import Log

from .sprite_group import SpriteGroup
from .spritesheet import SpriteSheet


class FruitGroup(SpriteGroup):
    def __init__(self, manager: Any, raw_data:Any = None, **sheet_files: str) -> None:
        super().__init__(manager, raw_data=raw_data, **sheet_files)
        self.containers = {}
        self.seed_bags = {}
        self.cache = {}

    def load(self) -> None:
        crops = self.raw_data.get("crops", [])
        trees = self.raw_data.get("trees", [])
        ranks = self.raw_data.get("ranks", [])
        bags_pos = self.raw_data.get("bags_pos")
        
        
        self._extract_supplies("crops", crops, ranks)
        self._extract_supplies("trees", trees, ranks)
        
        supplies_sheet = self.get_sheet("supplies")
        if supplies_sheet:
            self.seed_bags = self._create_strip(supplies_sheet, bags_pos, ranks[1:], 2, 3)

    def _extract_supplies(self, sheet_key: str, order_list: list, ranks: list) -> None:
        """Processes a supplies spritesheet using the shared row iterator."""
        c_x, c_w = 0, 48
        f_x, f_w = 48, 32
        
        # Use the parent class's row generator
        for name, current_y, row_h, sheet in self._iter_rows(sheet_key, order_list):
            clean_key = name.lower().replace(" ", "_")
            
            # Extract fruit (in ranks)
            fruit, fruit_bounds = self._get_tight_strip(sheet, c_x, current_y, c_w, row_h)
            if fruit and fruit_bounds:
                rank_w = c_w // len(ranks)
                items = {}
                
                for rank_idx, rank in enumerate(ranks):
                    rank_key = rank.value if isinstance(rank, Enum) else rank
                    rank_img = fruit.subsurface((rank_idx * rank_w, 0, rank_w, fruit_bounds.h))
                    items[rank_key] = pygame.transform.scale(
                        rank_img, (rank_w * self.SCALE_FACTOR, fruit_bounds.h * self.SCALE_FACTOR)
                    )
                self.storage[clean_key] = items

            # Extract box of fruit
            fruit_box, box_bounds = self._get_tight_strip(sheet, f_x, current_y, f_w, row_h)
            if fruit_box and box_bounds:
                self.containers[clean_key] = fruit_box
                
    def _create_strip(self, sheet: SpriteSheet, rect: SpriteRect, ranks: Sequence[Any], num: int, scale_f: int) -> dict[str, pygame.Surface]:
        items: dict[str, pygame.Surface] = {}
        w = rect.w // num
        for i, rank in enumerate(ranks):
            rank_key = rank.value if isinstance(rank, Enum) else rank
            items[rank_key] = sheet.get_image(
                rect.x + (i * w), rect.y, w, rect.h,
                (w * scale_f, rect.h * scale_f)
            )
        return items

    def get(self, key: str) -> pygame.Surface | None:
        data = self.storage.get(key, {})
        return data.get("BRONZE") or data.get("SILVER") or data.get("GOLD")

    def get_seed(self, item_id: str, quality: Quality = Quality.BRONZE) -> pygame.Surface | None:
        if "_seeds" not in item_id.lower():
            return None
        quality_key = quality.value if isinstance(quality, Quality) else quality
        clean_id = item_id.lower().replace("_seeds","").replace(" ", "_")
        cache_key = f"{quality_key}_{clean_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        bag = self.seed_bags.get(quality_key)
        fruit_data = self.storage.get(clean_id, {})
        fruit = fruit_data.get("GOLD")
        if not bag:
            Log.error("no bag")
            return self.manager.images.get_image(f"MISSING_BAG_{clean_id}")
        elif not fruit:
            Log.error("no fruit")
            return bag
        comp = bag.copy()
        bx, by = comp.get_rect().center
        fx, fy = fruit.get_rect().size
        comp.blit(fruit, (bx - fx // 2, by - fy // 2 - 2))
        self.cache[cache_key] = comp
        return comp