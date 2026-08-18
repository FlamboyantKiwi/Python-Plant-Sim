from __future__ import annotations
import pygame
from enum import Enum
from typing import Sequence, Any
from src.core import SpriteSheet, Log
from src.core.types import SpriteRect, Quality
from src.core.assets.asset_data import CROPS_ORDER, TREES_ORDER, FRUIT_RANKS, SEED_BAGS_POS
from .sprite_group import SpriteGroup

class FruitGroup(SpriteGroup):
    def __init__(self, manager: Any, **sheet_files: str) -> None:
        super().__init__(manager, **sheet_files)
        self.containers = {}
        self.seed_bags = {}
        self.cache = {}

    def load(self) -> None:
        def extract_supplies(sheet_key: str, order_list: list):
            sheet = self.get_sheet(sheet_key)
            if not sheet or not order_list:
                return
            row_h = sheet.sheet.get_height() // len(order_list)
            c_x, c_w = 0, 48
            f_x, f_w = 48, 32
            for i, name in enumerate(order_list):
                clean_key = name.lower().replace(" ", "_")
                current_y = i * row_h
                padded_container = sheet.get_image(c_x, current_y, c_w, row_h)
                c_bounds = padded_container.get_bounding_rect()
                if c_bounds.h > 0:
                    tight_container = padded_container.subsurface((0, c_bounds.y, c_w, c_bounds.h))
                    num_ranks = 3
                    rank_w = c_w // num_ranks
                    scale_f = 2
                    items = {}
                    for rank_idx, rank in enumerate(FRUIT_RANKS):
                        rank_key = rank.value if isinstance(rank, Enum) else rank
                        rank_img = tight_container.subsurface((rank_idx * rank_w, 0, rank_w, c_bounds.h))
                        items[rank_key] = pygame.transform.scale(rank_img, (rank_w * scale_f, c_bounds.h * scale_f))
                    self.storage[clean_key] = items
                padded_fruit = sheet.get_image(f_x, current_y, f_w, row_h)
                f_bounds = padded_fruit.get_bounding_rect()
                if f_bounds.h > 0:
                    self.containers[clean_key] = padded_fruit.subsurface((0, 0, f_w, f_bounds.h))

        extract_supplies("crops", CROPS_ORDER)
        extract_supplies("trees", TREES_ORDER)
        supplies_sheet = self.get_sheet("supplies")
        if supplies_sheet:
            self.seed_bags = self._create_strip(supplies_sheet, SEED_BAGS_POS, FRUIT_RANKS[1:], 2, 3)

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
        clean_id = item_id.lower().replace("_seeds", "").replace(" ", "_")
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