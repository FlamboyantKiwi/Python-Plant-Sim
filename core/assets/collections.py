from __future__ import annotations
import pygame
from .base import ConfigGroup, AssetGroup
from core.types import TextConfig
from core.assets.asset_data import COLOURS, TEXT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_types import Colour
    from core.assets import AssetLoader

class TextGroup(ConfigGroup):
    """Manages TextConfig styles (presets like 'TITLE', 'HUD')."""
    def load(self) -> None:
        self.storage.update(TEXT)
        self.default = self.storage.get("default", TextConfig())


    def get_config(self, key: str) ->TextConfig:
        return self.get_val(key)
   
class ColourGroup(ConfigGroup):
    """Manages game palette and provides debug printing."""
    def __init__(self, manager: AssetLoader) -> None:
        super().__init__(manager)
        self.default = pygame.Color(255, 0, 255)

    def load(self) -> None:
        # Pygame natively converts Hex strings to Color objects!
        for name, hex_str in COLOURS.items():
            self.storage[name] = pygame.Color(hex_str)
            
        self.default = self.storage.get("DEFAULT", pygame.Color(255, 0, 255))

    def get_colour(self, name: Colour, fallback_type: Colour | None = None) -> pygame.Color:
        """Tiered lookup: Name -> Fallback -> Default."""
        
        # Try exact match
        col = self.storage.get(name)
        if col: 
            return col
        
        # Try fallback category
        if fallback_type:
            col = self.storage.get(fallback_type)
            if col: 
                return col
        
        # Fallback to generic missing logic
        return self.get_val(name) or self.default

class ImageGroup(AssetGroup):
    """Manages standalone images (UI, backgrounds, icons) 
        that aren't part of a spritesheet."""
    def __init__(self, manager: AssetLoader) -> None:
        super().__init__(manager)
        self.failures = set()
    def load(self) -> None: pass # ImageGroup loads on demand, so load() is empty
    def get_image(self, filename: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
        """Tries to get a cached image. If not found, loads from disk.
            If loading fails, generates a fallback. appends .png if missing."""
        if "." not in filename:
            filename = f"{filename}.png"
            
        # Create a unique cache key (Filename + Scale)
        # We need this because "icon.png" at 32x32 is different from "icon.png" at 64x64
        key = (filename, scale)

        # Return Cached if exists
        if key in self.storage:         
            return self.storage[key]
        # Check if we already failed this file (Prevent log spam)
        if filename in self.failures:   
            return self.generate_fallback(filename, scale)

        # Attempt Load
        try:
            full_path = self.manager.get_asset_path(filename)
            img = pygame.image.load(full_path).convert_alpha()
            
            #Adjust size of image
            if scale:   
                img = pygame.transform.scale(img, scale)
            # Store image in cache
            self.storage[key] = img
            return img

        except (pygame.error, FileNotFoundError):
            print(f"Warning: Failed to load standalone image '{filename}'.")
            self.failures.add(filename)
            
            # Create and Cache the fallback so we don't recalculate it every frame
            fallback = self.generate_fallback(filename, scale)
            self.storage[key] = fallback
            return fallback

    def generate_fallback(self, name: str, scale: tuple[int, int] | None) -> pygame.Surface:
        """Internal helper to make the pink squares."""
        w, h = scale if scale else (32, 32)
        surf = pygame.Surface((w, h))
        
        # Use our ColourGroup for the fallback colour!
        col = self.manager.colours.get_colour(name.upper(), "HIGHLIGHT")
        surf.fill(col)
        
        # Draw a little 'X' or border to show it's missing
        pygame.draw.rect(surf, (0,0,0), (0,0,w,h), 1)
        return surf
    def debug_print(self) -> None:
        super().debug_print()
        if not self.failures:
            print("No image load failures. All good!")
        else:
            print(f" MISSING IMAGES ({len(self.failures)}):")
            for name in sorted(self.failures):
                print(f"  [MISSING] • {name}")
        self.print_line_break()

class FontGroup(AssetGroup):
    """ Internal helper class to manage font caching."""
    def __init__(self, manager: AssetLoader) -> None:
        super().__init__(manager)
        
    def load(self) -> None: pass # fonts load on demand - so this isn't needed
    
    def get_font(self, config: TextConfig) -> pygame.font.Font:
        # Create a unique key for the cache
        key = (config.name, config.size, config.bold, config.italic)
        
        if key not in self.storage:
            if not pygame.font.get_init(): 
                pygame.font.init()
            # Load and store
            self.storage[key] = pygame.font.SysFont(
                config.name, config.size, config.bold, config.italic)
        return self.storage[key]

    def debug_print(self) -> None:
        super().debug_print()
        for key in self.storage:
            name, size, bold, italic = key
            styles = []
            if bold: 
                styles.append("Bold")
            if italic: 
                styles.append("Italic")
            style_str = " + ".join(styles) if styles else "Normal"
            print(f" Name: {name:<20} | Size: {size:<3} | Style: {style_str}")
        self.print_line_break()
