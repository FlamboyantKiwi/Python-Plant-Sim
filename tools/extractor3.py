import os
from dataclasses import dataclass

import pygame

from tools.project_environment import ProjectEnv


# --- 1. Define the structures needed for the script ---
@dataclass
class SpriteRect:
    x: int
    y: int
    w: int
    h: int
    def extract_from(self, source_surf: pygame.Surface) -> pygame.Surface:
        """Safely extracts this rect's area from a given source surface."""
        if self.w <= 0 or self.h <= 0:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
            
        target = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        target.blit(source_surf, (0, 0), (self.x, self.y, self.w, self.h))
        return target

@dataclass
class CropVisualData:
    container: SpriteRect
    fruit: SpriteRect
    world_art: SpriteRect
    is_tree: bool = False

# The finalized dictionary
CROP_VISUALS = {
    # --- SINGLE HARVEST VEGETABLES ---
    "Beet": CropVisualData(
        container=SpriteRect(240, 192, 48, 16),
        fruit=SpriteRect(224, 60, 16, 32),
        world_art=SpriteRect(144, 404, 64, 36)),
    "Onion": CropVisualData(
        container=SpriteRect(48, 208, 48, 16),
        fruit=SpriteRect(192, 60, 16, 32),
        world_art=SpriteRect(144, 368, 64, 36)),
    "Cabbage": CropVisualData(
        container=SpriteRect(48, 192, 48, 16),
        fruit=SpriteRect(260, 11, 24, 32),
        world_art=SpriteRect(0, 211, 128, 24)),
    "Squash": CropVisualData(
        container=SpriteRect(96, 208, 48, 16),
        fruit=SpriteRect(0, 0, 32, 48),
        world_art=SpriteRect(0, 235, 128, 36)),
    "Cauliflower": CropVisualData(
        container=SpriteRect(0, 192, 48, 16),
        fruit=SpriteRect(128, 8, 32, 38),
        world_art=SpriteRect(0, 133, 128, 24)),
    "Melon": CropVisualData(
        container=SpriteRect(60, 160, 48, 32),
        fruit=SpriteRect(64, 0, 32, 48),
        world_art=SpriteRect(0, 280, 128, 36)),
    
    # --- REGROWING CROPS ---
    "Green Bean": CropVisualData(
        container=SpriteRect(0, 208, 48, 16),
        fruit=SpriteRect(160, 60, 16, 32),
        world_art=SpriteRect(0, 171, 128, 36)),
    "Cucumber": CropVisualData(
        container=SpriteRect(240, 144, 48, 16),
        fruit=SpriteRect(100, 60, 24, 32),
        world_art=SpriteRect(0, 53, 128, 42)),
    "Red Pepper": CropVisualData(
        container=SpriteRect(192, 160, 48, 16),
        fruit=SpriteRect(4, 60, 24, 32),
        world_art=SpriteRect(0, 95, 128, 36)),
    "Grape": CropVisualData(
        container=SpriteRect(240, 208, 48, 16),
        fruit=SpriteRect(196, 11, 24, 32),
        world_art=SpriteRect(0, 6, 128, 42)),
    "Pineapple": CropVisualData(
        container=SpriteRect(240, 160, 48, 32),
        fruit=SpriteRect(32, 0, 32, 48),
        world_art=SpriteRect(0, 316, 128, 36)),

    # --- MUSHROOMS ---
    "Mushroom": CropVisualData(
        container=SpriteRect(192, 192, 48, 16),
        fruit=SpriteRect(68, 60, 24, 32),
        world_art=SpriteRect(224, 404, 64, 36)),
    "Chestnut Mushroom": CropVisualData(
        container=SpriteRect(144, 208, 48, 16),
        fruit=SpriteRect(36, 60, 24, 32),
        world_art=SpriteRect(224, 368, 64, 36)),

    # --- TREES ---
    "Apple": CropVisualData(
        container=SpriteRect(192, 144, 48, 16),
        fruit=SpriteRect(228, 11, 24, 32),
        world_art=SpriteRect(128, 146, 255, 64),
        is_tree=True),
    "Lemon": CropVisualData(
        container=SpriteRect(240, 128, 48, 16),
        fruit=SpriteRect(128, 60, 16, 32),
        world_art=SpriteRect(128, 82, 255, 64),
        is_tree=True),
    "Plum": CropVisualData(
        container=SpriteRect(192, 208, 48, 16),
        fruit=SpriteRect(256, 60, 16, 32),
        world_art=SpriteRect(128, 4, 255, 78),
        is_tree=True),
    "Coconut": CropVisualData(
        container=SpriteRect(192, 176, 48, 16),
        fruit=SpriteRect(160, 8, 32, 38),
        world_art=SpriteRect(128, 290, 255, 78),
        is_tree=True),
    "Banana": CropVisualData(
        container=SpriteRect(0, 176, 48, 16),
        fruit=SpriteRect(96, 8, 32, 38),
        world_art=SpriteRect(128, 212, 255, 78),
        is_tree=True),

    # --- OTHERS (Missing Art) ---
    "Corn": CropVisualData(
        container=SpriteRect(0, 0, 0, 0),
        fruit=SpriteRect(0, 0, 0, 0),
        world_art=SpriteRect(0, 352, 128, 36)),
    "Sunflower": CropVisualData(
        container=SpriteRect(0, 0, 0, 0),
        fruit=SpriteRect(0, 0, 0, 0),
        world_art=SpriteRect(0, 396, 128, 36))
}

class SpriteSheetBuilder:
    """A generic, reusable engine for slicing and reconstructing sprite assets."""
    
    def __init__(self, assets_dir: str, main_file: str, alt_file: str):
        self.assets_dir = assets_dir
        self.main_sheet = self._load_source(main_file)
        self.alt_sheet = self._load_source(alt_file)

    def _load_source(self, filename: str) -> pygame.Surface:
        path = os.path.join(self.assets_dir, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing required source image: {path}")

    def _calculate_dimensions(self, items_dict: dict[str, CropVisualData]) -> dict[str, int]:
        """Calculates sizing metrics for the uniform grid."""
        max_c_w = max((data.container.w for data in items_dict.values()), default=0)
        max_f_w = max((data.fruit.w for data in items_dict.values()), default=0)
        max_w_w = max((data.world_art.w for data in items_dict.values()), default=0)
        max_row_h = max((max(data.container.h, data.fruit.h, data.world_art.h) for data in items_dict.values()), default=0)
        
        return {
            "max_c_w": max_c_w,
            "max_f_w": max_f_w,
            "max_w_w": max_w_w,
            "max_row_h": max_row_h,
            "sheet_w": max_c_w + max_f_w + max_w_w,
            "sheet_h": max_row_h * len(items_dict)
        }

    def _draw_container(self, sheet: pygame.Surface, data: CropVisualData, max_c_w: int, max_row_h: int, current_y: int) -> None:
        """Extracts and bottom-centers the container graphic."""
        if data.container.w > 0:
            c_surf = data.container.extract_from(self.alt_sheet)
            c_offset_x = (max_c_w - data.container.w) // 2
            sheet.blit(c_surf, (c_offset_x, current_y + (max_row_h - data.container.h)))

    def _draw_fruit(self, sheet: pygame.Surface, data: CropVisualData, max_c_w: int, max_f_w: int, max_row_h: int, current_y: int) -> None:
        """Extracts and bottom-centers the fruit graphic."""
        if data.fruit.w > 0:
            f_surf = data.fruit.extract_from(self.alt_sheet)
            f_offset_x = (max_f_w - data.fruit.w) // 2
            sheet.blit(f_surf, (max_c_w + f_offset_x, current_y + (max_row_h - data.fruit.h)))

    def _draw_world_art(self, sheet: pygame.Surface, crop_name: str, data: CropVisualData, max_c_w: int, max_f_w: int, max_w_w: int, max_row_h: int, current_y: int, is_tree: bool) -> None:
        """Slices and maps the growing animation frames for world art."""
        if data.world_art.w <= 0:
            return

        num_frames = 5 if is_tree else 4
        uniform_frame_w = max_w_w // num_frames
        w_x = max_c_w + max_f_w

        if is_tree:
            orig_slices = [(0, 30), (32, 30), (66, 60), (131, 60), (195, 60)]
        else:
            orig_frame_w = data.world_art.w // num_frames
            orig_slices = [(j * orig_frame_w, orig_frame_w) for j in range(num_frames)]
            
            # --- NEW: Swap 3rd and 4th states for specific re-growable crops ---
            if crop_name in ["Green Bean", "Cucumber", "Red Pepper", "Grape"]:
                orig_slices[2], orig_slices[3] = orig_slices[3], orig_slices[2]
            
        for frame_idx, (offset_x, orig_f_w) in enumerate(orig_slices):
            if orig_f_w <= 0: 
                continue
            
            frame_rect = SpriteRect(data.world_art.x + offset_x, data.world_art.y, orig_f_w, data.world_art.h)
            frame_img = frame_rect.extract_from(self.main_sheet)
            
            slot_x = w_x + (frame_idx * uniform_frame_w)
            center_offset_x = (uniform_frame_w - orig_f_w) // 2
            bottom_offset_y = max_row_h - data.world_art.h
            
            sheet.blit(frame_img, (slot_x + center_offset_x, current_y + bottom_offset_y))

    def build_group_sheet(self, items_dict: dict[str, CropVisualData], is_tree_group: bool) -> pygame.Surface | None:
        """Orchestrates dimension calculation and row rendering to build the complete sheet."""
        if not items_dict:
            return None
        
        dims = self._calculate_dimensions(items_dict)
        new_sheet = pygame.Surface((dims["sheet_w"], dims["sheet_h"]), pygame.SRCALPHA)
        
        # Unpack the crop_name from the items_dict
        for i, (crop_name, data) in enumerate(items_dict.items()):
            current_y = i * dims["max_row_h"]
            
            # Compose each section of the row using focused helper methods
            self._draw_container(new_sheet, data, dims["max_c_w"], dims["max_row_h"], current_y)
            self._draw_fruit(new_sheet, data, dims["max_c_w"], dims["max_f_w"], dims["max_row_h"], current_y)
            
            # Pass 'crop_name' down to allow specific filtering!
            self._draw_world_art(new_sheet, crop_name, data, dims["max_c_w"], dims["max_f_w"], dims["max_w_w"], dims["max_row_h"], current_y, is_tree_group)
            
        return new_sheet
    def save_sheet(self, sheet: pygame.Surface | None, filename: str) -> None:
        """Saves a generated sheet surface directly to the assets directory."""
        if sheet is None: 
            return
        out_path = os.path.join(self.assets_dir, filename)
        pygame.image.save(sheet, out_path)
        print(f"✅ Saved '{filename}' ({sheet.get_width()}x{sheet.get_height()}px) to Assets")


# ==========================================
# 3. MAIN EXECUTION PIPELINE
# ==========================================

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)

    assets_dir = ProjectEnv.ASSETS_DIR / "images"
    try:
        builder = SpriteSheetBuilder(str(assets_dir), 
            main_file="Plants.png", alt_file = "Supplies.png")
        
        # Declarative list of targets to build using our loop
        targets = [
            (False, "crops_only_sheet.png"),
            (True, "trees_only_sheet.png")
        ]

        for is_tree, filename in targets:
            filtered_data = {k: v for k, v in CROP_VISUALS.items() if v.is_tree == is_tree}
            sheet = builder.build_group_sheet(filtered_data, is_tree)
            builder.save_sheet(sheet, filename)

    except (OSError, pygame.error) as e:
        print(f"Execution failed:\n{e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()