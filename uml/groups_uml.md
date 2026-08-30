```mermaid
classDiagram
    Group <|-- UIGroup
    Group <|-- PlantGroup
    Group <|-- CameraGroup
    Group <|-- MapTileGroup
    class Group
    class UIGroup {
        +draw()
        +elements()
        +handle_event()
        +update()
    }
    class PlantGroup {
        -__init__()
        +add()
        +get_plant_at_grid()
        +grow_all()
        +plants()
    }
    class CameraGroup {
        +display_surface
        +offset
        +offset_x
        +offset_y
        -__init__()
        +custom_draw()
        +entities()
    }
    class MapTileGroup {
        +display_surface
        +offset_x
        +offset_y
        -__init__()
        +custom_draw()
    }
```