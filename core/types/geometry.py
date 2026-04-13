from __future__ import annotations
from dataclasses import dataclass
from .enums import Direction

@dataclass(frozen=True)
class SpriteRect:
    """Defines a basic region on a sprite sheet."""
    x: int
    y: int
    w: int
    h: int

@dataclass(frozen=True)
class ScaleRect(SpriteRect):
    """Defines a region containing multiple tiles of a specific size."""
    tile_w: int
    tile_h: int

@dataclass(frozen=True)
class RectPair:
    """ Used for Fruits.
    a: The Fruit Strip (3 frames: Gold, Silver, Bronze)
    b: The Container (Crate/Basket) """
    a: SpriteRect
    b: SpriteRect


@dataclass
class AnimationGrid(dict):
    """ A dictionary-like object that auto-slices a SpriteRect into directions.
        It behaves exactly like dict[Direction, SpriteRect]."""
    def __init__(self, rect: SpriteRect, directions: list[Direction]|None = None, is_vertical: bool = True):
        super().__init__() # Initialize the underlying dict
        if directions is None:
            for d in Direction:
                self[d] = rect
            return
        count = len(directions)
        
        if count == 0: # Empty List: Default to DOWN
            self[Direction.DOWN] = rect
            return
        
        # Calculate slice dimensions
        step_h = rect.h // count if is_vertical else rect.h
        step_w = rect.w // count if not is_vertical else rect.w
        
        # Slice and populate self
        for i, direction in enumerate(directions):
            new_x = rect.x + (i * step_w if not is_vertical else 0)
            new_y = rect.y + (i * step_h if is_vertical else 0)
            
            # This assigns the key/value into the dictionary itself
            self[direction] = SpriteRect(new_x, new_y, step_w, step_h)
    @classmethod
    def non_directional(cls, rect:SpriteRect, assign_to_all:bool = True):
        """Creates an animation entry for non-directional actions (e.g., Death).
        
        assign_to_all: 
            If True, maps the SAME rect to Down, Up, Left, Right.
            (Useful if you want the same anim to play regardless of facing).
            If False, maps only to Direction.DOWN. """
        instance = cls(rect, [], True) # Empty init
        
        if assign_to_all:
            # Map the same rectangle to all directions so lookups never fail
            for d in Direction:
                instance[d] = rect
        else:
            # Just map to Down (default)
            instance[Direction.DOWN] = rect
            
        return instance

def get_axis(value: int, lessthan: Direction, greaterthan: Direction) -> Direction:
    """Returns 'lessthan' if value < 0, otherwise returns 'greaterthan'."""
    return lessthan if value < 0 else greaterthan
    
def get_direction(dx: int, dy: int, tick: int = 0) -> Direction | None:
    """Determines the primary direction based on velocity and tick cycle."""
    abs_dx, abs_dy = abs(dx), abs(dy)
    if abs_dx == 0 and abs_dy == 0:
        return None
        
    if abs_dx == abs_dy:
        if tick % 16 < 8:
            return get_axis(dx, Direction.LEFT, Direction.RIGHT)
        else:
            return get_axis(dy, Direction.UP, Direction.DOWN)

    if abs_dx > abs_dy:
        return get_axis(dx, Direction.LEFT, Direction.RIGHT)
    else: 
        return get_axis(dy, Direction.UP, Direction.DOWN)
    
