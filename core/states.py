from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from entities.player import Player
from ui.hud import HUD
from ui.ui_elements import Button
from ui.InventoryUI import ShopMenu
from groups.ui_group import UIGroup
from world.level import Level
from settings import WIDTH, HEIGHT
from core.helper import draw_text
from core.asset_loader import ASSETS
from groups.camera import CameraGroup
from groups.plant_group import PlantGroup
from core.types import ShopData

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos, UIElement

class GameState(ABC):
    def __init__(self, game:Game):
        self.game = game
        # Event Mapping Dict
        self.key_binds: dict[int, Callable] = {} # e.g. pygame.K_ESCAPE: self.func
        self.mouse_binds: dict[int, Callable[[Pos], None]] = {
            1: self.on_left_click,
            2: self.on_middle_click,
            3: self.on_right_click}
        
    @abstractmethod
    def update(self)-> None: pass

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
        self.ui_group = UIGroup()

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.ui_group.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        self.ui_group.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Handle UI Clicks
        if self.ui_group.handle_event(event):
            return True
        return super().handle_event(event)

class ShopState(BaseUIState):
    def __init__(self, game:Game, player: Player, shop_data: ShopData):
        super().__init__(game)
        self.player = player
       
        self.key_binds = {
            pygame.K_ESCAPE: self.close_menu,
            pygame.K_p: self.close_menu
        }

        self.shop_menu = ShopMenu(self.player, data=shop_data) 
        self.shop_menu.is_open = True

        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128)) # Black with 50% alpha
    def update(self)-> None:
        # Update Buttons
        super().update()
        
        # Update Shop Menu explicitly
        mouse_pos = pygame.mouse.get_pos()
        self.shop_menu.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the game behind the menu (Transparent look)
        self.game.draw_previous()
        
        # Blit the pre-calculated overlay (Dim the background)
        screen.blit(self.overlay, (0, 0))

        self.shop_menu.draw(screen)
        
        # Draw Buttons
        super().draw(screen)

    def on_left_click(self, pos: Pos) -> None:
        # Check if we clicked inside the shop menu (slots/buying)
        if self.shop_menu.rect.collidepoint(pos):
            self.shop_menu.handle_click(pos)
        
        # Clicked OUTSIDE the shop menu -> Close Shop
        else:
            self.close_menu()
    def on_right_click(self, pos: Pos) -> None:
        self.close_menu()
    def close_menu(self, *args:Any) -> None:
        self.game.pop()

class PlayingState(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.all_sprites = CameraGroup()
        self.plant_group = PlantGroup()

        self.player = Player(WIDTH // 2, HEIGHT // 2, self.all_sprites)
        self.hud = HUD(self.player)

        self.level = Level(
            plant_group=self.plant_group,
            player_sprite=self.player,
            map_data=None 
        )
     
        self.level.spawn_plant("apple", 5, 5, self.all_sprites)
        self.level.spawn_plant("onion", 6, 5, self.all_sprites)

        self.key_binds = {
            pygame.K_ESCAPE: self.quit_game,
            pygame.K_p: lambda: self.open_shop("general_store")
        }

    """def add_plant_to_world(self, plant):
        #Adds a plant to the game and links it to its tile.
        target_tile = self.level.get_tile(plant.grid_x, plant.grid_y)
        if target_tile and hasattr(target_tile, 'plant'):
            setattr(target_tile, 'plant', plant)"""

    def update(self) -> None:
        # Calculate Delta Time (dt) in seconds
        dt = self.game.clock.get_time() / 1000 
        mouse_pos = pygame.mouse.get_pos()
        
        # Update world objects
        self.level.update()
        collidables = self.level.tile_list + self.plant_group.plants
        self.all_sprites.update(dt, collidables)
        self.hud.update(mouse_pos)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.plant_group.grow_all(0.1)
                    
    def draw(self, screen: pygame.Surface) -> None:
        # Draw the game world
        screen.fill(ASSETS.get_colour("WATER")) 
        
        # Draw ground tiles (passing camera offset)
        self.level.draw(self.all_sprites.offset)
        
        # Draw all entities (Y-Sorted & Camera-Offset)
        self.all_sprites.custom_draw(self.player)
            
        self.hud.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        collidables = self.level.tile_list + self.plant_group.plants
        self.player.handle_event(event, collidables)
        return super().handle_event(event)

    def on_left_click(self,pos: Pos) -> None:
        action = self.hud.handle_click(pos)
        
        if action == "OPEN_SHOP":
            self.open_shop("general_store")
            return 
        elif action:
            return  
        
    def on_right_click(self, pos: Pos) -> None:
        print("Right Click detected! (Maybe cancel action?)")
        ASSETS.debug_assets()
  
    def open_shop(self, shop_id: str = "general_store") -> None:
        """ Opens the shop state with data loaded from the database. """
        shop_data = ASSETS.get_shop_data(shop_id)

        self.game.push(ShopState(self.game, self.player, shop_data))
        
    def quit_game(self) -> None:
        self.game.running = False

class MenuState(BaseUIState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.menu_actions = {
            "New Game": self.start_new_game,
            "Continue": self.continue_game,
            "Credits": self.open_credits,
            "Quit": self.quit_game
        }
        self.create_buttons()
    
    def create_buttons(self)-> None:
        # Calculate Layout
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        gap = 60
        btn_width, btn_height = 200, 50

        for i, (text, func) in enumerate(self.menu_actions.items()):
            rect = pygame.Rect(0, 0, btn_width, btn_height)
            rect.center = (center_x, start_y + (i * gap))
            
            btn = Button.create_bordered_button(rect=rect, text=text, function=func)
            self.ui_group.add(btn)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(ASSETS.get_colour("MenuBG"))

        draw_text(screen, "Python Plant Sim", "TITLE", x=WIDTH//2, y=HEIGHT//4, 
                  colour_name="MenuTitle", align="center")
        
        super().draw(screen)

    # button actions:
    def start_new_game(self) -> None:
        print("Starting New Game...")
        # Push the playing state to the stack
        self.game.change(PlayingState(self.game))
    def continue_game(self) -> None:
        print("Loading Save...")
        # Create state, load data, then switch
        playing_state = PlayingState(self.game)
        # playing_state.load_save() # implementation depends on your save system
        self.game.change(playing_state)
    def open_credits(self) -> None:
        print("Opening Credits...")
        # self.game.state_manager.push(CreditsState(self.game))
    def quit_game(self) -> None:
        print("Quitting...")
        self.game.running = False
