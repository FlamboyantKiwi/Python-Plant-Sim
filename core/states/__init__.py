
from .base import GameState, BaseUIState
from .playing import PlayingState
from .menus import MenuState, ShopState, CharacterSelectState
from core.types.enums import StateID

STATES = {
    StateID.MENU: MenuState,
    StateID.PLAYING: PlayingState,
    StateID.SHOP: ShopState,
    StateID.CHAR_SELECT: CharacterSelectState
}