from __future__ import annotations
from typing import Any
from src.ui.timer import Timer
from .base_wrapper import BaseWrapper

class FlashWrapper(BaseWrapper):
    """ Wraps any object that has an update() and draw() method 
    to provide flashing/blinking functionality without altering the original class."""
    def __init__(self, target: Any, interval: float = 0.25):
        super().__init__(target)
        self.interval = interval
        
        self.flash_timer = Timer(interval)
        self.is_flashing = False
        self.is_blank = False # True means the object is currently "invisible" in the blink

    def start_flash(self) -> None:
        """Begins the flashing effect."""
        self.is_flashing = True
        self.is_blank = False
        self.flash_timer.start()

    def stop_flash(self) -> None:
        """Stops the flashing and ensures the object is visible."""
        self.is_flashing = False
        self.is_blank = False

    def update(self, *args, **kwargs) -> None:
        """Updates the underlying target and handles blink timing."""
        # Always update the target object first (passing along any arguments like mouse_pos)
        self.target.update(*args, **kwargs)

        # Handle the flash timer logic
        if self.is_flashing:
            # If the timer hits 0 (update returns False)
            if not self.flash_timer.update():
                self.is_blank = not self.is_blank  # Toggle visibility
                self.flash_timer.start()        # Reset the timer for the next blink

    def draw(self, screen: Any) -> None:
        """Draws the underlying target only if it isn't in a blank flash frame."""
        if not self.is_blank:
            self.target.draw(screen)
    