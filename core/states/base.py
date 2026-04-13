
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Any
import pygame
from groups.ui_group import UIGroup
from settings import WIDTH, HEIGHT
from ui.ui_elements import Button


# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos

class GameState(ABC):
    def __init__(self, game:Game):
        self.game = game
        # Flags control how the Game stack behaves
        self.transparent: bool = False  # If True, the state below will draw first
        self.suppress_update: bool = True # If True, the state below freezes logic
        # Event Mapping Dict
        self.key_binds: dict[int, Callable] = {} # e.g. pygame.K_ESCAPE: self.func
        self.mouse_binds: dict[int, Callable[[Pos], None]] = {
            1: self.on_left_click,
            2: self.on_middle_click,
            3: self.on_right_click}

    @abstractmethod
    def update(self, dt:float, is_paused: bool = False) -> None: pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None: pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if action := self.key_binds.get(event.key): 
                action()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if action := self.mouse_binds.get(event.button): 
                action(event.pos)
        return False

    def enter_state(self) -> None: pass
    def exit_state(self) -> None: pass

    #Click actions - override in child classes
    def on_left_click(self, pos: Pos) -> None: pass
    def on_right_click(self, pos: Pos) -> None: pass
    def on_middle_click(self, pos: Pos) -> None: pass

class BaseUIState(GameState):
    """"Parent class managing a list of UI elements via the UIElementProtocol.
    (Menu, Shop, Inventory, Credits, etc)."""
    def __init__(self, game: Game):
        super().__init__(game)
        self.transparent = True     
        self.suppress_update = False
        self.ui_group = UIGroup()

    def update(self, dt:float, is_paused: bool = False) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.ui_group.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        self.ui_group.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Handle UI Clicks
        if self.ui_group.handle_event(event):
            return True
        return super().handle_event(event)
    
    def add_back_button(self, x: int | None = None, y: int | None = None, 
                       width: int = 200, height: int = 50, text: str = "Back"):
        """Adds a back button. Defaults to bottom-center if x/y are None."""
        
        # 1. Default Logic: Center it horizontally, 50px from the bottom
        final_x = x if x is not None else (WIDTH // 2) - 100
        final_y = y if y is not None else (HEIGHT - 100)

        rect = pygame.Rect(0, 0, width, height)
        rect.center = (final_x, final_y)

        # 2. Create the button and link it to the stack pop
        btn = Button.create_bordered_button(
            rect=rect, 
            text=text, 
            function=self.game.pop # Use the alias we made!
        )
        
        self.ui_group.add(btn)

        # 3. Always bind ESC to 'Back' for a better player experience
        self.key_binds[pygame.K_ESCAPE] = self.game.pop
