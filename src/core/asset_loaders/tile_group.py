from __future__ import annotations
import pygame
from src.config import BLOCK_SIZE, QUAD_SIZE, MarchingLayout
from .sprite_group import SpriteGroup

class TileGroup(SpriteGroup):
    def load(self) -> None:
        marching_sets = {
            "GRASS_A": ("grass_a", 160, 48),
            "GRASS_B": ("grass_b", 160, 48),
            "DIRT":    ("dirt",    160, 48),
        }
        for key, (alias, w, h) in marching_sets.items():
            sheet = self.get_sheet(alias)
            if sheet:
                self.storage[key] = sheet.extract_tiles_by_dimensions(
                    0, 0, w, h, 16, 16, self.SCALE_FACTOR
                )
        dirt_tiles = self.storage.get("DIRT")
        if dirt_tiles and len(dirt_tiles) > 11:
            self.storage["DIRT_IMAGE"] = pygame.transform.scale(
                dirt_tiles[11], (BLOCK_SIZE, BLOCK_SIZE)
            )
        detail_sheet = self.get_sheet("details")
        if detail_sheet:
            for key, rect_list in self.raw_data.items():
                storage_key = f"DETAIL_{key.upper()}"
                self.storage[storage_key] = []
                for r in rect_list:
                    tiles = detail_sheet.extract_tiles_by_dimensions(
                        r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, self.SCALE_FACTOR
                    )
                    self.storage[storage_key].extend(tiles)

    def build_marching_tile(self, tileset_key: str, layout: MarchingLayout, neighbors: list[bool], sheet_width=10) -> pygame.Surface:
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        tileset: list[pygame.Surface] | None = self.storage.get(tileset_key)
        if not tileset:
            surface.fill(self.manager.colours.get_colour("DEFAULT"))
            return surface
        quads = [
            (neighbors[0], neighbors[1], neighbors[3], neighbors[4]),
            (neighbors[1], neighbors[2], neighbors[4], neighbors[5]),
            (neighbors[3], neighbors[4], neighbors[6], neighbors[7]),
            (neighbors[4], neighbors[5], neighbors[7], neighbors[8]),
        ]
        blit_pos = [(0, 0), (QUAD_SIZE, 0), (0, QUAD_SIZE), (QUAD_SIZE, QUAD_SIZE)]
        for i, inputs in enumerate(quads):
            mask = (inputs[0]*1) + (inputs[1]*2) + (inputs[2]*4) + (inputs[3]*8)
            row, col, rotation = layout.get_variant(mask)
            index = row * sheet_width + col
            sub_tile = tileset[index]
            if rotation != 0:
                sub_tile = pygame.transform.rotate(sub_tile, rotation)
            surface.blit(sub_tile, blit_pos[i])
        return surface