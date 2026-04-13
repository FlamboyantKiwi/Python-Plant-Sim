from __future__ import annotations
import sys
import pygame
from typing import TYPE_CHECKING

from settings import WIDTH, HEIGHT, FPS
from core.assets import ASSETS
from core.states import GameState, MenuState, PlayingState, ShopState
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

    def pop(self) -> None:
        """Remove the top state (e.g., close shop)"""
        if self.stack:
            top = self.stack.pop()
            top.exit_state()
        if self.stack:
            self.stack[-1].enter_state()

    def change(self, state:GameState) -> None:
        """Hard switch (e.g., Menu -> Playing)"""
        if self.stack:
            self.stack.pop().exit_state()
        self.stack.append(state)
        state.enter_state()

    def peek(self) -> GameState|None:
        """Returns the current active state"""
        return self.stack[-1] if self.stack else None

    def draw_previous(self) -> None:
        """Draws the state underneath the current one (for transparent menus)"""
        if len(self.stack) > 1:
            self.stack[-2].draw(self.screen)
            
    def update_previous(self):
        """Updates the state underneath the current one (for active backgrounds)"""
        if len(self.stack) > 1:
            self.stack[-2].update()
        

    # Main Loop
    def run(self) -> None:
        while self.running:
            self.tick += 1
            current_state = self.peek()
            
            # Safety check: If no states left, quit
            if not current_state: 
                self.running = False
                break
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                current_state.handle_event(event)

            # Update & Draw
            current_state.update()
            current_state.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(FPS)
 
    # State Transition Helpers
    def start_new_game(self) -> None:
        """Changes the current state to the Playing state."""
        self.change(PlayingState(self))

    def load_save_game(self) -> None:
        """Changes to Playing state and triggers load logic."""
        playing_state = PlayingState(self)
        # playing_state.load_save() # Add your save logic later!
        self.change(playing_state)

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
    
    