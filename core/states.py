# core/states.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from entities.player import Player
from entities.inventory import ShopMenu
from ui.hud import HUD
from ui.button import Button
from world.level import Level
from settings import WIDTH, HEIGHT, SHOPS
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
    def __init__(self, game:"Game", player: Player, shop_data: dict):
        super().__init__(game)
        self.player = player
       
        self.ui_elements = []

        self.shop_menu = ShopMenu(self.player, data=shop_data) 
        self.shop_menu.is_open = True
        self.ui_elements.append(self.shop_menu)

        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128)) # Black with 50% alpha

    def update(self):  
        mouse_pos = pygame.mouse.get_pos()
        # Update all UI elements (Grid, Buttons, potentially Dialogue later)
        for element in self.ui_elements:
            if hasattr(element, "update"):
                element.update(mouse_pos)

    def draw(self, screen):
        # 1. Draw the game behind the menu (Transparent look)
        self.game.state_manager.draw_previous(screen)
        
        # 2. Blit the pre-calculated overlay (Dim the background)
        screen.blit(self.overlay, (0, 0))

        # 3. Draw all UI elements
        for element in self.ui_elements:
            element.draw(screen)

    def handle_event(self, event): #### Improve
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.close_menu()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.shop_menu.rect.collidepoint(event.pos):
                self.shop_menu.handle_click(event.pos)
            else:
                self.close_menu()

    def close_menu(self):
        self.game.state_manager.pop()

class PlayingState(GameState):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.all_tiles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.hud = HUD(self.player)

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
                return # Stop processing
            elif event.key == pygame.K_p:
                self.open_shop("general_store")
                return # Stop processing
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                # Check if we hit a button or inventory slot
                action = self.hud.handle_click(event.pos)
                
                if action == "OPEN_SHOP":
                    self.open_shop("general_store")
                    return
                elif action:
                    return

        self.handle_player_input(event)

    def handle_player_input(self, event):
        """Clean separation for player controls"""
        if event.type == pygame.KEYDOWN:
            self.player.key_down(event.key, self.level.all_tiles)
        elif event.type == pygame.KEYUP:
            self.player.key_up(event.key)

    def open_shop(self, shop_id="general_store"): 
        """
        Opens the shop state with data loaded from settings.
        :param shop_id: The key matching a dictionary in settings.SHOPS
        """
        # 1. Get the data from settings
        shop_data = SHOPS.get(shop_id)
        
        if not shop_data:
            print(f"Error: Shop ID '{shop_id}' not found in settings.")
            return

        # 2. Push the Shop State, passing the specific data
        print(f"Opening Shop: {shop_data['type']}")
        self.game.state_manager.push(ShopState(self.game, self.player, shop_data))
class MenuState(GameState):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)
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
