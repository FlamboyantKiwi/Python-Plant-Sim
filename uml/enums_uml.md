```mermaid
classDiagram
    class StateID {
        +CHAR_SELECT
        +HUD
        +MENU
        +PLAYING
        +SETTINGS
        +SHOP
    }
    class EntityState {
        +IDLE
        +RUN
        +WALK
    }
    class Direction {
        +DOWN
        +LEFT
        +RIGHT
        +UP
    }
    class EntityCategory {
        +FARM_ANIMALS
        +NPC
        +PLAYER
    }
    class ItemType {
        +AXE
        +BOW
        +COPPER
        +CROP
        +DAGGER
        +FRUIT
        +GENERIC
        +GOLD
        +HAMMER
        +HOE
        +IRON
        +PICKAXE
        +ROD
        +SCYTHE
        +SEED
        +SHOVEL
        +STAFF
        +STONE
        +SWORD
        +TOOL
        +WATERING_CAN
        +WOOD
        +category
        +use_id
        -__init__()
    }
    class ItemCategory {
        +CROP
        +FRUIT
        +MISC
        +SEED
        +TOOL
    }
    class ToolType {
        +AXE
        +BOW
        +DAGGER
        +GENERIC
        +HAMMER
        +HOE
        +PICKAXE
        +ROD
        +SCYTHE
        +SHOVEL
        +STAFF
        +SWORD
        +WATER
    }
    class Material {
        +COPPER
        +GOLD
        +IRON
        +WOOD
    }
    class Quality {
        +BRONZE
        +GOLD
        +SILVER
    }
    class FontType {
        +HUD
        +SLOT
    }
```