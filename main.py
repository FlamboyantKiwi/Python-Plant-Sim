from __future__ import annotations
import sys
import pygame
from typing import TYPE_CHECKING

from settings import WIDTH, HEIGHT, FPS
from core.assets import ASSETS
from core.states import GameState, MenuState, PlayingState, ShopState, CharacterSelectState
from core.types import ShopData

if TYPE_CHECKING:  
    pass

class Game:
    def __init__(self) -> None:
        # Pygame Setup 
        pygame.init()
        pygame.display.set_caption("Freddy's Python Plant Sim")
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.tick: int = 0

        # Load Assets
        ASSETS.load_all()
        
        # State Management
        self.stack: list[GameState] = []
        
        # Start with the Menu
        self.push(MenuState(self))

    # State Logic
    def push(self, state:GameState) -> None:
        """Add a state to the top (e.g., open shop)"""
        if self.stack:
            self.stack[-1].exit_state()
        self.stack.append(state)
        state.enter_state()

    def pop(self) -> GameState|None:
        """Remove the top state (e.g., close shop)"""
        if self.stack:
            top = self.stack.pop()
            top.exit_state()
        if self.stack:
            self.stack[-1].enter_state()
        return top or None

    def change(self, state:GameState) -> None:
        """Hard switch (e.g., Menu -> Playing)"""
        while self.stack:
            self.stack.pop().exit_state()
        self.stack.append(state)
        state.enter_state()

    def peek(self) -> GameState|None:
        """Returns the current active state"""
        return self.stack[-1] if self.stack else None

    # --- Core Loop Logic ---
    def update(self) -> None:
        """Handles the multi-layered update logic."""
        if not self.stack: return
        
        current = self.stack[-1]
        # If the top state allows it, update the state beneath it as 'paused'
        if not current.suppress_update and len(self.stack) > 1:
            self.stack[-2].update(is_paused=True)
            
        current.update(is_paused=False)

    def draw(self) -> None:
        """Simple Recursive Painter: Draws everything from the floor up."""
        if not self.stack: return

        # Find the 'floor' (the first state that isn't transparent)
        start_idx = len(self.stack) - 1
        while start_idx > 0 and self.stack[start_idx].transparent:
            start_idx -= 1
            
        # Draw every layer in order. 
        for i in range(start_idx, len(self.stack)):
            self.stack[i].draw(self.screen)

    def run(self) -> None:
        """The main game loop."""
        while self.running:
            self.tick += 1
            current_state = self.peek()
            
            if not current_state: 
                self.quit()
                break
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                current_state.handle_event(event)

            # Update & Draw 
            self.update()
            self.draw()
            
            pygame.display.update()
            self.clock.tick(FPS)
    # State Transition Helpers
    def open_main_menu(self):
        self.change(MenuState(self))

    def open_character_select(self) -> None:
        """Transitions from Menu to Character Selection."""
        self.change(CharacterSelectState(self))

    def start_new_game(self, character_type) -> None:
        self.change(PlayingState(self, character_type))

    def load_save_game(self) -> None:
        """Changes to Playing state and triggers load logic."""
        self.change(PlayingState(self))

    def open_shop(self, player_ref, shop_data: ShopData) -> None:
        """Pushes the Shop menu over the current state."""
        self.push(ShopState(self, player_ref, shop_data))

    def open_credits(self) -> None: pass

    def quit(self) -> None:
        """Safely shuts down the game, cleans assets, and exits."""
        print("Initiating shutdown sequence...")
        self.running = False
        ASSETS.clean_up()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
    
    