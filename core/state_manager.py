class StateManager:
    def __init__(self, game):
        self.game = game
        self.stack = []

    def push(self, state):
        """Add a state to the top (e.g., open menu)"""
        if self.stack:
            self.stack[-1].exit_state() # Pause the previous state
        self.stack.append(state)
        state.enter_state()

    def pop(self):
        """Remove the top state (e.g., close menu)"""
        if self.stack:
            top = self.stack.pop()
            top.exit_state()
        
        # Resume the state below it
        if self.stack:
            self.stack[-1].enter_state()

    def change(self, state):
        """Hard switch (e.g., Main Menu -> Playing)"""
        if self.stack:
            self.stack.pop().exit_state()
        self.stack.append(state)
        state.enter_state()

    def current(self):
        return self.stack[-1] if self.stack else None
    
    def draw_previous (self, screen):
        if len(self.stack) > 1:
            self.stack[-2].draw(screen)