# core/states.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from entities.player import Player
from entities.inventory import ShopMenu
from ui.hud import HUD
from ui.button import Button
from world.level import Level
from settings import WIDTH, HEIGHT
from core.helper import get_colour, draw_text
import pygame

if TYPE_CHECKING:   from core.game import Game

class GameState(ABC):
    def __init__(self, game:"Game"):
        self.game = game

    @abstractmethod
    def update(self): pass

    @abstractmethod
    def draw(self, screen): pass

    @abstractmethod
    def handle_event(self, event): pass

    def enter_state(self): pass
    def exit_state(self): pass

class ShopState(GameState):
    def __init__(self, game:"Game", shop_menu:ShopMenu):
        super().__init__(game)
        self.shop_menu = shop_menu # Store the passed instance
        self.shop_menu.is_open = True

    def update(self):   pass #game is paused

    def draw(self, screen):
        # 1. Draw the game behind the menu (Transparent look)
        self.game.state_manager.draw_previous(screen)
        
        # 2. Draw a semi-transparent overlay (Dim the background)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128)) # Black with 50% alpha
        screen.blit(overlay, (0,0))

        # 3. Draw the Shop Menu
        self.shop_menu.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.close_menu()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.shop_menu.rect.collidepoint(event.pos):
                self.shop_menu.handle_click(event.pos)
            else:
                self.close_menu()

    def close_menu(self):
        self.shop_menu.is_open = False
        self.game.state_manager.pop()

class PlayingState(GameState):
    def __init__(self, game: "Game"):
        super().__init__(game)

        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.hud = HUD(self.player)
        self.shop_menu = ShopMenu(self.player)
        
        self.all_tiles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.level = Level(
            all_tiles_group=self.all_tiles,
            player_sprite=self.player,
            map_data=None 
        )

    def update(self):
        # Update the actual game world
        self.level.update()
        self.player.update(self.level.all_tiles, self.game.tick)

    def draw(self, screen):
        # Draw the game world
        screen.fill(get_colour("WATER")) # Or use settings.COLOURS
        self.all_tiles.draw(screen)
        self.all_sprites.draw(screen)
        self.hud.draw(screen)

    def handle_event(self, event):
        """ Handles user input while the game is running (Movement, Interaction, UI). """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                # Check if we hit a button or inventory slot
                action = self.hud.handle_click(event.pos)
                
                if action == "OPEN_SHOP":
                    self.open_shop()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: # Alternative Hotkey to open Shop/Pause
                self.open_shop()

            #elif event.key == pygame.K_F5: # Quick Save logic
                #self.game.level.save_map("level_data.json")

            elif event.key == pygame.K_ESCAPE:
                # Stop the 'while' loop in core/game.py
                self.game.running = False

            else: # pass to Player for movement/interaction
                self.player.key_down(event.key, self.level.all_tiles)

        # --- 3. KEYBOARD RELEASES ---
        elif event.type == pygame.KEYUP:
            # Essential for stopping player movement when key is released
            self.player.key_up(event.key)

    def open_shop(self): 
        self.game.state_manager.push(ShopState(self.game, self.shop_menu))


class MenuState(GameState):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("ariel", 80, bold=True)
        self.menu_actions = {
            "New Game": self.start_new_game,
            "Continue": self.continue_game,
            "Credits": self.open_credits,
            "Quit": self.quit_game
        }
        self.buttons = self.create_buttons()
    
    def create_buttons(self):
        buttons = []
        # Calculate Layout
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        gap = 60
        btn_width, btn_height = 200, 50

        for i, option in enumerate(self.menu_actions.keys()):
            x = center_x - (btn_width // 2)
            y = start_y + (i * gap)
            rect = pygame.Rect(x, y, btn_width, btn_height)
            
            # Create the Button Instance
            # Ensure "button_bg" exists in your assets, or pass a fallback image
            btn = Button(rect, text=option, image_filename="button_bg") 
            buttons.append(btn)
        return buttons
    
    def update(self):
        # Update hover states for all buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def draw(self, screen):
        screen.fill(get_colour("MenuBG"))
        draw_text(screen, 
                  "Python Plant Sim", 
                  self.title_font, 
                  WIDTH//2, 
                  HEIGHT//4, 
                  get_colour("MenuTitle"))
        for btn in self.buttons:
            btn.draw(screen)

    def start_new_game(self):
        print("Starting New Game...")
        # Push the playing state to the stack
        self.game.state_manager.change(PlayingState(self.game))
    def continue_game(self):
        print("Loading Save...")
        # Create state, load data, then switch
        playing_state = PlayingState(self.game)
        # playing_state.load_save() # implementation depends on your save system
        self.game.state_manager.change(playing_state)
    def open_credits(self):
        print("Opening Credits...")
        # self.game.state_manager.push(CreditsState(self.game))
    def quit_game(self):
        print("Quitting...")
        self.game.running = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #left click
            for btn in self.buttons:
                if btn.is_click(event.pos):
                    action = self.menu_actions.get(btn.text)
                    if action:
                        action()







