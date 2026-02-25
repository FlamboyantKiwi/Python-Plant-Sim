import sys
import pygame

from settings import WIDTH, HEIGHT, FPS
from core.asset_loader import ASSETS
from core.states import GameState, MenuState

class Game:
    def __init__(self):
        # 1. Pygame Setup
        pygame.init()
        pygame.display.set_caption("Freddy's Python Plant Sim")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.tick = 0

        # 2. Load Assets
        ASSETS.load_all()
        
        # 3. State Management
        self.stack: list[GameState] = []
        
        # Start with the Menu
        self.push(MenuState(self))

    # State Logic
    def push(self, state:GameState):
        """Add a state to the top (e.g., open shop)"""
        if self.stack:
            self.stack[-1].exit_state()
        self.stack.append(state)
        state.enter_state()

    def pop(self):
        """Remove the top state (e.g., close shop)"""
        if self.stack:
            top = self.stack.pop()
            top.exit_state()
        if self.stack:
            self.stack[-1].enter_state()

    def change(self, state:GameState):
        """Hard switch (e.g., Menu -> Playing)"""
        if self.stack:
            self.stack.pop().exit_state()
        self.stack.append(state)
        state.enter_state()

    def peek(self):
        """Returns the current active state"""
        return self.stack[-1] if self.stack else None

    def draw_previous(self):
        """Draws the state underneath the current one (for transparent menus)"""
        if len(self.stack) > 1:
            self.stack[-2].draw(self.screen)

    # Main Loop
    def run(self):
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

if __name__ == "__main__":
    game = Game()
    game.run()
    
    # Cleanup on exit
    pygame.quit()
    sys.exit()