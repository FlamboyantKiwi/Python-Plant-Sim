from __future__ import annotations
from typing import Any
import pygame
from .. import Log
from .asset_group import AssetGroup

class ImageGroup(AssetGroup):
    """Manages standalone images (UI, backgrounds, icons) that aren't part of a spritesheet."""
    def __init__(self, manager: Any, raw_data:Any = None) -> None:
        super().__init__(manager, raw_data=raw_data)
        self.failures = set()

    def load(self) -> None:
        pass

    def get_image(self, filename: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
        if "." not in filename:
            filename = f"{filename}.png"
        key = (filename, scale)
        if key in self.storage:
            return self.storage[key]
        if filename in self.failures:
            return self.generate_fallback(filename, scale)
        try:
            full_path = self.manager.get_image_path(filename)
            img = pygame.image.load(full_path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            self.storage[key] = img
            return img
        except (pygame.error, FileNotFoundError):
            Log.error(f"Warning: Failed to load standalone image '{filename}'.")
            self.failures.add(filename)
            fallback = self.generate_fallback(filename, scale)
            self.storage[key] = fallback
            return fallback

    def generate_fallback(self, name: str, scale: tuple[int, int] | None) -> pygame.Surface:
        w, h = scale if scale else (32, 32)
        surf = pygame.Surface((w, h))
        col = self.manager.colours.get_colour(name.upper(), "HIGHLIGHT")
        surf.fill(col)
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, w, h), 1)
        return surf

    def debug_print(self) -> None:
        super().debug_print()
        if not self.failures:
            Log.success("No image load failures. All good!")
        else:
            Log.error(f" MISSING IMAGES ({len(self.failures)}):")
            for name in sorted(self.failures):
                Log.error(f"  [MISSING]   {name}")
        self.print_line_break()