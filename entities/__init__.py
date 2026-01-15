# Expose the main actors
# Assumes you renamed 'playerClass.py' to 'player.py'
from .player import Player

# Expose the animal base class (and specific animals if you subclass them)
from .animal import Animal

# Expose Inventory management
from .inventory import Inventory

# Expose Items
# (Assumes you kept 'item.py', or renamed it to 'items.py')
from .items import (
    Item,
)